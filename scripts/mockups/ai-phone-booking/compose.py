"""Place the AI phone booking screenshots on the laptop and phone in scene-original.jpg.

Inputs (this folder): scene-original.jpg, laptop.png (1440x900 @2x), phone.png (390x844 @3x),
corners.json (from find_corners.py).
Outputs: cover.png (1600x1000), cover.webp, and cover-full.jpg (full-size check image).

Usage: python compose.py   (needs Pillow, numpy and opencv-python; cwebp for the WebP file)
"""
import json
import subprocess

import cv2
import numpy as np
from PIL import Image

# 16:10 crop of the 6000x4000 photo: full width, so the whole phone (down to y ~3820)
# and the top of the laptop lid (y ~240) both fit
CROP = (0, 120, 6000, 120 + 3750)
OUT_SIZE = (1600, 1000)
# Screen white in the warm, sunny scene: a little warmer than pure white
TINT = np.array([1.0, 0.975, 0.93])

rng = np.random.default_rng(7)
scene = np.ascontiguousarray(cv2.imread("scene-original.jpg")[:, :, ::-1], dtype=np.float32) / 255
H, W = scene.shape[:2]
corners = json.load(open("corners.json"))
lum = 0.299 * scene[..., 0] + 0.587 * scene[..., 1] + 0.114 * scene[..., 2]


def load(path):
    return np.asarray(Image.open(path).convert("RGB")).astype(np.float32) / 255


def warp(img, quad, scale_to=None):
    """Perspective-warp img (float RGB) onto quad (TL, TR, BR, BL) in scene coordinates."""
    if scale_to:  # pre-shrink with area averaging so the warp doesn't alias text
        img = cv2.resize(img, scale_to, interpolation=cv2.INTER_AREA)
    h, w = img.shape[:2]
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    m = cv2.getPerspectiveTransform(src, np.float32(quad))
    out = cv2.warpPerspective(img, m, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
    mask = cv2.warpPerspective(np.ones((h, w), np.float32), m, (W, H), flags=cv2.INTER_LINEAR)
    return np.clip(out, 0, 1), np.clip(mask, 0, 1)


def grow(quad, px):
    """Move each corner px pixels away from the quad's centre."""
    q = np.float32(quad)
    d = q - q.mean(axis=0)
    return (q + d / np.linalg.norm(d, axis=1, keepdims=True) * px).tolist()


def screen_mask(quad_mask, threshold):
    """The bright blank screen in the photo, inside the quad.

    Rounded screen corners and the camera notches are dark in the photo, so they are left
    out and stay on top of the screenshot. The sunlit gold bezel can be as bright as the
    screen, so pixels must also be neutral (the blank screens are grey-white). Grown by three
    pixels so the screen's soft, slightly blue-fringed edge doesn't show as a light line.
    """
    chroma = scene.max(axis=2) - scene.min(axis=2)
    m = ((lum > threshold) & (chroma < 0.08)).astype(np.float32)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))  # drop stray specks
    m = cv2.dilate(m, np.ones((7, 7), np.uint8))
    return cv2.GaussianBlur(m * quad_mask, (0, 0), 0.8)


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
    return np.clip(1 - np.abs(t - 0.3) / 0.35, 0, 1) ** 2 * strength * mask


def place(base, content, mask, blur_sigma, noise):
    content = cv2.GaussianBlur(content, (0, 0), blur_sigma)
    content = content + rng.normal(0, noise, content.shape).astype(np.float32)
    m = mask[..., None]
    return base * (1 - m) + np.clip(content, 0, 1) * m


out = scene.copy()

# --- Laptop (call dashboard) ---
lq = corners["laptop"]
# Grown a little past the measured edges; the brightness mask still clips it to the screen
lap, lap_quad = warp(load("laptop.png"), grow(lq, 8), scale_to=(2880, 1800))
lap_mask = screen_mask(lap_quad, 0.6)
lap = lap * TINT * shade_map(lap_mask, 0.94)[..., None] + glare(lap_mask, lq, 0.06)[..., None]
out = place(out, lap, lap_mask, 0.9, 0.006)

# --- Phone (text conversation) ---
pq = corners["phone"]
phone, phone_quad = warp(load("phone.png"), grow(pq, 6), scale_to=(1170, 2532))
phone_mask = screen_mask(phone_quad, 0.55)
phone = phone * TINT * shade_map(phone_mask, 0.86)[..., None] + glare(phone_mask, pq, 0.05)[..., None]
out = place(out, phone, phone_mask, 0.9, 0.006)

full = (np.clip(out, 0, 1) * 255).astype(np.uint8)
Image.fromarray(full).save("cover-full.jpg", quality=90)

cover = Image.fromarray(full).crop(CROP).resize(OUT_SIZE, Image.LANCZOS)
cover.save("cover.png", optimize=True)
# The sofa weave is very detailed, so let cwebp pick the quality that fits about 145 KB
subprocess.run(["cwebp", "-quiet", "-size", "145000", "-pass", "6", "-m", "6", "-sharp_yuv", "cover.png", "-o", "cover.webp"], check=True)
print("saved cover.png, cover.webp, cover-full.jpg")
