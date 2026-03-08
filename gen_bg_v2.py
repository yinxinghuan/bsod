#!/usr/bin/env python3
"""Generate BSOD room background v2.
Composition: portrait_C layout (perspective, cat, bed+desk, big window, LED ceiling)
Culture: indie music (vinyl records, band posters) replacing anime posters.
"""

import json, time, random, urllib.request, urllib.parse, shutil, os

COMFYUI_URL = "http://127.0.0.1:8188"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")
os.makedirs(OUT_DIR, exist_ok=True)

STYLE = (
    "anime visual novel illustration style, painterly detailed interior, "
    "soft shading with clean linework, no characters, no people"
)

# Same composition as portrait_C: corner-perspective view of a small room
COMPOSITION = (
    "small apartment room seen from a 3/4 corner-perspective angle, "
    "tall portrait format, viewer stands at the door looking into the room, "
    "large floor-to-ceiling window on back wall spanning almost full width, "
    "heavy rain streaking down the glass, dark rainy night outside, "
    "dense city skyline with neon signs glowing purple pink and blue through rain, "
    "dark curtains pulled to the sides of the window, "
    "LED light strip along the entire ceiling edge glowing dim purple-blue, "
    # Left side: bed
    "left side of room: single bed pushed against left wall, "
    "rumpled sheets and blanket piled up, pillow heap, "
    "clothes thrown onto the bed, charging cable snaking across mattress, "
    # Black cat — must be present
    "small black cat curled up sleeping on the floor between the bed and desk, "
    # Right side: desk setup
    "right side of room: L-shaped gaming desk, "
    "two large monitors side by side glowing bright, "
    "condenser microphone on boom arm, RGB mechanical keyboard, "
    "ring light on flexible arm, "
    "energy drink cans lined along desk edge, "
    "gaming chair with hoodie draped over it, "
    "PC tower on floor under desk with blue LED strips glowing, "
    # Floor cables
    "cables tangled all over the floor between desk and cat, "
    "power strip visible on floor with cables fanning out"
)

# INDIE MUSIC CULTURE — replaces anime aesthetic entirely
INDIE = (
    # Posters on walls — punk/alternative/classic rock ONLY
    "walls covered in overlapping band posters: "
    "Ramones eagle logo poster, Nirvana nevermind poster, "
    "The Doors psychedelic concert poster, Pink Floyd prism poster, "
    "Joy Division unknown pleasures poster, "
    "some posters slightly torn at corners, concert ticket stubs pinned beside them, "
    # Vinyl records and turntable
    "vintage turntable record player sitting on a low shelf or floor near the bed, "
    "vinyl record sleeves spread across the floor around the turntable, "
    "a milk crate full of vinyl records against the wall, "
    # Guitar
    "electric guitar leaning against the wall near the window, "
    # Other music details
    "cassette tapes on the desk shelf, "
    "band stickers on the PC tower, "
    "a beaten-up music magazine on the bed"
)

CLUTTER = (
    "floor partially covered in: clothes, vinyl records out of sleeves, "
    "empty noodle cups, crumpled papers, "
    "cardboard delivery boxes stacked in corner, "
    "water bottles and snack wrappers near the desk"
)

LIGHTING = (
    "room lit by monitor glow, dim LED ceiling strip, and faint neon from window, "
    "deep blue-purple night atmosphere, moody and atmospheric, "
    "screen light casting cool blue on everything, "
    "rainy night cozy-melancholy mood"
)

BASE = f"{STYLE}, {COMPOSITION}, {INDIE}, {CLUTTER}, {LIGHTING}"

TESTS = [
    {
        "name": "bg_v2_A",
        "w": 432, "h": 936,
        "prompt": BASE + ", black cat prominently visible sleeping on floor",
    },
    {
        "name": "bg_v2_B",
        "w": 432, "h": 936,
        "prompt": BASE + (
            ", turntable and vinyl records very visible in foreground, "
            "band posters dominating left wall, black cat on floor"
        ),
    },
    {
        "name": "bg_v2_C",
        "w": 432, "h": 936,
        "prompt": BASE + (
            ", guitar leaning against window frame center, "
            "pink floyd prism poster large on right wall, "
            "black cat curled between bed and desk"
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
               "inputs": {"images": ["12", 0], "filename_prefix": "bg_v2"}},
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
        print(f"ComfyUI v{v} — room v2 indie chaos ({len(TESTS)} variants)\n")
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

    print("\nAll done! Check test_output/bg_v2_A/B/C.png")
