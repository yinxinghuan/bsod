#!/usr/bin/env python3
"""
Generate Isaya condition-state sprites (worn / rundown / wreck) via ComfyUI,
then auto-remove the grey background.

Run:
  python3 gen_isaya_condition.py
"""

import json, time, random, urllib.request, urllib.parse, shutil, os, sys
import numpy as np
from PIL import Image

COMFYUI_URL = "http://127.0.0.1:8188"
IMG_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src/BSOD/img")
os.makedirs(IMG_DIR, exist_ok=True)

# ── Prompt base — must match the VN sprites exactly ───────────────────────────

BASE = (
    "anime visual novel character sprite, full body, "
    "young woman, long straight blue hair, no bangs, no fringe, "
    "forehead fully visible, hair falls straight down on both sides of face, "
    "middle part, clean forehead, "
    "large black over-ear headphones resting on top of head covering ears, "
    "black oversized hoodie, dark shorts, pale skin, soft blue eyes, "
    "standing pose, centered, "
    "simple flat light grey background #999999, "
    "anime illustration style, soft cel shading, clean linework, "
    "expressive eyes, detailed face"
)

SPRITES = [
    {
        "name": "isaya_worn",
        "prompt": BASE + (
            ", mild fatigue, slight dark circles under eyes, "
            "slightly tired half-lidded eyes, hair a little messy at the ends only, "
            "hoodie slightly wrinkled, arms hanging loosely at sides, "
            "mildly drained expression, still holding it together"
        ),
    },
    {
        "name": "isaya_rundown",
        "prompt": BASE + (
            ", moderate exhaustion, obvious dark circles under eyes, "
            "dull pale complexion, hair ends noticeably messy and tangled, "
            "hunched posture, shoulders drooping, "
            "hollow tired eyes, blank distant expression, clearly worn out"
        ),
    },
    {
        "name": "isaya_wreck",
        "prompt": BASE + (
            ", severe exhaustion and burnout, deep sunken dark circles under eyes, "
            "hair very disheveled and tangled at ends, very pale almost grey skin, "
            "hollow cheeks, dead flat eyes with no spark, "
            "heavily slouched barely standing posture, "
            "completely drained, running on empty"
        ),
    },
]

W, H = 512, 768


# ── ComfyUI helpers ────────────────────────────────────────────────────────────

