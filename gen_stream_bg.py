"""
Generate stream scene background: Laisa at streaming desk, top-down anime style.
Output: src/BSOD/img/bg_stream.png  (432×936 portrait)
"""
import json, time, urllib.request, urllib.parse, random
from pathlib import Path

API = "http://127.0.0.1:8188"
OUT = Path(__file__).parent / "src/BSOD/img"
W, H = 432, 936

PROMPT = (
    "anime illustration, top-down bird's eye view, teenage girl with teal blue hair and large headphones "
    "sitting at a chaotic streaming desk, multiple glowing monitors showing stream overlays and chat, "
    "RGB mechanical keyboard, colorful screen glow illuminating from below, "
    "cluttered desk with papers sticky notes cables snacks coffee cup, "
    "dark room lit only by monitor glow, vibrant neon colors cyan magenta green purple, "
    "loose anime art style, flat cel shading, bold outlines, "
    "dynamic composition, chaotic energy, colorful chaos aesthetic, "
    "isometric-like overhead perspective, no background just dark void, "
    "high quality anime key visual, detailed illustration"
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
              "inputs": {"steps": 8, "width": W, "height": H}},
        "10": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "11": {"class_type": "SamplerCustomAdvanced",
               "inputs": {"noise": ["7", 0], "guider": ["6", 0], "sampler": ["10", 0],
                          "sigmas": ["9", 0], "latent_image": ["8", 0]}},
        "12": {"class_type": "VAEDecode",
               "inputs": {"samples": ["11", 0], "vae": ["3", 0]}},
        "13": {"class_type": "SaveImage",
               "inputs": {"images": ["12", 0], "filename_prefix": "bg_stream"}},
    }

seed = random.randint(0, 2**32)
print(f"Generating bg_stream.png (seed {seed})...")
data = json.dumps({"prompt": build_workflow(PROMPT, seed)}).encode()
req = urllib.request.Request(f"{API}/prompt", data=data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as r:
    pid = json.loads(r.read())["prompt_id"]
print(f"Submitted {pid[:8]}... waiting")

start = time.time()
while time.time() - start < 400:
    with urllib.request.urlopen(f"{API}/history/{pid}") as r:
        h = json.loads(r.read())
    if pid in h:
        imgs = []
        for v in h[pid].get("outputs", {}).values():
            imgs.extend(v.get("images", []))
        if imgs:
            url = f"{API}/view?filename={urllib.parse.quote(imgs[0]['filename'])}&type=output"
            dest = OUT / "bg_stream.png"
            with urllib.request.urlopen(url) as r:
                dest.write_bytes(r.read())
            print(f"Saved → {dest}")
        else:
            print("ERROR: no output images")
        break
    time.sleep(2)
