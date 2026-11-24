"""Place the Common Ground screenshots on the laptop and phone in scene-original.jpg.

Inputs (this folder): scene-original.jpg, desktop.png (1440x900 @2x), mobile.png (390x844 @3x),
corners.json (from find_corners.py).
Outputs: cover.png (1600x1000), cover.webp, and cover-full.jpg (full-size check image).

Usage: python compose.py   (needs Pillow, numpy and opencv-python; cwebp for the WebP file)
"""
import json
import subprocess

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

GREEN = (0x1F, 0x4D, 0x3A)
# 16:10 crop of the 5760x3840 photo, framed around both devices
CROP = (1450, 1060, 1450 + 3920, 1060 + 2450)
OUT_SIZE = (1600, 1000)
# Screen white in the scene: a touch warmer than pure white
TINT = np.array([1.0, 0.985, 0.955])

rng = np.random.default_rng(7)
scene = np.ascontiguousarray(cv2.imread("scene-original.jpg")[:, :, ::-1], dtype=np.float32) / 255
H, W = scene.shape[:2]
corners = json.load(open("corners.json"))
lum = 0.299 * scene[..., 0] + 0.587 * scene[..., 1] + 0.114 * scene[..., 2]


def smoothstep(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def warp(img, quad, scale_to=None):
    """Perspective-warp img (float RGB) onto quad (TL, TR, BR, BL) in scene coordinates."""
    if scale_to:  # pre-shrink with area averaging so the warp doesn't alias text
        img = cv2.resize(img, scale_to, interpolation=cv2.INTER_AREA)
    h, w = img.shape[:2]
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    m = cv2.getPerspectiveTransform(src, np.float32(quad))
    out = cv2.warpPerspective(img, m, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
    mask = cv2.warpPerspective(np.ones((h, w), np.float32), m, (W, H), flags=cv2.INTER_LINEAR)
    return np.clip(out, 0, 1), mask, m


def remove_bezel_logo(img):
    """Paint out the small model name printed on the laptop's bottom bezel.

    The text sits on a thin slanted bezel strip, with the silver hinge right below it, so
    only the (slightly grown) text pixels are replaced, using the bezel colour just above.
    """
    x0, x1, y0, y1 = 3190, 3370, 2520, 2600
    region = img[y0:y1, x0:x1]
    g = lum[y0:y1, x0:x1]
    alpha = np.zeros(g.shape, np.float32)
    fill = np.zeros_like(region)
    for i, x in enumerate(range(x0, x1)):
        top = int(2530 + (x - 3200) * 0.17)  # just above the letters; the bezel runs downhill
        hinge = int(2540 + (x - 3050) * 0.134)  # where the bezel meets the silver hinge
        ref = img[top - 9:top - 3, x]
        fill[:, i] = np.median(ref, axis=0)
        ys = np.arange(max(top - 3, y0), min(top + 26, hinge - 2))
        alpha[ys - y0, i] = smoothstep(g[ys - y0, i] - np.median(lum[top - 9:top - 3, x]), 0.02, 0.08)
    alpha = cv2.GaussianBlur(cv2.dilate(alpha, np.ones((5, 5), np.uint8)), (0, 0), 1.0)
    fill = fill + rng.normal(0, 0.006, fill.shape).astype(np.float32)
    img[y0:y1, x0:x1] = region * (1 - alpha[..., None]) + fill * alpha[..., None]


def phone_screen_image():
    """Mobile screenshot under a small green status bar (time, signal, battery)."""
    shot = Image.open("mobile.png").convert("RGB")  # 1170 x 2532
    w, h = shot.size
    bar = 141  # 47pt status bar @3x
    canvas = Image.new("RGB", (w, h), GREEN)
    canvas.paste(shot.crop((0, 0, w, h - bar)), (0, bar))
    d = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", 50)
    except OSError:
        font = ImageFont.load_default()
    d.text((120, 46), "9:41", fill="white", font=font)
    # signal bars, wifi-ish dot arc, battery
    x = 860
    for i, bh in enumerate((14, 20, 27, 34)):
        d.rounded_rectangle((x + i * 17, 92 - bh, x + i * 17 + 10, 92), 2, fill="white")
    d.rounded_rectangle((955, 60, 1040, 94), 9, outline="white", width=4)
    d.rounded_rectangle((962, 67, 1022, 87), 5, fill="white")
    d.rounded_rectangle((1043, 71, 1049, 83), 2, fill="white")
    return np.asarray(canvas).astype(np.float32) / 255


def grow(quad, px):
    """Move each corner px pixels away from the quad's centre."""
    q = np.float32(quad)
    c = q.mean(axis=0)
    d = q - c
    return (q + d / np.linalg.norm(d, axis=1, keepdims=True) * px).tolist()


def shade_map(region_mask, white_level):
    """Screen brightness falloff taken from the blank screens in the photo."""
    shade = np.clip(lum / white_level, 0.6, 1.0)
    shade = cv2.GaussianBlur(shade, (0, 0), 40)
    return shade * region_mask + (1 - region_mask)


def glare(mask, quad, strength):
    """Very soft diagonal reflection across the screen."""
    (x0, y0), _, (x1, y1), _ = quad
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = ((xx - x0) * (x1 - x0) + (yy - y0) * (y1 - y0)) / ((x1 - x0) ** 2 + (y1 - y0) ** 2)
    g = np.clip(1 - np.abs(t - 0.25) / 0.35, 0, 1) ** 2 * strength
    return g * mask


def place(base, content, mask, blur_sigma, noise):
    if blur_sigma:
        content = cv2.GaussianBlur(content, (0, 0), blur_sigma)
    content = content + rng.normal(0, noise, content.shape).astype(np.float32)
    m = mask[..., None]
    return base * (1 - m) + np.clip(content, 0, 1) * m


remove_bezel_logo(scene)
lum = 0.299 * scene[..., 0] + 0.587 * scene[..., 1] + 0.114 * scene[..., 2]
out = scene.copy()

# --- Laptop ---
lq = corners["laptop"]
desktop = np.asarray(Image.open("desktop.png").convert("RGB")).astype(np.float32) / 255
lap, lap_quad_mask, _ = warp(desktop, grow(lq, 3), scale_to=(1800, 1125))
# Visible screen: the bright blank screen in the photo, grown by a pixel so its soft
# edge doesn't show as a light line, and kept inside the (slightly grown) quad
lap_mask = cv2.dilate((lum > 0.5).astype(np.float32), np.ones((3, 3), np.uint8))
lap_mask = cv2.GaussianBlur(lap_mask * np.clip(lap_quad_mask, 0, 1), (0, 0), 0.8)
lap = lap * TINT * shade_map(lap_mask, 0.95)[..., None]
lap = lap + glare(lap_mask, lq, 0.07)[..., None]
out = place(out, lap, lap_mask, 0.9, 0.006)

# --- Phone ---
pq = corners["phone"]
phone, phone_quad_mask, _ = warp(phone_screen_image(), pq, scale_to=(480, 1039))
# Visible screen = the bluish blank screen in the photo. This leaves out the rounded
# corners, the notch and the stand in front of the phone, so they stay on top.
blue_minus_red = scene[..., 2] - scene[..., 0]
phone_mask = np.clip(phone_quad_mask, 0, 1) * smoothstep(blue_minus_red, 0.02, 0.07) * smoothstep(lum, 0.45, 0.6)
phone_mask = cv2.morphologyEx(phone_mask, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
phone_mask = cv2.GaussianBlur(phone_mask, (0, 0), 1.6)
phone = phone * TINT * shade_map(phone_mask, 0.80)[..., None]
phone = phone + glare(phone_mask, pq, 0.06)[..., None]
# The phone sits a little behind the focus plane, so it is softer than the laptop
out = place(out, phone, phone_mask, 2.6, 0.008)

full = (np.clip(out, 0, 1) * 255).astype(np.uint8)
Image.fromarray(full).save("cover-full.jpg", quality=90)

cover = Image.fromarray(full).crop(CROP).resize(OUT_SIZE, Image.LANCZOS)
cover.save("cover.png", optimize=True)
subprocess.run(["cwebp", "-quiet", "-q", "80", "-m", "6", "-sharp_yuv", "cover.png", "-o", "cover.webp"], check=True)
print("saved cover.png, cover.webp, cover-full.jpg")
