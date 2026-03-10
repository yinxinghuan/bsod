#!/usr/bin/env python3
"""
Generate stream event illustration images (one per event) via online img2img API.
Reference image: bg_stream.png (dark gaming room aesthetic).

Usage:
  python3 gen_stream_event_imgs.py           # generate all
  python3 gen_stream_event_imgs.py s_lag     # generate one by ID
"""

import json, os, ssl, sys, time, math, urllib.request, urllib.error
from PIL import Image
from collections import deque

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src/BSOD/img/stream_events")
os.makedirs(IMG_DIR, exist_ok=True)

API_URL  = "http://aiservice.wdabuliu.com:8019/genl_image"
REF_URL  = "https://raw.githubusercontent.com/yinxinghuan/bsod/master/src/BSOD/img/bg_stream.png"
USER_ID  = "bsod_game"
RATE_WAIT = 78
API_TIMEOUT = 90

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

# ── Style base ─────────────────────────────────────────────────────────────────

STYLE = (
    "anime illustration, dark gaming room atmosphere, purple neon accent lighting, "
    "cinematic close-up, moody dramatic lighting, digital screen glow, "
    "no characters, no people, UI and environment only, "
    "sharp detailed render, dark background"
)

# ── Event image prompts ────────────────────────────────────────────────────────

EVENTS = [
    {
        "id": "s_died10",
        "prompt": STYLE + ", game over screen on monitor showing death counter x10, "
            "pixelated YOU DIED text in red, dark gaming aesthetic, dramatic"
    },
    {
        "id": "s_change_game",
        "prompt": STYLE + ", live chat interface flooded with scrolling text messages "
            "all saying CHANGE GAME over and over, chaotic chat wall, blue tinted screen"
    },
    {
        "id": "s_state",
        "prompt": STYLE + ", warm glowing super chat donation notification pinned on screen, "
            "caring message tone, soft pink and amber light, streaming platform UI"
    },
    {
        "id": "s_new_viewer",
        "prompt": STYLE + ", streaming chat notification showing NEW VIEWER joined, "
            "fresh arrival badge, question mark icon, welcoming atmosphere"
    },
    {
        "id": "s_technical",
        "prompt": STYLE + ", close-up of microphone with large red X icon, "
            "audio waveform flatlined on dark monitor, technical failure mood"
    },
    {
        "id": "s_superchat",
        "prompt": STYLE + ", glowing super chat message pinned at top of stream, "
            "warm light radiating from the message, heartfelt donation notification"
    },
    {
        "id": "s_collab",
        "prompt": STYLE + ", collab request notification popup on screen, "
            "two streamer avatar icons side by side with plus symbol between them"
    },
    {
        "id": "s_challenge",
        "prompt": STYLE + ", chat challenge notification on screen, "
            "gift box icons floating around, enthusiastic chat messages, hype energy"
    },
    {
        "id": "s_silence",
        "prompt": STYLE + ", empty chat window, no messages, single blinking cursor, "
            "very quiet atmosphere, dim screen, abandoned feeling"
    },
    {
        "id": "s_milestone",
        "prompt": STYLE + ", follower counter on streaming platform showing exactly 2000, "
            "soft celebratory glow, milestone achievement notification, golden light"
    },
    {
        "id": "s_hate_raid",
        "prompt": STYLE + ", stream chat flooded with red angry spam messages, "
            "warning overlay flashing, hostile takeover of chat, chaotic red tones, "
            "raid alert notification with danger red color"
    },
    {
        "id": "s_algorithm",
        "prompt": STYLE + ", platform recommendation notification on screen, "
            "trending arrow pointing up sharply, green graph spike, algorithm boost alert"
    },
    {
        "id": "s_fanart",
        "prompt": STYLE + ", fan art image displayed on dark streaming screen, "
            "beautiful detailed artwork glowing on monitor, purple accent, artistic warmth"
    },
    {
        "id": "s_big_donation",
        "prompt": STYLE + ", massive donation notification with golden light burst, "
            "large glowing number on screen, chat explosion, gold and amber tones"
    },
    {
        "id": "s_lag",
        "prompt": STYLE + ", stream screen with heavy lag artifacts and pixelation, "
            "buffering wheel icon, frame drop visualization, network signal bars dropping"
    },
    {
        "id": "s_trending",
        "prompt": STYLE + ", trending chart on platform screen with name highlighted, "
            "fire icon trending indicator, orange and red glow, rising chart"
    },
    {
        "id": "s_sniping",
        "prompt": STYLE + ", large verified streamer badge appearing in dark chat, "
            "big lightning bolt icon notification, chaos energy in chat, blue electric glow"
    },
    {
        "id": "s_clip_viral",
        "prompt": STYLE + ", viral clip view counter rapidly increasing on screen, "
            "fire icon viral notification, 10000 views ticker, golden orange glow"
    },
    {
        "id": "s_hate_comment",
        "prompt": STYLE + ", single harsh comment highlighted in red among dark chat messages, "
            "one toxic message standing out, red glow, uncomfortable atmosphere"
    },
    {
        "id": "s_spoiler",
        "prompt": STYLE + ", large SPOILER WARNING text covering game screen, "
            "red and black warning overlay, dramatic impact"
    },
    {
        "id": "s_argue",
        "prompt": STYLE + ", two chat messages clashing on screen with lightning between them, "
            "argument visualization in live chat, tense confrontation energy"
    },
    {
        "id": "s_request_face",
        "prompt": STYLE + ", chat flooded with face cam request messages, "
            "camera icon with spotlight, audience demand visualization"
    },
    {
        "id": "s_personal_best",
        "prompt": STYLE + ", personal best score achievement notification on gaming screen, "
            "PERSONAL BEST text with golden glow, achievement unlocked celebration"
    },
    {
        "id": "s_platform_down",
        "prompt": STYLE + ", platform server maintenance warning notification on screen, "
            "server icon with warning symbol, yellow caution tone"
    },
    {
        "id": "s_viewer_crisis",
        "prompt": STYLE + ", private message notification glowing softly on screen, "
            "emotional DM alert, gentle light, intimate and quiet atmosphere"
    },
    {
        "id": "s_comparison",
        "prompt": STYLE + ", split comparison on screen showing 50000 vs small number, "
            "stark contrast of follower counts, shadow and light, competitive pressure"
    },
    {
        "id": "s_small_collab_dm",
        "prompt": STYLE + ", DM notification from tiny streamer with 30 followers shown, "
            "small humble message notification, warm sincere tone"
    },
    {
        "id": "s_international_wave",
        "prompt": STYLE + ", chat filled with messages in multiple languages and country flags, "
            "international viewers flooding in, colorful multilingual chat wall"
    },
    {
        "id": "s_raid_out",
        "prompt": STYLE + ", raid outgoing notification on streaming platform, "
            "arrow sending viewers to another channel, blue wave sending energy forward"
    },
    {
        "id": "s_irl_slip",
        "prompt": STYLE + ", chat exploding with shocked reaction emojis after personal reveal, "
            "surprise wave of messages, moment of vulnerability, soft dramatic light"
    },
    {
        "id": "s_game_crashed",
        "prompt": STYLE + ", windows error crash dialog on dark screen, "
            "game crash blue screen of death aesthetic, dark humor, computer failure"
    },
    {
        "id": "s_mass_follow",
        "prompt": STYLE + ", follower counter rapidly ticking up on streaming platform, "
            "wave of follow notifications flooding in, blue numbers rising, surge energy"
    },
    {
        "id": "s_clip_editor_dm",
        "prompt": STYLE + ", DM notification from clip editor with video scissors icon, "
            "editing timeline visible, collaboration proposal aesthetic"
    },
    {
        "id": "s_sponsor_dm",
        "prompt": STYLE + ", official brand sponsorship email or DM on screen, "
            "business card aesthetic, gold accent, first sponsor notification feeling"
    },
    {
        "id": "s_platform_strike",
        "prompt": STYLE + ", red copyright strike warning notification from platform, "
            "DMCA warning overlay on screen, urgent red and black, music note with X"
    },
]

