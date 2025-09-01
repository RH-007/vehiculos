
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


## Agregando de filtros
st.header("🔍 Vista previa de los datos")

tipo = st.multiselect("Tipo de vehículo", options=df["tipo"].unique(), default=df["tipo"].unique())
marca = st.multiselect("Marca", options=df["marca"].unique(), default=df["marca"].unique())
año = st.multiselect("Año", options=df["año"].unique(), default=df["año"].unique())
precio_etiqueta = st.multiselect("Rango de precio", options=df["precio_etiqueta"].unique(), default=df["precio_etiqueta"].unique())

filtro = df[
    df["tipo"].isin(tipo) &
    df["marca"].isin(marca) & 
    df["año"].isin(año) & 
    df["precio_etiqueta"].isin(precio_etiqueta)
    ]

st.dataframe(filtro)

st.divider()

st.header("🤖 Pregúntale a la IA sobre los datos")
st.info("La IA buscará en toda la base de datos para encontrar la información más relevante y responder tu pregunta.")

# --- Sección de IA con Gemini ---

# 1. Pedir la API Key (en una app real, usa st.secrets)
try:
    # Intenta obtener la clave desde los secretos de Streamlit
    api_key = st.secrets["GOOGLE_API_KEY"]
except (FileNotFoundError, KeyError):
    # Si no la encuentra, pide que se ingrese manualmente
    api_key = st.text_input("Ingresa tu API Key de Google AI", type="password", help="Consigue tu clave en https://aistudio.google.com/app/apikey")

if not api_key:
    st.warning("Por favor, ingresa tu API Key para poder chatear con la IA.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash') # Usamos el modelo flash que es rápido y eficiente

    # Creamos o cargamos desde caché el vector store
    vector_index, documents = create_vector_store(df)

    # 2. Campo de texto para la pregunta del usuario
    # user_question = st.text_input("Ej: ¿Cuál es el precio promedio de los autos Toyota?")
    user_question = st.text_area("Ej: ¿Cuál es el precio promedio de los autos Toyota?")

    if st.button("Preguntar a Gemini"):
        if user_question:
            with st.spinner("Buscando información relevante y generando respuesta... 🧠"):
                # 3. FASE DE RECUPERACIÓN (RETRIEVAL)
                # Convertir la pregunta del usuario en un embedding
                question_embedding = genai.embed_content(
                    model="models/embedding-001",
                    content=user_question,
                    task_type="RETRIEVAL_QUERY"
                )["embedding"]

                # Aumentamos k para darle a la IA un contexto más amplio para filtrar.
                # En lugar de 5, buscamos los 25 documentos más relevantes.
                # Esto aumenta la probabilidad de encontrar vehículos que cumplan los criterios del usuario.
                k = 1500
                distances, indices = vector_index.search(np.array([question_embedding]), k)

                # Obtener los documentos relevantes
                relevant_docs = [documents[i] for i in indices[0]]
                context = "\n".join(relevant_docs)

                # 4. FASE DE GENERACIÓN
                # Crear el prompt con el contexto recuperado
                prompt = f"""
                Eres un asistente experto en análisis de datos de vehículos que actúa como un filtro inteligente.
                Tu tarea es analizar la "Pregunta del usuario" y luego filtrar los "Datos Relevantes" proporcionados para encontrar únicamente los registros que cumplen con TODOS los criterios de la pregunta.

                Datos Relevantes:
                {context}

                Pregunta del usuario: "{user_question}"
                
                Responde presentando una lista o un resumen de los vehículos que encontraste en los "Datos Relevantes" que coinciden con la pregunta.
                Si después de filtrar los datos no encuentras suficientes registros para responder completamente (por ejemplo, si te piden 10 y solo encuentras 3), presenta los que encontraste e indica que no hay más en la información proporcionada que cumplan con todos los criterios.
                """
                response = model.generate_content(prompt)
                st.markdown(response.text)
        else:
            st.error("Por favor, escribe una pregunta.")
