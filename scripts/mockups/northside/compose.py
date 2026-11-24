"""Place the Northside Heating & Air screenshots on the laptop and phone in scene-original.jpg.

Inputs (this folder): scene-original.jpg, desktop.png (1440x900 @2x), mobile.png (390x844 @3x),
corners.json (from find_corners.py).
Outputs: cover.png (1600x900, 16:9 like the Velvet Haus cover), cover.webp, and cover-full.jpg
(full-size check image).

Usage: python compose.py   (needs Pillow, numpy and opencv-python; cwebp for the WebP file)
"""
import json
import subprocess

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# 16:9 crop of the 5760x3840 photo (the card image shape, same as the Velvet Haus cover),
# framed tightly around the laptop (x ~2130-4110) and the phone on its stand (to x ~4900),
# so the devices fill most of the frame and the vases on the left stay out
CROP = (2025, 1370, 2025 + 2980, 1370 + 1676)
OUT_SIZE = (1600, 900)
# Screen white in this warm room: a touch warmer than pure white
TINT = np.array([1.0, 0.985, 0.955])

rng = np.random.default_rng(7)
scene = np.ascontiguousarray(cv2.imread("scene-original.jpg")[:, :, ::-1], dtype=np.float32) / 255
H, W = scene.shape[:2]
corners = json.load(open("corners.json"))
lum = 0.299 * scene[..., 0] + 0.587 * scene[..., 1] + 0.114 * scene[..., 2]


def load(path):
    return np.asarray(Image.open(path).convert("RGB")).astype(np.float32) / 255


def rounded_rect(w, h, radius):
    """Anti-aliased rounded-rectangle alpha mask, drawn at 4x and scaled down."""
    s = 4
    m = np.zeros((h * s, w * s), np.uint8)
    r = int(radius * s)
    cv2.rectangle(m, (r, 0), (w * s - r, h * s), 255, -1)
    cv2.rectangle(m, (0, r), (w * s, h * s - r), 255, -1)
    for cx, cy in ((r, r), (w * s - r, r), (r, h * s - r), (w * s - r, h * s - r)):
        cv2.circle(m, (cx, cy), r, 255, -1)
    return cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255


