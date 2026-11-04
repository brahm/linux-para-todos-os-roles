// Gera a imagem social (1280×640 px) do repositório e do site, a partir dos SVGs da marca.
// usage: node marca/ferramentas/social.js [pasta-da-marca] [saida.png]
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
(async () => {
  const B = process.argv[2] || 'marca';
  const out = process.argv[3] || path.join(B, 'png', 'imagem-social.png');
  const logo = fs.readFileSync(path.join(B, 'logotipo', 'logotipo-horizontal.svg'), 'utf8').replace(/<\?xml[^>]*>/, '');
  const sym = fs.readFileSync(path.join(B, 'icones', 'hicolor', 'symbolic', 'apps', 'br.com.brahm.Bora-symbolic.svg'), 'utf8');
  const d = sym.match(/ d="([^"]+)"/)[1];
  // Trilha de pegadas ao longo de uma curva, alternando os lados.
  const pts = [[-40, 600], [360, 700], [760, 380], [1320, 470]];
  const bez = (t) => {
    const u = 1 - t, [a, b, c, e] = pts;
    const x = u * u * u * a[0] + 3 * u * u * t * b[0] + 3 * u * t * t * c[0] + t * t * t * e[0];
    const y = u * u * u * a[1] + 3 * u * u * t * b[1] + 3 * u * t * t * c[1] + t * t * t * e[1];
    const dx = 3 * u * u * (b[0] - a[0]) + 6 * u * t * (c[0] - b[0]) + 3 * t * t * (e[0] - c[0]);
    const dy = 3 * u * u * (b[1] - a[1]) + 6 * u * t * (c[1] - b[1]) + 3 * t * t * (e[1] - c[1]);
    return [x, y, dx, dy];
  };
  let trilha = '';
  for (let i = 0; i < 16; i++) {
    const [x, y, dx, dy] = bez(i / 15), L = Math.hypot(dx, dy), s = i % 2 ? 1 : -1;
    const cx = x - (dy / L) * 20 * s, cy = y + (dx / L) * 20 * s, ang = Math.atan2(dy, dx) * 180 / Math.PI + 90;
    trilha += `<svg x="${cx - 22}" y="${cy - 22}" width="44" height="44" viewBox="0 0 16 16" overflow="visible"><path transform="rotate(${ang} 8 8)" fill="#ff7800" opacity="0.22" d="${d}"/></svg>`;
  }
  const html = `<html><body style="margin:0">
  <div style="width:1280px;height:640px;position:relative;overflow:hidden;background:linear-gradient(165deg,#fff6ec 30%,#ffe6cc)">
    <svg width="1280" height="640" style="position:absolute;inset:0">${trilha}</svg>
    <div style="position:absolute;left:110px;top:200px;width:1060px">${logo.replace(/width="[\d.]+" height="[\d.]+"/, 'width="1060" height="143.3"')}</div>
  </div></body></html>`;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 640 }, deviceScaleFactor: 1 });
  await page.setContent(html);
  await page.waitForTimeout(100);
  await page.screenshot({ path: out, type: 'png' });
  await browser.close();
  console.log('png', out);
})();
