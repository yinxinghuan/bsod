#!/usr/bin/env python3
"""
Generate Isaya condition sprites (worn / rundown / wreck) via online img2img API,
then auto-remove the grey background.

Usage:
  python3 gen_isaya_condition_online.py
"""

import json, os, ssl, sys, time, tempfile, urllib.request, urllib.error
from PIL import Image
import math
from collections import deque

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src/BSOD/img")
REF_URL = "https://raw.githubusercontent.com/yinxinghuan/bsod/master/src/BSOD/img/isaya_idle.png"

API_URL     = "http://aiservice.wdabuliu.com:8019/genl_image"
UPLOAD_URL  = "https://0x0.st"
API_TIMEOUT = 90
RATE_WAIT   = 78
USER_ID     = "bsod_game"

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

# ── Character base — mirrors gen_isaya_vn.py BASE exactly ─────────────────────

BASE = (
    "anime visual novel character sprite, full body, "
    "young woman, long straight blue hair, NO BANGS, NO FRINGE, "
    "forehead completely clear and visible, hair parted in the middle, "
    "hair falls straight down on both sides of face, hair behind ears, "
    "large black over-ear headphones on top of head covering ears, "
    "black oversized hoodie, dark shorts, pale skin, soft blue eyes, "
    "standing pose, centered, "
    "solid flat bright green background #00FF00, green screen background, "
    "anime illustration style, soft cel shading, clean linework"
)

SPRITES = [
    {
        "name": "isaya_worn",
        "prompt": BASE + (
            ", mild fatigue state, "
            "slight dark circles under eyes, slightly tired half-lidded eyes, "
            "hair ends slightly messy (NOT the top, only the ends), "
            "hoodie slightly wrinkled, arms hanging loosely, "
            "mildly drained but still composed expression"
        ),
    },
    {
        "name": "isaya_rundown",
        "prompt": BASE + (
            ", moderate exhaustion state, "
            "obvious dark circles under eyes, dull pale complexion, "
            "hair ends noticeably tangled and messy (NOT adding bangs or fringe), "
            "hunched posture, shoulders drooping forward, "
            "hollow tired eyes, blank distant expression, clearly worn out"
        ),
    },
    {
        "name": "isaya_wreck",
        "prompt": BASE + (
            ", severe burnout and exhaustion state, "
            "deep sunken dark circles, very pale almost grey skin tone, "
            "hair very disheveled and tangled at ends (still no bangs, still parted in middle), "
            "hollow cheeks, completely dead flat eyes, "
            "heavily slouched posture barely standing, running on empty"
        ),
    },
]

# ── Helpers ────────────────────────────────────────────────────────────────────

def make_grey_ref(src_path: str) -> str:
    """Composite transparent sprite onto grey background → temp PNG."""
    img = Image.open(src_path).convert("RGBA")
    bg  = Image.new("RGBA", img.size, (153, 153, 153, 255))
    bg.paste(img, mask=img.split()[3])
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    bg.convert("RGB").save(tmp.name)
    return tmp.name


def upload(path: str) -> str:
    print(f"  ↑ uploading reference to 0x0.st…")
    with open(path, "rb") as f:
        data = f.read()
    boundary = "----FormBoundary7MA4YWxkTrZu0gW"
    filename  = os.path.basename(path)
    body  = f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode()
    body += b"Content-Type: image/png\r\n\r\n"
    body += data
    body += f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        UPLOAD_URL, data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30, context=_SSL_CTX) as r:
        url = r.read().decode().strip()
    print(f"  ✓ {url}")
    return url


def call_api(ref_url: str, prompt: str) -> str | None:
    payload = json.dumps({
        "query": "",
        "params": {"url": ref_url, "prompt": prompt, "user_id": USER_ID},
    }).encode()
    req = urllib.request.Request(
        API_URL, data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=API_TIMEOUT) as r:
            result = json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            result = json.loads(body)
        except Exception:
            sys.exit(f"HTTP {e.code}: {body}")
    code = result.get("code")
    if code == 200:
        return result["url"]
    if code == 429:
        raise RuntimeError("rate_limit")
    print(f"  ✗ API code={code}")
    return None


