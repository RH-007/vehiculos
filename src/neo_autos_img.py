import json
from io import BytesIO
from pathlib import Path
from typing import List, Dict, Any
import statistics as stats

import streamlit as st
from PIL import Image
import requests

st.set_page_config(page_title="Comparador A vs B (Marca→Modelo + Cascada)")

# ------------------ Utilidades ------------------
def _norm(x): return (x or "").strip()

def _safe_int(x):
    try:
        s = str(x).strip().replace(" ", "").replace(",", "")
        return int(s)
    except Exception:
        return None

def price_to_usd(px):
    if not px: return None
    s = (px.replace("US$", "").replace("$", "").replace("USD", "").replace(",", "").strip())
    return _safe_int(s)

def _fmt_aviso_label(a):
    anio = _norm(a.get("año",""))
    titulo = _norm(a.get("titulo",""))
    precio = _norm(a.get("precio","")) or "—"
    kms = a.get("kilometraje_km")
    kms_txt = f"{kms:,}" if isinstance(kms, int) else (str(kms) if kms else "—")
    return f"{anio} • {titulo} • {precio} • Kms: {kms_txt}"

def _orden_aviso_precio(a):
    # True va después de False, así los sin precio se van al final
    usd = a.get("_usd")
    kms = a.get("_kms")
    return (usd is None, usd if usd is not None else 10**12, kms if kms is not None else 10**12)


def modelo_key(row: Dict[str, Any]) -> str:
    return f"{_norm(row.get('marca',''))} | {_norm(row.get('modelo',''))}"

def dedupe(seq: List[str]) -> List[str]:
    seen, out = set(), []
    for x in seq:
        if x and x not in seen:
            seen.add(x); out.append(x)
    return out

