#!/usr/bin/env python3
"""Generate the ONE definitive BSOD night room background.
Focus: giant window, extreme clutter, anime VN style, flat side view."""

import json, time, random, urllib.request, urllib.parse, shutil, os

COMFYUI_URL = "http://127.0.0.1:8188"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")
os.makedirs(OUT_DIR, exist_ok=True)

ORTHO = (
    "flat orthographic side view, no perspective, no vanishing point, "
    "parallel horizontal lines, 2D platformer side-scrolling game background"
)

STYLE = (
    "anime illustration style, visual novel background art, "
    "painterly soft shading, detailed interior, clean linework"
)

# Window is now the DOMINANT feature — takes 50%+ of the back wall
WINDOW = (
    "enormous floor-to-ceiling panoramic window spanning most of the back wall, "
    "very wide window taking up half the total image width, "
    "heavy rain streaking down the glass, "
    "dark rainy night city outside, tall buildings with lit windows, "
    "neon signs glowing purple and blue through the rain, "
    "wet reflections on the glass, window condensation, "
    "dark curtains pulled to the sides"
)

# Clutter: every surface is covered
CLUTTER = (
    # Desk zone (right side)
    "right side: L-shaped desk completely covered in stuff, "
    "two glowing monitors side by side, mechanical keyboard with RGB backlight, "
    "mic arm with condenser mic, ring light on stand, "
    "six empty energy drink cans lined up on desk edge, "
    "sticky notes covering monitor bezels, phone charging on stand, "
    "headphones resting on monitor, snack wrappers and chip bags, "
    "external hard drives stacked, a mug with pens and scissors, "
    "gaming chair with hoodie draped over it, "
    "PC tower on floor under desk with blue LED strips, "
    "cables tangled all over the floor under desk, "
    "small black cat sleeping curled up under the desk, "
    # Bed/living zone (left-center)
    "center-left: low bed pushed against wall, "
    "sheets completely rumpled and piled up, three pillows in a heap, "
    "plushie half-buried under blanket, clothes thrown on the bed, "
    "charging cable snaking across the bed, "
    "bedside floor has skincare bottles, a book face-down, water bottle, "
    # Bookshelf
    "tall overstuffed bookshelf, manga volumes crammed in every space, "
    "anime figurines on top of books, plushies stacked on top shelf, "
    "a jacket draped over the bookshelf corner, "
    # Walls
    "walls densely covered with overlapping anime posters, "
    "cluster of polaroid photos pinned with thumbtacks, "
    "sticky notes everywhere on wall near desk, "
    "LED strip along ceiling edge glowing dim blue-purple, "
    # Floor
    "floor: clothes scattered, empty plastic bottles, "
    "pizza box near the wall, power strip with cables fanning out, "
    "a gaming controller on the floor, "
    # Left zone: mini kitchen
    "far left: small kitchen counter, mini fridge covered in stickers, "
    "electric kettle, instant noodle cups stacked, "
    "small table with takeout containers and chopsticks"
)

TESTS = [
    {
        "name": "bg_final_A",
        "w": 1280, "h": 576,
        "prompt": (
            f"anime visual novel background, {ORTHO}, {STYLE}, "
            f"streamer studio apartment interior, no characters, "
            f"{WINDOW}, "
            f"{CLUTTER}, "
            "late night atmosphere, room lit by monitor blue glow and dim LED strips, "
            "deep blue-purple ambient, moody dark cozy, every corner packed with life"
        ),
    },
    {
        "name": "bg_final_B",
        "w": 1280, "h": 576,
        "prompt": (
            f"anime visual novel background, {ORTHO}, {STYLE}, "
            f"messy streamer studio apartment, no characters, "
            f"{WINDOW}, "
            f"{CLUTTER}, "
            "midnight streaming session, monitors the only real light source, "
            "cool blue ambient from screens, warm red LED accent on desk, "
            "rain sound atmosphere, city visible through rain-streaked giant window"
        ),
    },
    {
        "name": "bg_final_C",
        "w": 1536, "h": 576,
        "prompt": (
            f"anime visual novel background, {ORTHO}, {STYLE}, "
            f"wide panoramic streamer apartment interior, no characters, "
            f"{WINDOW}, "
            f"{CLUTTER}, "
            "bathroom door on far right slightly ajar, "
            "late night, monitor glow, blue-purple darkness, "
            "maximally detailed and cluttered, lived-in chaos, "
            "rain on enormous window dominating the background"
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
               "inputs": {"images": ["12", 0], "filename_prefix": "bg_final"}},
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


if __name__ == "__main__":
    try:
        v = api_get("/system_stats").get("system", {}).get("comfyui_version", "?")
        print(f"ComfyUI v{v} — final room background ({len(TESTS)} variants)\n")
    except Exception as e:
        print(f"Cannot connect: {e}"); exit(1)

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

    print("\nAll done!")
