from pathlib import Path
import streamlit as st
from Pages import planteamiento_del_problema, marco_teorico, marco_metodologico
from Pages import analisis, conclusiones, cuestionario

st.set_page_config(page_title="FIRE DATA | Grupo 2", page_icon="FD", layout="wide", initial_sidebar_state="expanded")
css_path = Path(__file__).resolve().parent / "assets" / "estilos.css"
with css_path.open(encoding="utf-8") as archivo:
    st.markdown(f"<style>{archivo.read()}</style>", unsafe_allow_html=True)

st.sidebar.markdown('<div class="brand">FIRE<span>DATA</span></div>', unsafe_allow_html=True)
st.sidebar.caption("INVESTIGACIÓN ESTADÍSTICA · GRUPO 2")
st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
secciones = {
    "Inicio": None,
    "Planteamiento del problema": planteamiento_del_problema.render,
    "Marco teórico": marco_teorico.render,
    "Marco metodológico": marco_metodologico.render,
    "Análisis": analisis.render,
    "Conclusiones": conclusiones.render,
    "Cuestionario": cuestionario.render,
}
with st.sidebar.expander("MENÚ DE NAVEGACIÓN", expanded=True):
    seleccion = st.radio("Secciones", list(secciones), label_visibility="collapsed")
st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
st.sidebar.caption("ESTUDIO HISTÓRICO · 1992–2015")
st.sidebar.caption("California · Texas · Oregón")
st.sidebar.caption("Computación II | Estadística y Ciencias Actuariales")

if secciones[seleccion] is None:
    st.markdown('<div class="eyebrow">FIRE DATA / INVESTIGACIÓN ESTADÍSTICA</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">Incendios forestales<br><span>en Estados Unidos</span></h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-description">Análisis descriptivo de la evolución temporal y espacial de los incendios forestales en California, Texas y Oregón, durante el período 1992–2015.</p>', unsafe_allow_html=True)
    st.markdown('<div class="tag-row"><span>1992–2015</span><span>CALIFORNIA · TEXAS · OREGÓN</span><span>ESTUDIO DESCRIPTIVO</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">PANORAMA DE LA INVESTIGACIÓN</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="medium")
    for col, number, label, note in [
        (c1, "03", "Estados analizados", "California, Texas y Oregón"),
        (c2, "24", "Años de estudio", "Período 1992–2015"),
        (c3, "1992—2015", "Cobertura temporal", "Registros históricos de incendios"),
    ]:
        with col:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{number}</div><div class="stat-label">{label}</div><div class="stat-note">{note}</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">ÁMBITO GEOGRÁFICO</div>', unsafe_allow_html=True)
    left, right = st.columns([1.65, 1], gap="large")
    with left:
        st.markdown('''<div class="feature-panel"><div class="panel-kicker">ESTADOS UNIDOS / 1992–2015</div><div class="panel-title">Tres estados. Un estudio histórico.</div><p>La investigación examina los registros de incendios de tres regiones con condiciones geográficas y climáticas diferentes, mediante indicadores de frecuencia, duración, localización y causas.</p><div class="region-list"><span>CA <strong>California</strong></span><span>TX <strong>Texas</strong></span><span>OR <strong>Oregón</strong></span></div><div class="panel-footnote">La visualización geográfica de eventos se incorporará cuando se conecte la base de datos.</div></div>''', unsafe_allow_html=True)
    with right:
        st.markdown('''<div class="feature-panel side-panel"><div class="panel-kicker">ENFOQUE ACADÉMICO</div><div class="panel-title">¿Qué investigamos?</div><div class="focus-item"><b>01</b><span>Frecuencia anual y estacional</span></div><div class="focus-item"><b>02</b><span>Duración de los incendios</span></div><div class="focus-item"><b>03</b><span>Distribución espacial</span></div><div class="focus-item"><b>04</b><span>Severidad según la causa</span></div></div>''', unsafe_allow_html=True)
    st.markdown('<div class="section-label">EXPLORA EL PROYECTO</div>', unsafe_allow_html=True)
    st.markdown('<div class="closing-panel"><div><div class="panel-kicker">GRUPO 2 · COMPUTACIÓN II</div><div class="panel-title">De los datos a la interpretación</div><p>Consulta el planteamiento, los fundamentos teóricos, la metodología y las secciones de análisis mediante el menú lateral.</p></div></div>', unsafe_allow_html=True)
else:
    secciones[seleccion]()
