#!/usr/bin/env python3
"""
Demo: 测试 See-through PSD 分层 API
提交 Isaya idle 立绘 → 轮询 → 下载所有图层 PNG + metadata
"""
import sys
import json
import time
import requests
from pathlib import Path
from PIL import Image

API_BASE = "https://u545921-2wvn-c338e6ee.westb.seetacloud.com:8443/api/v1"
INPUT_IMAGE = Path(__file__).parent / "src/BSOD/img/isaya_idle.png"
OUTPUT_DIR = Path(__file__).parent / "test_output/seethrough_demo"
POLL_INTERVAL = 10  # seconds


def prepare_image(src: Path) -> Path:
    """RGBA → RGB white bg, pad to square."""
    img = Image.open(src).convert("RGBA")
    w, h = img.size
    size = max(w, h)

    # White background
    bg = Image.new("RGB", (size, size), (255, 255, 255))
    offset_x = (size - w) // 2
    offset_y = (size - h) // 2
    bg.paste(img, (offset_x, offset_y), img)  # use alpha as mask

    out = OUTPUT_DIR / "input_padded.png"
    bg.save(out)
    print(f"[prep] {src.name} ({w}x{h}) → padded to {size}x{size} → {out}")
    return out


def submit_task(image_path: Path) -> str:
    """POST image to API, return task_id."""
    config = {
        "resolution": 1280,
        "inference_steps": 30,
        "save_to_psd": True,
    }
    with open(image_path, "rb") as f:
        resp = requests.post(
            f"{API_BASE}/tasks",
            files={"image": (image_path.name, f, "image/png")},
            data={"config": json.dumps(config)},
            timeout=30,
        )
    resp.raise_for_status()
    data = resp.json()
    task_id = data["task_id"]
    print(f"[submit] task_id={task_id}, status={data['status']}")
    return task_id


def poll_task(task_id: str) -> dict:
    """Poll until completed or failed."""
    url = f"{API_BASE}/tasks/{task_id}"
    while True:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        status = data["status"]
        progress = data.get("progress") or {}
        msg = progress.get("message", "")
        stage_pct = progress.get("stage_progress") or 0

        print(f"[poll] status={status} {msg} ({stage_pct:.0%})")

        if status == "completed":
            return data
        elif status == "failed":
            print(f"[error] Task failed: {data.get('error', 'unknown')}")
            sys.exit(1)

        time.sleep(POLL_INTERVAL)


def download_files(task_id: str, layer_tags: list[str]):
    """Download metadata, preview, and individual layer PNGs."""
    base = f"{API_BASE}/tasks/{task_id}/files"

    # Metadata
    resp = requests.get(f"{base}/metadata", timeout=15)
    resp.raise_for_status()
    meta_path = OUTPUT_DIR / "metadata.json"
    meta_path.write_text(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    print(f"[dl] metadata → {meta_path}")

    # Preview
    resp = requests.get(f"{base}/preview", timeout=30)
    resp.raise_for_status()
    preview_path = OUTPUT_DIR / "preview.png"
    preview_path.write_bytes(resp.content)
    print(f"[dl] preview → {preview_path}")

    # PSD
    resp = requests.get(f"{base}/psd", timeout=60)
    resp.raise_for_status()
    psd_path = OUTPUT_DIR / "output.psd"
    psd_path.write_bytes(resp.content)
    print(f"[dl] psd → {psd_path} ({len(resp.content) / 1024:.0f} KB)")

    # Individual layers
    layers_dir = OUTPUT_DIR / "layers"
    layers_dir.mkdir(exist_ok=True)
    for tag in layer_tags:
        resp = requests.get(f"{base}/layer/{tag}.png", timeout=30)
        if resp.status_code == 404:
            print(f"[dl] layer/{tag}.png → 404, skipping")
            continue
        resp.raise_for_status()
        layer_path = layers_dir / f"{tag}.png"
        layer_path.write_bytes(resp.content)
        print(f"[dl] layer/{tag}.png → {layer_path} ({len(resp.content) / 1024:.0f} KB)")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: prepare
    padded = prepare_image(INPUT_IMAGE)

    # Step 2: submit
    task_id = submit_task(padded)

    # Step 3: poll
    result = poll_task(task_id)

    # Step 4: download
    layers_info = result.get("result", {}).get("layers", [])
    layer_tags = [l["tag"] for l in layers_info]
    print(f"\n[info] {len(layer_tags)} layers: {layer_tags}")
    print(f"[info] frame_size: {result['result'].get('frame_size')}")

    download_files(task_id, layer_tags)
    print(f"\n✓ Done! Output in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
