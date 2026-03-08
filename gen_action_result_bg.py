"""
Generate two background images for ActionResultScreen:
  1. bg_surveillance.png  — CCTV security camera angle of a hikikomori room
  2. bg_livestream.png    — Cozy streaming setup with RGB lights and monitors

Output: src/BSOD/img/  (430 × 936, portrait)
"""

import json, time, urllib.request, urllib.parse, random, shutil
from pathlib import Path

API = "http://127.0.0.1:8188"
OUT = Path(__file__).parent / "src/BSOD/img"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 432, 936   # portrait, same as game screen

# ── Workflow builder ──────────────────────────────────────────────────────────

def build_workflow(prompt: str, seed: int, w=W, h=H) -> dict:
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
        "7": {"class_type": "RandomNoise",
              "inputs": {"noise_seed": seed}},
        "8": {"class_type": "EmptyFlux2LatentImage",
              "inputs": {"width": w, "height": h, "batch_size": 1}},
        "9": {"class_type": "Flux2Scheduler",
              "inputs": {"steps": 6, "width": w, "height": h}},
        "10": {"class_type": "KSamplerSelect",
               "inputs": {"sampler_name": "euler"}},
        "11": {"class_type": "SamplerCustomAdvanced",
               "inputs": {"noise": ["7", 0], "guider": ["6", 0], "sampler": ["10", 0],
                          "sigmas": ["9", 0], "latent_image": ["8", 0]}},
        "12": {"class_type": "VAEDecode",
               "inputs": {"samples": ["11", 0], "vae": ["3", 0]}},
        "13": {"class_type": "SaveImage",
               "inputs": {"images": ["12", 0], "filename_prefix": "bsod_ar"}},
    }


# ── API helpers ───────────────────────────────────────────────────────────────

def post_prompt(workflow: dict) -> str:
    data = json.dumps({"prompt": workflow}).encode()
    req = urllib.request.Request(f"{API}/prompt", data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["prompt_id"]

def poll(prompt_id: str, timeout=300) -> dict:
    start = time.time()
    while time.time() - start < timeout:
        with urllib.request.urlopen(f"{API}/history/{prompt_id}") as r:
            hist = json.loads(r.read())
        if prompt_id in hist:
            return hist[prompt_id]
        time.sleep(2)
    raise TimeoutError("Generation timed out")

def download(filename: str, dest: Path):
    url = f"{API}/view?filename={urllib.parse.quote(filename)}&type=output"
    with urllib.request.urlopen(url) as r:
        dest.write_bytes(r.read())


# ── Prompts ───────────────────────────────────────────────────────────────────

PROMPTS = {
    "bg_surveillance": (
        "security camera CCTV footage still frame, wide angle fisheye lens view from high corner of a cluttered dark bedroom, "
        "messy hikikomori room with band posters on walls, glowing computer monitor, vinyl records and music equipment scattered, "
        "dim atmospheric lighting, security camera perspective looking down at angle, "
        "film grain noise texture overlay, monochromatic dark atmosphere, "
        "cinematic still frame, no people, empty room, realistic photography style, "
        "dark desaturated tones, mysterious lonely atmosphere"
    ),
    "bg_livestream": (
        "cozy indie streamer bedroom setup, wide shot from in front of streaming desk, "
        "dual monitors with colorful stream overlay on screens, RGB LED strip lighting glowing soft purple and blue, "
        "ring light casting warm glow, vinyl records on wall, band posters, dreamcatcher, fairy lights, "
        "cluttered but cute aesthetic, indie music culture decor, polaroid photos strung on wall, "
        "dark room lit by screen glow, cinematic photography, "
        "portrait orientation, no people, empty streamer room, atmospheric lighting, "
        "warm and cool color contrast, bokeh background"
    ),
}

# ── Generate ──────────────────────────────────────────────────────────────────

seed = random.randint(0, 2**32)

for name, prompt in PROMPTS.items():
    print(f"\n{'='*60}")
    print(f"Generating: {name}")
    print(f"Seed: {seed}")

    wf = build_workflow(prompt, seed)
    pid = post_prompt(wf)
    print(f"Submitted prompt_id: {pid}")
    print("Waiting...", end="", flush=True)

    result = poll(pid)
    print(" done!")

    # Extract output filename
    outputs = result.get("outputs", {})
    images = []
    for node_out in outputs.values():
        images.extend(node_out.get("images", []))

    if not images:
        print(f"ERROR: no images in output for {name}")
        print("Output keys:", list(outputs.keys()))
        for k, v in outputs.items():
            print(f"  node {k}:", list(v.keys()))
        continue

    filename = images[0]["filename"]
    dest = OUT / f"{name}.png"
    download(filename, dest)
    print(f"Saved → {dest}")
    seed += 1   # different seed for second image

print("\n✓ All done!")