def build_workflow(prompt, seed):
    return {
        "1": {"class_type": "UNETLoader",
              "inputs": {"unet_name": "flux-2-klein-4b.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader",
              "inputs": {"clip_name": "qwen_3_4b.safetensors", "type": "flux2"}},
        "3": {"class_type": "VAELoader",
              "inputs": {"vae_name": "flux2-vae.safetensors"}},
        "4": {"class_type": "CLIPTextEncode",
              "inputs": {"text": prompt, "clip": ["2", 0]}},
        "5": {"class_type": "ConditioningZeroOut",
              "inputs": {"conditioning": ["4", 0]}},
        "6": {"class_type": "CFGGuider",
              "inputs": {"model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0], "cfg": 1.0}},
        "7": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
        "8": {"class_type": "EmptyFlux2LatentImage",
              "inputs": {"width": W, "height": H, "batch_size": 1}},
        "9": {"class_type": "Flux2Scheduler",
              "inputs": {"steps": 6, "width": W, "height": H}},
        "10": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "11": {"class_type": "SamplerCustomAdvanced",
               "inputs": {"noise": ["7", 0], "guider": ["6", 0], "sampler": ["10", 0],
                          "sigmas": ["9", 0], "latent_image": ["8", 0]}},
        "12": {"class_type": "VAEDecode",
               "inputs": {"samples": ["11", 0], "vae": ["3", 0]}},
        "13": {"class_type": "SaveImage",
               "inputs": {"images": ["12", 0], "filename_prefix": "isaya_condition"}},
    }


def api_post(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(f"{COMFYUI_URL}{path}", data=body,
                                  headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def api_get(path):
    with urllib.request.urlopen(f"{COMFYUI_URL}{path}", timeout=30) as r:
        return json.loads(r.read())

def wait(prompt_id, timeout=600):
    start = time.time()
    while time.time() - start < timeout:
        try:
            h = api_get(f"/history/{prompt_id}")
            if prompt_id in h:
                entry = h[prompt_id]
                if entry.get("status", {}).get("status_str") == "error":
                    raise RuntimeError("ComfyUI error")
                if entry.get("outputs"):
                    print(f"  done ({int(time.time()-start)}s)")
                    return entry
        except RuntimeError:
            raise
        except Exception:
            pass
        time.sleep(3)
        print(f"  ... {int(time.time()-start)}s", flush=True, end="\r")
    raise TimeoutError("timeout")

def download(filename, subfolder, out_path):
    params = urllib.parse.urlencode({"filename": filename, "subfolder": subfolder, "type": "output"})
    with urllib.request.urlopen(f"{COMFYUI_URL}/view?{params}", timeout=60) as r:
        with open(out_path, "wb") as f:
            shutil.copyfileobj(r, f)
    print(f"  -> {os.path.basename(out_path)}  ({os.path.getsize(out_path)//1024} KB)")


# ── Background removal — same as remove_bg.py ─────────────────────────────────

FEATHER = 20
MARGIN  = 0.02

def remove_grey_bg(img_path, target_grey=152, threshold=28):
    img = Image.open(img_path).convert("RGBA")
    orig_w, orig_h = img.size
    data = np.array(img, dtype=np.float32)
    r, g, b = data[:, :, 0], data[:, :, 1], data[:, :, 2]

    dist = np.sqrt(
        (r - target_grey) ** 2 +
        (g - target_grey) ** 2 +
        (b - target_grey) ** 2
    )

    alpha_remove = np.clip(1.0 - (dist - threshold) / FEATHER, 0.0, 1.0)
    data[:, :, 3] = data[:, :, 3] * (1.0 - alpha_remove)
    result = Image.fromarray(data.astype(np.uint8))

    alpha = np.array(result)[:, :, 3]
    rows  = np.any(alpha > 10, axis=1)
    cols  = np.any(alpha > 10, axis=0)
    if not rows.any():
        result.save(img_path)
        return

    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]

    pad_h = int((rmax - rmin) * MARGIN)
    pad_w = int((cmax - cmin) * MARGIN)
    rmin  = max(0, rmin - pad_h)
    rmax  = min(orig_h - 1, rmax + pad_h)
    cmin  = max(0, cmin - pad_w)
    cmax  = min(orig_w - 1, cmax + pad_w)

    cropped = result.crop((cmin, rmin, cmax + 1, rmax + 1))
    crop_w, crop_h = cropped.size
    scale  = min(orig_w / crop_w, orig_h / crop_h)
    scaled = cropped.resize((int(crop_w * scale), int(crop_h * scale)), Image.LANCZOS)

    canvas = Image.new("RGBA", (orig_w, orig_h), (0, 0, 0, 0))
    canvas.paste(scaled, ((orig_w - scaled.width) // 2, orig_h - scaled.height))
    canvas.save(img_path)
    print(f"  bg removed -> {os.path.basename(img_path)}  ({os.path.getsize(img_path)//1024} KB)")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        v = api_get("/system_stats").get("system", {}).get("comfyui_version", "?")
        print(f"ComfyUI v{v} — generating {len(SPRITES)} condition sprites\n")
    except Exception as e:
        print(f"Cannot connect to ComfyUI: {e}")
        print("Please start ComfyUI first.")
        sys.exit(1)

    for s in SPRITES:
        print(f"\n[{s['name']}]")
        seed = random.randint(0, 2**32 - 1)
        wf = build_workflow(s["prompt"], seed)
        pid = api_post("/prompt", {"prompt": wf})["prompt_id"]
        print(f"  prompt_id: {pid[:8]}...")
        entry = wait(pid)

        out_path = os.path.join(IMG_DIR, f"{s['name']}.png")
        for node_out in entry["outputs"].values():
            for img in node_out.get("images", []):
                download(img["filename"], img["subfolder"], out_path)
                break

        print(f"  removing background...")
        remove_grey_bg(out_path)

    print(f"\nAll done! -> {IMG_DIR}")
    print("Sprites: isaya_worn.png, isaya_rundown.png, isaya_wreck.png")
