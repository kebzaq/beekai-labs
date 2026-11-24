# AI phone booking cover mockup

Source files for the AI Phone Booking Assistant portfolio cover
(`src/assets/work/ai-phone-booking-assistant/`). Nothing here is part of the site build.

1. `laptop.html` (call dashboard) and `phone.html` (text conversation) are the two screens.
2. `node screenshot.mjs`: saves `laptop.png` (1440x900 @2x) and `phone.png` (390x844 @3x).
   Needs `playwright-core` and Google Chrome.
3. `python find_corners.py`: measures the laptop and phone screen corners in
   `scene-original.jpg` and writes `corners.json` (plus `corners-check.jpg` to check by eye).
4. `python compose.py`: warps the screenshots onto the screens and saves `cover.png`
   (1600x1000), `cover.webp` and `cover-full.jpg`. Needs Pillow, numpy, opencv-python and `cwebp`.
