#!/usr/bin/env python3
"""Generate BSOD room background v3.
Base: bg_v2_A composition (perspective, cat, bed-left + desk-right, big window, LED ceiling)
Enhanced: extreme clutter + nostalgic retro items (dreamcatcher, polaroids, etc.)
"""

import json, time, random, urllib.request, urllib.parse, shutil, os

COMFYUI_URL = "http://127.0.0.1:8188"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")
os.makedirs(OUT_DIR, exist_ok=True)

STYLE = (
    "anime visual novel illustration style, painterly detailed interior, "
    "soft shading with clean linework, no characters, no people"
)

COMPOSITION = (
    "small apartment room seen from a 3/4 corner-perspective angle, "
    "tall portrait format, viewer at doorway looking into the room, "
    "large floor-to-ceiling window on back wall spanning almost full width, "
    "heavy rain streaking down the glass, dark rainy night outside, "
    "dense city skyline with neon signs glowing purple pink and blue through rain, "
    "dark curtains half-drawn to the sides, "
    "LED light strip along entire ceiling edge glowing dim purple-blue, "
    # Left: bed
    "left side: single bed pushed against wall, "
    "sheets completely rumpled and twisted, multiple pillows in a heap, "
    "plush toy half-buried under blanket, "
    "clothes and hoodies piled on top of the bed, "
    "charging cable snaking across mattress, "
    # Cat — must be visible
    "small black cat curled up sleeping on the floor between bed and desk, "
    # Right: desk
    "right side: L-shaped desk with two large glowing monitors, "
    "condenser microphone on boom arm, RGB mechanical keyboard, "
    "ring light, energy drink cans along desk edge, "
    "gaming chair with hoodie draped over backrest, "
    "PC tower under desk with blue LED strips, "
    "cables tangled on floor under and around desk"
)

INDIE_MUSIC = (
    "walls covered in overlapping band posters: Ramones, Nirvana, The Doors, "
    "Pink Floyd prism, Joy Division unknown pleasures, "
    "some posters torn at edges and re-taped, "
    "vintage turntable record player on low shelf near bed, "
    "vinyl records and album sleeves spread across floor near turntable, "
    "milk crate full of vinyl records against wall, "
    "electric guitar leaning against wall near window, "
    "cassette tapes on shelves, band stickers on PC tower"
)

# KEY NEW ELEMENTS — nostalgic, retro, hikikomori
NOSTALGIC = (
    # Dreamcatcher
    "large dreamcatcher hanging in window, feathers dangling, "
    "catching the neon light from outside, "
    # Polaroids
    "strings of polaroid photos hung from wall to wall with mini clothespins, "
    "dozens of polaroid photos creating a canopy of memories above the bed, "
    "more polaroids pinned directly to wall in a loose collage, "
    # Other retro nostalgic
    "a stack of dog-eared paperback novels on the nightstand, "
    "fairy lights woven through the polaroid strings, "
    "a cork pinboard on wall with torn concert tickets, receipts, "
    "notes, washi tape strips pinning things down, "
    "old film camera sitting on the shelf, "
    "a lava lamp glowing dim orange on the desk corner, "
    "scented candle melted almost to the holder on nightstand"
)

# EXTREME CLUTTER — entropy has won
ENTROPY = (
    "floor almost completely covered: "
    "clothes piled everywhere, vinyl records out of their sleeves, "
    "empty instant noodle cups, takeout bags, crumpled receipts, "
    "water bottles on their side, headphone cable snaking across floor, "
    "power strip buried under stuff with cables radiating outward, "
    "cardboard boxes stacked in corner never unpacked, "
    "a skateboard deck leaning against the wall, "
    "desk surface barely visible under: sticky notes on monitor bezel, "
    "snack wrappers, stacked empty cans, a mug with pens, "
    "open laptop beside the main monitors, "
    "bookshelves crammed to overflowing, items balanced on top of items"
)

LIGHTING = (
    "room lit by: dual monitor glow casting cool blue light on everything, "
    "dim purple-blue LED ceiling strip, lava lamp warm orange glow, "
    "fairy lights warm yellow glow, neon city light through rainy window, "
    "deep moody night atmosphere, melancholy cozy, "
    "every surface catching a different colored light"
)

BASE = f"{STYLE}, {COMPOSITION}, {INDIE_MUSIC}, {NOSTALGIC}, {ENTROPY}, {LIGHTING}"

TESTS = [
    {
        "name": "bg_v3_A",
        "w": 432, "h": 936,
        "prompt": BASE + (
            ", dreamcatcher prominently in window catching purple neon, "
            "polaroid photo strings clearly visible above bed, "
            "black cat sleeping on cluttered floor"
        ),
    },
    {
        "name": "bg_v3_B",
        "w": 432, "h": 936,
        "prompt": BASE + (
            ", polaroid canopy over bed very visible, fairy lights glowing warm, "
            "cork board with tickets and notes on wall, "
            "black cat on floor, lava lamp orange glow on desk"
        ),
    },
    {
        "name": "bg_v3_C",
        "w": 432, "h": 936,
        "prompt": BASE + (
            ", maximum floor clutter in foreground, vinyl records everywhere, "
            "dreamcatcher in window, polaroids on wall, "
            "black cat curled between record crate and desk"
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
               "inputs": {"images": ["12", 0], "filename_prefix": "bg_v3"}},
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
        print(f"ComfyUI v{v} — room v3 chaos + nostalgia ({len(TESTS)} variants)\n")
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

    print("\nAll done! Check test_output/bg_v3_A/B/C.png")
