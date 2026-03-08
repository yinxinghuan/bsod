"""
Generate 8 surveillance footage background images (384×288, 4:3 CRT ratio).
Saved to src/BSOD/img/sv_<name>.png
"""
import json, time, urllib.request, urllib.parse, random
from pathlib import Path

API = "http://127.0.0.1:8188"
OUT = Path(__file__).parent / "src/BSOD/img"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 384, 288   # 4:3, classic CRT / CCTV ratio

FOOTAGE = {
    "sv_rest": (
        "security camera CCTV still frame, bird's eye view looking straight down at a messy bed, "
        "crumpled sheets and pillows, cluttered bedroom floor with clothes and items, "
        "dim room, curtains closed, phone charging on nightstand, "
        "fisheye wide angle from ceiling corner, grainy film texture, "
        "cinematic still, no people, dark moody atmosphere"
    ),
    "sv_eat": (
        "security camera overhead view of a small cluttered dining table, "
        "instant noodle bowl, chopsticks, takeout containers, cup of tea, "
        "messy tabletop with crumbs and papers, bird's eye angle from high corner, "
        "CCTV footage style, grainy texture, dim indoor lighting, empty chair"
    ),
    "sv_phone": (
        "CCTV security camera view from above, close angle on a bed or floor, "
        "a smartphone screen glowing in a dark room, screen light reflecting on ceiling, "
        "blanket and pillow around the phone, late night atmosphere, "
        "overhead angle, grainy film, very dark surroundings, only screen light visible"
    ),
    "sv_desk": (
        "security camera bird's eye view of a computer desk covered in clutter, "
        "dual monitors glowing, keyboard and mouse, scattered notes and cables, "
        "coffee mug, headphones on desk, LED strip light glow, "
        "high corner CCTV angle, grainy surveillance texture, dark room"
    ),
    "sv_walk": (
        "security camera footage of an empty narrow apartment hallway or stairwell, "
        "concrete walls, fluorescent overhead lighting, door at end of hallway, "
        "wide angle fisheye from ceiling corner, grainy CCTV texture, "
        "institutional lighting, slightly overexposed"
    ),
    "sv_setup": (
        "security camera overhead view of a streaming desk setup, "
        "ring light turned on glowing bright, camera on tripod, monitor with streaming software visible, "
        "microphone, headphones, keyboard, cable management, "
        "bird's eye angle from high corner, CCTV grain, RGB glow from equipment"
    ),
    "sv_relax": (
        "CCTV security camera view from high corner of a dark bedroom, "
        "person-shaped lump under blankets on bed, room completely dark except phone screen glow, "
        "messy floor with items scattered, overhead fisheye angle, "
        "grainy surveillance footage, late night, curtains blocking all light"
    ),
    "sv_video": (
        "security camera overhead view, small filming setup on a desk, "
        "phone on a mini tripod, ring light illuminating the scene, "
        "notepad with scribblings visible, cables, backdrop fabric or wall, "
        "bird's eye CCTV angle, grainy texture, focused light spot"
    ),
    "sv_game": (
        "security camera overhead view of gaming setup, "
        "monitor with colorful game screen glowing intensely, gaming keyboard with RGB lighting, "
        "mouse and mousepad, energy drink can, snack wrappers, "
        "dark room lit only by monitor, high corner angle, CCTV grain, "
        "dramatic screen glow on ceiling"
    ),
}

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
              "inputs": {"steps": 6, "width": W, "height": H}},
        "10": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "11": {"class_type": "SamplerCustomAdvanced",
               "inputs": {"noise": ["7", 0], "guider": ["6", 0], "sampler": ["10", 0],
                          "sigmas": ["9", 0], "latent_image": ["8", 0]}},
        "12": {"class_type": "VAEDecode",
               "inputs": {"samples": ["11", 0], "vae": ["3", 0]}},
        "13": {"class_type": "SaveImage",
               "inputs": {"images": ["12", 0], "filename_prefix": "sv"}},
    }

def post(wf):
    data = json.dumps({"prompt": wf}).encode()
    req = urllib.request.Request(f"{API}/prompt", data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["prompt_id"]

def wait(pid, timeout=300):
    start = time.time()
    while time.time() - start < timeout:
        with urllib.request.urlopen(f"{API}/history/{pid}") as r:
            h = json.loads(r.read())
        if pid in h:
            return h[pid]
        time.sleep(2)
    raise TimeoutError

def download(filename, dest):
    url = f"{API}/view?filename={urllib.parse.quote(filename)}&type=output"
    with urllib.request.urlopen(url) as r:
        dest.write_bytes(r.read())

seed = random.randint(0, 2**32)
for name, prompt in FOOTAGE.items():
    print(f"\n→ {name}")
    pid = post(build_workflow(prompt, seed))
    print(f"  submitted {pid[:8]}...", end=" ", flush=True)
    result = wait(pid)
    imgs = []
    for v in result.get("outputs", {}).values():
        imgs.extend(v.get("images", []))
    if not imgs:
        print("ERROR: no output")
        continue
    dest = OUT / f"{name}.png"
    download(imgs[0]["filename"], dest)
    print(f"saved → {dest.name}")
    seed += 1

print("\n✓ Done")
