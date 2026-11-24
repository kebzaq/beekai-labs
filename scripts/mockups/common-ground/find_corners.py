"""Measure the laptop and phone screen corners in scene-original.jpg.

Starting from rough corners, each side's edge is found along normals (the screen is
brighter than the bezel), a line is fitted through the edge points and the corners are
the intersections of neighbouring lines. Prints JSON for compose.py and saves
corners-check.jpg with the result drawn on zoomed crops.
Usage: python find_corners.py
"""
import json
import cv2
import numpy as np

im = cv2.imread("scene-original.jpg")
gray = cv2.GaussianBlur(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32), (5, 5), 0)

# Rough corners (TL, TR, BR, BL), read off the photo
ROUGH = {
    "laptop": [(2814, 1348), (4398, 1462), (4140, 2633), (2543, 2384)],
    # Lines through the straight parts of the phone screen (the corners are rounded).
    # The bottom of the screen is hidden by the wooden stand, so the bottom corners are
    # set from the screen's aspect ratio instead of measured.
    "phone": [(4612, 2058), (5020, 2120), (4740, 3170), (4330, 3110)],
}
# Parts of each side (TL-TR, TR-BR, BR-BL, BL-TL) that are clean straight edges
SPANS = {
    "laptop": [[(0.08, 0.92)]] * 4,
    # top: either side of the notch; sides: above the stand; bottom: not measured
    "phone": [[(0.13, 0.2), (0.8, 0.87)], [(0.12, 0.7)], None, [(0.3, 0.88)]],
}
# Length of the phone screen along its sides, in photo pixels. The bottom is hidden by the
# stand and the phone is turned away from the camera (so it looks narrower than 390:844);
# this puts the screen bottom just below the stand's front edge.
PHONE_SCREEN_LENGTH = 1060


def sample(img, x, y):
    return cv2.getRectSubPix(img, (1, 1), (float(x), float(y)))[0, 0]


def edge_points(p, q, center, ranges, reach=24, n=40):
    p, q, center = map(np.array, (p, q, center))
    d = (q - p) / np.linalg.norm(q - p)
    normal = np.array([-d[1], d[0]])
    if np.dot(center - p, normal) < 0:
        normal = -normal  # normal points into the screen
    pts = []
    ts = np.concatenate([np.linspace(a, b, n) for a, b in ranges])
    for t in ts:
        base = p + (q - p) * t
        offs = np.arange(-reach, reach + 1, 0.5)
        prof = np.array([sample(gray, *(base + normal * o)) for o in offs])
        grad = np.gradient(prof)
        i = int(np.argmax(grad))  # dark bezel -> bright screen, going inwards
        pts.append(base + normal * offs[i])
    return np.array(pts)


def fit_line(pts):
    for _ in range(3):
        vx, vy, x0, y0 = cv2.fitLine(pts.astype(np.float32), cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
        dist = np.abs((pts[:, 0] - x0) * vy - (pts[:, 1] - y0) * vx)
        keep = dist < max(1.5, np.median(dist) * 3)
        pts = pts[keep]
    return np.array([x0, y0]), np.array([vx, vy])


def intersect(l1, l2):
    (p, r), (q, s) = l1, l2
    cross = lambda a, b: a[0] * b[1] - a[1] * b[0]
    t = cross(q - p, s) / cross(r, s)
    return p + r * t


result = {}
for name, rough in ROUGH.items():
    center = np.mean(rough, axis=0)
    lines = [
        fit_line(edge_points(rough[i], rough[(i + 1) % 4], center, SPANS[name][i])) if SPANS[name][i] else None
        for i in range(4)
    ]
    if name == "phone":
        top, right, _, left = lines
        tl, tr = intersect(left, top), intersect(top, right)
        # Side directions, pointing down the screen
        dl = left[1] if left[1][1] > 0 else -left[1]
        dr = right[1] if right[1][1] > 0 else -right[1]
        corners = [tl, tr, tr + dr * PHONE_SCREEN_LENGTH, tl + dl * PHONE_SCREEN_LENGTH]
    else:
        corners = [intersect(lines[(i - 1) % 4], lines[i]) for i in range(4)]
    result[name] = [[round(float(x), 1), round(float(y), 1)] for x, y in corners]

print(json.dumps(result))
json.dump(result, open("corners.json", "w"), indent=2)

# Zoomed crops around every corner for checking by eye
crops = []
for name, cs in result.items():
    for x, y in cs:
        x, y = int(x), int(y)
        c = im[y - 60:y + 60, x - 60:x + 60].copy()
        c = cv2.resize(c, (240, 240), interpolation=cv2.INTER_NEAREST)
        cv2.drawMarker(c, (120, 120), (0, 0, 255), cv2.MARKER_CROSS, 30, 1)
        crops.append(c)
cv2.imwrite("corners-check.jpg", np.vstack([np.hstack(crops[:4]), np.hstack(crops[4:])]))
