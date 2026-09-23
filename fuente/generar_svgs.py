"""
Genera los SVG del README de perfil (banner + Sprint 72h) con la identidad 6D.

Las fuentes (Montserrat, JetBrains Mono, Inter) se incrustan RECORTADAS dentro de
cada SVG para que se vean bien aunque quien visite el perfil no las tenga instaladas.

Uso:  python fuente/generar_svgs.py
Requiere: fonttools + brotli, y las fuentes de Google Fonts en %TEMP%/f6d
(las descarga solas si faltan).
"""
import base64, io, os, re, urllib.request
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools import subset

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "assets"
FUENTES = Path(os.environ.get("TEMP", "/tmp")) / "f6d"
ISOTIPO = Path.home() / ".claude/6D-brand-kit/logos/isotipo/isotipo dorado.svg"

URLS = {
    "Montserrat.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/montserrat/Montserrat%5Bwght%5D.ttf",
    "Inter.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf",
    "JetBrainsMono.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf",
}

# ---------- Tokens 6D (HEX = fuente de verdad) ----------
BG, SURFACE, RAISED = "#160D2A", "#1F1440", "#2A1C55"
BORDER, BORDER_STRONG = "#3A2A66", "#4E3A80"
TXT, TXT2, MUTED = "#F3EFFA", "#CFC4E6", "#A99FC4"
V500, V600, V700 = "#835CBE", "#64368C", "#482682"
GOLD = ("#875425", "#FFD66F", "#B3681F")


# ---------- Fuentes ----------
def _ttf(nombre):
    ruta = FUENTES / nombre
    if not ruta.exists():
        FUENTES.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(URLS[nombre], ruta)
    return ruta


class Fuente:
    """Instancia estática de una fuente variable: mide texto y se incrusta recortada."""

    def __init__(self, archivo, familia, peso):
        self.familia, self.peso = familia, peso
        f = TTFont(_ttf(archivo))
        ejes = {a.axisTag: a for a in f["fvar"].axes}
        coords = {"wght": peso}
        if "opsz" in ejes:
            coords["opsz"] = ejes["opsz"].defaultValue
        self.font = instantiateVariableFont(f, coords)
        self.upm = self.font["head"].unitsPerEm
        self.cmap = self.font.getBestCmap()
        self.hmtx = self.font["hmtx"]
        self.usado = set()

    def ancho(self, texto, tam, tracking=0.0):
        self.usado.update(texto)
        u = sum(self.hmtx[self.cmap.get(ord(c), self.cmap[ord("?")])][0] for c in texto)
        return u * tam / self.upm + tracking * tam * max(len(texto) - 1, 0)

    def css(self):
        buf = io.BytesIO()
        self.font.save(buf)
        buf.seek(0)
        f = TTFont(buf)
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = ["kern", "liga"]
        s = subset.Subsetter(opts)
        s.populate(text="".join(sorted(self.usado)) + " ")
        s.subset(f)
        out = io.BytesIO()
        f.flavor = "woff2"
        f.save(out)
        b64 = base64.b64encode(out.getvalue()).decode()
        return (f"@font-face{{font-family:'{self.familia}';font-weight:{self.peso};"
                f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}")


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def texto(f, t, x, y, tam, color, tracking=0.0, anchor="start", extra=""):
    f.ancho(t, tam, tracking)
    ls = f' letter-spacing="{tracking * tam:.2f}"' if tracking else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="\'{f.familia}\',sans-serif" '
            f'font-weight="{f.peso}" font-size="{tam}" fill="{color}"{ls} '
            f'text-anchor="{anchor}"{extra}>{esc(t)}</text>')


def isotipo(x, y, alto, sufijo):
    """Isotipo dorado original, incrustado como SVG anidado (sin deformar)."""
    src = ISOTIPO.read_text(encoding="utf-8")
    src = re.sub(r"<\?xml.*?\?>|<!--.*?-->", "", src, flags=re.S)
    cuerpo = re.search(r"<svg[^>]*>(.*)</svg>", src, re.S).group(1)
    # ids y clases únicos para que no choquen dentro del documento
    cuerpo = cuerpo.replace("New_Gradient_Swatch_copy_10", f"iso{sufijo}_g")
    cuerpo = re.sub(r"\bst(\d)\b", rf"iso{sufijo}_\1", cuerpo)
    ancho = alto * 841.89 / 595.28
    return (f'<svg x="{x:.1f}" y="{y:.1f}" width="{ancho:.1f}" height="{alto:.1f}" '
            f'viewBox="0 0 841.89 595.28">{cuerpo}</svg>')


