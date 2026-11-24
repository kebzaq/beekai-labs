// Screenshots for the cover: laptop.png (laptop.html, 1440x900 @2x) and phone.png (phone.html, 390x844 @3x).
// Usage: node screenshot.mjs   (needs playwright-core and Google Chrome; set CHROME_PATH to use another browser)
import { chromium } from "playwright-core";
import { fileURLToPath, pathToFileURL } from "node:url";
import { dirname, join } from "node:path";

// MOCKUP_DIR lets a copy of this script run from a folder that has playwright-core installed
const here = process.env.MOCKUP_DIR || dirname(fileURLToPath(import.meta.url));
const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
});

const shots = [
  { page: "laptop.html", file: "laptop.png", viewport: { width: 1440, height: 900 }, scale: 2, mobile: false },
  { page: "phone.html", file: "phone.png", viewport: { width: 390, height: 844 }, scale: 3, mobile: true },
];
for (const { page: html, file, viewport, scale, mobile } of shots) {
  const ctx = await browser.newContext({ viewport, deviceScaleFactor: scale, isMobile: mobile, hasTouch: mobile });
  const page = await ctx.newPage();
  await page.goto(pathToFileURL(join(here, html)).href, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: join(here, file), type: "png" });
  console.log("saved", file);
  await ctx.close();
}
await browser.close();
