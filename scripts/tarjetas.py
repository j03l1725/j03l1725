#!/usr/bin/env python3
"""Genera el banner de INSIDEEBB, las tarjetas de proyectos y los botones de redes (img/*.webp), al doble de tamaño.

Uso: ARCHIVO_TTF=… PW=… JOELSPHERE=<public de joelsphere> IDENTIDAD=<identidad de INSIDEEBB> python3 scripts/tarjetas.py
Las capturas de Bizzio y del globo y el cohete recortado viven en scripts/medios/.
"""
import os, subprocess, tempfile
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parent.parent
E_ = os.environ
ARCHIVO, PUB, ID = E_['ARCHIVO_TTF'], E_['JOELSPHERE'], E_['IDENTIDAD']
MEDIOS = REPO / 'scripts/medios'

BASE = f"""<!doctype html><meta charset=utf-8><style>
@font-face{{font-family:Ar;src:url(file://{ARCHIVO}) format('truetype');font-weight:100 900;font-stretch:62% 125%}}
html,body{{margin:0;background:transparent;font-family:Ar;-webkit-font-smoothing:antialiased}}
.tj{{width:408px;height:298px;box-sizing:border-box;border:1px solid #2A2F3A;border-radius:14px;background:#0A0C11;overflow:hidden;display:flex;flex-direction:column}}
.im{{height:192px;background-size:cover;flex:none;border-bottom:1px solid #1B1F28}}
.tx{{padding:15px 18px 0}}
h3{{margin:0 0 6px;font-size:21px;font-weight:800;letter-spacing:-.2px;color:#fff}}
p{{margin:0;font-size:14px;line-height:1.42;color:#A9B0BE}}
.bn{{position:relative;width:846px;height:236px;box-sizing:border-box;border:1px solid #2A2F3A;border-radius:14px;background:#0E0D0B;overflow:hidden}}
.bn .lg{{position:absolute;left:252px;top:30px;height:30px}}
.bn h2{{position:absolute;left:252px;top:80px;margin:0;width:560px;font-size:27px;line-height:1.14;font-weight:800;letter-spacing:-.4px;color:#fff}}
.bn p{{position:absolute;left:252px;top:152px;width:540px;font-size:14.5px;color:#CDCAD4}}
.bn .co{{position:absolute;left:0;top:-3px;height:240px}}
.bm{{position:relative;width:408px;height:286px;box-sizing:border-box;border:1px solid #2A2F3A;border-radius:14px;background:#0E0D0B;overflow:hidden}}
.bm .lg{{position:absolute;left:138px;top:46px;height:27px}}
.bm h2{{position:absolute;left:22px;top:122px;margin:0;width:364px;font-size:24px;line-height:1.14;font-weight:800;letter-spacing:-.3px;color:#fff}}
.bm p{{position:absolute;left:22px;top:214px;width:364px;font-size:15.5px;color:#CDCAD4}}
.bm .co{{position:absolute;left:0;top:-3px;height:126px}}
.bt{{display:inline-flex;align-items:center;gap:8px;height:42px;box-sizing:border-box;padding:0 15px 0 13px;border:1px solid #2A2F3A;border-radius:10px;background:#0A0C11;color:#fff;font-size:14.5px;font-weight:600}}
.bt svg,.bt img{{width:18px;height:18px;display:block}}
</style>"""


def foto(ruta, pos='center', extra=''):
    return f"background-image:url(file://{ruta});background-position:{pos};{extra}"


TARJETAS = [
    ('t-bizzio', foto(f'{MEDIOS}/bizzio.webp'), 'Bizzio',
     'Comercio electrónico con IA. Tienda en línea con vendedor virtual y pagos integrados. Dirijo su desarrollo.'),
    ('t-uit', foto(f'{MEDIOS}/globo.webp'), 'Youth Envoy de la UIT',
     'Generation Connect Américas, 2026-2030. Represento a Ecuador en una cohorte de 184 jóvenes de 61 países.'),
    ('t-campusbot', foto(f'{PUB}/perfil/pub/ingenia-x-d0b2f6.webp', '30% 50%'), 'CampusBot-UTI',
     'Asistente virtual sobre la normativa universitaria, en infraestructura propia y evaluado con usuarios reales.'),
    ('t-madurez', foto(f'{PUB}/reciente/2026-10-15-ticec-2026.webp', '0% 30%'), 'Plataforma de madurez digital',
     'Autodiagnóstico para microemprendimientos. Publicada en la Revista Tecnológica ESPOL y expuesta en TICEC 2026.'),
    ('t-kuntur', foto(f'{PUB}/perfil/lugares/quito/4-322e69.webp', '50% 66%'), 'KUNTUR',
     'Robot humanoide del club que presidí. Primero en performance y tercero en combate en ROBO ONE.'),
    ('t-colmena', foto(f'{PUB}/perfil/lugares/sarayaku/2-da4994.webp', '50% 60%'), 'Colmena',
     'Servidores locales sin internet para comunidades de la Amazonía, con la red de comunicadoras de CORAPE.'),
]