# ── Helpers ────────────────────────────────────────────────────────────────────

def call_api(ref_url, prompt):
    payload = json.dumps({
        "query": "",
        "params": {"url": ref_url, "prompt": prompt, "user_id": USER_ID},
    }).encode()
    req = urllib.request.Request(API_URL, data=payload,
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=API_TIMEOUT) as r:
            result = json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            result = json.loads(body)
        except Exception:
            print(f"  HTTP {e.code}: {body[:200]}")
            return None
    if result.get("code") == 200: return result["url"]
    if result.get("code") == 429: raise RuntimeError("rate_limit")
    print(f"  ✗ code={result.get('code')}")
    return None

def download(url, path, retries=3):
    src_ext = os.path.splitext(url.split("?")[0])[1].lower()
    tmp = path + src_ext if src_ext != ".png" else path
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30, context=_SSL_CTX) as r:
                data = r.read()
            break
        except Exception as e:
            if attempt < retries - 1:
                print(f"  download error ({e}), retrying…")
                time.sleep(3)
            else:
                raise
    with open(tmp, "wb") as f: f.write(data)
    if tmp != path:
        import subprocess
        subprocess.run(["sips", "-s", "format", "png", tmp, "--out", path],
                       check=True, capture_output=True)
        os.remove(tmp)

def remove_green(img_path, threshold=60, feather=30):
    img = Image.open(img_path).convert("RGBA")
    data = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = data[x, y]
            greenness = g - max(r, b)
            if greenness > threshold:
                remove = min(1.0, (greenness - threshold) / feather)
                data[x, y] = (r, g, b, int(a * (1 - remove)))
    img.save(img_path)

# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    tasks = [e for e in EVENTS if target is None or e["id"] == target]

    if not tasks:
        sys.exit(f"Event '{target}' not found")

    print(f"Generating {len(tasks)} stream event image(s)…\n")

    for i, ev in enumerate(tasks):
        out = os.path.join(IMG_DIR, f"{ev['id']}.png")
        if os.path.exists(out) and target is None:
            print(f"[{i+1}/{len(tasks)}] {ev['id']} — already exists, skipping")
            continue

        print(f"[{i+1}/{len(tasks)}] {ev['id']}")
        while True:
            try:
                result_url = call_api(REF_URL, ev["prompt"])
                break
            except RuntimeError:
                print(f"  rate limited — waiting {RATE_WAIT}s…")
                time.sleep(RATE_WAIT)

        if not result_url:
            print(f"  ✗ skipping")
            continue

        print(f"  ↓ downloading…")
        download(result_url, out)
        remove_green(out)
        size = os.path.getsize(out) // 1024
        print(f"  ✓ {size} KB")

        if i < len(tasks) - 1 and target is None:
            print(f"  ⏳ waiting {RATE_WAIT}s…")
            time.sleep(RATE_WAIT)

    print(f"\n── Done ── → {IMG_DIR}")
