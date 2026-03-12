#!/usr/bin/env python3
"""
Generate BSOD game poster via online AI API (img2img with Laisa ref).

Usage: ~/miniconda3/bin/python3 generate_poster.py
"""

import datetime
import hashlib
import hmac
import json
import os
import ssl
import subprocess
import sys
import time
import urllib.request
import urllib.error
import urllib.parse

API_URL     = "http://aiservice.wdabuliu.com:8019/genl_image"
API_TIMEOUT = 360
USER_ID     = 123456

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

# ── Cloudflare R2 ──────────────────────────────────────────────────────────
R2_ACCOUNT_ID  = "bdccd2c68ff0d2e622994d24dbb1bae3"
R2_ACCESS_KEY  = "b203adb7561b4f8800cbc1fa02424467"
R2_SECRET_KEY  = "e7926e4175b7a0914496b9c999afd914cd1e4af7db8f83e0cf2bfad9773fa2b0"
R2_BUCKET      = "aigram"

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
REF_PATH    = os.path.join(SCRIPT_DIR, "laisa_idle_square.png")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "src/BSOD/img/poster.png")

PROMPT = (
    "epic video game poster art, 1:1 square aspect ratio, anime illustration style, "
    "young woman with long straight blue hair, pale skin, blue-grey eyes, "
    "wearing black oversized hoodie, large black headphones on top of head covering ears, "
    "she is trapped inside a cracked glowing computer monitor screen, "
    "hands pressing against the glass from inside, desperate yet beautiful expression, "
    "the monitor displays blue screen of death error text and glitch artifacts, "
    "dark room background with only the monitor glow illuminating her face, "
    "digital glitch effects, scanlines, pixel corruption around the edges, "
    "dramatic blue and cyan lighting from the screen, deep shadows, "
    'huge bold glowing neon blue title letters B S O D spelled out "BSOD" at the top, '
    "professional game cover art, 8k quality, atmospheric, cinematic lighting"
)


def _sign(key, msg):
    return hmac.new(key, msg.encode(), hashlib.sha256).digest()


def upload_ref(path: str) -> str:
    """Upload ref image to Cloudflare R2 → public CDN URL."""
    with open(path, 'rb') as f:
        data = f.read()

    obj_key    = "refs/" + os.path.basename(path)
    host       = f"{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
    now        = datetime.datetime.utcnow()
    amz_date   = now.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = now.strftime("%Y%m%d")
    region     = "auto"
    service    = "s3"

    content_type = "image/png"
    content_hash = hashlib.sha256(data).hexdigest()
    canon_uri    = "/" + R2_BUCKET + "/" + urllib.parse.quote(obj_key, safe="/")

    canon_headers = (
        f"content-type:{content_type}\n"
        f"host:{host}\n"
        f"x-amz-content-sha256:{content_hash}\n"
        f"x-amz-date:{amz_date}\n"
    )
    signed_headers = "content-type;host;x-amz-content-sha256;x-amz-date"

    canon_req = "\n".join([
        "PUT", canon_uri, "",
        canon_headers, signed_headers, content_hash,
    ])

    cred_scope = f"{date_stamp}/{region}/{service}/aws4_request"
    str_to_sign = "\n".join([
        "AWS4-HMAC-SHA256", amz_date, cred_scope,
        hashlib.sha256(canon_req.encode()).hexdigest(),
    ])

    k_date    = _sign(("AWS4" + R2_SECRET_KEY).encode(), date_stamp)
    k_region  = _sign(k_date, region)
    k_service = _sign(k_region, service)
    k_signing = _sign(k_service, "aws4_request")
    signature = hmac.new(k_signing, str_to_sign.encode(), hashlib.sha256).hexdigest()

    auth = (
        f"AWS4-HMAC-SHA256 Credential={R2_ACCESS_KEY}/{cred_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )

    url = f"https://{host}/{R2_BUCKET}/{urllib.parse.quote(obj_key, safe='/')}"
    req = urllib.request.Request(url, data=data, method="PUT", headers={
        "Content-Type": content_type,
        "Host": host,
        "x-amz-content-sha256": content_hash,
        "x-amz-date": amz_date,
        "Authorization": auth,
    })

    with urllib.request.urlopen(req, timeout=60, context=_SSL_CTX) as resp:
        resp.read()

    public_url = f"https://images.aiwaves.tech/{obj_key}"
    print(f"  Uploaded ref -> {public_url}")
    return public_url


def call_api(ref_url: str, prompt: str) -> str | None:
    payload = json.dumps({
        "query": "",
        "params": {
            "url": ref_url,
            "prompt": prompt,
            "user_id": USER_ID,
        },
    }).encode()

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    print("  Calling API (may take ~200s)...", flush=True)
    try:
        with urllib.request.urlopen(req, timeout=API_TIMEOUT) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            result = json.loads(body)
        except Exception:
            print(f"  ERROR: HTTP {e.code} — {body}")
            return None

    code = result.get("code")
    if code == 200:
        return result["url"]
    if code == 429:
        return "RATE_LIMIT"
    print(f"  API returned code={code}: {result}")
    return None


def download_image(url: str, out_path: str) -> None:
    print(f"  Downloading result...")
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)

    src_ext = os.path.splitext(url.split("?")[0])[1].lower()
    dst_ext = os.path.splitext(out_path)[1].lower()
    tmp_path = out_path if src_ext == dst_ext else out_path + src_ext

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60, context=_SSL_CTX) as resp:
        data = resp.read()
    with open(tmp_path, "wb") as f:
        f.write(data)

    if src_ext != dst_ext and dst_ext in (".png", ".jpg", ".jpeg"):
        fmt = "png" if dst_ext == ".png" else "jpeg"
        subprocess.run(["sips", "-s", "format", fmt, tmp_path, "--out", out_path],
                       check=True, capture_output=True)
        os.remove(tmp_path)
        print(f"  Converted {src_ext} -> {dst_ext}")
    elif tmp_path != out_path:
        os.rename(tmp_path, out_path)

    size_kb = os.path.getsize(out_path) // 1024
    print(f"  Saved -> {out_path}  ({size_kb} KB)")


def main():
    print("BSOD Poster Generator (Online API, img2img)")
    print(f"Ref: {REF_PATH}")
    print(f"Output: {OUTPUT_PATH}\n")

    # Upload reference image
    print("Uploading reference image...")
    ref_url = upload_ref(REF_PATH)

    # Generate
    while True:
        result_url = call_api(ref_url, PROMPT)
        if result_url == "RATE_LIMIT":
            print("  Rate limited — waiting 78s...")
            time.sleep(78)
            continue
        break

    if not result_url:
        print("ERROR: Generation failed")
        sys.exit(1)

    print(f"  Result URL: {result_url}")
    download_image(result_url, OUTPUT_PATH)
    print("\nDone!")


if __name__ == "__main__":
    main()
