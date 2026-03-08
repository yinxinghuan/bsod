#!/usr/bin/env python3
"""Generate BSOD game poster with Laisa character + PIL pixel-font text overlay."""

import json, time, random, urllib.request, urllib.parse, shutil, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

COMFYUI_URL = "http://127.0.0.1:8188"
IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src/BSOD/img")
os.makedirs(IMG_DIR, exist_ok=True)

W, H = 1024, 1024

# Laisa: blue hair NO bangs, cat-ear headphones, black hoodie
# No text in image — added via PIL post-processing
PROMPT = (
    "game key art poster, anime illustration style, "
    "young woman streamer, long straight blue hair, "
    "absolutely no bangs no fringe, hair parted in middle swept behind ears, "
    "clean forehead fully visible, "
    "large black over-ear headphones with small cat-ear shapes on top of headphone cups, "
    "black oversized hoodie, pale skin, bright blue eyes, "
    "sitting at a glowing gaming desk with multiple monitors showing streaming interface, "
    "dark rainy night, neon blue and purple glow from screens, "
    "rain streaks on window behind her, blurred city lights, "
    "dramatic side lighting, tired but focused expression looking at camera, "
    "dark moody atmosphere, blue and purple color palette, "
    "cinematic game key art, highly detailed anime illustration"
)


def build_workflow(prompt, seed):
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
              "inputs": {"width": W, "height": H, "batch_size": 1}},
        "9": {"class_type": "Flux2Scheduler",
              "inputs": {"steps": 4, "width": W, "height": H}},
        "10": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "11": {"class_type": "SamplerCustomAdvanced",
               "inputs": {"noise": ["7", 0], "guider": ["6", 0], "sampler": ["10", 0],
                          "sigmas": ["9", 0], "latent_image": ["8", 0]}},
        "12": {"class_type": "VAEDecode",
               "inputs": {"samples": ["11", 0], "vae": ["3", 0]}},
        "13": {"class_type": "SaveImage",
               "inputs": {"images": ["12", 0], "filename_prefix": "bsod_poster"}},
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
    print(f"  → raw image saved ({os.path.getsize(out_path)//1024} KB)")


def add_text_overlay(img_path, out_path):
    """Composite pixel-font title + subtitle onto the poster."""
    font_path = "/tmp/VT323-Regular.ttf"
    if not os.path.exists(font_path):
        print("  VT323 font not found at /tmp/VT323-Regular.ttf — skipping text overlay")
        shutil.copy(img_path, out_path)
        return

    img = Image.open(img_path).convert("RGBA")
    W, H = img.size

    # Dark gradient at top so title is readable
    gradient = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_grad = ImageDraw.Draw(gradient)
    for y in range(int(H * 0.28)):
        alpha = int(180 * (1 - y / (H * 0.28)))
        draw_grad.line([(0, y), (W, y)], fill=(4, 6, 20, alpha))
    img = Image.alpha_composite(img, gradient)

    draw = ImageDraw.Draw(img)

    # ── Main title: BSOD ─────────────────────────────────────────────────────
    title_size = 160
    font_title = ImageFont.truetype(font_path, title_size)
    title = "BSOD"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    tx = (W - tw) // 2
    ty = 28

    # Blue glow layers
    for dx, dy, alpha in [(-4, 0, 40), (4, 0, 40), (0, -4, 40), (0, 4, 40),
                           (-2, 0, 70), (2, 0, 70), (0, -2, 70), (0, 2, 70)]:
        draw.text((tx + dx, ty + dy), title, font=font_title,
                  fill=(80, 140, 255, alpha))
    # Main white text
    draw.text((tx, ty), title, font=font_title, fill=(232, 238, 255, 240))

    # ── Subtitle: BLUE SCREEN OF DOOM ────────────────────────────────────────
    sub_size = 28
    font_sub = ImageFont.truetype(font_path, sub_size)
    subtitle = "BLUE SCREEN OF DOOM"
    sbbox = draw.textbbox((0, 0), subtitle, font=font_sub)
    sw = sbbox[2] - sbbox[0]
    sx = (W - sw) // 2
    sy = ty + (bbox[3] - bbox[1]) + 8
    draw.text((sx, sy), subtitle, font=font_sub, fill=(100, 160, 255, 160))

    out = img.convert("RGB")
    out.save(out_path, "PNG", optimize=True)
    print(f"  → {os.path.basename(out_path)} with text overlay ({os.path.getsize(out_path)//1024} KB)")


if __name__ == "__main__":
    try:
        v = api_get("/system_stats").get("system", {}).get("comfyui_version", "?")
        print(f"ComfyUI v{v} — generating BSOD poster ({W}x{H})\n")
    except Exception as e:
        print(f"Cannot connect: {e}"); exit(1)

    seed = random.randint(0, 2**32 - 1)
    print(f"[bsod_poster] seed={seed}")
    wf = build_workflow(PROMPT, seed)
    pid = api_post("/prompt", {"prompt": wf})["prompt_id"]
    print(f"  id: {pid[:8]}...")
    entry = wait(pid)

    raw_path = os.path.join(IMG_DIR, "poster_raw.png")
    out_path = os.path.join(IMG_DIR, "poster.png")

    for node_out in entry["outputs"].values():
        for img in node_out.get("images", []):
            download(img["filename"], img["subfolder"], raw_path)
            break

    print("Adding pixel-font text overlay...")
    add_text_overlay(raw_path, out_path)
    os.remove(raw_path)

    print(f"\nDone! → {out_path}")
