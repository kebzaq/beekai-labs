"""Measure the laptop and phone screen corners in scene-original.jpg.

Both blank screens are much brighter than their bezels. Starting from rough corners, the
edge is found along normals on the straight parts of each side (away from the rounded
corners and the notches), a line is fitted through the edge points and the corners are the
intersections of neighbouring lines. Writes corners.json for compose.py and saves
corners-check.jpg (zoomed crops with the corners marked) to check by eye.
Usage: python find_corners.py
"""
import json

import cv2
import numpy as np

im = cv2.imread("scene-original.jpg")
gray = cv2.GaussianBlur(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32), (5, 5), 0)

# Rough corners (TL, TR, BR, BL), read off zoomed crops of the photo
ROUGH = {
    "laptop": [(408, 1322), (3662, 258), (4050, 2107), (1038, 3188)],
    "phone": [(4370, 2465), (4915, 2690), (4420, 3720), (3775, 3460)],
}
# Straight parts of each side (TL-TR, TR-BR, BR-BL, BL-TL), as fractions along the side
SPANS = {
    # top edge has the camera notch in the middle
    "laptop": [[(0.06, 0.4), (0.62, 0.94)], [(0.06, 0.94)], [(0.06, 0.94)], [(0.06, 0.94)]],
    # phone: big rounded corners, notch in the top edge
    "phone": [[(0.1, 0.32)], [(0.2, 0.8)], [(0.25, 0.75)], [(0.2, 0.8)]],
}


def sample(img, x, y):
    return cv2.getRectSubPix(img, (1, 1), (float(x), float(y)))[0, 0]


def edge_points(p, q, center, ranges, reach=45, n=40):
    p, q, center = map(np.array, (p, q, center))
    d = (q - p) / np.linalg.norm(q - p)
    normal = np.array([-d[1], d[0]])
    if np.dot(center - p, normal) < 0:
        normal = -normal  # normal points into the screen
    pts = []
    for t in np.concatenate([np.linspace(a, b, n) for a, b in ranges]):
        base = p + (q - p) * t
        offs = np.arange(-reach, reach + 1, 0.5)
        prof = np.array([sample(gray, *(base + normal * o)) for o in offs])
        i = int(np.argmax(np.gradient(prof)))  # dark bezel -> bright screen, going inwards
        pts.append(base + normal * offs[i])
    return np.array(pts)


def fit_line(pts):
    for _ in range(3):
        vx, vy, x0, y0 = cv2.fitLine(pts.astype(np.float32), cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
        dist = np.abs((pts[:, 0] - x0) * vy - (pts[:, 1] - y0) * vx)
        pts = pts[dist < max(1.5, np.median(dist) * 3)]
    return np.array([x0, y0]), np.array([vx, vy])


def intersect(l1, l2):
    (p, r), (q, s) = l1, l2
    cross = lambda a, b: a[0] * b[1] - a[1] * b[0]
    return p + r * (cross(q - p, s) / cross(r, s))


result = {}
for name, rough in ROUGH.items():
    center = np.mean(rough, axis=0)
    lines = [fit_line(edge_points(rough[i], rough[(i + 1) % 4], center, SPANS[name][i])) for i in range(4)]
    corners = [intersect(lines[(i - 1) % 4], lines[i]) for i in range(4)]
    result[name] = [[round(float(x), 1), round(float(y), 1)] for x, y in corners]

print(json.dumps(result))
json.dump(result, open("corners.json", "w"), indent=2)

crops = []
for name, cs in result.items():
    for x, y in cs:
        x, y = int(x), int(y)
        c = im[y - 80:y + 80, x - 80:x + 80].copy()
        c = cv2.resize(c, (240, 240), interpolation=cv2.INTER_NEAREST)
        cv2.drawMarker(c, (120, 120), (0, 0, 255), cv2.MARKER_CROSS, 30, 1)
        crops.append(c)
cv2.imwrite("corners-check.jpg", np.vstack([np.hstack(crops[:4]), np.hstack(crops[4:])]))
