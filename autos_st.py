
## Proyecto Análisis de Autos
## ===========================:

## librerias
import pandas as pd
import numpy as np
import streamlit as st


## Titulo
st.set_page_config(layout="wide")
st.title("Análisis Vehicular 🚘📊")

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


@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path, sep="|")
    return df


data_general = load_data(file_path_general)

data_categoria = load_data(file_path_categoria)


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
    
## ================ ##
## Analisis General ##
## ================ ##

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