#!/usr/bin/env python3
"""
Process Laisa sprites: remove grey background, keep original resolution exactly.
No cropping, no rescaling — transparent background only.

Input:  test_output/laisa_*_ref.png  (768x1152)
Output: src/BSOD/img/laisa_*.png    (768x1152, transparent bg)
"""
import os
import numpy as np
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE, "test_output")
DST_DIR = os.path.join(BASE, "src/BSOD/img")

# source_name -> dest_name
SPRITE_MAP = {
    "laisa_idle_ref":      "laisa_idle",
    "laisa_happy_ref":     "laisa_happy",
    "laisa_sad_ref":       "laisa_sad",
    "laisa_surprised_ref": "laisa_surprised",
    "laisa_tired_ref":     "laisa_tired",
    "laisa_focused_ref":   "laisa_focused",
}

# Grey background: target ~#989898 (152,152,152)
TARGET_GREY = 152
THRESHOLD   = 35   # euclidean distance threshold
FEATHER     = 18   # feather width
MAX_CHROMA  = 22   # max R-G-B spread to be considered "grey" (protects colored hair/clothes)


def remove_grey_bg(src_path: str, dst_path: str):
    img  = Image.open(src_path).convert("RGBA")
    data = np.array(img, dtype=np.float32)

    r, g, b = data[:, :, 0], data[:, :, 1], data[:, :, 2]

    # Euclidean distance from target grey
    dist = np.sqrt(
        (r - TARGET_GREY) ** 2 +
        (g - TARGET_GREY) ** 2 +
        (b - TARGET_GREY) ** 2
    )

    # Chroma = max(R,G,B) - min(R,G,B): near 0 for grey, high for colored pixels
    # This protects blue hair, skin tones, clothing colors from being removed
    chroma = (np.maximum(r, np.maximum(g, b)) - np.minimum(r, np.minimum(g, b)))
    is_grey = chroma < MAX_CHROMA  # True only for near-achromatic pixels

    # Blend: distance-based alpha BUT only applied where pixel is truly grey
    alpha_removal = np.clip(1.0 - (dist - THRESHOLD) / FEATHER, 0.0, 1.0)
    alpha_removal = alpha_removal * is_grey.astype(np.float32)

    data[:, :, 3] = data[:, :, 3] * (1.0 - alpha_removal)

    result = Image.fromarray(data.astype(np.uint8))
    # Save at original size — no resize, no crop
    result.save(dst_path, optimize=False)

    src_kb = os.path.getsize(src_path) // 1024
    dst_kb = os.path.getsize(dst_path) // 1024
    w, h   = result.size
    print(f"  {os.path.basename(src_path)} ({src_kb}KB, {w}x{h})  ->  {os.path.basename(dst_path)} ({dst_kb}KB)")


if __name__ == "__main__":
    print(f"Processing {len(SPRITE_MAP)} sprites...\n")
    for src_name, dst_name in SPRITE_MAP.items():
        src = os.path.join(SRC_DIR, f"{src_name}.png")
        dst = os.path.join(DST_DIR, f"{dst_name}.png")
        if not os.path.exists(src):
            print(f"  SKIP (not found): {src_name}.png")
            continue
        remove_grey_bg(src, dst)

    print("\nDone.")