def warp(img, quad, scale_to=None, corner_radius=0):
    """Perspective-warp img (float RGB) onto quad (TL, TR, BR, BL) in scene coordinates.

    corner_radius (a fraction of the image width) rounds the warped mask's corners, for
    phone screens whose rounded corners sit next to bright surfaces.
    """
    if scale_to:  # pre-shrink with area averaging so the warp doesn't alias text
        img = cv2.resize(img, scale_to, interpolation=cv2.INTER_AREA)
    h, w = img.shape[:2]
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    m = cv2.getPerspectiveTransform(src, np.float32(quad))
    out = cv2.warpPerspective(img, m, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
    shape = rounded_rect(w, h, corner_radius * w) if corner_radius else np.ones((h, w), np.float32)
    mask = cv2.warpPerspective(shape, m, (W, H), flags=cv2.INTER_LINEAR)
    return np.clip(out, 0, 1), np.clip(mask, 0, 1)


def grow(quad, px):
    """Move each corner px pixels away from the quad's centre."""
    q = np.float32(quad)
    d = q - q.mean(axis=0)
    return (q + d / np.linalg.norm(d, axis=1, keepdims=True) * px).tolist()


def screen_mask(quad_mask, threshold):
    """The bright blank screen in the photo, inside the quad.

    Rounded screen corners, the laptop's camera notch and the phone's Dynamic Island are
    dark in the photo, so they are left out and stay on top of the screenshot. Grown by a
    pixel so the screen's soft edge doesn't show as a light line.
    """
    # A soft ramp around the threshold (not a hard cut) keeps the edge from looking jagged
    t = np.clip((lum - (threshold - 0.08)) / 0.12, 0, 1)
    m = t * t * (3 - 2 * t)
    m = cv2.dilate(m, np.ones((3, 3), np.uint8))
    return cv2.GaussianBlur(m * quad_mask, (0, 0), 0.6)


def phone_screen_image():
    """Mobile screenshot under a navy status bar (time, signal, battery), so the phone's
    notch covers the status bar instead of the site's top bar."""
    shot = Image.open("mobile.png").convert("RGB")  # 1170 x 2532
    w, h = shot.size
    bar = 141  # 47pt status bar @3x
    canvas = Image.new("RGB", (w, h), (0x15, 0x2B, 0x47))
    canvas.paste(shot.crop((0, 0, w, h - bar)), (0, bar))
    d = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", 50)
    except OSError:
        font = ImageFont.load_default()
    d.text((120, 46), "9:41", fill="white", font=font)
    x = 860  # signal bars, then battery
    for i, bh in enumerate((14, 20, 27, 34)):
        d.rounded_rectangle((x + i * 17, 92 - bh, x + i * 17 + 10, 92), 2, fill="white")
    d.rounded_rectangle((955, 60, 1040, 94), 9, outline="white", width=4)
    d.rounded_rectangle((962, 67, 1022, 87), 5, fill="white")
    d.rounded_rectangle((1043, 71, 1049, 83), 2, fill="white")
    return np.asarray(canvas).astype(np.float32) / 255


def remove_bezel_logo(img):
    """Paint out the small model name printed on the laptop's bottom bezel.

    The text (x ~3031-3159, y ~2494-2515) sits on a level strip of dark bezel with the silver
    hinge just below (y ~2520), so only the light text pixels are replaced, with the bezel
    colour from just above the letters in the same column.
    """
    x0, x1, y0, y1 = 3020, 3172, 2488, 2519
    region = img[y0:y1, x0:x1]
    ref = img[2478:2486, x0:x1]
    fill = np.repeat(np.median(ref, axis=0)[None], y1 - y0, axis=0)
    ref_lum = np.median(lum[2478:2486, x0:x1], axis=0)
    t = np.clip((lum[y0:y1, x0:x1] - ref_lum - 0.02) / 0.06, 0, 1)
    alpha = cv2.GaussianBlur(cv2.dilate(t * t * (3 - 2 * t), np.ones((5, 5), np.uint8)), (0, 0), 1.0)
    fill = fill + rng.normal(0, 0.006, fill.shape).astype(np.float32)
    img[y0:y1, x0:x1] = region * (1 - alpha[..., None]) + fill * alpha[..., None]


def shade_map(region_mask, white_level):
    """Screen brightness falloff taken from the blank screens in the photo."""
    shade = np.clip(lum / white_level, 0.6, 1.0)
    shade = cv2.GaussianBlur(shade, (0, 0), 20)
    return shade * region_mask + (1 - region_mask)


def glare(mask, quad, strength):
    """Very soft diagonal reflection across the screen."""
    (x0, y0), _, (x1, y1), _ = quad
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = ((xx - x0) * (x1 - x0) + (yy - y0) * (y1 - y0)) / ((x1 - x0) ** 2 + (y1 - y0) ** 2)
    return np.clip(1 - np.abs(t - 0.3) / 0.35, 0, 1) ** 2 * strength * mask


def place(base, content, mask, blur_sigma, noise):
    content = cv2.GaussianBlur(content, (0, 0), blur_sigma)
    content = content + rng.normal(0, noise, content.shape).astype(np.float32)
    m = mask[..., None]
    return base * (1 - m) + np.clip(content, 0, 1) * m


remove_bezel_logo(scene)
lum = 0.299 * scene[..., 0] + 0.587 * scene[..., 1] + 0.114 * scene[..., 2]
out = scene.copy()

# --- Laptop (desktop homepage) ---
lq = corners["laptop"]
# Grown a little past the measured edges; the brightness mask still clips it to the screen
lap, lap_quad = warp(load("desktop.png"), grow(lq, 3), scale_to=(1800, 1125))
lap_mask = screen_mask(lap_quad, 0.6)
lap = lap * TINT * shade_map(lap_mask, 0.97)[..., None] + glare(lap_mask, lq, 0.06)[..., None]
out = place(out, lap, lap_mask, 0.8, 0.006)

# --- Phone (mobile homepage) ---
pq = corners["phone"]
# The screen's real shape (rounded corners) limits the screenshot; the brightness mask then
# leaves out the dark notch and the wooden stand in front of the phone, so they stay on top
phone, phone_quad = warp(phone_screen_image(), grow(pq, 3), scale_to=(480, 1039), corner_radius=0.13)
phone_mask = screen_mask(phone_quad, 0.68)
phone = phone * TINT * shade_map(phone_mask, 0.86)[..., None] + glare(phone_mask, pq, 0.05)[..., None]
out = place(out, phone, phone_mask, 1.0, 0.006)

full = (np.clip(out, 0, 1) * 255).astype(np.uint8)
Image.fromarray(full).save("cover-full.jpg", quality=90)

cover = Image.fromarray(full).crop(CROP).resize(OUT_SIZE, Image.LANCZOS)
cover.save("cover.png", optimize=True)
# Let cwebp pick the quality that fits about 145 KB
subprocess.run(["cwebp", "-quiet", "-size", "145000", "-pass", "6", "-m", "6", "-sharp_yuv", "cover.png", "-o", "cover.webp"], check=True)
print("saved cover.png, cover.webp, cover-full.jpg")