@st.cache_data(show_spinner=False)
def fetch_image(url: str) -> Image.Image | None:
    try:
        r = requests.get(url, timeout=12, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        return Image.open(BytesIO(r.content)).convert("RGB")
    except Exception:
        return None

def upscale(img: Image.Image, factor: int, method: str) -> Image.Image:
    if factor <= 1 or img is None: return img
    w, h = img.size
    return img.resize((w*factor, h*factor), Image.NEAREST if method=="Nítido (NEAREST)" else Image.LANCZOS)

def metricas(avisos: List[Dict[str,Any]]):
    precios = [a["_usd"] for a in avisos if a.get("_usd") is not None]
    kms = [a["_kms"] for a in avisos if a.get("_kms") is not None]
    return {
        "n": len(avisos),
        "p50": int(stats.median(precios)) if precios else None,
        "pmin": min(precios) if precios else None,
        "pmax": max(precios) if precios else None,
        "k50": int(stats.median(kms)) if kms else None
    }

# ------------------ Carga de datos ------------------
st.sidebar.title("Fuente de datos")
modo = st.sidebar.radio("Cargar JSON", ["Subir archivo", "Pegar texto"], horizontal=True)
if modo == "Subir archivo":
    up = st.sidebar.file_uploader("Sube tu JSON", type=["json"])
    if not up: st.stop()
    try:
        data = json.load(up)
    except Exception as e:
        st.error(f"No pude leer el JSON: {e}"); st.stop()
else:
    txt = st.sidebar.text_area("Pega el JSON", height=240, value="")
    if not txt: st.info("Pega el JSON y ejecuta nuevamente."); st.stop()
    try:
        data = json.loads(txt)
    except Exception as e:
        st.error(f"JSON inválido: {e}"); st.stop()

# Normalización mínima
for d in data:
    d.setdefault("marca",""); d.setdefault("modelo",""); d.setdefault("año","")
    d.setdefault("titulo",""); d.setdefault("precio",""); d.setdefault("kilometraje_km", None)
    d.setdefault("img_urls", []); d.setdefault("url_auto","")
    d.setdefault("combustible",""); d.setdefault("tipo_transmision",""); d.setdefault("caja", None)
    d["_modelo_key"] = modelo_key(d)
    d["_usd"] = price_to_usd(d.get("precio"))
    d["_kms"] = d.get("kilometraje_km") or _safe_int(d.get("kilometraje_km"))

# ------------------ Controles globales ------------------
st.title("⚖️ Comparador A vs B: Marca → Modelo y fotos en cascada")
zoom = st.slider("Escala de zoom", 1, 4, 2)
metodo = st.radio("Método de escalado", ["Suave (LANCZOS)", "Nítido (NEAREST)"], horizontal=True)
max_imgs = st.slider("Máx. imágenes por modelo", 6, 120, 36, step=2)
st.caption("Consejo: para fotos 196×165 (CDN), prueba NEAREST=contornos nítidos, LANCZOS=foto suave.")

# ------------------ Selección lado A y B (Marca → Modelo) ------------------
marcas_all = sorted({ _norm(x.get("marca","")) for x in data if _norm(x.get("marca","")) })
colA, colB = st.columns(2)

def pick_model(col, lado: str):
    with col:
        st.markdown(f"### {'🅰️' if lado=='A' else '🅱️'} Modelo {lado}")

        # 1) Marca
        marca = st.selectbox(
            f"Marca ({lado})",
            ["(Elige)"] + marcas_all,
            key=f"marca_{lado}"
        )
        if marca == "(Elige)":
            st.info("Elige una marca para continuar.")
            return None, [], None

        # 2) Modelo
        modelos_marca = sorted({
            _norm(x.get("modelo",""))
            for x in data if _norm(x.get("marca","")) == marca
        })
        modelo = st.selectbox(
            f"Modelo ({lado})",
            ["(Elige)"] + modelos_marca,
            key=f"modelo_{lado}"
        )
        if modelo == "(Elige)":
            st.info("Elige un modelo para continuar.")
            return f"{marca} | (modelo)", [], None

        # 3) Avisos del modelo
        avisos = [
            x for x in data
            if _norm(x.get("marca","")) == marca and _norm(x.get("modelo","")) == modelo
        ]
        avisos_sorted = sorted(avisos, key=_orden_aviso_precio)
        if not avisos_sorted:
            st.warning("No hay anuncios para esta selección.")
            return f"{marca} | {modelo}", [], None

        # 4) Select de anuncio (SOLO UNO)
        opciones = [_fmt_aviso_label(a) for a in avisos_sorted]
        aviso_sel_label = st.selectbox(
            f"Anuncio ({lado}) • ordenado por precio (↑)",
            opciones,
            index=0,
            key=f"anuncio_{lado}"      # ← clave ÚNICA por lado
        )
        aviso_sel = avisos_sorted[opciones.index(aviso_sel_label)]

        # 5) Botón/enlace al anuncio seleccionado
        url = aviso_sel.get("url_auto")
        if url:
            st.link_button(f"Abrir anuncio ({lado})", url, use_container_width=True)

        # 6) (Opcional) top 5 enlaces más baratos
        with st.expander(f"Ver enlaces (top 5 baratos) — {lado}", expanded=False):
            for a in avisos_sorted[:5]:
                if a.get("url_auto"):
                    st.markdown(f"- [{_fmt_aviso_label(a)}]({a['url_auto']})")

        return f"{marca} | {modelo}", avisos, aviso_sel


# Llamadas (sin coma al final 😉)
m1_name, avisos_m1, aviso_m1 = pick_model(colA, "A")
m2_name, avisos_m2, aviso_m2 = pick_model(colB, "B")

if not avisos_m1 or not avisos_m2:
    st.stop()

# Toggle: ver solo imágenes del anuncio elegido
solo_sel = st.toggle("Mostrar solo imágenes del anuncio seleccionado (A y B)", value=True)


# ------------------ Métricas rápidas ------------------
st.markdown("---")
st.subheader("📊 Métricas")
mc1, mc2 = st.columns(2)
for (name, avisos, c) in [(m1_name, avisos_m1, mc1), (m2_name, avisos_m2, mc2)]:
    with c:
        met = metricas(avisos)
        st.markdown(f"**{name}**")
        st.metric("Avisos", met["n"])
        st.metric("Precio mediano (US$)", f"{met['p50']:,}" if met["p50"] else "—")
        st.caption(f"Rango: {met['pmin']:,} – {met['pmax']:,}" if met["pmin"] else "—")
        st.metric("Kilometraje mediano (km)", f"{met['k50']:,}" if met["k50"] else "—")

# ------------------ Visores en cascada ------------------
st.markdown("---")
st.subheader("🖼️ Fotos en cascada (todas las imágenes apiladas)")

def imagenes_de_avisos(avisos: List[Dict[str,Any]]) -> List[str]:
    urls = []
    for a in avisos:
        urls.extend(a.get("img_urls", []))
    return dedupe(urls)[:max_imgs]

# Antes de mostrar en cascada:
if solo_sel:
    urls1 = dedupe((aviso_m1.get("img_urls", []) if aviso_m1 else []) )[:max_imgs]
    urls2 = dedupe((aviso_m2.get("img_urls", []) if aviso_m2 else []) )[:max_imgs]
else:
    urls1 = imagenes_de_avisos(avisos_m1)
    urls2 = imagenes_de_avisos(avisos_m2)


cascA, cascB = st.columns(2, gap="large")

def mostrar_cascada(col, nombre, urls, key_prefix):
    with col:
        st.markdown(f"**{nombre}** — {len(urls)} imagen(es)")
        if not urls:
            st.info("Sin imágenes.")
            return
        # # Botón para desplegar/abrir URLs
        # with st.expander("Ver URLs de imágenes"):
        #     st.write(urls)
        # Render en cascada (apiladas)
        for i, u in enumerate(urls, start=1):
            img = fetch_image(u)
            if img:
                img = upscale(img, zoom, metodo)
                st.image(img, use_container_width=True, caption=f"{i}/{len(urls)} — {Path(u).name}")
            else:
                st.warning(f"No se pudo cargar: {u}")

mostrar_cascada(cascA, m1_name, urls1, "m1")
mostrar_cascada(cascB, m2_name, urls2, "m2")

# ------------------ (Opcional) Avisos listados ------------------
with st.expander("Ver avisos de cada lado"):
    la, lb = st.columns(2)
    def list_avisos(avisos):
        for a in avisos[:50]:
            st.markdown(f"**{a.get('titulo','')}**")
            st.caption(f"{a.get('año','')} • {a.get('combustible','')} • {a.get('tipo_transmision','')}{' - '+str(a.get('caja')) if a.get('caja') else ''}")
            st.write(f"**Precio:** {a.get('precio','')}  |  **Kms:** {a.get('kilometraje_km','—')}")
            if a.get('url_auto'): st.link_button("Abrir aviso", a['url_auto'], use_container_width=True)
            st.markdown("---")
    with la:
        st.markdown(f"### {m1_name}")
        list_avisos(avisos_m1)
    with lb:
        st.markdown(f"### {m2_name}")
        list_avisos(avisos_m2)
