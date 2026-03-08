"""
Generate 5 pixel art stat icons (256×256) then trim to tight bounding box.
Saved to src/BSOD/img/icon_<stat>.png with transparent background.
"""
import json, time, urllib.request, urllib.parse, random
from pathlib import Path

try:
    from PIL import Image
    import numpy as np
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("WARNING: Pillow not found, skipping background removal")

API = "http://127.0.0.1:8188"
OUT = Path(__file__).parent / "src/BSOD/img"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 256, 256

ICONS = {
    "icon_energy": (
        "pixel art icon, single lightning bolt symbol, bright yellow, "
        "bold chunky pixel style, centered on pure black background, "
        "16-bit retro game icon style, no anti-aliasing, clean hard edges, "
        "simple flat shape, vibrant yellow #FFD700, black background"
    ),
    "icon_mood": (
        "pixel art icon, simple heart shape, bright pink-red color, "
        "chunky pixel style, centered on pure black background, "
        "16-bit retro game icon, no anti-aliasing, hard pixel edges, "
        "simple flat heart, vibrant pink #FF69B4, black background"
    ),
    "icon_focus": (
        "pixel art icon, simple eye symbol or bullseye target circle, "
        "bright purple color, chunky pixel style, centered on pure black background, "
        "16-bit retro game icon, no anti-aliasing, hard pixel edges, "
        "simple flat shape, vibrant purple #C084FC, black background"
    ),
    "icon_followers": (
        "pixel art icon, simple person silhouette or star shape, "
        "bright pink color, chunky pixel style, centered on pure black background, "
        "16-bit retro game icon, no anti-aliasing, hard pixel edges, "
        "simple flat shape, vibrant pink #F472B6, black background"
    ),
    "icon_connection": (
        "pixel art icon, two interlocked chain links or chain symbol, "
        "bright cyan-blue color, chunky pixel style, centered on pure black background, "
        "16-bit retro game icon, no anti-aliasing, hard pixel edges, "
        "simple flat shape, vibrant cyan #38BDF8, black background"
    ),
}

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
               "inputs": {"images": ["12", 0], "filename_prefix": "icon"}},
    }

def post(wf):
    data = json.dumps({"prompt": wf}).encode()
    req = urllib.request.Request(f"{API}/prompt", data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["prompt_id"]

def wait(pid, timeout=300):
    start = time.time()
    while time.time() - start < timeout:
        with urllib.request.urlopen(f"{API}/history/{pid}") as r:
            h = json.loads(r.read())
        if pid in h:
            return h[pid]
        time.sleep(2)
    raise TimeoutError

def download_bytes(filename):
    url = f"{API}/view?filename={urllib.parse.quote(filename)}&type=output"
    with urllib.request.urlopen(url) as r:
        return r.read()

def remove_black_bg(img_bytes, threshold=40):
    """Remove near-black background, keep colored icon pixels."""
    import io
    img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    arr = np.array(img, dtype=np.float32)
    r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    brightness = (r + g + b) / 3.0
    # mask: dark pixels become transparent
    alpha = np.clip((brightness - threshold) / 40.0, 0, 1)
    arr[:,:,3] = (alpha * 255).astype(np.uint8)
    result = Image.fromarray(arr.astype(np.uint8), "RGBA")
    # Trim to bounding box of non-transparent pixels
    bbox = result.getbbox()
    if bbox:
        result = result.crop(bbox)
    out = io.BytesIO()
    result.save(out, format="PNG")
    return out.getvalue()

seed = random.randint(0, 2**32)
for name, prompt in ICONS.items():
    print(f"\n→ {name}")
    pid = post(build_workflow(prompt, seed))
    print(f"  submitted {pid[:8]}...", end=" ", flush=True)
    result = wait(pid)
    imgs = []
    for v in result.get("outputs", {}).values():
        imgs.extend(v.get("images", []))
    if not imgs:
        print("ERROR: no output")
        continue
    raw = download_bytes(imgs[0]["filename"])
    dest = OUT / f"{name}.png"
    if HAS_PIL:
        dest.write_bytes(remove_black_bg(raw))
        print(f"saved (bg removed) → {dest.name}")
    else:
        dest.write_bytes(raw)
        print(f"saved (no bg removal) → {dest.name}")
    seed += 1

print("\n✓ Done")
