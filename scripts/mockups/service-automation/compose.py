"""Place the service automation screenshots on the laptop and phone in scene-original.jpg.

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

# 16:10 crop of the 3000x2001 photo, centred on the laptop (x 415-1650) and the phone on
# its notebook (up to x ~2530), with a little of the monitor stand and desk lamp around them
CROP = (272, 312, 272 + 2400, 312 + 1500)
OUT_SIZE = (1600, 1000)
# The blank screens in this photo have a slight cool, teal cast (the photo's colour grade);
# half of it is applied to the screenshots so they sit in the same light
CAST_STRENGTH = 0.5

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


def screen_cast(mask):
    """Colour of the blank screen in the photo, normalised so its brightest channel is 1."""
    c = (scene * mask[..., None]).reshape(-1, 3).sum(0) / mask.sum()
    return 1 + (c / c.max() - 1) * CAST_STRENGTH


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


out = scene.copy()

# --- Laptop (automation workflow) ---
lq = corners["laptop"]
# Grown a little past the measured edges; the brightness mask still clips it to the screen
lap, lap_quad = warp(load("laptop.png"), grow(lq, 3), scale_to=(1360, 850))
lap_mask = screen_mask(lap_quad, 0.33)
lap = lap * screen_cast(lap_mask) * shade_map(lap_mask, 0.74)[..., None] + glare(lap_mask, lq, 0.05)[..., None]
out = place(out, lap, lap_mask, 0.45, 0.008)

# --- Phone (lock screen alerts) ---
pq = corners["phone"]
# The phone screen's rounded corners border the bright notebook page, so the brightness
# mask alone would let the screenshot's square corners show; use the real screen shape
phone, phone_quad = warp(load("phone.png"), pq, scale_to=(300, 650), corner_radius=0.15)
phone_mask = screen_mask(phone_quad, 0.45)
phone = phone * screen_cast(phone_mask) * shade_map(phone_mask, 0.82)[..., None] + glare(phone_mask, pq, 0.05)[..., None]
out = place(out, phone, phone_mask, 0.45, 0.008)

full = (np.clip(out, 0, 1) * 255).astype(np.uint8)
Image.fromarray(full).save("cover-full.jpg", quality=90)

cover = Image.fromarray(full).crop(CROP).resize(OUT_SIZE, Image.LANCZOS)
cover.save("cover.png", optimize=True)
# Let cwebp pick the quality that fits about 145 KB
subprocess.run(["cwebp", "-quiet", "-size", "145000", "-pass", "6", "-m", "6", "-sharp_yuv", "cover.png", "-o", "cover.webp"], check=True)
print("saved cover.png, cover.webp, cover-full.jpg")
