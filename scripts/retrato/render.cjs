// Renderiza el retrato cuadro a cuadro en Chromium sin ventana. Uso:
// node render.cjs <salida> <cuadros> <w> <h> <s> [parámetros de consulta] [--uno N]
// THREE_DIR: carpeta build de three; RETRATO_BIN: la nube de puntos publicada en joelsphere.
const http = require('node:http'), fs = require('node:fs'), path = require('node:path');
const { chromium } = require(process.env.PW || 'playwright-core');
const [sal, cuadros, w, h, s, extra = '', uno] = process.argv.slice(2);
const T = process.env.THREE_DIR, BIN = process.env.RETRATO_BIN;
const tipos = { '.js': 'text/javascript', '.html': 'text/html' };
const srv = http.createServer((q, r) => { const u = q.url.split('?')[0];
  const f = u === '/retrato.bin' ? BIN : u === '/render.html' ? path.join(__dirname, 'render.html') : path.join(T, path.basename(u));
  if (!fs.existsSync(f)) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'content-type': tipos[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(r); });
srv.listen(0, async () => { const port = srv.address().port; fs.mkdirSync(sal, { recursive: true });
  const b = await chromium.launch({ headless: true, args: (process.env.GL || '--use-angle=swiftshader,--enable-unsafe-swiftshader,--ignore-gpu-blocklist').split(',') });
  const p = await b.newPage(); p.on('pageerror', (e) => console.error('ERR', e.message));
  await p.goto(`http://127.0.0.1:${port}/render.html?w=${w}&h=${h}&s=${s}&${extra}`);
  await p.waitForFunction('window.listo', { timeout: 30000 });
  console.log(await p.evaluate(() => { const g = document.getElementById('c').getContext('webgl2'); const e = g.getExtension('WEBGL_debug_renderer_info'); return { ...window.listo, gl: e ? g.getParameter(e.UNMASKED_RENDERER_WEBGL) : '?' }; }));
  const total = +cuadros, ini = Date.now(); const lista = uno ? [+uno] : [...Array(total).keys()];
  for (const f of lista) { const d = await p.evaluate(([a, t]) => window.dibujar(a, t), [f, total]);
    fs.writeFileSync(path.join(sal, `f${String(f).padStart(4, '0')}.png`), Buffer.from(d.split(',')[1], 'base64')); }
  console.log('ms/cuadro', Math.round((Date.now() - ini) / lista.length)); await b.close(); srv.close(); });
