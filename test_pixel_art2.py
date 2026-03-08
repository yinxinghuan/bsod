#!/usr/bin/env python3
"""Test round 2 — no cat ears, finer pixel grain."""

import json, time, random, urllib.request, urllib.parse, shutil, os

COMFYUI_URL = "http://127.0.0.1:8188"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")
os.makedirs(OUT_DIR, exist_ok=True)

LAISA = (
    "young woman, long straight blue hair, large black over-ear headphones (no animal ears, no cat ears), "
    "black oversized hoodie, pale skin, blue-grey eyes, black cat nearby"
)
NEG = (
    "worst quality, low quality, blurry, watermark, text, deformed, 3d, photo, "
    "cat ears, animal ears, nekomimi, kemonomimi, cat hood, ear accessories"
)

TESTS = [
    {
        "name": "room_fine_pixel",
        "w": 1024, "h": 1024,
        "steps": 32, "cfg": 7.5, "lora_strength": 0.85,
        "prompt": (
            f"fine detailed pixel art, {LAISA}, "
            "sitting at glowing computer desk in dark bedroom at night, "
            "dual monitors casting blue light, rain on window, city lights outside, "
            "lo-fi cozy aesthetic, deep blue purple night palette, "
            "high resolution fine pixel art, small pixel size, intricate details, "
            "indie game illustration, atmospheric lighting, black cat sleeping on desk"
        ),
    },
    {
        "name": "sprite_fine_pixel",
        "w": 640, "h": 960,
        "steps": 32, "cfg": 7.0, "lora_strength": 0.85,
        "prompt": (
            f"fine pixel art character sprite, {LAISA}, "
            "full body standing idle pose, slight three-quarter angle, "
            "clean solid color background, detailed fine pixel art, "
            "small pixel size, high resolution pixel art, "
            "indie RPG character sprite, expressive face, no cat ears"
        ),
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
              "inputs": {"images": ["7", 0], "filename_prefix": "bsod_test2"}},
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

def wait(prompt_id, timeout=300):
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
    print(f"  → {out_path}  ({os.path.getsize(out_path)//1024} KB)")


if __name__ == "__main__":
    try:
        v = api_get("/system_stats").get("system", {}).get("comfyui_version", "?")
        print(f"ComfyUI v{v} ready\n")
    except Exception as e:
        print(f"Cannot connect: {e}"); exit(1)

    for t in TESTS:
        print(f"\n[{t['name']}]  {t['w']}x{t['h']}, {t['steps']} steps, LoRA={t['lora_strength']}")
        seed = random.randint(0, 2**32 - 1)
        wf = build_workflow(t["prompt"], seed, t["w"], t["h"], t["steps"], t["cfg"], t["lora_strength"])
        pid = api_post("/prompt", {"prompt": wf})["prompt_id"]
        print(f"  prompt_id: {pid[:8]}...")
        entry = wait(pid)
        for node_out in entry["outputs"].values():
            for img in node_out.get("images", []):
                out = os.path.join(OUT_DIR, f"{t['name']}.png")
                download(img["filename"], img["subfolder"], out)
                break

    print("\nAll done!")
