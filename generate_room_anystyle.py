#!/usr/bin/env python3
"""
Generate BSOD assets in anime illustration style (no pixel art):
  - Room backgrounds x4 time-of-day variants
  - Isaya character sprites x4 poses

Based on room_ultra_B composition: cluttered streamer studio apartment,
flat side view, wide horizontal, anime VN background style.
"""

import json, time, random, urllib.request, urllib.parse, shutil, os

COMFYUI_URL = "http://127.0.0.1:8188"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src/BSOD/img")
os.makedirs(OUT_DIR, exist_ok=True)
TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")
os.makedirs(TEST_DIR, exist_ok=True)

ROOM_STYLE = (
    "anime illustration style, visual novel background art, "
    "detailed interior scene, painterly soft shading, "
    "flat orthographic side view, no perspective distortion, "
    "parallel horizontal floor lines, 2D side-scrolling game background, "
    "no characters in scene"
)

ROOM_LAYOUT = (
    # Left zone
    "small kitchen counter on far left with microwave, electric kettle, "
    "mini fridge covered in stickers and magnets, small folding table with takeout boxes, "
    # Bed/living zone
    "low bed with dark rumpled sheets and plushies, "
    "tall bookshelf overflowing with manga volumes and anime figurines, "
    "clothes draped over chair, anime posters on walls, polaroid photos pinned in clusters, "
    # Window - dominant feature
    "large floor-to-ceiling window in center-background, "
    # PC zone
    "L-desk with dual glowing monitors, mechanical keyboard, mic arm, ring light, "
    "gaming chair, PC tower on floor with LED glow, "
    "energy drink cans, cables tangled on floor, small black cat curled under desk, "
    # Right zone
    "bathroom door slightly ajar on far right, jacket hung on wall hook, "
    "LED strips along ceiling edge"
)

ROOM_ASSETS = [
    {
        "name": "bg_night",
        "out": "bg_night.png",
        "w": 1280, "h": 576,
        "prompt": (
            f"{ROOM_STYLE}, {ROOM_LAYOUT}, "
            "late night atmosphere, room lit only by glowing monitors and RGB LED strips, "
            "deep blue-purple ambient light, heavy rain streaming down window glass, "
            "wet city lights and neon signs blurred outside window, "
            "moody dark cozy atmosphere, monitor glow casting blue light on everything"
        ),
    },
    {
        "name": "bg_evening",
        "out": "bg_evening.png",
        "w": 1280, "h": 576,
        "prompt": (
            f"{ROOM_STYLE}, {ROOM_LAYOUT}, "
            "golden evening sunset through window, orange-purple gradient sky outside, "
            "warm golden light mixing with cool monitor glow, "
            "dust particles in sunbeams, both monitors on with stream overlay, "
            "cozy golden hour atmosphere"
        ),
    },
    {
        "name": "bg_morning",
        "out": "bg_morning.png",
        "w": 1280, "h": 576,
        "prompt": (
            f"{ROOM_STYLE}, {ROOM_LAYOUT}, "
            "soft morning light through window, warm golden sunrise outside, "
            "pale yellow-white natural light filling the room, "
            "monitors off or in sleep mode, peaceful quiet morning, "
            "slight haze and soft shadows, cozy morning atmosphere"
        ),
    },
    {
        "name": "bg_afternoon",
        "out": "bg_afternoon.png",
        "w": 1280, "h": 576,
        "prompt": (
            f"{ROOM_STYLE}, {ROOM_LAYOUT}, "
            "bright afternoon daylight, clear blue sky outside window, "
            "strong natural white light from window, sharp defined shadows, "
            "one monitor on showing game footage, energetic daytime feel, "
            "room clearly visible in full detail"
        ),
    },
]

ISAYA_BASE = (
    "anime character sprite, young woman, long straight blue hair, "
    "large black over-ear headphones with small cat ear attachments, "
    "black oversized hoodie, dark shorts, pale skin, soft blue eyes, "
    "full body standing pose, centered vertically, "
    "clean simple light grey background #aaaaaa, "
    "anime visual novel character illustration style, "
    "soft cel shading, clean linework, expressive face"
)

SPRITE_ASSETS = [
    {
        "name": "isaya_idle",
        "out": "isaya_idle.png",
        "w": 512, "h": 768,
        "prompt": ISAYA_BASE + (
            ", neutral relaxed expression, looking slightly downward, "
            "arms relaxed at sides, calm idle pose"
        ),
    },
    {
        "name": "isaya_happy",
        "out": "isaya_happy.png",
        "w": 512, "h": 768,
        "prompt": ISAYA_BASE + (
            ", bright warm smile, slight head tilt to the side, "
            "one hand raised in small wave, rosy cheeks, cheerful energy"
        ),
    },
    {
        "name": "isaya_sad",
        "out": "isaya_sad.png",
        "w": 512, "h": 768,
        "prompt": ISAYA_BASE + (
            ", sad tired expression, looking down, shoulders slightly slumped, "
            "slight frown, melancholy quiet mood"
        ),
    },
    {
        "name": "isaya_focused",
        "out": "isaya_focused.png",
        "w": 512, "h": 768,
        "prompt": ISAYA_BASE + (
            ", sharp focused expression, leaning slightly forward, "
            "eyes narrowed in concentration, gaming mode, determined look"
        ),
    },
]

ALL_ASSETS = ROOM_ASSETS + SPRITE_ASSETS


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
               "inputs": {"images": ["12", 0], "filename_prefix": "bsod"}},
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
    kb = os.path.getsize(out_path) // 1024
    print(f"  -> {os.path.basename(out_path)}  ({kb} KB)")


if __name__ == "__main__":
    import sys
    # Allow running subset: python3 generate_room_anystyle.py rooms
    #                        python3 generate_room_anystyle.py sprites
    filter_arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    if filter_arg == "rooms":
        assets = ROOM_ASSETS
    elif filter_arg == "sprites":
        assets = SPRITE_ASSETS
    else:
        assets = ALL_ASSETS

    try:
        v = api_get("/system_stats").get("system", {}).get("comfyui_version", "?")
        print(f"ComfyUI v{v} — generating {len(assets)} assets [{filter_arg}]\n")
    except Exception as e:
        print(f"Cannot connect: {e}"); exit(1)

    for a in assets:
        print(f"\n[{a['name']}]  {a['w']}x{a['h']}")
        seed = random.randint(0, 2**32 - 1)
        wf = build_workflow(a["prompt"], seed, a["w"], a["h"])
        pid = api_post("/prompt", {"prompt": wf})["prompt_id"]
        print(f"  id: {pid[:8]}...")
        entry = wait(pid)
        for node_out in entry["outputs"].values():
            for img in node_out.get("images", []):
                # Save to test dir for review, also to src/img if approved
                test_out = os.path.join(TEST_DIR, a["out"])
                download(img["filename"], img["subfolder"], test_out)
                break

    print(f"\nAll done! -> {TEST_DIR}")
