# Service request automation cover mockup

Source files for the Service Request Automation portfolio cover
(`src/assets/work/service-request-automation/`). Nothing here is part of the site build.

1. `laptop.html` (automation workflow) and `phone.html` (lock screen alerts) are the two screens.
2. `node screenshot.mjs`: saves `laptop.png` (1440x900 @2x) and `phone.png` (390x844 @3x).
   Needs `playwright-core` and Google Chrome.
3. `python find_corners.py`: measures the laptop and phone screen corners in
   `scene-original.jpg` and writes `corners.json` (plus `corners-check.jpg` to check by eye).
4. `python compose.py`: warps the screenshots onto the screens and saves `cover.png`
   (1600x1000), `cover.webp` and `cover-full.jpg`. Needs Pillow, numpy, opencv-python and `cwebp`.
