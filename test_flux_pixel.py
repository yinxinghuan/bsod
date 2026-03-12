#!/usr/bin/env python3
"""Test Flux2 Klein — pure prompt vs RetroAnimeFluxV1 LoRA for pixel art sprites."""

import json, time, random, urllib.request, urllib.parse, shutil, os

COMFYUI_URL = "http://127.0.0.1:8188"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")
os.makedirs(OUT_DIR, exist_ok=True)

ISAYA = (
    "young woman with long straight blue hair, large black over-ear headphones, "
    "black oversized hoodie, pale skin, cat ears, black cat nearby"
)

TESTS = [
    # ── Pure Flux2 Klein, no LoRA ─────────────────────────────────────────
    {
        "name": "flux_pure_chibi",
        "lora": None,
        "w": 512, "h": 768,
        "prompt": (
            f"pixel art character sprite, {ISAYA}, "
            "chibi proportions, large head small body, "
            "full body standing idle pose, facing forward, "
            "flat color pixel art, small pixel size, clean pixel edges, "
            "solid light grey background, centered, "
            "indie game character, soft shading, expressive face"
        ),
    },
    {
        "name": "flux_pure_topdown",
        "lora": None,
        "w": 768, "h": 768,
        "prompt": (
            "pixel art top-down RPG bedroom interior, "
            "streamer's cozy room seen from above, bird's eye view, "
            "PC desk with glowing monitors on left, bed with dark sheets on right, "
            "bookshelf, rug on wooden floor, window with city view, "
            "warm lamp light, black cat on desk, "
            "Stardew Valley style, soft pixel art, atmospheric lighting, "
            "detailed top-down room, no characters"
        ),
    },
    # ── Flux2 Klein + RetroAnimeFluxV1 LoRA ───────────────────────────────
    {
        "name": "flux_retro_chibi",
        "lora": "RetroAnimeFluxV1.safetensors",
        "lora_strength": 1.0,
        "w": 512, "h": 768,
        "prompt": (
            f"pixel art character sprite, {ISAYA}, "
            "chibi proportions, large head small body, "
            "full body standing idle pose, facing forward, "
            "retro anime pixel art style, soft shading, "
            "solid light background, centered, expressive cute face"
        ),
    },
    {
        "name": "flux_retro_room",
        "lora": "RetroAnimeFluxV1.safetensors",
        "lora_strength": 0.8,
        "w": 768, "h": 768,
        "prompt": (
            "pixel art top-down RPG bedroom, streamer room from above, "
            "PC desk with monitors, bed, bookshelf, window, cozy rug, "
            "warm lamp atmosphere, black cat sleeping, "
            "retro anime pixel art style, Stardew Valley cozy feel, "
            "detailed room interior, no characters"
        ),
    },
]


def build_workflow_no_lora(prompt, seed, w, h):
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
              "inputs": {"width": w, "height": h, "batch_size": 1}},
        "9": {"class_type": "Flux2Scheduler",
              "inputs": {"steps": 4, "width": w, "height": h}},
        "10": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "11": {"class_type": "SamplerCustomAdvanced",
               "inputs": {"noise": ["7", 0], "guider": ["6", 0], "sampler": ["10", 0],
                          "sigmas": ["9", 0], "latent_image": ["8", 0]}},
        "12": {"class_type": "VAEDecode",
               "inputs": {"samples": ["11", 0], "vae": ["3", 0]}},
        "13": {"class_type": "SaveImage",
               "inputs": {"images": ["12", 0], "filename_prefix": "flux_test"}},
    }


def build_workflow_lora(prompt, seed, w, h, lora_name, lora_strength):
    return {
        "1": {"class_type": "UNETLoader",
              "inputs": {"unet_name": "flux-2-klein-4b.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader",
              "inputs": {"clip_name": "qwen_3_4b.safetensors", "type": "flux2"}},
        "3": {"class_type": "VAELoader",
              "inputs": {"vae_name": "flux2-vae.safetensors"}},
        "14": {"class_type": "LoraLoader",
               "inputs": {"model": ["1", 0], "clip": ["2", 0],
                          "lora_name": lora_name,
                          "strength_model": lora_strength,
                          "strength_clip": lora_strength}},
        "4": {"class_type": "CLIPTextEncode",
              "inputs": {"text": prompt, "clip": ["14", 1]}},
        "5": {"class_type": "ConditioningZeroOut",
              "inputs": {"conditioning": ["4", 0]}},
        "6": {"class_type": "CFGGuider",
              "inputs": {"model": ["14", 0], "positive": ["4", 0], "negative": ["5", 0], "cfg": 1.0}},
        "7": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
        "8": {"class_type": "EmptyFlux2LatentImage",
              "inputs": {"width": w, "height": h, "batch_size": 1}},
        "9": {"class_type": "Flux2Scheduler",
              "inputs": {"steps": 4, "width": w, "height": h}},
        "10": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "11": {"class_type": "SamplerCustomAdvanced",
               "inputs": {"noise": ["7", 0], "guider": ["6", 0], "sampler": ["10", 0],
                          "sigmas": ["9", 0], "latent_image": ["8", 0]}},
        "12": {"class_type": "VAEDecode",
               "inputs": {"samples": ["11", 0], "vae": ["3", 0]}},
        "13": {"class_type": "SaveImage",
               "inputs": {"images": ["12", 0], "filename_prefix": "flux_test"}},
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
        time.sleep(2)
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
        print(f"ComfyUI v{v} ready  (Flux2 Klein — 4 steps)\n")
    except Exception as e:
        print(f"Cannot connect: {e}"); exit(1)

    for t in TESTS:
        print(f"\n[{t['name']}]  {t['w']}x{t['h']}  lora={t.get('lora', 'none')}")
        seed = random.randint(0, 2**32 - 1)
        if t["lora"]:
            wf = build_workflow_lora(t["prompt"], seed, t["w"], t["h"],
                                     t["lora"], t.get("lora_strength", 1.0))
        else:
            wf = build_workflow_no_lora(t["prompt"], seed, t["w"], t["h"])
        pid = api_post("/prompt", {"prompt": wf})["prompt_id"]
        print(f"  id: {pid[:8]}...")
        entry = wait(pid)
        for node_out in entry["outputs"].values():
            for img in node_out.get("images", []):
                out = os.path.join(OUT_DIR, f"{t['name']}.png")
                download(img["filename"], img["subfolder"], out)
                break

    print("\nAll done!")