def defs_comunes():
    return f"""
    <linearGradient id="oro" x1="0" y1="0" x2="1" y2="0.35">
      <stop offset="0" stop-color="{GOLD[0]}"/><stop offset=".55" stop-color="{GOLD[1]}"/><stop offset="1" stop-color="{GOLD[2]}"/>
    </linearGradient>
    <linearGradient id="marca" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#482682"/><stop offset=".46" stop-color="#5A2F94"/><stop offset="1" stop-color="#64368C"/>
    </linearGradient>
    <radialGradient id="m1" cx=".18" cy=".22" r=".55"><stop offset="0" stop-color="#5A2F94" stop-opacity=".85"/><stop offset="1" stop-color="#5A2F94" stop-opacity="0"/></radialGradient>
    <radialGradient id="m2" cx=".86" cy=".2" r=".5"><stop offset="0" stop-color="#64368C" stop-opacity=".75"/><stop offset="1" stop-color="#64368C" stop-opacity="0"/></radialGradient>
    <radialGradient id="m3" cx=".8" cy=".95" r=".5"><stop offset="0" stop-color="#B3681F" stop-opacity=".38"/><stop offset="1" stop-color="#B3681F" stop-opacity="0"/></radialGradient>
    <radialGradient id="m4" cx=".3" cy="1" r=".55"><stop offset="0" stop-color="#2B1A4D" stop-opacity=".9"/><stop offset="1" stop-color="#2B1A4D" stop-opacity="0"/></radialGradient>
    <radialGradient id="halo" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFD66F" stop-opacity=".22"/><stop offset=".6" stop-color="#B3681F" stop-opacity=".07"/><stop offset="1" stop-color="#B3681F" stop-opacity="0"/></radialGradient>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#FFFFFF" stroke-opacity=".035"/></pattern>"""


def fondo(w, h):
    return f"""
  <rect width="{w}" height="{h}" rx="18" fill="{BG}"/>
  <g clip-path="url(#card)">
    <rect width="{w}" height="{h}" fill="url(#m4)"/><rect width="{w}" height="{h}" fill="url(#m1)"/>
    <rect width="{w}" height="{h}" fill="url(#m2)"/><rect width="{w}" height="{h}" fill="url(#m3)"/>
    <rect width="{w}" height="{h}" fill="url(#grid)"/>
  </g>
  <rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="17.5" fill="none" stroke="{BORDER_STRONG}" stroke-opacity=".7"/>"""


def documento(w, h, fuentes, cuerpo, titulo):
    css = "".join(f.css() for f in fuentes)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(titulo)}">
  <title>{esc(titulo)}</title>
  <style>{css}</style>
  <defs>{defs_comunes()}
    <clipPath id="card"><rect width="{w}" height="{h}" rx="18"/></clipPath>
  </defs>{fondo(w, h)}{cuerpo}
