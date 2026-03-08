#!/usr/bin/env python3
"""Generate BSOD night room background — indie music chaos aesthetic.

Two key directions:
1. Extreme entropy/hikikomori: floor invisible under piled items, cables
   dominate every surface, notes hanging from ceiling, entropy has won
2. Indie music identity: vinyl records + turntable prominent, band posters
   (punk/alternative/classic rock — Ramones, Nirvana, The Doors, Pink Floyd,
   Metallica, Joy Division), NOT anime / K-pop / mainstream gaming culture
"""

import json, time, random, urllib.request, urllib.parse, shutil, os

COMFYUI_URL = "http://127.0.0.1:8188"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")
os.makedirs(OUT_DIR, exist_ok=True)

STYLE = (
    "anime visual novel background art, painterly soft shading, clean linework, "
    "detailed interior illustration, no characters, no people, "
    "2D game background, side view"
)

WINDOW = (
    "large window on back wall, heavy rain streaking down the glass, "
    "dark rainy night city outside, tall buildings with lit windows far away, "
    "neon signs glowing through rain, window condensation, "
    "dark curtains half-drawn"
)

# INDIE MUSIC IDENTITY — the most important aesthetic layer
INDIE_MUSIC = (
    # Vinyl + turntable as centrepiece
    "vintage turntable record player on the floor surrounded by vinyl record sleeves, "
    "dozens of vinyl records leaning against the wall in crates, "
    "record sleeves spread across the floor like a carpet, "
    "album covers visible: black and white punk band posters, "
    # Band posters on walls — punk / alternative / classic rock
    "walls covered in band posters: Ramones logo, Nirvana logo, The Doors poster, "
    "Pink Floyd dark side of the moon prism poster, Joy Division unknown pleasures poster, "
    "Metallica black album poster, Radiohead poster, "
    "posters overlapping each other, some torn at edges, "
    "concert ticket stubs pinned to wall, "
    "a guitar leaning against the wall, "
    "cassette tapes and CD cases scattered on shelves, "
    "a bass guitar case half-open on the floor, "
    "band stickers on the mini fridge door"
)

# ENTROPY CHAOS — the lived-in collapse
ENTROPY = (
    # Floor almost invisible
    "floor completely buried under: clothes in piles, vinyl records, "
    "empty instant noodle cups, crumpled paper, tangled headphone cables, "
    "power strips with cables fanning out in all directions, "
    "empty coffee mugs, overflowing ashtray, "
    "cardboard boxes never unpacked stacked in corner, "
    # Hanging elements from ceiling
    "strings of polaroid photos hanging from ceiling on clothespins, "
    "fairy lights tangled along ceiling edge, "
    "sticky note papers hanging from strings above the desk, "
    "a dreamcatcher tangled with cables near the window, "
    # Desk: maximum clutter
    "desk completely buried: monitor with sticky notes on bezel, "
    "microphone arm, keyboard hidden under papers, "
    "energy drink cans lined along desk edge, "
    "takeout boxes stacked on corner of desk, "
    "cables absolutely everywhere tangling everything, "
    # Shelves overflowing
    "bookshelves crammed with books spine-out AND face-out mixed, "
    "items balanced on top of items, stacks threatening to fall, "
    "a broken lamp tucked into the shelf, "
    # General chaos
    "laundry piled on the single chair, "
    "no clear path across the floor, "
    "total organized chaos of a person who gave up cleaning months ago"
)

LIGHTING = (
    "room lit only by monitor blue glow and dim warm fairy lights, "
    "deep blue-purple ambient night, moody dark atmosphere, "
    "soft shadows in corners, screen light reflecting on vinyl records"
)

BASE_PROMPT = f"{STYLE}, {WINDOW}, {INDIE_MUSIC}, {ENTROPY}, {LIGHTING}"

TESTS = [
    {
        "name": "bg_indie_A",
        "w": 432, "h": 936,
        "prompt": BASE_PROMPT + (
            ", portrait orientation, tall room view, "
            "turntable prominent in lower foreground area"
        ),
    },
    {
        "name": "bg_indie_B",
        "w": 432, "h": 936,
        "prompt": BASE_PROMPT + (
            ", portrait orientation, tall room view, "
            "guitar leaning against wall in center, "
            "band posters dominating back wall, "
            "vinyl crates along the base"
        ),
    },
    {
        "name": "bg_indie_C",
        "w": 432, "h": 936,
        "prompt": BASE_PROMPT + (
            ", portrait orientation, tall room view, "
            "emphasize hanging polaroids and fairy lights from ceiling, "
            "floor entirely covered in records and clothes, "
            "deep atmospheric night mood"
        ),
    },
]


def build_workflow(prompt, seed, w, h):
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
              "inputs": {"steps": 6, "width": w, "height": h}},
        "10": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "11": {"class_type": "SamplerCustomAdvanced",
               "inputs": {"noise": ["7", 0], "guider": ["6", 0], "sampler": ["10", 0],
                          "sigmas": ["9", 0], "latent_image": ["8", 0]}},
        "12": {"class_type": "VAEDecode",
               "inputs": {"samples": ["11", 0], "vae": ["3", 0]}},
        "13": {"class_type": "SaveImage",
               "inputs": {"images": ["12", 0], "filename_prefix": "bg_indie"}},
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
                    raise RuntimeError("ComfyUI reported an error")
                if entry.get("outputs"):
                    print(f"  done ({int(time.time()-start)}s)")
                    return entry
        except RuntimeError:
            raise
        except Exception:
            pass
        time.sleep(3)
        print(f"  ... {int(time.time()-start)}s", flush=True, end="\r")
    raise TimeoutError("timeout waiting for ComfyUI")

def download(filename, subfolder, out_path):
    params = urllib.parse.urlencode({"filename": filename, "subfolder": subfolder, "type": "output"})
    with urllib.request.urlopen(f"{COMFYUI_URL}/view?{params}", timeout=60) as r:
        with open(out_path, "wb") as f:
            shutil.copyfileobj(r, f)
    print(f"  -> {os.path.basename(out_path)}  ({os.path.getsize(out_path)//1024} KB)")


if __name__ == "__main__":
    try:
        v = api_get("/system_stats").get("system", {}).get("comfyui_version", "?")
        print(f"ComfyUI v{v} — indie chaos room ({len(TESTS)} variants)\n")
    except Exception as e:
        print(f"Cannot connect to ComfyUI: {e}"); exit(1)

    for t in TESTS:
        print(f"\n[{t['name']}]  {t['w']}x{t['h']}")
        seed = random.randint(0, 2**32 - 1)
        wf = build_workflow(t["prompt"], seed, t["w"], t["h"])
        pid = api_post("/prompt", {"prompt": wf})["prompt_id"]
        print(f"  id: {pid[:8]}...")
        entry = wait(pid)
        for node_out in entry["outputs"].values():
            for img in node_out.get("images", []):
                out = os.path.join(OUT_DIR, f"{t['name']}.png")
                download(img["filename"], img["subfolder"], out)
                break

    print("\nAll done! Check test_output/bg_indie_A/B/C.png")