def download(url: str, out_path: str) -> None:
    print(f"  ↓ downloading…")
    src_ext = os.path.splitext(url.split("?")[0])[1].lower()
    tmp = out_path + src_ext if src_ext != ".png" else out_path
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30, context=_SSL_CTX) as r:
        data = r.read()
    with open(tmp, "wb") as f:
        f.write(data)
    if tmp != out_path:
        import subprocess
        subprocess.run(["sips", "-s", "format", "png", tmp, "--out", out_path],
                       check=True, capture_output=True)
        os.remove(tmp)
    print(f"  ✓ saved ({os.path.getsize(out_path)//1024} KB)")


def remove_bg(img_path: str, threshold=40, feather=20) -> None:
    """Flood-fill from edges to remove green screen background."""
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size
    pixels = list(img.getdata())

    # Target: bright green #00FF00 — but API may shift it, so detect from corners
    corner_samples = [pixels[0], pixels[w-1], pixels[(h-1)*w], pixels[h*w-1], pixels[w//2]]
    opaque = [(r,g,b) for r,g,b,a in corner_samples if a > 128]
    if not opaque:
        print(f"  already transparent"); return
    tr = sum(c[0] for c in opaque) // len(opaque)
    tg = sum(c[1] for c in opaque) // len(opaque)
    tb = sum(c[2] for c in opaque) // len(opaque)
    print(f"  bg=({tr},{tg},{tb})")

    def dist(r,g,b): return math.sqrt((r-tr)**2+(g-tg)**2+(b-tb)**2)

    # Flood-fill BFS from all edges
    visited = bytearray(w * h)
    queue = deque()
    for x in range(w):
        for y in [0, h-1]:
            idx = y*w+x
            if not visited[idx] and dist(*pixels[idx][:3]) < threshold+feather:
                visited[idx] = 1; queue.append(idx)
    for y in range(h):
        for x in [0, w-1]:
            idx = y*w+x
            if not visited[idx] and dist(*pixels[idx][:3]) < threshold+feather:
                visited[idx] = 1; queue.append(idx)
    while queue:
        idx = queue.popleft()
        x, y = idx % w, idx // w
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < w and 0 <= ny < h:
                nidx = ny*w+nx
                if not visited[nidx]:
                    if dist(*pixels[nidx][:3]) < threshold+feather:
                        visited[nidx] = 1; queue.append(nidx)
                    else:
                        visited[nidx] = 2

    new_pixels = []
    for idx, (r,g,b,a) in enumerate(pixels):
        if visited[idx] == 1:
            d = dist(r,g,b)
            remove = max(0.0, min(1.0, 1.0-(d-threshold)/feather))
            new_pixels.append((r,g,b, int(a*(1-remove))))
        else:
            new_pixels.append((r,g,b,a))

    result = Image.new("RGBA", (w,h))
    result.putdata(new_pixels)
    result.save(img_path)
    print(f"  ✓ bg removed ({os.path.getsize(img_path)//1024} KB)")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Using reference: {REF_URL}")
    ref_url = REF_URL

    for i, s in enumerate(SPRITES):
        print(f"\n[{i+1}/{len(SPRITES)}] {s['name']}")
        out_path = os.path.join(IMG_DIR, f"{s['name']}.png")

        while True:
            try:
                result_url = call_api(ref_url, s["prompt"])
            except RuntimeError:
                print(f"  ⏳ rate limited — waiting {RATE_WAIT}s…")
                time.sleep(RATE_WAIT)
                continue
            break

        if not result_url:
            print(f"  ✗ generation failed, skipping")
            continue

        download(result_url, out_path)
        print(f"  removing background…")
        remove_bg(out_path)

        if i < len(SPRITES) - 1:
            print(f"  ⏳ waiting {RATE_WAIT}s before next request…")
            time.sleep(RATE_WAIT)

    print(f"\n── Done ──")
    print(f"isaya_worn / isaya_rundown / isaya_wreck → {IMG_DIR}")
