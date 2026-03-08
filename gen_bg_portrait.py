#!/usr/bin/env python3
"""Generate portrait-format full-screen room background for BSOD game."""

import json, time, random, urllib.request, urllib.parse, shutil, os

COMFYUI_URL = "http://127.0.0.1:8188"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 432, 936  # portrait, ~9:19.5 ratio

STYLE = (
    "anime illustration style, visual novel background art, "
    "painterly soft shading, highly detailed interior, "
    "no characters in scene"
)

ROOM = (
    "streamer studio apartment interior, portrait orientation, "
    "full room visible from floor to ceiling, wide angle view, "
    # Window - large, prominent
    "large floor-to-ceiling window on the back wall showing rainy night city outside, "
    "heavy rain streaking down glass, city buildings with lit windows, "
    "neon signs glowing purple and blue through rain, wet glass reflections, "
    "dark curtain pulled to one side, "
    # Desk area - right side
    "L-shaped desk on right side with two glowing monitors, "
    "mechanical keyboard RGB backlight, mic arm with condenser mic, ring light, "
    "six empty energy drink cans on desk edge, sticky notes on monitors, "
    "headphones on monitor, snack wrappers, external hard drives stacked, "
    "gaming chair with hoodie draped over it, "
    "PC tower on floor with blue LED strips, cables tangled on floor, "
    "small black cat sleeping curled under desk, "
    # Bed area - left side
    "low bed against left wall, dark rumpled sheets piled up, "
    "plushie on pillow, clothes thrown on bed, "
    "tall bookshelf beside bed overflowing with manga and figurines, "
    # Walls
    "walls covered with overlapping anime posters and polaroid photos, "
    "LED strip along ceiling glowing dim blue-purple, "
    "sticky notes on wall near desk, "
    # Floor
    "floor littered with clothes, empty bottles, power strip with cables, "
    "pizza box near wall, gaming controller on floor"
)

VARIANTS = [
    {
        "name": "bg_portrait_A",
        "prompt": f"{STYLE}, {ROOM}, "
                  "late night, room lit only by monitor blue glow and LED strips, "
                  "deep blue-purple ambient, moody dark cozy atmosphere",
    },
    {
        "name": "bg_portrait_B",
        "prompt": f"{STYLE}, {ROOM}, "
                  "midnight, warm orange desk lamp on left mixing with cool monitor blue, "
                  "rain on window, city neon outside, intimate cluttered space",
    },
    {
        "name": "bg_portrait_C",
        "prompt": f"{STYLE}, {ROOM}, "
                  "late night, only the monitors are on, deep darkness in corners, "
                  "blue-white screen light dramatically illuminating the room, "
                  "rain outside, very moody cinematic",
    },
]


def build_workflow(prompt, seed):
    return {
        "1":  {"class_type": "UNETLoader",           "inputs": {"unet_name": "flux-2-klein-4b.safetensors", "weight_dtype": "default"}},
        "2":  {"class_type": "CLIPLoader",            "inputs": {"clip_name": "qwen_3_4b.safetensors", "type": "flux2"}},
        "3":  {"class_type": "VAELoader",             "inputs": {"vae_name": "flux2-vae.safetensors"}},
        "4":  {"class_type": "CLIPTextEncode",        "inputs": {"text": prompt, "clip": ["2", 0]}},
        "5":  {"class_type": "ConditioningZeroOut",   "inputs": {"conditioning": ["4", 0]}},
        "6":  {"class_type": "CFGGuider",             "inputs": {"model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0], "cfg": 1.0}},
        "7":  {"class_type": "RandomNoise",           "inputs": {"noise_seed": seed}},
        "8":  {"class_type": "EmptyFlux2LatentImage", "inputs": {"width": W, "height": H, "batch_size": 1}},
        "9":  {"class_type": "Flux2Scheduler",        "inputs": {"steps": 6, "width": W, "height": H}},
        "10": {"class_type": "KSamplerSelect",        "inputs": {"sampler_name": "euler"}},
        "11": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["7", 0], "guider": ["6", 0], "sampler": ["10", 0], "sigmas": ["9", 0], "latent_image": ["8", 0]}},
        "12": {"class_type": "VAEDecode",             "inputs": {"samples": ["11", 0], "vae": ["3", 0]}},
        "13": {"class_type": "SaveImage",             "inputs": {"images": ["12", 0], "filename_prefix": "bg_portrait"}},
    }


def api_post(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(f"{COMFYUI_URL}{path}", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def api_get(path):
    with urllib.request.urlopen(f"{COMFYUI_URL}{path}", timeout=30) as r:
        return json.loads(r.read())

def wait(pid, timeout=600):
    start = time.time()
    while time.time() - start < timeout:
        try:
            h = api_get(f"/history/{pid}")
            if pid in h:
                entry = h[pid]
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


if __name__ == "__main__":
    try:
        v = api_get("/system_stats").get("system", {}).get("comfyui_version", "?")
        print(f"ComfyUI v{v} — portrait room backgrounds ({len(VARIANTS)} variants)\n")
    except Exception as e:
        print(f"Cannot connect: {e}"); exit(1)

    for v in VARIANTS:
        print(f"\n[{v['name']}]  {W}x{H}")
        seed = random.randint(0, 2**32-1)
        wf = build_workflow(v["prompt"], seed)
        pid = api_post("/prompt", {"prompt": wf})["prompt_id"]
        print(f"  id: {pid[:8]}...")
        entry = wait(pid)
        for node_out in entry["outputs"].values():
            for img in node_out.get("images", []):
                out = os.path.join(OUT_DIR, f"{v['name']}.png")
                download(img["filename"], img["subfolder"], out)
                break

    print("\nAll done!")
