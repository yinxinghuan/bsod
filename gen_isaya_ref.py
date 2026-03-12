#!/usr/bin/env python3
"""
Generate Isaya BSOD sprites using ReferenceLatent — same method as convenience-store-v2.
Reference: convenience store isaya_normal.png + isaya_sad.png for likeness consistency.
"""
import json, time, random, os, urllib.request, urllib.parse, shutil

BASE    = "http://127.0.0.1:8188"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")
os.makedirs(OUT_DIR, exist_ok=True)

# Reference images from convenience store (established character look)
CS_IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "../convenience-store-v2/src/ConvenienceStore/img/customers")
REF1 = os.path.join(CS_IMG_DIR, "isaya_normal.png")
REF2 = os.path.join(CS_IMG_DIR, "isaya_sad.png")

W, H = 768, 1152

STYLE_PREFIX = (
    "anime style, retro anime illustration, visual novel character sprite, "
    "full body standing pose, head to feet visible, "
    "centered horizontally, simple flat grey background #888888, "
    "no background objects, clean solid background, "
)

CHAR_BASE = (
    "young woman, long straight blue hair, center parted, absolutely no bangs, "
    "forehead completely exposed, hair falls straight down both sides, "
    "large black over-ear headphones worn on top of head covering ears, "
    "no headphones around neck, no headphones on shoulders, "
    "only one pair of headphones, headphones on head only, "
    "black oversized hoodie with front pocket and drawstrings, "
    "dark shorts, pale skin, soft blue eyes, "
)

EMOTIONS = {
    "isaya_idle":      "neutral calm expression, slight downward gaze, arms relaxed at sides",
    "isaya_happy":     "warm genuine smile, eyes curved happily, slight head tilt, rosy cheeks",
    "isaya_sad":       "sad tired expression, eyes downcast, shoulders gently slumped, subdued mood",
    "isaya_focused":   "sharp focused expression, eyes narrowed in concentration, leaning slightly forward",
    "isaya_surprised": "wide eyes, mouth slightly open, eyebrows raised, startled expression",
    "isaya_tired":     "exhausted half-lidded eyes, slight dark circles, slouching, holding coffee mug",
}


def upload_image(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    mime = "image/png"
    filename = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        data = f.read()
    boundary = "----FormBoundary" + hex(random.randint(0, 0xFFFFFF))[2:]
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
        f"Content-Type: {mime}\r\n\r\n"
    ).encode() + data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        f"{BASE}/upload/image", data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["name"]


def build_workflow(prompt, ref1_name, ref2_name, seed):
    return {
        "1":  {"class_type": "UNETLoader",             "inputs": {"unet_name": "flux-2-klein-4b.safetensors", "weight_dtype": "default"}},
        "2":  {"class_type": "CLIPLoader",              "inputs": {"clip_name": "qwen_3_4b.safetensors", "type": "flux2"}},
        "3":  {"class_type": "VAELoader",               "inputs": {"vae_name": "flux2-vae.safetensors"}},
        "4":  {"class_type": "CLIPTextEncode",          "inputs": {"text": prompt, "clip": ["2", 0]}},
        "5":  {"class_type": "ConditioningZeroOut",     "inputs": {"conditioning": ["4", 0]}},
        "6":  {"class_type": "CFGGuider",               "inputs": {"model": ["1", 0], "positive": ["21", 0], "negative": ["5", 0], "cfg": 1.0}},
        "7":  {"class_type": "RandomNoise",             "inputs": {"noise_seed": seed}},
        "8":  {"class_type": "EmptyFlux2LatentImage",   "inputs": {"width": W, "height": H, "batch_size": 1}},
        "9":  {"class_type": "Flux2Scheduler",          "inputs": {"steps": 6, "width": W, "height": H}},
        "10": {"class_type": "KSamplerSelect",          "inputs": {"sampler_name": "euler"}},
        "11": {"class_type": "SamplerCustomAdvanced",   "inputs": {"noise": ["7", 0], "guider": ["6", 0], "sampler": ["10", 0], "sigmas": ["9", 0], "latent_image": ["8", 0]}},
        "12": {"class_type": "VAEDecode",               "inputs": {"samples": ["11", 0], "vae": ["3", 0]}},
        "13": {"class_type": "SaveImage",               "inputs": {"images": ["12", 0], "filename_prefix": "isaya_ref"}},
        # Reference image 1 (isaya_normal)
        "14": {"class_type": "LoadImage",               "inputs": {"image": ref1_name}},
        "15": {"class_type": "ImageScaleToTotalPixels", "inputs": {"image": ["14", 0], "upscale_method": "lanczos", "megapixels": 0.25, "resolution_steps": 1}},
        "16": {"class_type": "VAEEncode",               "inputs": {"pixels": ["15", 0], "vae": ["3", 0]}},
        "17": {"class_type": "ReferenceLatent",         "inputs": {"conditioning": ["4", 0], "latent": ["16", 0]}},
        # Reference image 2 (isaya_sad)
        "18": {"class_type": "LoadImage",               "inputs": {"image": ref2_name}},
        "19": {"class_type": "ImageScaleToTotalPixels", "inputs": {"image": ["18", 0], "upscale_method": "lanczos", "megapixels": 0.25, "resolution_steps": 1}},
        "20": {"class_type": "VAEEncode",               "inputs": {"pixels": ["19", 0], "vae": ["3", 0]}},
        "21": {"class_type": "ReferenceLatent",         "inputs": {"conditioning": ["17", 0], "latent": ["20", 0]}},
    }


def api_post(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(f"{BASE}{path}", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def api_get(path):
    with urllib.request.urlopen(f"{BASE}{path}", timeout=30) as r:
        return json.loads(r.read())

def wait(pid, timeout=900):
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
    with urllib.request.urlopen(f"{BASE}/view?{params}", timeout=60) as r:
        with open(out_path, "wb") as f:
            shutil.copyfileobj(r, f)
    print(f"  -> {os.path.basename(out_path)}  ({os.path.getsize(out_path)//1024} KB)")


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "all"

    try:
        v = api_get("/system_stats").get("system", {}).get("comfyui_version", "?")
        print(f"ComfyUI v{v}\n")
    except Exception as e:
        print(f"Cannot connect: {e}"); exit(1)

    print("Uploading reference images...")
    ref1_server = upload_image(REF1)
    ref2_server = upload_image(REF2)
    print(f"  ref1: {ref1_server}")
    print(f"  ref2: {ref2_server}\n")

    emotions = EMOTIONS if target == "all" else {k: v for k, v in EMOTIONS.items() if target in k}

    for name, emotion_desc in emotions.items():
        print(f"[{name}]")
        prompt = STYLE_PREFIX + CHAR_BASE + emotion_desc
        seed = random.randint(0, 2**31)
        wf = build_workflow(prompt, ref1_server, ref2_server, seed)
        pid = api_post("/prompt", {"prompt": wf})["prompt_id"]
        print(f"  id: {pid[:8]}...")
        entry = wait(pid)
        for node_out in entry["outputs"].values():
            for img in node_out.get("images", []):
                out = os.path.join(OUT_DIR, f"{name}_ref.png")
                download(img["filename"], img["subfolder"], out)
                break

    print(f"\nAll done! -> {OUT_DIR}")
