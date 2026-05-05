/**
 * Playwright demo recorder for Date Architect
 *
 * Takes screenshots at key moments, then stitches them into an animated GIF
 * using ffmpeg. Works with Playwright's chromium headless shell (no full
 * browser video-recording support required).
 *
 * Outputs:
 *   docs/demo.gif — animated GIF for README
 *
 * Usage (from repo root):
 *   node scripts/record_demo.js
 */

const { chromium } = require("playwright");
const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const BASE_URL = "http://localhost:3000";
const FRAMES_DIR = path.join(__dirname, "frames");
const GIF_OUT = path.join(__dirname, "..", "docs", "demo.gif");

async function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function shot(page, name, repeat = 1) {
  const file = path.join(FRAMES_DIR, `${name}.png`);
  await page.screenshot({ path: file, fullPage: false });
  // Write duplicate frames to control how long each step displays in the GIF
  for (let i = 1; i < repeat; i++) {
    fs.copyFileSync(file, path.join(FRAMES_DIR, `${name}_${i}.png`));
  }
  console.log(`  [frame] ${name} (×${repeat})`);
}

(async () => {
  // Clean and recreate frames directory
  if (fs.existsSync(FRAMES_DIR)) fs.rmSync(FRAMES_DIR, { recursive: true });
  fs.mkdirSync(FRAMES_DIR);

  // Clean stale webm if exists from previous run
  const staleWebm = path.join(__dirname, "demo.webm");
  if (fs.existsSync(staleWebm)) fs.unlinkSync(staleWebm);

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1100, height: 860 },
  });
  const page = await context.newPage();

  // ── Step 1: App loads ──────────────────────────────────────────────────────
  console.log("→ Loading app...");
  await page.goto(BASE_URL, { waitUntil: "networkidle" });
  await page.waitForSelector("select option[value='maya']", { state: "attached", timeout: 10000 });
  await sleep(600);
  await shot(page, "01_app_loaded", 6);

  // ── Step 2: Select Maya + Alex ─────────────────────────────────────────────
  console.log("→ Selecting Maya + Alex...");
  const selects = page.locator("select");
  await selects.nth(0).selectOption("maya");
  await selects.nth(1).selectOption("alex");
  await sleep(400);
  await shot(page, "02_maya_alex_selected", 4);

  // ── Step 3: Click Find Our Date ────────────────────────────────────────────
  console.log("→ Clicking Find Our Date...");
  await page.click("button:has-text('Find Our Date')");
  await sleep(300);
  await shot(page, "03_loading", 3);

  // ── Step 4: Result renders ─────────────────────────────────────────────────
  await page.waitForSelector("text=Elixr Coffee Roasters", { timeout: 10000 });
  await sleep(400);
  await shot(page, "04_maya_alex_result_top", 6);

  // ── Step 5: Scroll down to show venue + persona cards ─────────────────────
  console.log("→ Scrolling to show full result...");
  await page.evaluate(() => window.scrollBy({ top: 350, behavior: "instant" }));
  await sleep(300);
  await shot(page, "05_maya_alex_scrolled", 6);

  await page.evaluate(() => window.scrollBy({ top: 300, behavior: "instant" }));
  await sleep(300);
  await shot(page, "06_maya_alex_cards", 6);

  // ── Step 6: Switch to Jordan + Sam ────────────────────────────────────────
  console.log("→ Switching to Jordan + Sam...");
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" }));
  await sleep(300);
  await selects.nth(0).selectOption("jordan");
  await selects.nth(1).selectOption("sam");
  await sleep(400);
  await shot(page, "07_jordan_sam_selected", 4);

  // ── Step 7: Generate Jordan + Sam plan ────────────────────────────────────
  await page.click("button:has-text('Find Our Date')");
  await sleep(300);
  await shot(page, "08_loading_2", 2);

  await page.waitForSelector("text=Champs", { timeout: 10000 });
  await sleep(400);
  await shot(page, "09_jordan_sam_result", 6);

  await page.evaluate(() => window.scrollBy({ top: 350, behavior: "instant" }));
  await sleep(300);
  await shot(page, "10_jordan_sam_scrolled", 6);

  await context.close();
  await browser.close();

  // ── Convert frames → GIF ──────────────────────────────────────────────────
  const frames = fs.readdirSync(FRAMES_DIR)
    .filter((f) => f.endsWith(".png"))
    .sort()
    .map((f) => path.join(FRAMES_DIR, f));

  console.log(`→ Stitching ${frames.length} frames into GIF...`);

  // Build a concat input file for ffmpeg
  const concatFile = path.join(FRAMES_DIR, "concat.txt");
  const concatContent = frames.map((f) => `file '${f}'\nduration 0.18`).join("\n");
  fs.writeFileSync(concatFile, concatContent);

  execSync(
    `ffmpeg -y -f concat -safe 0 -i "${concatFile}" \
      -vf "scale=900:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer" \
      "${GIF_OUT}"`,
    { stdio: "inherit" }
  );

  console.log(`✓ GIF saved → ${GIF_OUT}`);
  console.log("  Cleaning up frames...");
  fs.rmSync(FRAMES_DIR, { recursive: true });
})();
