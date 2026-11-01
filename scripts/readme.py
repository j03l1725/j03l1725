#!/usr/bin/env python3
"""Escribe README.md. Cada imagen va en un <picture> con su versión clara y oscura; GitHub elige según el tema."""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
UIT = 'https://www.itu.int/generationconnect/generation-connect-americas-youth-envoys-gc-ams-2026-2030/'
CORREO = 'joelm@insideebb.com'
CLARO, OSCURO = '(prefers-color-scheme: light)', '(prefers-color-scheme: dark)'
ESTRECHO, QUIETO = '(max-width: 640px)', '(prefers-reduced-motion: reduce)'


def fuente(media, ruta):
    return f'  <source media="{" and ".join(media)}" srcset="{ruta}">'


def imagen(nombre, alt, attrs, movil=None):
    """Claro y oscuro; con `movil`, además su versión estrecha."""
    s = []
    if movil:
        s += [fuente([tm, ESTRECHO], f'img/{t}/{movil}.webp') for t, tm in (('claro', CLARO), ('oscuro', OSCURO))]
    s += [fuente([tm], f'img/{t}/{nombre}.webp') for t, tm in (('claro', CLARO), ('oscuro', OSCURO))]
    return '<picture>\n' + '\n'.join(s) + f'\n  <img src="img/oscuro/{nombre}.webp" {attrs} alt="{alt}">\n</picture>'


def cabecera(alt):
    s = []
    for extra, sufijo in (([QUIETO], '-quieto'), ([], '')):
        for estrecho, nombre in (([ESTRECHO], 'hero-vertical'), ([], 'hero')):
            for t, tm in (('claro', CLARO), ('oscuro', OSCURO)):
                s.append(fuente([tm] + extra + estrecho, f'img/{t}/{nombre}{sufijo}.webp'))
    return '<picture>\n' + '\n'.join(s) + f'\n  <img src="img/oscuro/hero.webp" width="100%" alt="{alt}">\n</picture>'


BOTONES = [('https://joelsphere.com', 'b-web', 'joelsphere.com'), ('https://insideebb.com', 'b-insideebb', 'INSIDEEBB'),
           ('https://www.linkedin.com/in/j03l1725', 'b-linkedin', 'LinkedIn'), ('https://x.com/j03l1725', 'b-x', 'X'),
           ('https://www.instagram.com/joel.morales03_/', 'b-instagram', 'Instagram'),
           ('https://orcid.org/0009-0009-9661-8529', 'b-orcid', 'ORCID'), (f'mailto:{CORREO}', 'b-correo', f'Correo: {CORREO}')]
TARJETAS = [('https://bizzio.shop', 't-bizzio', 'Bizzio. Comercio electrónico con IA. Tienda en línea con vendedor virtual y pagos integrados.'),
            (UIT, 't-uit', 'Youth Envoy de la UIT. Generation Connect Américas, 2026-2030.'),
            ('https://joelsphere.com/escritos/titulacion-campusbot/', 't-campusbot', 'CampusBot-UTI. Asistente virtual sobre la normativa universitaria, en infraestructura propia y evaluado con usuarios reales.'),
            ('https://doi.org/10.37815/rte.v38nE1.1591', 't-madurez', 'Plataforma de madurez digital. Autodiagnóstico para microemprendimientos, publicado en la Revista Tecnológica ESPOL.'),
            ('https://joelsphere.com', 't-kuntur', 'KUNTUR. Robot humanoide, primero en performance y tercero en combate en ROBO ONE.'),
            ('https://joelsphere.com', 't-colmena', 'Colmena. Servidores locales sin internet para comunidades de la Amazonía.')]

botones = '\n'.join(f'<a href="{u}">{imagen(n, a, chr(104) + "eight=" + chr(34) + "42" + chr(34))}</a>' for u, n, a in BOTONES)
tarjetas = '\n'.join(f'<a href="{u}">{imagen(n, a, "width=" + chr(34) + "414" + chr(34))}</a>' for u, n, a in TARJETAS)
HERO_ALT = 'Joel Morales. Lo difícil de la IA es que funcione de verdad. Cofundador de INSIDEEBB. Youth Envoy de la UIT para las Américas.'
BANNER_ALT = 'INSIDEEBB. Desarrollamos software y capacitamos a los equipos que lo usan. Plataformas, sistemas a medida e inteligencia artificial integrados a la operación de cada empresa.'

(REPO / 'README.md').write_text(f"""<a href="https://joelsphere.com">
{cabecera(HERO_ALT)}
</a>

<p>
{botones}
</p>

Construyo software que entra en operación: plataformas, agentes de IA e infraestructura que alguien usa al día siguiente de desplegarlos.

## Hoy

<a href="https://insideebb.com">
{imagen('t-insideebb', BANNER_ALT, 'width="100%"', 't-insideebb-movil')}
</a>

- **[INSIDEEBB](https://insideebb.com), cofundador.** Desarrollo de software, inteligencia artificial aplicada y capacitación de equipos. [Bizzio](https://bizzio.shop) es nuestra plataforma de comercio electrónico con IA.
- **[UIT, Generation Connect Américas]({UIT}), Youth Envoy 2026-2030.** Represento a Ecuador en el programa de juventud de la agencia de las Naciones Unidas para las tecnologías digitales.
- **Universidad Indoamérica, Centro de Inteligencia Artificial.** Desarrollo los sistemas internos que usa la universidad en su gestión diaria.
- **Sector público.** Plataformas para programas de transformación digital y emprendimiento.

## Proyectos

<p>
{tarjetas}
</p>

## Investigación y charlas

- **[Ingeniería de una plataforma web para la evaluación de la madurez digital de microemprendimientos ecuatorianos](https://doi.org/10.37815/rte.v38nE1.1591).** Revista Tecnológica ESPOL, 38(E1), 154-171, 2026. Con Ivanna Sánchez-Montero y Viviana Cajas-Cajas.
- **Diseño de un elevador de carga como medida para reducir riesgos ergonómicos.** Artículo indexado en Scopus, en coautoría, 2024.
- **Charlas.** TICEC 2026, Track Técnico · Ingenia X 2026 · Semana de la Interculturalidad 2025, *Voces de la Amazonía* · FLISOL 2024, *GNU/Linux: la montaña rusa de la ingeniería*.

## Con qué trabajo

- **Inteligencia artificial.** Agentes, RAG, modelos locales y en la nube, evaluación y seguridad.
- **Desarrollo.** TypeScript, Python, Node.js, NestJS, FastAPI, React, Next.js, Three.js.
- **Infraestructura.** Linux, Docker, PostgreSQL, servidores propios y despliegue continuo.
""")
