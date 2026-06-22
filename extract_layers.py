#!/usr/bin/env python3
"""
Extract See-through PSD layers to individual PNGs.
Usage: python3 extract_layers.py <input.psd> [output_dir]
"""
import sys
from pathlib import Path
from psd_tools import PSDImage
from psd_tools.constants import Tag

def extract(psd_path: str, out_dir: str | None = None):
    psd = PSDImage.open(psd_path)
    name = Path(psd_path).stem
    out = Path(out_dir) if out_dir else Path(psd_path).parent / f"{name}_layers"
    out.mkdir(exist_ok=True)

    print(f"Canvas: {psd.width}x{psd.height}")
    print(f"Layers ({len(psd)}):")

    def walk(layers, prefix="", depth=0):
        for i, layer in enumerate(layers):
            indent = "  " * depth
            print(f"{indent}[{i:02d}] '{layer.name}' visible={layer.visible} kind={layer.kind}")
            if layer.is_group():
                walk(layer, prefix=f"{prefix}{i:02d}_", depth=depth+1)
            else:
                if not layer.visible:
                    continue
                img = layer.composite()
                if img is None:
                    continue
                safe_name = layer.name.replace("/", "-").replace(" ", "_")
                fname = out / f"{prefix}{i:02d}_{safe_name}.png"
                img.save(fname)
                print(f"{indent}    → saved: {fname.name} ({img.size})")

    walk(psd)
    print(f"\nDone. Files saved to: {out}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract_layers.py <input.psd> [output_dir]")
        sys.exit(1)
    extract(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
