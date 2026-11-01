// Muestra un fichero dentro de <img>, como GitHub, y saca dos capturas separadas para distinguir animado de quieto.
// node ver.cjs <firefox|chromium> <fichero> <ancho> <salida>
const { firefox, chromium } = require(process.env.PW); const fs = require('node:fs');
(async () => { const [mot, f, ancho, sal] = process.argv.slice(2);
  const b = await ({ firefox, chromium })[mot].launch({ headless: true });
  const p = await b.newPage({ viewport: { width: +ancho + 40, height: Math.round(+ancho * 1.5) }, deviceScaleFactor: 2 });
  fs.writeFileSync(sal + '.html', `<!doctype html><body style="margin:20px;background:#0d1117"><img id=i src="file://${f}" style="width:${ancho}px;display:block">`);
  await p.goto('file://' + sal + '.html', { waitUntil: 'load', timeout: 15000 });
  const box = await (await p.$('#i')).boundingBox();
  await p.waitForTimeout(700); await p.screenshot({ path: sal + '-a.png', clip: box });
  await p.waitForTimeout(1500); await p.screenshot({ path: sal + '-b.png', clip: box }); await b.close(); })().catch((e) => { console.error(e.message); process.exit(1); });
