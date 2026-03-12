"""
Generate stream background with ReferenceLatent to keep Isaya's appearance consistent.
More chaotic desk, correct look.
"""
import json, time, random, shutil, urllib.request, urllib.parse
from pathlib import Path

BASE = "http://127.0.0.1:8188"
OUT  = Path(__file__).parent / "src/BSOD/img"

CS_DIR = Path(__file__).parent.parent / "convenience-store-v2/src/ConvenienceStore/img/customers"
REF1 = CS_DIR / "isaya_normal.png"
REF2 = CS_DIR / "isaya_sad.png"

W, H = 432, 936

PROMPT = (
    "anime illustration, top-down bird's eye isometric view, "
    "young woman with long straight blue hair and large black headphones on head, "
    "black oversized hoodie, sitting at an extremely chaotic streaming desk, "
    "desk completely covered in clutter: empty energy drink cans, instant noodle cups, "
    "scattered papers notes cables USB drives, snack wrappers, plushies, "
    "three glowing monitors showing stream chat overlay and game, "
    "colorful RGB mechanical keyboard, ring light on, "
    "headphone stand, microphone, stickers on laptop, "
    "dark bedroom, only screen glow and RGB light sources, "
    "neon cyan magenta purple green lighting from screens, "
    "loose anime cel shading style, bold outlines, flat colors, "
    "dynamic chaotic energy, extremely messy cluttered aesthetic, "
    "overhead perspective looking down at girl and desk, "
    "detailed anime key visual illustration"
)

def upload(path):
    name = path.name
    data = path.read_bytes()
    boundary = "----B" + hex(random.randint(0, 0xFFFFFF))[2:]
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{name}\"\r\nContent-Type: image/png\r\n\r\n"
            .encode() + data + f"\r\n--{boundary}--\r\n".encode())
    req = urllib.request.Request(f"{BASE}/upload/image", data=body,
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["name"]

def build_workflow(prompt, ref1, ref2, seed):
    return {
        "1":  {"class_type": "UNETLoader",             "inputs": {"unet_name": "flux-2-klein-4b.safetensors", "weight_dtype": "default"}},
        "2":  {"class_type": "CLIPLoader",              "inputs": {"clip_name": "qwen_3_4b.safetensors", "type": "flux2"}},
        "3":  {"class_type": "VAELoader",               "inputs": {"vae_name": "flux2-vae.safetensors"}},
        "4":  {"class_type": "CLIPTextEncode",          "inputs": {"text": prompt, "clip": ["2", 0]}},
        "5":  {"class_type": "ConditioningZeroOut",     "inputs": {"conditioning": ["4", 0]}},
        "6":  {"class_type": "CFGGuider",               "inputs": {"model": ["1", 0], "positive": ["21", 0], "negative": ["5", 0], "cfg": 1.0}},
        "7":  {"class_type": "RandomNoise",             "inputs": {"noise_seed": seed}},
        "8":  {"class_type": "EmptyFlux2LatentImage",   "inputs": {"width": W, "height": H, "batch_size": 1}},
        "9":  {"class_type": "Flux2Scheduler",          "inputs": {"steps": 8, "width": W, "height": H}},
        "10": {"class_type": "KSamplerSelect",          "inputs": {"sampler_name": "euler"}},
        "11": {"class_type": "SamplerCustomAdvanced",   "inputs": {"noise": ["7", 0], "guider": ["6", 0], "sampler": ["10", 0], "sigmas": ["9", 0], "latent_image": ["8", 0]}},
        "12": {"class_type": "VAEDecode",               "inputs": {"samples": ["11", 0], "vae": ["3", 0]}},
        "13": {"class_type": "SaveImage",               "inputs": {"images": ["12", 0], "filename_prefix": "bg_stream_v2"}},
        # Reference 1
        "14": {"class_type": "LoadImage",               "inputs": {"image": ref1}},
        "15": {"class_type": "ImageScaleToTotalPixels", "inputs": {"image": ["14", 0], "upscale_method": "lanczos", "megapixels": 0.25, "resolution_steps": 1}},
        "16": {"class_type": "VAEEncode",               "inputs": {"pixels": ["15", 0], "vae": ["3", 0]}},
        "17": {"class_type": "ReferenceLatent",         "inputs": {"conditioning": ["4", 0], "latent": ["16", 0]}},
        # Reference 2
        "18": {"class_type": "LoadImage",               "inputs": {"image": ref2}},
        "19": {"class_type": "ImageScaleToTotalPixels", "inputs": {"image": ["18", 0], "upscale_method": "lanczos", "megapixels": 0.25, "resolution_steps": 1}},
        "20": {"class_type": "VAEEncode",               "inputs": {"pixels": ["19", 0], "vae": ["3", 0]}},
        "21": {"class_type": "ReferenceLatent",         "inputs": {"conditioning": ["17", 0], "latent": ["20", 0]}},
    }

def post(wf):
    data = json.dumps({"prompt": wf}).encode()
    req = urllib.request.Request(f"{BASE}/prompt", data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["prompt_id"]

def wait(pid, timeout=600):
    start = time.time()
    while time.time() - start < timeout:
        with urllib.request.urlopen(f"{BASE}/history/{pid}") as r:
            h = json.loads(r.read())
        if pid in h:
            return h[pid]
        time.sleep(3)
        print(f"  {int(time.time()-start)}s...", end="\r", flush=True)
    raise TimeoutError

print("Uploading reference images...")
r1 = upload(REF1)
r2 = upload(REF2)
print(f"  ref1: {r1}\n  ref2: {r2}")

seed = random.randint(0, 2**31)
print(f"\nGenerating (seed {seed})...")
pid = post(build_workflow(PROMPT, r1, r2, seed))
print(f"Submitted {pid[:8]}...")

result = wait(pid)
imgs = []
for v in result.get("outputs", {}).values():
    imgs.extend(v.get("images", []))

if imgs:
    params = urllib.parse.urlencode({"filename": imgs[0]["filename"], "subfolder": imgs[0].get("subfolder",""), "type": "output"})
    dest = OUT / "bg_stream.png"
    with urllib.request.urlopen(f"{BASE}/view?{params}") as r:
        dest.write_bytes(r.read())
    print(f"\nSaved → {dest}  ({dest.stat().st_size//1024} KB)")
else:
    print("ERROR: no output")