ICONOS = {
    'web': '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.7"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3.6 6 3.6 9s-.6 6-3.6 9c-3-3-3.6-6-3.6-9S9 6 12 3z"/></svg>',
    'insideebb': f'<img src="file://{ID}/logo/simbolo/simbolo-blanco.svg">',
    'linkedin': '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="4"/><path d="M8 10.5V16M8 7.6v.1M11.5 16v-5.5M11.5 13c0-1.6 1-2.6 2.4-2.6s2.3 1 2.3 2.6V16"/></svg>',
    'x': '<svg viewBox="0 0 24 24" fill="#fff"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>',
    'instagram': '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.2 6.8v.1"/></svg>',
    'orcid': '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="#fff"/><path fill="#0A0C11" d="M7.6 7.2h1.6v9.6H7.6zM11 7.2h3.5c3 0 4.5 2.2 4.5 4.8s-1.6 4.8-4.5 4.8H11zm1.6 1.4v6.8h1.8c2 0 3-1.5 3-3.4s-1-3.4-3-3.4z"/></svg>',
    'correo': '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.8" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="3"/><path d="M3.5 7.5 12 13l8.5-5.5"/></svg>',
}
BOTONES = [('web', 'joelsphere.com'), ('insideebb', 'INSIDEEBB'), ('linkedin', 'LinkedIn'), ('x', 'X'),
           ('instagram', 'Instagram'), ('orcid', 'ORCID'), ('correo', 'Correo')]


def pieza(tmp, nombre, cuerpo, w=900, h=400, q=86):
    f = Path(tmp) / f'{nombre}.html'; p = Path(tmp) / f'{nombre}.png'
    f.write_text(BASE + f'<body><div id="pieza" style="display:inline-block">{cuerpo}</div></body>')
    subprocess.run(['node', str(REPO / 'scripts/retrato/rasterizar.cjs'), str(f), str(p), str(w), str(h)], check=True)
    d = REPO / 'img' / f'{nombre}.webp'
    Image.open(p).convert('RGBA').save(d, quality=q, method=6, alpha_quality=100)
    print(nombre, Image.open(d).size, d.stat().st_size // 1024, 'KB')


def main():
    with tempfile.TemporaryDirectory() as t:
        pieza(t, 't-insideebb', f"""<div class="bn"><img class="co" src="file://{MEDIOS}/cohete.webp"><img class="lg" src="file://{ID}/logo/firma-horizontal/firma-horizontal-blanco.svg">
<h2>Desarrollamos software y capacitamos a los equipos que lo usan.</h2>
<p>Plataformas, sistemas a medida e inteligencia artificial integrados a la operación de cada empresa.</p></div>""")
        pieza(t, 't-insideebb-movil', f"""<div class="bm"><img class="co" src="file://{MEDIOS}/cohete.webp"><img class="lg" src="file://{ID}/logo/firma-horizontal/firma-horizontal-blanco.svg">
<h2>Desarrollamos software y capacitamos a los equipos que lo usan.</h2>
<p>Plataformas, sistemas a medida e inteligencia artificial integrados a la operación de cada empresa.</p></div>""", 500, 400)
        for n, est, tit, txt in TARJETAS:
            pieza(t, n, f'<div class="tj"><div class="im" style="{est}"></div><div class="tx"><h3>{tit}</h3><p>{txt}</p></div></div>')
        for i, txt in BOTONES:
            pieza(t, f'b-{i}', f'<div class="bt">{ICONOS[i]}<span>{txt}</span></div>', 300, 80, 92)


main()
