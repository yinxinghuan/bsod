#!/usr/bin/env python3
"""Test small apartment layout — multiple zones, dark rainy night, pixel art side view."""

import json, time, random, urllib.request, urllib.parse, shutil, os

COMFYUI_URL = "http://127.0.0.1:8188"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")
os.makedirs(OUT_DIR, exist_ok=True)

ORTHO = (
    "flat orthographic side view, no perspective, no vanishing point, "
    "parallel horizontal lines, 2D platformer side-scrolling background, "
    "walls flat vertical, floor flat horizontal"
)

STYLE = (
    "16-bit pixel art, small pixel size, muted dark blue-purple night palette, "
    "deep cool tones, soft pixel shading, indie game background, "
    "lofi aesthetic, atmospheric dark mood"
)

# Layout: from left to right across wide image
# [kitchen/dining] [living/bed] [large window] [pc desk] [bathroom door]
ZONES = (
    # === LEFT ZONE: kitchen / dining ===
    "far left: small kitchen counter with microwave, electric kettle, instant noodle cups stacked, "
    "mini fridge with magnets and photos, small dining table with one chair, "
    "takeout containers and chopsticks on table, "
    "cabinet above with dishes and snacks, overhead fluorescent light, "

    # === MIDDLE-LEFT ZONE: sleeping area ===
    "center-left: low bed with rumpled dark sheets and blanket piled up, "
    "clothes draped over bed corner, plushie on pillow, "
    "bookshelf next to bed overflowing with manga and light novels, figurines on top, "
    "small bedside lamp on floor, charging cable coiled on bed, "
    "anime poster on wall above bed, polaroid photos pinned in cluster, "

    # === CENTER ZONE: large window ===
    "center background: very large floor-to-ceiling window taking up most of back wall, "
    "heavy rain streaking down glass, dark rainy night city outside, "
    "building lights and neon signs glowing through rain, "
    "small plants on window sill, sticky notes on glass corner, "
    "dark curtain panel on one side of window, "

    # === RIGHT ZONE: PC / streaming desk ===
    "center-right: L-shaped desk with dual monitors glowing blue, "
    "keyboard with RGB backlight, mic on arm stand, ring light, "
    "gaming chair, tower PC on floor with blue LED, "
    "energy drink cans on desk, snack wrappers, phone on stand, "
    "headphones hung on monitor, stream overlay visible on screen, "
    "LED strip under desk casting blue glow on floor, "
    "tangled cables on floor, small black cat sleeping under desk, "

    # === FAR RIGHT ZONE: bathroom door ===
    "far right: bathroom door slightly ajar showing tile floor inside, "
    "small mirror reflection visible through door gap, "
    "hooks on wall next to door with jacket and bag hanging, "
    "narrow shelf with skincare items, "
    "power strip on floor with multiple plugs"
)

TESTS = [
    {
        "name": "apt_night_A",
        "w": 1536, "h": 576,
        "prompt": (
            f"pixel art small studio apartment interior, {ORTHO}, "
            f"extra wide panoramic view showing all zones left to right, "
            f"no characters, room only, "
            f"{ZONES}, "
            "night time, room lit only by monitor glow and LED strips, "
            "deep blue-purple ambient, rain on window, moody lofi atmosphere, "
            f"{STYLE}"
        ),
    },
    {
        "name": "apt_night_B",
        "w": 1280, "h": 576,
        "prompt": (
            f"pixel art small studio apartment interior, {ORTHO}, "
            f"wide panoramic view showing multiple living zones, "
            f"no characters, room only, "
            f"{ZONES}, "
            "late night streaming session, monitors casting blue glow, "
            "rain hitting window glass, city lights blurred outside, "
            "lived-in cozy chaos, every surface has something on it, "
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
               "inputs": {"images": ["12", 0], "filename_prefix": "apt"}},
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
        print(f"ComfyUI v{v} — small apartment room ({len(TESTS)} images)\n")
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
