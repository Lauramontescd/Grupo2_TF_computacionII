import streamlit as st
from Pages import planteamiento_del_problema, marco_teorico, marco_metodologico
from Pages import analisis, conclusiones, cuestionario

st.set_page_config(page_title="Incendios forestales | Grupo 2", page_icon="🔥", layout="wide")
with open("assets/estilos.css", encoding="utf-8") as archivo:
    st.markdown(f"<style>{archivo.read()}</style>", unsafe_allow_html=True)

st.sidebar.markdown("# 🔥 Grupo 2")
st.sidebar.caption("Computación II · Estadística y Ciencias Actuariales")
secciones = {
    "Inicio": None,
    "Planteamiento del problema": planteamiento_del_problema.render,
    "Marco teórico": marco_teorico.render,
    "Marco metodológico": marco_metodologico.render,
    "Análisis": analisis.render,
    "Conclusiones": conclusiones.render,
    "Cuestionario": cuestionario.render,
}
with st.sidebar.expander("☰ MENÚ DE NAVEGACIÓN", expanded=True):
    seleccion = st.radio("SECCIONES", list(secciones), label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.caption("California · Texas · Oregón | 1992–2015")
if secciones[seleccion] is None:
    st.title("🔥 Incendios forestales en Estados Unidos")
    st.subheader("Evolución temporal y espacial · 1992–2015")
    st.markdown("Investigación descriptiva de los incendios forestales en **California, Texas y Oregón**.")
    a,b,c = st.columns(3)
    a.metric("Estados estudiados", "3")
    b.metric("Período", "1992–2015")
    c.metric("Años analizados", "24")
    st.info("Utiliza el menú lateral para explorar los capítulos de la investigación.")
else:
    secciones[seleccion]()
