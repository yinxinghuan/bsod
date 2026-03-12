#!/usr/bin/env python3
"""Test sprite styles for BSOD — streetwear pixel + top-down."""

import json, time, random, urllib.request, urllib.parse, shutil, os

COMFYUI_URL = "http://127.0.0.1:8188"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")
os.makedirs(OUT_DIR, exist_ok=True)

ISAYA = (
    "young woman, long straight blue hair, large black over-ear headphones, "
    "black oversized hoodie, pale skin, cat ears"
)
NEG_SPRITE = (
    "worst quality, low quality, blurry, watermark, text, deformed, "
    "smooth shading, gradient, anti-aliasing, photorealistic, 3d, chibi, super deformed"
)
NEG_TOPDOWN = (
    "worst quality, low quality, blurry, watermark, text, deformed, "
    "side view, portrait, front view, smooth shading, gradient"
)

TESTS = [
    # ── Streetwear style (matching reference) ────────────────────────────
    {
        "name": "sprite_streetwear_A",
        "w": 512, "h": 768,
        "steps": 32, "cfg": 8.0, "lora": 1.2,
        "neg": NEG_SPRITE,
        "prompt": (
            f"pixel art character, {ISAYA}, "
            "full body standing pose, facing forward, "
            "flat color pixel art, no gradients, no dithering, "
            "hard clean pixel edges, chunky visible pixels, "
            "dark purple background, small drop shadow under feet, "
            "streetwear urban fashion style, "
            "Valenberg pixel art style, bold silhouette"
        ),
    },
    {
        "name": "sprite_streetwear_B",
        "w": 384, "h": 640,
        "steps": 32, "cfg": 8.5, "lora": 1.3,
        "neg": NEG_SPRITE,
        "prompt": (
            f"16-bit pixel art character sprite, {ISAYA}, "
            "standing idle, front facing, "
            "flat colors only, bold pixel blocks, visible pixel grid, "
            "no anti-aliasing, retro game sprite style, "
            "dark background, clean isolated character, "
            "strong color contrast, defined silhouette"
        ),
    },
    # ── Top-down with character ───────────────────────────────────────────
    {
        "name": "topdown_room_with_char",
        "w": 768, "h": 768,
        "steps": 32, "cfg": 7.5, "lora": 0.9,
        "neg": NEG_TOPDOWN,
        "prompt": (
            "pixel art top-down RPG room interior, "
            "streamer bedroom bird's eye overhead view, "
            "desk with PC monitors, bed with dark bedding, bookshelf, "
            "cozy rug on wooden floor, warm lamp light, "
            "small pixel art character with blue hair standing in center of room, "
            "Stardew Valley style, atmospheric top-down perspective, "
            "detailed pixel art, dark cozy atmosphere"
        ),
    },
]


def build_workflow(prompt, neg, seed, w, h, steps, cfg, lora):
    return {
        "1": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": "juggernautXL_ragnarokBy.safetensors"}},
        "2": {"class_type": "LoraLoader",
              "inputs": {"model": ["1", 0], "clip": ["1", 1],
                         "lora_name": "pixel-art-xl.safetensors",
                         "strength_model": lora, "strength_clip": lora}},
        "3": {"class_type": "CLIPTextEncode",
              "inputs": {"text": prompt, "clip": ["2", 1]}},
        "4": {"class_type": "CLIPTextEncode",
              "inputs": {"text": neg, "clip": ["2", 1]}},
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
              "inputs": {"images": ["7", 0], "filename_prefix": "topdown_test"}},
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
    print(f"  → {os.path.basename(out_path)}  ({os.path.getsize(out_path)//1024} KB)")


if __name__ == "__main__":
    try:
        v = api_get("/system_stats").get("system", {}).get("comfyui_version", "?")
        print(f"ComfyUI v{v} ready\n")
    except Exception as e:
        print(f"Cannot connect: {e}"); exit(1)

    for t in TESTS:
        print(f"\n[{t['name']}]  {t['w']}x{t['h']}, LoRA={t['lora']}")
        seed = random.randint(0, 2**32 - 1)
        wf = build_workflow(t["prompt"], t["neg"], seed, t["w"], t["h"],
                            t["steps"], t["cfg"], t["lora"])
        pid = api_post("/prompt", {"prompt": wf})["prompt_id"]
        print(f"  id: {pid[:8]}...")
        entry = wait(pid)
        for node_out in entry["outputs"].values():
            for img in node_out.get("images", []):
                out = os.path.join(OUT_DIR, f"{t['name']}.png")
                download(img["filename"], img["subfolder"], out)
                break

    print("\nAll done!")
