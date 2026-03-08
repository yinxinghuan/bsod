#!/usr/bin/env python3
"""Generate BSOD game poster with Laisa character via Flux2 Klein."""

import json, time, random, urllib.request, urllib.parse, shutil, os

COMFYUI_URL = "http://127.0.0.1:8188"
IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src/BSOD/img")
os.makedirs(IMG_DIR, exist_ok=True)

# Square poster: 1024x1024
W, H = 1024, 1024

PROMPT = (
    "game key art poster, anime illustration style, "
    "young woman streamer, long straight blue hair no bangs hair swept behind ears forehead fully visible, "
    "large black over-ear headphones with small cat ears on top, "
    "black oversized hoodie, pale skin, blue eyes, "
    "sitting at a glowing gaming desk, multiple monitors showing streaming interface and chat, "
    "dark rainy night atmosphere, neon blue and purple glow from screens, "
    "dramatic lighting, cinematic composition, "
    "tired but determined expression, looking at camera, "
    "rain streaks on window behind her, city lights blurred in background, "
    "dark moody color palette, blue and purple tones, volumetric light from monitors, "
    "bold title text \"BSOD\" at the top center in large glowing blue letters, "
    "subtitle text \"BLUE SCREEN OF DOOM\" below the title in smaller white letters, "
    "high quality anime game art, detailed, atmospheric"
)

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
              "inputs": {"steps": 4, "width": W, "height": H}},
        "10": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "11": {"class_type": "SamplerCustomAdvanced",
               "inputs": {"noise": ["7", 0], "guider": ["6", 0], "sampler": ["10", 0],
                          "sigmas": ["9", 0], "latent_image": ["8", 0]}},
        "12": {"class_type": "VAEDecode",
               "inputs": {"samples": ["11", 0], "vae": ["3", 0]}},
        "13": {"class_type": "SaveImage",
               "inputs": {"images": ["12", 0], "filename_prefix": "bsod_poster"}},
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
    print(f"  → {os.path.basename(out_path)}  ({os.path.getsize(out_path)//1024} KB)")


if __name__ == "__main__":
    try:
        v = api_get("/system_stats").get("system", {}).get("comfyui_version", "?")
        print(f"ComfyUI v{v} — generating BSOD poster ({W}x{H})\n")
    except Exception as e:
        print(f"Cannot connect: {e}"); exit(1)

    seed = random.randint(0, 2**32 - 1)
    print(f"[bsod_poster] seed={seed}")
    wf = build_workflow(PROMPT, seed)
    pid = api_post("/prompt", {"prompt": wf})["prompt_id"]
    print(f"  id: {pid[:8]}...")
    entry = wait(pid)
    for node_out in entry["outputs"].values():
        for img in node_out.get("images", []):
            out = os.path.join(IMG_DIR, "poster.png")
            download(img["filename"], img["subfolder"], out)
            break

    print(f"\nDone! → {IMG_DIR}/poster.png")
