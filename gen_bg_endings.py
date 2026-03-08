#!/usr/bin/env python3
"""Generate BSOD ending room backgrounds — 4 variants for 4 endings.

online  : best ending — room cleaned up, sunlight, curtains open, plants
offline : high followers, low connection — corporate/streamer grind, cold
restart : fresh start — room mid-tidy, new notebook open, hopeful
bsod    : worst ending — total collapse, monitors off, extreme chaos
"""

import json, time, random, urllib.request, urllib.parse, shutil, os

COMFYUI_URL = "http://127.0.0.1:8188"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")
os.makedirs(OUT_DIR, exist_ok=True)

STYLE = (
    "anime visual novel background art, painterly detailed interior, "
    "soft shading with clean linework, no characters, no people, "
    "small apartment room seen from 3/4 corner-perspective angle, "
    "tall portrait format"
)

# Shared room identity across all endings (same room, different state)
ROOM_IDENTITY = (
    "same small apartment room: "
    "large window on back wall, L-shaped desk on right side, "
    "single bed on left side, band posters on walls, "
    "dreamcatcher near window, record player shelf"
)

TESTS = [
    {
        "name": "bg_ending_online",
        "w": 432, "h": 936,
        "prompt": (
            f"{STYLE}, {ROOM_IDENTITY}, "
            "BEST ENDING — room is clean and organized for the first time, "
            "curtains fully open, warm afternoon sunlight streaming through window, "
            "desk tidied with only essentials, monitors displaying a large follower count, "
            "fresh flowers in a small vase on desk, "
            "floor completely clean and visible, "
            "clothes hung up, bed neatly made, "
            "small green potted plant on windowsill catching the light, "
            "warm golden sunlight, hopeful bright atmosphere, "
            "band posters still on walls but room feels lived-in and loved, "
            "a handwritten note pinned to the wall"
        ),
    },
    {
        "name": "bg_ending_offline",
        "w": 432, "h": 936,
        "prompt": (
            f"{STYLE}, {ROOM_IDENTITY}, "
            "OFFLINE ENDING — room shows signs of commercial success but emotional emptiness, "
            "multiple monitors showing stream analytics and graphs, "
            "professional ring light set up, branded merchandise boxes stacked in corner, "
            "desk covered in sponsor products and packaging, "
            "room semi-tidy but sterile, the personal touches fading, "
            "band posters partially covered by brand banners, "
            "cold blue monitor glow dominating, "
            "curtains half-closed blocking outside world, "
            "late night, lonely atmosphere despite apparent success, "
            "phone with many notifications visible on desk"
        ),
    },
    {
        "name": "bg_ending_restart",
        "w": 432, "h": 936,
        "prompt": (
            f"{STYLE}, {ROOM_IDENTITY}, "
            "RESTART ENDING — room mid-tidying, in the process of being cleaned, "
            "some areas clean, some still cluttered, work in progress, "
            "a fresh open notebook on the desk with a pen, first page written on, "
            "some vinyl records neatly stacked for the first time, "
            "a few garbage bags by the door ready to be taken out, "
            "morning light coming through window, curtains partially open, "
            "warm but modest atmosphere, realistic hope, "
            "black cat visible curled on the clean bed, "
            "the guitar propped up more carefully than before, "
            "soft morning blue-grey light, quiet contemplative mood"
        ),
    },
    {
        "name": "bg_ending_bsod",
        "w": 432, "h": 936,
        "prompt": (
            f"{STYLE}, {ROOM_IDENTITY}, "
            "BSOD WORST ENDING — total collapse and abandonment, "
            "all monitors are BLACK and turned off, "
            "room in extreme chaos far beyond normal clutter, "
            "takeout containers piled high, garbage overflowing, "
            "clothes covering every surface, floor invisible, "
            "empty energy drink cans everywhere, "
            "curtains fully closed, total darkness except one dim lamp, "
            "dusty surfaces, spider web in corner, "
            "abandoned feeling, like no one has engaged with the space in weeks, "
            "the black cat is GONE — empty where it used to sleep, "
            "one sad wilted plant knocked over, "
            "oppressive dark atmosphere, hopeless, suffocating clutter, "
            "blue error screen visible faintly reflected on dead monitor"
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
               "inputs": {"images": ["12", 0], "filename_prefix": "bg_ending"}},
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
        print(f"ComfyUI v{v} — ending backgrounds ({len(TESTS)} variants)\n")
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

    print("\nAll done! Check test_output/bg_ending_*.png")
