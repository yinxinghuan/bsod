#!/usr/bin/env python3
"""Test ultra-dense cluttered streamer room — flat orthographic side view."""

import json, time, random, urllib.request, urllib.parse, shutil, os

COMFYUI_URL = "http://127.0.0.1:8188"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")
os.makedirs(OUT_DIR, exist_ok=True)

# Shared base: strict orthographic, no perspective, dense clutter
ORTHO = (
    "flat orthographic side view, no perspective, no vanishing point, "
    "parallel horizontal lines, 2D platformer background, "
    "walls perfectly flat vertical, floor perfectly flat horizontal"
)

STYLE = (
    "16-bit pixel art, small pixel size, muted grey-blue cool palette, "
    "indie game background, soft pixel shading, detailed pixel art, "
    "image-rendering pixelated"
)

ROOM_BASE = (
    "streamer bedroom interior, {ORTHO}, "
    "full room visible left to right, side view, "
    "no characters, room only"
).format(ORTHO=ORTHO)

CLUTTER_EXTREME = (
    # Furniture
    "large L-shaped desk on left with two glowing monitors, keyboard, mouse, mic stand, ring light, "
    "gaming chair with worn fabric and stickers, "
    "single bed on right with rumpled dark sheets and three pillows piled up, "
    "tall bookshelf overflowing with manga volumes, figurines, plushies stacked on top, "
    # Wall decorations
    "walls completely covered with overlapping anime posters, band posters, sticky notes, "
    "polaroid photos taped in clusters, LED strip lights along ceiling glowing blue-purple, "
    "small whiteboard with scribbled notes pinned to wall, "
    # Floor clutter
    "floor littered with empty snack wrappers, soda cans, tangled headphone cable, "
    "clothes pile in corner, pizza box, gaming controller on floor, "
    "power strip with multiple cables snaking across floor, "
    # Desk clutter
    "desk covered with energy drink cans, sticky note pad, phone charging, "
    "second smaller monitor sideways, external hard drive, stacks of game cases, "
    "small potted cactus, cat sleeping on keyboard tray, "
    # Window
    "large window in background showing rainy city skyline at night, "
    "window sill has small plants, a cat figurine, more sticky notes on glass, "
    "rain streaks on window glass, neon signs visible outside"
)

TESTS = [
    {
        "name": "room_ultra_A",
        "w": 1280, "h": 512,
        "prompt": (
            f"{ROOM_BASE}, "
            f"{CLUTTER_EXTREME}, "
            "night time, room lit by monitor glow and LED strips, "
            "deep blue-purple ambient light, neon accents, "
            f"{STYLE}"
        ),
    },
    {
        "name": "room_ultra_B",
        "w": 1280, "h": 512,
        "prompt": (
            f"{ROOM_BASE}, "
            f"{CLUTTER_EXTREME}, "
            "evening warm light, orange sunset through window mixing with cool monitor light, "
            "cozy but chaotic, lived-in atmosphere, "
            f"{STYLE}"
        ),
    },
    {
        "name": "room_ultra_wide",
        "w": 1536, "h": 512,
        "prompt": (
            f"{ROOM_BASE}, "
            f"{CLUTTER_EXTREME}, "
            "extra wide room, more desk space on left extending further, "
            "hallway door visible on far right, night time, "
            "monitor glow, LED strips, dense pixel details throughout, "
            f"{STYLE}"
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
               "inputs": {"images": ["12", 0], "filename_prefix": "room_ultra"}},
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
        print(f"ComfyUI v{v} — ultra dense room test ({len(TESTS)} images)\n")
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
