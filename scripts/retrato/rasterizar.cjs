// Pasa un HTML a PNG con fondo transparente, al doble de densidad. Si hay #pieza, recorta a ese elemento.
// node rasterizar.cjs <html> <png> <ancho css> <alto css>
const { chromium } = require(process.env.PW);
(async () => { const [f, sal, w, h] = process.argv.slice(2); const b = await chromium.launch({ headless: true });
  const p = await b.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 2 });
  await p.goto('file://' + f, { waitUntil: 'load' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(150);
  const e = await p.$('#pieza'); if (e) await e.screenshot({ path: sal, omitBackground: true }); else await p.screenshot({ path: sal, omitBackground: true });
  await b.close(); })().catch((e) => { console.error(e.message); process.exit(1); });
