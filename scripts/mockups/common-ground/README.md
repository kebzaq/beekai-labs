# Common Ground cover mockup

Source files for the Common Ground Community Center portfolio cover
(`src/assets/work/nonprofit-website/`). Nothing here is part of the site build.

1. `site.html`: demo nonprofit homepage (photos in `photos/`, credits in `credits.txt`).
2. `node screenshot.mjs`: saves `desktop.png` (1440x900 @2x) and `mobile.png` (390x844 @3x).
   Needs `playwright-core` and Google Chrome.
3. `python find_corners.py`: measures the laptop and phone screen corners in
   `scene-original.jpg` and writes `corners.json` (plus `corners-check.jpg` to check by eye).
4. `python compose.py`: warps the screenshots onto the screens and saves `cover.png`
   (1600x1000), `cover.webp` and `cover-full.jpg`. Needs Pillow, numpy, opencv-python and `cwebp`.
