#!/usr/bin/env python3
"""Remove grey background from BSOD Isaya sprites using grey-screen chroma key."""
import os, sys
import numpy as np
from PIL import Image

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src/BSOD/img")
FEATHER = 20
MARGIN  = 0.02

SPRITES = ['isaya_idle', 'isaya_happy', 'isaya_sad', 'isaya_surprised']


def remove_grey_bg(img_path, target_grey=152, threshold=28):
    """Remove grey background using Euclidean color distance to target grey.
    target_grey: the grey level (~#999999 = 153), adjust if needed.
    threshold: max distance from grey to remove (lower = more conservative).
    """
    img = Image.open(img_path).convert("RGBA")
    orig_w, orig_h = img.size
    data = np.array(img, dtype=np.float32)
    r, g, b = data[:, :, 0], data[:, :, 1], data[:, :, 2]

    # Euclidean distance from target neutral grey (target_grey, target_grey, target_grey)
    dist = np.sqrt(
        (r - target_grey) ** 2 +
        (g - target_grey) ** 2 +
        (b - target_grey) ** 2
    )

    # Smooth fade: fully remove within threshold, feather up to threshold+FEATHER
    alpha_remove = np.clip(1.0 - (dist - threshold) / FEATHER, 0.0, 1.0)
    data[:, :, 3] = data[:, :, 3] * (1.0 - alpha_remove)
    result = Image.fromarray(data.astype(np.uint8))

    # Auto-crop to character bounding box
    alpha = np.array(result)[:, :, 3]
    rows  = np.any(alpha > 10, axis=1)
    cols  = np.any(alpha > 10, axis=0)
    if not rows.any():
        result.save(img_path)
        return

    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]

    pad_h = int((rmax - rmin) * MARGIN)
    pad_w = int((cmax - cmin) * MARGIN)
    rmin  = max(0, rmin - pad_h)
    rmax  = min(orig_h - 1, rmax + pad_h)
    cmin  = max(0, cmin - pad_w)
    cmax  = min(orig_w - 1, cmax + pad_w)

    cropped = result.crop((cmin, rmin, cmax + 1, rmax + 1))
    crop_w, crop_h = cropped.size
    scale  = min(orig_w / crop_w, orig_h / crop_h)
    scaled = cropped.resize((int(crop_w * scale), int(crop_h * scale)), Image.LANCZOS)

    # Paste to bottom-center (character stands on ground)
    canvas = Image.new("RGBA", (orig_w, orig_h), (0, 0, 0, 0))
    canvas.paste(scaled, ((orig_w - scaled.width) // 2, orig_h - scaled.height))
    canvas.save(img_path)
    print(f"  -> {os.path.basename(img_path)}  ({os.path.getsize(img_path)//1024} KB)")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    sprites = SPRITES if target == "all" else [s for s in SPRITES if target in s]

    for name in sprites:
        path = os.path.join(IMG_DIR, f"{name}.png")
        if os.path.exists(path):
            print(f"Processing {name}...")
            remove_grey_bg(path)
        else:
            print(f"  SKIP (not found): {path}")

    print("Done.")
