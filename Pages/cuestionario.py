import streamlit as st
from supabase import create_client, Client
import pandas as pd

@st.cache_resource
def init_connection() -> Client:
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Faltan las credenciales en '.streamlit/secrets.toml': {e}")
        st.stop()

supabase = init_connection()

@st.cache_data(ttl=600)
def get_fires_data(limit_rows: int = 1000):
    try:
        response = supabase.table("fires").select("*").limit(limit_rows).execute()
        return response.data
    except Exception as e:
        st.error(f"Error al ejecutar la consulta en Supabase: {e}")
        return []


def render():
    st.header("Cuestionario")
    st.write("Espacio para las preguntas de evaluación sobre el proyecto y su base de datos.")
    st.info("El documento original del cuestionario se conserva en el repositorio; las preguntas se incorporarán aquí tras su revisión.")