</svg>
"""


# ---------- Banner ----------
def banner():
    W, H = 1280, 440
    mx = Fuente("Montserrat.ttf", "Montserrat6D", 800)
    mb = Fuente("Montserrat.ttf", "Montserrat6DB", 700)
    mono = Fuente("JetBrainsMono.ttf", "JetBrains6D", 600)
    inter = Fuente("Inter.ttf", "Inter6D", 400)

    X = 72
    partes = []
    # Eyebrow
    partes.append(f'<rect x="{X}" y="74" width="28" height="2" fill="url(#oro)"/>')
    partes.append(texto(mono, "6D MATIC · MARKETING DIGITAL Y AUTOMATIZACIÓN", X + 40, 81, 15, "#E0A54A", tracking=0.14))
    # Nombre
    partes.append(texto(mx, "SAULO ARELLANO", X - 3, 158, 70, TXT, tracking=-0.02))
    # Titular
    partes.append(texto(mb, "Página que vende + WhatsApp", X, 222, 34, TXT2, tracking=-0.011))
    l2a = "que responde, califica y agenda. En "
    partes.append(texto(mb, l2a, X, 266, 34, TXT2, tracking=-0.011))
    ancho = mb.ancho(l2a, 34, -0.011)
    partes.append(texto(mb, "72 horas.", X + ancho + 4, 266, 34, "url(#oro)", tracking=-0.011))
    # Bajada
    partes.append(texto(inter, "Sistemas de captación para negocios locales: landing, WhatsApp, CRM y flujos de IA.",
                        X, 314, 18, MUTED))
    # Píldoras
    px = X
    for etiqueta, dorada in (("SPRINT 72H", True), ("ENTREGA EN 72 H O NO PAGAS", False), ("GARANTÍA 7 DÍAS", False)):
        w = mono.ancho(etiqueta, 13, 0.12) + 36
        if dorada:
            partes.append(f'<rect x="{px}" y="348" width="{w:.1f}" height="36" rx="18" fill="url(#oro)"/>')
            partes.append(texto(mono, etiqueta, px + w / 2, 371, 13, "#3A2607", tracking=0.12, anchor="middle"))
        else:
            partes.append(f'<rect x="{px + .5}" y="348.5" width="{w - 1:.1f}" height="35" rx="17.5" fill="{SURFACE}" fill-opacity=".7" stroke="{BORDER_STRONG}"/>')
            partes.append(texto(mono, etiqueta, px + w / 2, 371, 13, TXT2, tracking=0.12, anchor="middle"))
        px += w + 12
    # Isotipo con halo
    cx, cy = 1062, 214
    partes.append(f'<circle cx="{cx}" cy="{cy}" r="190" fill="url(#halo)"/>')
    partes.append(f'<circle cx="{cx}" cy="{cy}" r="150" fill="none" stroke="#FFD66F" stroke-opacity=".12"/>')
    partes.append(f'<circle cx="{cx}" cy="{cy}" r="178" fill="none" stroke="#FFD66F" stroke-opacity=".06" stroke-dasharray="2 8"/>')
    alto = 380
    partes.append(isotipo(cx - alto * 841.89 / 595.28 / 2, cy - alto / 2, alto, "b"))

    cuerpo = "\n  " + "\n  ".join(partes)
    return documento(W, H, [mx, mb, mono, inter], cuerpo,
                     "Saulo Arellano · 6D Matic · Página que vende + WhatsApp que responde, en 72 horas")


# ---------- Sprint 72h ----------
def sprint():
    W, H = 1280, 470
    mx = Fuente("Montserrat.ttf", "Montserrat6D", 800)
    mono = Fuente("JetBrainsMono.ttf", "JetBrains6D", 600)
    inter = Fuente("Inter.ttf", "Inter6DM", 500)

    dias = [
        ("0 — 24 H", "DÍA 1", "Radiografía", ["Llamada de 45 min, la única", "3 competidores de tu zona", "Estructura aprobada por ti"]),
        ("24 — 48 H", "DÍA 2", "Construcción", ["Landing de 8 secciones que vende", "WhatsApp con mensaje precargado", "Carga en menos de 2 segundos"]),
        ("48 — 72 H", "DÍA 3", "Encendido", ["Publicada en tu dominio", "Respuestas automáticas en WhatsApp", "7 días de soporte directo conmigo"]),
    ]
    partes = []
    X0, GAP = 56, 24
    cw = (W - 2 * X0 - 2 * GAP) / 3
    # Encabezado
    partes.append(texto(mono, "EL SPRINT 72H · HORA POR HORA", X0, 70, 14, "#E0A54A", tracking=0.14))
    partes.append(texto(mx, "TÚ DAS 45 MINUTOS. YO HAGO TODO LO DEMÁS.", X0, 112, 30, TXT, tracking=-0.015))
    # Línea de tiempo
    ly = 158
    partes.append(f'<rect x="{X0}" y="{ly - 1}" width="{W - 2 * X0}" height="2" rx="1" fill="{BORDER_STRONG}"/>')
    partes.append(f'<rect x="{X0}" y="{ly - 1.5}" width="{W - 2 * X0}" height="3" rx="1.5" fill="url(#oro)" opacity=".9"/>')
    for i, (rango, dia, titulo, items) in enumerate(dias):
        x = X0 + i * (cw + GAP)
        partes.append(f'<circle cx="{x + 14}" cy="{ly}" r="7" fill="{BG}" stroke="#FFD66F" stroke-width="3"/>')
        partes.append(f'<rect x="{x + 26}" y="{ly - 11}" width="{mono.ancho(rango, 12, 0.12) + 16:.1f}" height="22" rx="11" fill="{BG}"/>')
        partes.append(texto(mono, rango, x + 34, ly + 4.5, 12, "#E0A54A", tracking=0.12))
        # Tarjeta
        ty, th = 188, 236
        partes.append(f'<rect x="{x}" y="{ty}" width="{cw:.1f}" height="{th}" rx="18" fill="{SURFACE}" fill-opacity=".82" stroke="{BORDER}"/>')
        # franja superior de 8px con el degradado de marca, recortada a la tarjeta
        partes.append(f'<clipPath id="t{i}"><rect x="{x}" y="{ty}" width="{cw:.1f}" height="{th}" rx="18"/></clipPath>')
        partes.append(f'<rect x="{x}" y="{ty}" width="{cw:.1f}" height="8" fill="url(#oro)" clip-path="url(#t{i})"/>')
        partes.append(texto(mono, dia, x + 28, ty + 50, 13, "#C5B3E8", tracking=0.14))
        partes.append(texto(mx, titulo.upper(), x + 28, ty + 86, 26, TXT, tracking=-0.015))
        for j, it in enumerate(items):
            yy = ty + 132 + j * 34
            partes.append(f'<circle cx="{x + 36}" cy="{yy - 6}" r="9" fill="{V700}" stroke="{V500}"/>')
            partes.append(f'<path d="M{x + 31.5} {yy - 6}l3 3 5.5-6" fill="none" stroke="#FFD66F" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
            partes.append(texto(inter, it, x + 56, yy, 16, TXT2))
    # Pie
    partes.append(texto(mono, "SI NO CUMPLO LA FECHA POR CAUSA MÍA, TE DEVUELVO EL DINERO Y TERMINO EL TRABAJO DE TODOS MODOS.",
                        W / 2, 452, 11.5, MUTED, tracking=0.1, anchor="middle"))

    cuerpo = "\n  " + "\n  ".join(partes)
    return documento(W, H, [mx, mono, inter], cuerpo,
                     "Sprint 72h: Día 1 Radiografía, Día 2 Construcción, Día 3 Encendido")


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    for nombre, fn in (("banner.svg", banner), ("sprint-72h.svg", sprint)):
        svg = fn()
        (ASSETS / nombre).write_text(svg, encoding="utf-8")
        print(f"{nombre}: {len(svg.encode()) // 1024} KB")
