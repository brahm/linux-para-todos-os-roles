// Render an SVG file to PNG at a given pixel size using Chromium (accurate SVG rendering).
// usage: node render.js <svg> <out.png> <width> [height] [bg]
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
(async () => {
  const [svgPath, outPath, w, h, bg] = process.argv.slice(2);
  const width = parseInt(w, 10), height = parseInt(h || w, 10);
  const svg = fs.readFileSync(svgPath, 'utf8');
  const b64 = Buffer.from(svg).toString('base64');
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  await page.setContent(`<html><body style="margin:0;background:${bg || 'transparent'}"><img src="data:image/svg+xml;base64,${b64}" style="display:block;width:${width}px;height:${height}px"></body></html>`);
  await page.waitForTimeout(100);
  await page.screenshot({ path: outPath, omitBackground: !bg, type: 'png' });
  await browser.close();
})();
