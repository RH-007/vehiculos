
## Proyecto Análisis de Autos
## ===========================:

## librerias
import pandas as pd
import numpy as np
import streamlit as st
import re
import hashlib
import uuid
from streamlit.components.v1 import html as st_html
import json


## Titulo
st.set_page_config(layout="wide")
st.title("Compara Bien: Mercado Vehicular")

"""

Aqui podemos agregar una descripción del proyecto, su objetivo y las herramientas que se utilizarán.

El objetivo del aplicativo es descrbir, comparar y analizar los datos de vehiculos usados, seminuevos y nuevos 
segun diferentes tipos de vehiculo, marcas, modelos, años, precios, km, etc. 

Se usa como fuente de datos la pagina web Neo Autos (https://www.neoautos.com/) y se emplea la libreria Streamlit para crear el aplicativo web.

---
"""

## Carga de datos
file_path_general = "./data/neo_autos_general.csv"
file_path_categoria = "./data/neo_autos_categoria.csv"
file_path_json = rf"C:\Users\PC\Desktop\Proyectos\Proyectos_Py\7.Analisis_Autos\neo_autos_img_autos_camionetas-suv_seminuevos.json"


@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path, sep="|")
    return df

@st.cache_data
def load_json_specs(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return pd.DataFrame(data)

data_general = load_data(file_path_general)
data_categoria = load_data(file_path_categoria)
data_img = load_json_specs(file_path_json)


## Variables
tipo = data_general["tipo"].unique().tolist()
tipo.append("Todos")

marca = data_general["marca"].unique().tolist()
marca.append("Todos")

precio_etiqueta = data_general["precio_etiqueta"].unique().tolist()
precio_etiqueta.append("Todos")


## ==================##
##      Pestañas     ##
## ==================##
    
tab1, tab2, tab3, tab4 = st.tabs(["🔎 Análisis General", "📦 Categorias", "📊 Seminuevos", "💰 Usados"])


## ================ ##
## Analisis General ##
## ================ ##

with tab1:

    c1, c2, c3 = st.columns(3, gap="small")
    with c1:
        st.markdown("**Tipo de Autos**")
        input_tipo = st.selectbox(
            "Tipo de Auto", tipo, key="key_tipo",
            label_visibility="collapsed"
        )
        
    with c2:
        st.markdown("**Elegir marca**")
        input_marca = st.selectbox(
            "marca", marca, key="key_marca",
            label_visibility="collapsed"
        )
        
    ## Modelo (Filtro dinámico)
    # Creamos un dataframe temporal para filtrar los modelos disponibles.
    # Esto asegura que la lista de modelos se actualice según las selecciones de tipo y marca.
    df_para_modelos = data_general.copy()
    if input_tipo != "Todos":
        df_para_modelos = df_para_modelos[df_para_modelos["tipo"] == input_tipo]
    if input_marca != "Todos":
        df_para_modelos = df_para_modelos[df_para_modelos["marca"] == input_marca]

    modelos = df_para_modelos["modelo"].unique().tolist()
    modelos.append("Todos")
        
    with c3:
        st.markdown("**Elegir Modelo**")
        # Renombramos la variable y la key para mayor claridad (input_zona -> input_modelo)
        input_modelo = st.selectbox(
            "Elegir Modelo",
            modelos,
            key="key_modelo",
            label_visibility="collapsed",
            index=0
        )

    ## Filtrado de Datos
    # Empezamos con el dataframe completo y aplicamos filtros secuencialmente.
    # Este método es robusto y maneja todas las combinaciones de "Todos".
    df_filtrado = data_general.copy()

    if input_tipo != "Todos":
        df_filtrado = df_filtrado[df_filtrado["tipo"] == input_tipo]
    
    if input_marca != "Todos":
        df_filtrado = df_filtrado[df_filtrado["marca"] == input_marca]

    if input_modelo != "Todos":
        df_filtrado = df_filtrado[df_filtrado["modelo"] == input_modelo]

    st.write("Cantidad de autos encontrados:", df_filtrado.shape[0])
    # st.dataframe(df_filtrado, use_container_width=True, height=1000)
    
    existing_cols = [
        "url_auto", "titulo","modelo", "año", 
        "kilometraje_km", "precio", "precio_etiqueta",
        "tipo_transmision", "detalle", 
        ]
    
    config = {
        # "precio": st.column_config.TextColumn("Fuente", disabled=True),
        # "direccion": st.column_config.TextColumn("Dirección", disabled=True),
        # "area": st.column_config.NumberColumn("Área", format="%d m²", width="small", disabled=True),
        # "dormitorio": st.column_config.NumberColumn("Dorm.", width="small", disabled=True),
        # "baños": st.column_config.NumberColumn("Baños", width="small", disabled=True),
        # "estacionamientos": st.column_config.NumberColumn("Estac.", width="small", disabled=True),
        # "caracteristica": st.column_config.TextColumn("Características", disabled=True),
        # "enlace": st.column_config.LinkColumn("Anuncio", display_text="🔗 Abrir", validate=r"^https?://.*$"),
        "precio": st.column_config.NumberColumn("Precio ($.)", format="$. %d", disabled=True),
        "kilometraje_km": st.column_config.NumberColumn("km", format="%d km.", disabled=True),
        "tipo_transmision": st.column_config.TextColumn("Transmision", disabled=True),
        "url_auto": st.column_config.LinkColumn("Anuncio", display_text="🔗 Abrir", validate=r"^https?://.*$"),
    }

    
    
    st.data_editor(
        df_filtrado[existing_cols].sort_values("precio", ascending=True)
        , hide_index=True
        , use_container_width=True
        , column_config=config
        , disabled=True
        # , height=1000
    )
    
## ========== ##
## Categoria  ##
## ========== ##

data_categoria = load_data(file_path_categoria)


## Variables
tipo_c = ["Todos"] +  data_categoria["tipo"].unique().tolist()

marca_c = ["Todos"] + data_categoria["marca"].unique().tolist()

precio_etiqueta_c = ["Todos"] +  data_categoria["precio_etiqueta"].unique().tolist()

categoria_c = ["Todos"] +  data_categoria["categoria"].unique().tolist()

with tab2:
    
    st.subheader("Estadisticas por Categoria", divider = "blue")
    
    c1, c2 = st.columns(2, gap="small")
    with c1:
        st.markdown("**Tipo de Autos**")
        input_tipo_ce = st.selectbox(
            "Tipo de Auto", tipo_c, key="key_tipo_c_e",
            label_visibility="collapsed"
        )
        
    with c2:
        st.markdown("**Elegir Categoria**")
        input_marca_ce = st.selectbox(
            "marca", categoria_c, key="key_marca_c_e",
            label_visibility="collapsed"
        )
        
    df_filtrado_c = data_categoria.copy()

    if input_tipo_ce != "Todos":
        df_filtrado_c = df_filtrado_c[df_filtrado_c["tipo"] == input_tipo_ce].reset_index(drop=True)
    
    if input_marca_ce != "Todos":
        df_filtrado_c = df_filtrado_c[df_filtrado_c["categoria"] == input_marca_ce].reset_index(drop=True)

    st.write("Cantidad de autos encontrados:", df_filtrado_c.shape[0])
    
    # st.table(df_filtrado_c)
    
    data_agrupada = df_filtrado_c.groupby("marca")
    
    data_agrupada_df_cat = data_agrupada["precio"].agg(
        n="count",
        min="min", max="max",
        p05=lambda s: s.quantile(0.05),
        q1=lambda s: s.quantile(0.25),
        median="median",
        promedio="mean",
        q3=lambda s: s.quantile(0.75).round(2),
        p95=lambda s: s.quantile(0.95).round(2)
        )

    cols_precios = [c for c in data_agrupada_df_cat.columns if c != "n"]
    data_agrupada_df_fmt = data_agrupada_df_cat.copy()
    data_agrupada_df_fmt[cols_precios] = data_agrupada_df_fmt[cols_precios]\
        .applymap(lambda x: f"$ {x:,.0f}")

    st.data_editor(
        data_agrupada_df_fmt.sort_values("n", ascending=False),
        use_container_width=True,
        column_config={
            "marca": st.column_config.TextColumn("Marca", disabled=True)
        },
        disabled=True,
        key="data_agrupada_df_fmt"
    )


    st.subheader("Análisis Detallado por Vehículo", divider="blue")

    c1, c2, c3, c4 = st.columns(4, gap="small")

    # --- Lógica de Filtros Dependientes ---
    # Empezamos con una copia del dataframe de categorías para esta sección.
    df_filtrado_detalle = data_categoria.copy()

    # Filtro 1: Tipo de Auto
    with c1:
        st.markdown("**Tipo de Autos**")
        tipos_disponibles = ["Todos"] + df_filtrado_detalle["tipo"].unique().tolist()
        input_tipo_detalle = st.selectbox(
            "Tipo de Auto", tipos_disponibles, key="key_tipo_detalle",
            label_visibility="collapsed"
        )
    if input_tipo_detalle != "Todos":
        df_filtrado_detalle = df_filtrado_detalle[df_filtrado_detalle["tipo"] == input_tipo_detalle]

    # Filtro 2: Categoría
    with c2:
        st.markdown("**Elegir Categoria**")
        categorias_disponibles = ["Todos"] + df_filtrado_detalle["categoria"].unique().tolist()
        input_categoria_detalle = st.selectbox(
            "Elegir Categoria",
            categorias_disponibles,
            key="key_categoria_detalle",
            label_visibility="collapsed"
        )
    if input_categoria_detalle != "Todos":
        df_filtrado_detalle = df_filtrado_detalle[df_filtrado_detalle["categoria"] == input_categoria_detalle]

    # Filtro 3: Marca
    with c3:
        st.markdown("**Elegir marca**")
        marcas_disponibles = ["Todos"] + df_filtrado_detalle["marca"].unique().tolist()
        input_marca_detalle = st.selectbox(
            "marca", marcas_disponibles, key="key_marca_detalle",
            label_visibility="collapsed"
        )
    if input_marca_detalle != "Todos":
        df_filtrado_detalle = df_filtrado_detalle[df_filtrado_detalle["marca"] == input_marca_detalle]

    # Filtro 4: Modelo
    with c4:
        st.markdown("**Elegir Modelo**")
        modelos_disponibles = ["Todos"] + df_filtrado_detalle["modelo"].unique().tolist()
        input_modelo_detalle = st.selectbox(
            "Elegir Modelo",
            modelos_disponibles,
            key="key_modelo_detalle",
            label_visibility="collapsed"
        )
    if input_modelo_detalle != "Todos":
        df_filtrado_detalle = df_filtrado_detalle[df_filtrado_detalle["modelo"] == input_modelo_detalle]

    # --- Visualización de Datos ---
    st.write("Cantidad de autos encontrados:", df_filtrado_detalle.shape[0])
    
    existing_cols = [
        "url_auto", "titulo","modelo", "categoria", "año", 
        "kilometraje_km", "precio", "precio_etiqueta",
        "tipo_transmision", "detalle", 
        ]

    config = {
        "precio": st.column_config.NumberColumn("Precio ($.)", format="$. %d", disabled=True),
        "kilometraje_km": st.column_config.NumberColumn("km", format="%d km.", disabled=True),
        "tipo_transmision": st.column_config.TextColumn("Transmision", disabled=True),
        "url_auto": st.column_config.LinkColumn("Anuncio", display_text="🔗 Abrir", validate=r"^https?://.*$"),
    }

    
    st.data_editor(
        df_filtrado_detalle[existing_cols].sort_values("precio", ascending=True)
        , hide_index=True
        , use_container_width=True
        , column_config=config
        , disabled=True
    )
    
## =========== ##
## Seminuevos  ##
## =========== ##

marcas_all = data_img["marca"].unique().tolist()

df = data_img.copy()
df["tipo_vehiculo"] = df["tipo_vehiculo"].str.lower().str.strip()
df["categoria"] = df["categoria"].str.lower().str.strip()
df = df[(df["tipo_vehiculo"] == "seminuevos") & (df["categoria"] == "camionetas-suv")].copy()


# Helpers
def _norm(x):
    return (x or "").strip()

def _parse_usd(s):
    """Devuelve monto en USD como float si el string es tipo 'US$ 34,200' (None si no matchea)."""
    if not isinstance(s, str):
        return None
    m = re.search(r"US\$\s*([0-9\.,]+)", s)
    if not m:
        return None
    val = m.group(1).replace(".", "").replace(",", "")
    try:
        return float(val)
    except:
        return None

def _fmt_aviso_label(row):
    anio = _norm(row.get("año", ""))
    titulo = _norm(row.get("titulo", ""))
    precio = _norm(row.get("precio", "")) or "—"
    kms = row.get("kilometraje_km")
    kms_txt = f"{kms:,}" if isinstance(kms, (int, float)) else (str(kms) if kms else "—")
    return f"{anio} • {titulo} • {precio} • Kms: {kms_txt}"

def _opciones_ofertas(df_sub):
    tmp = df_sub.copy()
    tmp["precio_usd"] = tmp["precio"].apply(_parse_usd)
    tmp = tmp.sort_values(["precio_usd", "kilometraje_km"], ascending=[True, True], na_position="last")
    labels = [_fmt_aviso_label(r) for _, r in tmp.iterrows()]
    return labels, tmp.reset_index(drop=True)

def _uniq_key(base: str) -> str:
    return hashlib.md5(base.encode("utf-8")).hexdigest()[:10]

def _opciones_ofertas(df_sub):
    tmp = df_sub.copy()
    tmp["precio_usd"] = tmp["precio"].apply(_parse_usd)
    tmp = tmp.sort_values(["precio_usd", "kilometraje_km"], ascending=[True, True], na_position="last")
    labels = [_fmt_aviso_label(r) for _, r in tmp.iterrows()]
    return labels, tmp.reset_index(drop=True)

def _tarjeta(aviso, lado):
    # col1, col2 = st.columns([1, 1])
    # with col1:
    st.markdown(f"**{aviso.get('marca','')} {aviso.get('modelo','')} {aviso.get('año','')}**")
    st.markdown(f"**Precio:** {aviso.get('precio','—')}")
    st.markdown(f"**Kms:** {aviso.get('kilometraje_km','—')}")
    st.markdown(f"**Combustible:** {aviso.get('combustible','—')}")
    st.markdown(f"**Transmisión:** {aviso.get('tipo_transmision','—')}")
    st.markdown(f"**Ubicación:** {aviso.get('ubicacion','—')}")
    url = aviso.get("url_auto")
    if url:
        st.link_button(f"Abrir anuncio ({lado})", url, use_container_width=True)
    
    # ## Presentacion de iamgenes
    # imgs = aviso.get("imagenes") or []
    # if isinstance(imgs, list) and len(imgs) > 0:
    #     st.image(imgs, use_container_width=True, caption=[f"{lado} {i+1}" for i in range(len(imgs))])
        # st.image_carousel_with_arrows(imgs, aviso.get("url_auto", aviso.get("titulo","")))

    else:
        st.info("Sin imágenes")
        
    st.markdown(f"**Descripción:** {aviso.get('descripcion','—')}")
    
def _uniq_key(base: str) -> str:
    return hashlib.md5((base or "").encode()).hexdigest()[:10]

def _money_usd(s):
    if s is None: return None
    if isinstance(s, (int,float)): return f"US$ {s:,.0f}"
    m = re.search(r"US\$\s*([0-9\.,]+)", str(s))
    if not m: return s
    n = m.group(1).replace(".","").replace(",","")
    try:
        return f"US$ {int(float(n)):,.0f}"
    except: return s

def _km_fmt(x):
    try:
        return f"{int(float(x)):,.0f} km"
    except:
        return "—"

def _badge(text):
    return f"""<span style="
        display:inline-block;background:#202633;border:1px solid #2c3547;
        padding:2px 8px;border-radius:999px;font-size:0.85rem;margin-right:6px;">
        {text}</span>"""

# # ---- Carrusel simple (slider) ----
# def image_carousel(urls, key_base: str):
#     if not urls:
#         st.info("Sin imágenes.")
#         return
#     k = _uniq_key(key_base)
#     idx = st.slider("Imágenes", 1, len(urls), 1, key=f"crsl_{k}", label_visibility="collapsed")
#     st.image(urls[idx-1], use_container_width =True, caption=f"{idx}/{len(urls)}")

def tarjeta_mejorada(aviso: dict, titulo_btn: str):
    # CARRUSEL
    imgs = aviso.get("imagenes") or []
    # image_carousel(imgs, aviso.get("url_auto", aviso.get("titulo",""))) ## descomentar
    image_carousel_with_arrows(imgs, height=520, show_thumbs=True, key_base=aviso.get("url_auto",""))

    # INFO
    st.markdown("—")  # separador fino
    marca = aviso.get("marca",""); modelo = aviso.get("modelo",""); anio = aviso.get("año","")
    st.markdown(f"### {marca} {modelo} {anio}")

    precio = _money_usd(aviso.get("precio"))
    kms    = _km_fmt(aviso.get("kilometraje_km"))
    comb   = aviso.get("combustible","—")
    trans  = aviso.get("tipo_transmision","—")
    ubic   = aviso.get("ubicacion","—")
    tags   = [t.strip() for t in (aviso.get("tags") or "").split(",") if t.strip()]

    # badges de resumen
    badges = "".join([
        _badge(precio or "—"),
        _badge(kms),
        _badge(comb),
        _badge(trans)
    ] + ([_badge(t) for t in tags] if tags else []))
    st.markdown(badges, unsafe_allow_html=True)

    st.write(f"**Ubicación:** {ubic}")

    url = aviso.get("url_auto")
    if url:
        st.link_button(titulo_btn, url, use_container_width=True)

def image_carousel_with_arrows(img_urls, *, height=520, show_thumbs=True, key_base=""):
    """Carrusel con flechas dentro de la imagen (funciona en Streamlit usando components.html)."""
    if not isinstance(img_urls, list) or len(img_urls) == 0:
        st.info("Sin imágenes disponibles.")
        return

    cid = f"crsl_{uuid.uuid4().hex[:8]}"
    imgs_json = json.dumps(img_urls)

    thumbs_html = """
      <div class="thumbs">
        <!-- thumbs renderizadas por JS -->
      </div>
    """ if show_thumbs else ""

    html_code = f"""
    <div id="{cid}" class="carousel">
      <button class="nav prev">&#10094;</button>
      <img class="main" src="" alt="img">
      <button class="nav next">&#10095;</button>
      <div class="caption"></div>
      {thumbs_html}
    </div>

    <script>
      (function(){{
        const imgs = {imgs_json};
        let idx = 0;
        const root = document.getElementById("{cid}");
        const main = root.querySelector("img.main");
        const cap  = root.querySelector(".caption");
        const prev = root.querySelector(".prev");
        const next = root.querySelector(".next");
        const thumbs = root.querySelector(".thumbs");

        function render() {{
          main.src = imgs[idx];
          cap.textContent = (idx+1) + " / " + imgs.length;
          if (thumbs) {{
            [...thumbs.children].forEach((el,i)=>{{
              el.className = "thumb" + (i===idx ? " active" : "");
            }});
          }}
        }}

        function plus(n) {{
          idx = (idx + n + imgs.length) % imgs.length;
          render();
        }}

        prev.addEventListener("click", ()=>plus(-1));
        next.addEventListener("click", ()=>plus(1));

        if (thumbs) {{
          thumbs.innerHTML = imgs.map((u,i)=>`<img src="${{u}}" class="thumb">`).join("");
          [...thumbs.children].forEach((t,i)=> t.addEventListener("click", ()=>{{ idx=i; render(); }}));
        }}

        render();
      }})();
    </script>

    <style>
      #{cid}.carousel {{
        position: relative;
        width: 100%;
        height: 100%;
        background: transparent;
        display:flex;
        flex-direction:column;
        align-items:center;
        gap: 10px;
      }}
      #{cid} img.main {{
        width: 100%;
        height: 100%;
        object-fit: contain;
        border-radius: 12px;
        background: #111;
      }}
      #{cid} .nav {{
        position:absolute;
        top: 45%;
        transform: translateY(-50%);
        padding: 8px 12px;
        border:none;
        border-radius: 50%;
        background: rgba(0,0,0,0.45);
        color:#fff;
        font-size:18px;
        cursor:pointer;
        z-index:2;
      }}
      #{cid} .prev {{ left: 10px; }}
      #{cid} .next {{ right: 10px; }}
      #{cid} .nav:hover {{ background: rgba(0,0,0,0.75); }}
      #{cid} .caption {{
        font-size: .9rem;
        color: #bbb;
        text-align:center;
      }}
      #{cid} .thumbs {{
        display:flex; gap:8px; overflow-x:auto; width:100%;
      }}
      #{cid} .thumb {{
        width:70px; height:50px; object-fit:cover; border-radius:6px; opacity:.7; cursor:pointer;
        border:1px solid #333;
      }}
      #{cid} .thumb.active {{ outline:2px solid #888; opacity:1; }}
    </style>
    """

    st_html(html_code, height=height, scrolling=False)
    
    
## presentacion de Resultados            
            
with tab3:
    st.subheader("Comparar Modelos (Seminuevos • SUV)", divider="blue")

    # Listas de marcas disponibles
    marcas_all = sorted(df["marca"].dropna().unique().tolist())
    colA, colB = st.columns(2)

    # ======= LADO A =======
    marca1 = colA.selectbox("Marca 1", ["(Elige)"] + marcas_all, key="semi_marca1")
    if marca1 != "(Elige)":
        modelos_marca1 = sorted(df[df["marca"] == marca1]["modelo"].dropna().unique().tolist())
    else:
        modelos_marca1 = []
    modelo1 = colA.selectbox("Modelo 1", ["(Elige)"] + modelos_marca1, key="semi_modelo1")

    df_a = df[(df["marca"] == marca1) & (df["modelo"] == modelo1)] if (marca1 != "(Elige)" and modelo1 != "(Elige)") else df.head(0)
    if len(df_a) > 0:
        opts_a, tmp_a = _opciones_ofertas(df_a)
        oferta1 = colA.selectbox("Oferta 1 (orden: precio ↑)", opts_a if opts_a else ["(Sin ofertas)"], key="semi_oferta1")
        sel_a = tmp_a.iloc[opts_a.index(oferta1)].to_dict() if opts_a else None
    else:
        sel_a = None     
        
    # ======= LADO B =======
    marca2 = colB.selectbox("Marca 2", ["(Elige)"] + marcas_all, key="semi_marca2")
    if marca2 != "(Elige)":
        modelos_marca2 = sorted(df[df["marca"] == marca2]["modelo"].dropna().unique().tolist())
    else:
        modelos_marca2 = []
    modelo2 = colB.selectbox("Modelo 2", ["(Elige)"] + modelos_marca2, key="semi_modelo2")

    df_b = df[(df["marca"] == marca2) & (df["modelo"] == modelo2)] if (marca2 != "(Elige)" and modelo2 != "(Elige)") else df.head(0)
    if len(df_b) > 0:
        opts_b, tmp_b = _opciones_ofertas(df_b)
        oferta2 = colB.selectbox("Oferta 2 (orden: precio ↑)", opts_b if opts_b else ["(Sin ofertas)"], key="semi_oferta2")
        sel_b = tmp_b.iloc[opts_b.index(oferta2)].to_dict() if opts_b else None
    else:
        sel_b = None       
        
    # ======= TÍTULO COMPARATIVO =======
    if (marca1 != "(Elige)" and modelo1 != "(Elige)") and (marca2 != "(Elige)" and modelo2 != "(Elige)"):
        st.markdown(f"### Comparación : {marca1} {modelo1} vs {marca2} {modelo2}")

    # ======= TARJETAS =======
    colL, colR = st.columns(2)
    with colL:
        if sel_a:
            _tarjeta(sel_a,  f"{marca1} {modelo1}")
        else:
            st.info("Selecciona una oferta en el Lado A")
    with colR:
        if sel_b:
            _tarjeta(sel_b,  f"{marca2} {modelo2}")
        else:
            st.info("Selecciona una oferta en el Lado B")

    colL, colR = st.columns(2)
    with colL:
        if sel_a: tarjeta_mejorada(sel_a, f"Abrir anuncio ({sel_a.get('modelo','')})")
        else: st.info("Selecciona una oferta en el Lado A.")
    
    with colR:
        if sel_b: tarjeta_mejorada(sel_b, f"Abrir anuncio ({sel_b.get('modelo','')})")
        else: st.info("Selecciona una oferta en el Lado B.")
    
    # ====== Comparativa compacta (opcional pero útil) ======
    def _num_usd(s):
        if s is None: return None
        if isinstance(s,(int,float)): return float(s)
        m = re.search(r"US\$\s*([0-9\.,]+)", str(s))
        if not m: return None
        try: return float(m.group(1).replace(".","").replace(",",""))
        except: return None
    
    if sel_a and sel_b:
        # --- Extraer valores numéricos seguros ---
        def _num_usd(s):
            if s is None: return None
            if isinstance(s,(int,float)): return float(s)
            import re
            m = re.search(r"US\$\s*([0-9\.,]+)", str(s))
            if not m: return None
            try: return float(m.group(1).replace(".","").replace(",",""))
            except: return None
    
        def _safe_int(x):
            try: return int(str(x).strip())
            except: return None
    
        a_prec = _num_usd(sel_a.get("precio"))
        b_prec = _num_usd(sel_b.get("precio"))
        a_km   = sel_a.get("kilometraje_km")
        b_km   = sel_b.get("kilometraje_km")
        a_anio = _safe_int(sel_a.get("año"))
        b_anio = _safe_int(sel_b.get("año"))
    
        # --- Etiquetas de encabezado ---
        label_a = f"{sel_a.get('marca','')} {sel_a.get('modelo','')}".strip() or "Lado A"
        label_b = f"{sel_b.get('marca','')} {sel_b.get('modelo','')}".strip() or "Lado B"
    
        # --- Tabla comparativa ---
        tabla = pd.DataFrame({
            "Campo": ["Precio (US$)", "Kilometraje (km)", "Año"],
            label_a: [
                f"{a_prec:,.0f}" if a_prec is not None else "—",
                f"{int(a_km):,}" if a_km not in (None,"") else "—",
                a_anio if a_anio else "—"
            ],
            label_b: [
                f"{b_prec:,.0f}" if b_prec is not None else "—",
                f"{int(b_km):,}" if b_km not in (None,"") else "—",
                b_anio if b_anio else "—"
            ],
            "Δ (B − A)": [
                f"{(b_prec - a_prec):,.0f}" if (a_prec is not None and b_prec is not None) else "—",
                f"{(int(b_km) - int(a_km)):,}" if (a_km not in (None,"") and b_km not in (None,"")) else "—",
                (b_anio - a_anio) if (a_anio and b_anio) else "—"
            ]
        })
    
        st.markdown("#### Comparativa rápida")
        st.table(tabla)

