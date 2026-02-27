import streamlit as st
import PyPDF2
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Ayudante de Estudio IA", page_icon="📚", layout="wide")

with st.sidebar:
    st.title("⚙️ Configuración")
    api_key = st.text_input("🔑 Ingresa tu Google API Key:", type="password")
    st.divider()
    st.markdown("### 💡 ¿Qué puedes pedirle?")
    st.markdown("- Hazme un resumen de la página 3 a la 10.")
    st.markdown("- Explícame el concepto X como si tuviera 10 años.")
    st.markdown("- Hazme 5 preguntas de opción múltiple para practicar.")

st.title("📚 Tu Ayudante de Estudio Universitario")
st.markdown("Sube tu PDF denso y pregúntale lo que quieras, o usa los botones rápidos para extraer información clave.")

# --- FUNCIÓN PARA LEER EL PDF ---
@st.cache_data # Guardamos en caché para no reprocesar el PDF cada vez que interactúas
def extraer_texto_pdf(archivo_pdf):
    texto = ""
    lector = PyPDF2.PdfReader(archivo_pdf)
    for pagina in lector.pages:
        # Extraemos el texto y nos aseguramos de que no sea nulo
        texto_pagina = pagina.extract_text()
        if texto_pagina:
            texto += texto_pagina + "\n"
    return texto

# --- INTERFAZ PRINCIPAL ---
# 1. Carga de archivo
archivo_subido = st.file_uploader("Sube tu documento PDF aquí", type=["pdf"])

if archivo_subido is not None:
    # Extraemos el texto
    with st.spinner("Leyendo el documento..."):
        texto_documento = extraer_texto_pdf(archivo_subido)
    
    st.success("✅ ¡Documento cargado y leído con éxito! Puedes empezar a estudiar.")
    
    # Preparamos el LLM
    if api_key:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key, temperature=0.3)
        parser = StrOutputParser() #
        
        # Plantilla maestra que recibe el documento y la petición del usuario
        prompt_template = PromptTemplate(
            input_variables=["documento", "peticion"],
            template="""Eres un tutor universitario experto. Usa ÚNICAMENTE el siguiente documento para responder a la petición del estudiante.
            
            DOCUMENTO:
            {documento}
            
            PETICIÓN DEL ESTUDIANTE:
            {peticion}
            
            Respuesta estructurada y clara:"""
        )
        
        # Cadena de LangChain
        cadena = prompt_template | llm | parser #
        
        st.divider()
        st.markdown("### ⚡ Acciones Rápidas")
        col1, col2, col3 = st.columns(3)
        
        # Variables de estado para controlar la acción rápida elegida
        accion = None
        
        with col1:
            if st.button("📝 Generar Resumen General", use_container_width=True):
                accion = "Haz un resumen estructurado del texto completo, destacando los 5 puntos más importantes en viñetas."
        with col2:
            if st.button("🔑 Extraer Ideas Principales", use_container_width=True):
                accion = "Extrae las 10 ideas o conceptos más importantes y explícalos en una sola línea cada uno."
        with col3:
            if st.button("🗂️ Crear Flashcards", use_container_width=True):
                accion = "Crea 5 flashcards de estudio. Formato: 'Concepto: [Nombre] | Definición: [Explicación simple]'"
                
        # Barra libre para chatear
        peticion_libre = st.chat_input("O escribe tu propia pregunta sobre el texto...")
        
        # Lógica de ejecución
        peticion_final = peticion_libre if peticion_libre else accion
        
        if peticion_final:
            st.markdown(f"**Tu petición:** {peticion_final}")
            with st.spinner("Generando la mejor respuesta basada en tu documento..."):
                try:
                    # Invocamos la cadena inyectando todo el texto del PDF y la petición
                    respuesta = cadena.invoke({
                        "documento": texto_documento,
                        "peticion": peticion_final
                    }) #
                    st.info(respuesta)
                except Exception as e:
                    st.error("Hubo un error al conectar con Google Gemini. Revisa tu API Key.")
    else:
        st.warning("👈 Ingresa tu API Key en el menú lateral para interactuar con el documento.")