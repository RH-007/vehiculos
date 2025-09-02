
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
file_path = "./data/neo_autos.csv"

@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path, sep="|")
    return df


data = load_data(file_path)


## Variables
tipo = data["tipo"].unique().tolist()
tipo.append("Todos")

marca = data["marca"].unique().tolist()
marca.append("Todos")

precio_etiqueta = data["precio_etiqueta"].unique().tolist()
precio_etiqueta.append("Todos")


## ==================##
##      Pestañas     ##
## ==================##
    
tab1, tab2, tab3, tab4 = st.tabs(["🔎 Análisis General", "📦 Nuevos", "📊 Seminuevos", "💰 Usados"])


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
    df_para_modelos = data.copy()
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
    df_filtrado = data.copy()

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
        df_filtrado[existing_cols].sort_values("precio", ascending=True),
        hide_index=True, use_container_width=True, column_config=config, disabled=True, height=1000
    )