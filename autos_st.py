## Librerias

import pandas as pd
import numpy as np
import streamlit as st
import google.generativeai as genai
import faiss # pip install faiss-cpu


## Carga de datos
file_path = rf"C:\Users\PC\Desktop\Proyectos\Proyectos_Py\7.Analisis_Autos\vehiculos\neo_autos.csv"
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path, sep="|")
    return df


df = load_data(file_path)

# --- INICIO DE LA CONFIGURACIÓN DE RAG (INDEXACIÓN) ---

@st.cache_resource
def create_vector_store(dataframe):
    """Crea un vector store (índice FAISS) a partir de un DataFrame."""
    # 1. Convertir cada fila del DataFrame a un string (nuestro "documento")
    # Usamos .to_json() porque maneja bien diferentes tipos de datos.
    documents = dataframe.apply(lambda row: row.to_json(), axis=1).tolist()

    # 2. Crear los embeddings para cada documento
    # Usamos el modelo de embeddings de Google. 'task_type' mejora la calidad.
    st.write("Creando embeddings para los datos (esto solo se hace una vez)...")
    embeddings = genai.embed_content(
        model="models/embedding-001",
        content=documents,
        task_type="RETRIEVAL_DOCUMENT"
    )["embedding"]

    # 3. Crear y poblar el índice FAISS
    # Obtenemos la dimensión de los embeddings (e.g., 768)
    d = len(embeddings[0])
    index = faiss.IndexFlatL2(d)
    index.add(np.array(embeddings))

    return index, documents

# --- FIN DE LA CONFIGURACIÓN DE RAG ---

st.title("Análisis de datos - Neo Autos")
st.write("Cantidad de registros:", df.shape[0])