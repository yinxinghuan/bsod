#!/usr/bin/env python3
"""
Generate BSOD game assets:
  - Room backgrounds x4 (morning / afternoon / evening / night)
  - Isaya pixel sprites x3 (idle-front, walk-left, walk-right)

Output: src/BSOD/img/
Run:    python3 generate_assets.py
"""

import json, time, random, urllib.request, urllib.parse, shutil, os

COMFYUI_URL = "http://127.0.0.1:8188"
IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src/BSOD/img")
os.makedirs(IMG_DIR, exist_ok=True)

NEG = (
    "worst quality, low quality, blurry, watermark, text, deformed, 3d, photo, "
    "cat ears, animal ears, nekomimi, extra limbs, multiple people"
)

ROOM_BASE = (
    "pixel art bedroom, streamer's room, "
    "desk with dual PC monitors on the left side, gaming chair, "
    "cozy single bed with dark bedding on the right side, "
    "large window in the center background showing city skyline, "
    "shelves with figures and plants, black cat curled on bed, "
    "wooden floor with visible pixel grain, side-view interior, "
    "fine detailed pixel art, small pixel size, 16-bit indie game background, "
    "no characters, empty room"
)

ISAYA_BASE = (
    "pixel art character sprite, young woman, long straight blue hair, "
    "large black over-ear headphones, black oversized hoodie, dark shorts, "
    "pale skin, blue-grey eyes, full body, "
    "fine detailed pixel art, small pixel size, clean edges"
)

ASSETS = [
    # ── Room backgrounds ────────────────────────────────────────────────────
    {
        "name": "bg_morning",
        "out": "bg_morning.png",
        "w": 1024, "h": 640, "steps": 30, "cfg": 7.5, "lora": 0.85,
        "prompt": ROOM_BASE + ", "
            "morning light, warm golden sunrise streaming through window, "
            "soft amber and cream tones, dust particles in sunbeams, "
            "peaceful quiet morning atmosphere, monitors off",
    },
    {
        "name": "bg_afternoon",
        "out": "bg_afternoon.png",
        "w": 1024, "h": 640, "steps": 30, "cfg": 7.5, "lora": 0.85,
        "prompt": ROOM_BASE + ", "
            "bright afternoon daylight, clear blue sky outside window, "
            "natural white light filling the room, clean and bright, "
            "one monitor on showing game footage, energetic daytime feel",
    },
    {
        "name": "bg_evening",
        "out": "bg_evening.png",
        "w": 1024, "h": 640, "steps": 30, "cfg": 7.5, "lora": 0.85,
        "prompt": ROOM_BASE + ", "
            "evening sunset, orange and purple gradient sky outside window, "
            "warm orange glow mixing with monitor blue light, "
            "both monitors on showing stream overlay, cozy golden hour",
    },
    {
        "name": "bg_night",
        "out": "bg_night.png",
        "w": 1024, "h": 640, "steps": 30, "cfg": 7.5, "lora": 0.85,
        "prompt": ROOM_BASE + ", "
            "deep night, dark blue-purple sky with city lights outside window, "
            "room lit only by glowing monitors casting blue light, "
            "rain droplets on window glass, atmospheric and moody, "
            "streaming setup glowing, ring light on, very atmospheric",
    },

    # ── Isaya sprites ───────────────────────────────────────────────────────
    {
        "name": "isaya_pixel_idle",
        "out": "isaya_pixel_idle.png",
        "w": 512, "h": 768, "steps": 32, "cfg": 7.0, "lora": 0.85,
        "prompt": ISAYA_BASE + ", "
            "standing idle pose, facing slightly forward, neutral expression, "
            "solid flat grey background #808080, centered in frame",
    },
    {
        "name": "isaya_pixel_walk_right",
        "out": "isaya_pixel_walk_right.png",
        "w": 512, "h": 768, "steps": 32, "cfg": 7.0, "lora": 0.85,
        "prompt": ISAYA_BASE + ", "
            "walking pose, facing right, mid-stride, slight forward lean, "
            "solid flat grey background #808080, centered in frame",
    },
    {
        "name": "isaya_pixel_happy",
        "out": "isaya_pixel_happy.png",
        "w": 512, "h": 768, "steps": 32, "cfg": 7.0, "lora": 0.85,
        "prompt": ISAYA_BASE + ", "
            "standing, smiling happily, slight head tilt, one hand raised in small wave, "
            "bright cheerful expression, solid flat grey background, centered in frame",
    },
    {
        "name": "isaya_pixel_sad",
        "out": "isaya_pixel_sad.png",
        "w": 512, "h": 768, "steps": 32, "cfg": 7.0, "lora": 0.85,
        "prompt": ISAYA_BASE + ", "
            "standing, looking down, sad tired expression, shoulders slightly slumped, "
            "melancholy mood, solid flat grey background, centered in frame",
    },
]


def build_workflow(prompt, seed, w, h, steps, cfg, lora_strength):
    return {
        "1": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": "juggernautXL_ragnarokBy.safetensors"}},
        "2": {"class_type": "LoraLoader",
              "inputs": {"model": ["1", 0], "clip": ["1", 1],
                         "lora_name": "pixel-art-xl.safetensors",
                         "strength_model": lora_strength,
                         "strength_clip": lora_strength}},
        "3": {"class_type": "CLIPTextEncode",
              "inputs": {"text": prompt, "clip": ["2", 1]}},
        "4": {"class_type": "CLIPTextEncode",
              "inputs": {"text": NEG, "clip": ["2", 1]}},
        "5": {"class_type": "EmptyLatentImage",
              "inputs": {"width": w, "height": h, "batch_size": 1}},
        "6": {"class_type": "KSampler",
              "inputs": {"model": ["2", 0], "positive": ["3", 0], "negative": ["4", 0],
                         "latent_image": ["5", 0], "seed": seed,
                         "control_after_generate": "fixed",
                         "steps": steps, "cfg": cfg,
                         "sampler_name": "dpmpp_2m", "scheduler": "karras",
                         "denoise": 1.0}},
        "7": {"class_type": "VAEDecode",
              "inputs": {"samples": ["6", 0], "vae": ["1", 2]}},
        "8": {"class_type": "SaveImage",
              "inputs": {"images": ["7", 0], "filename_prefix": "bsod_asset"}},
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

def wait(prompt_id, timeout=400):
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
    kb = os.path.getsize(out_path) // 1024
    print(f"  → {os.path.basename(out_path)}  ({kb} KB)")


if __name__ == "__main__":
    try:
        v = api_get("/system_stats").get("system", {}).get("comfyui_version", "?")
        print(f"ComfyUI v{v} ready — generating {len(ASSETS)} assets\n")
    except Exception as e:
        print(f"Cannot connect: {e}"); exit(1)

    for a in ASSETS:
        print(f"[{a['name']}]  {a['w']}x{a['h']}")
        seed = random.randint(0, 2**32 - 1)
        wf = build_workflow(a["prompt"], seed, a["w"], a["h"], a["steps"], a["cfg"], a["lora"])
        pid = api_post("/prompt", {"prompt": wf})["prompt_id"]
        print(f"  id: {pid[:8]}...")
        entry = wait(pid)
        for node_out in entry["outputs"].values():
            for img in node_out.get("images", []):
                out = os.path.join(IMG_DIR, a["out"])
                download(img["filename"], img["subfolder"], out)
                break

    print(f"\nAll done! → {IMG_DIR}")
