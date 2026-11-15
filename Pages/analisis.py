import streamlit as st
import numpy as np
import pandas as pd

import indicators as ind
from data import NOMBRES_ESTADO, cargar_incendios

CLASES_GRAVES = {"D": "D (100 acres o más)", "E": "E (300 o más)", "F": "F (1.000 o más)", "G": "G (5.000 o más)"}


def _frase(t: dict, sujeto: str, unidad: str, decimales: int = 2) -> str:
    """Convierte el resultado de ind.tendencia() en una oración."""
    if np.isnan(t["pendiente"]):
        return f"No hay datos suficientes para estimar la tendencia de {sujeto}."
    sentido = "aumenta" if t["pendiente"] > 0 else "disminuye"
    return (f"{sujeto[0].upper() + sujeto[1:]} {sentido} en promedio {abs(t['pendiente']):.{decimales}f} {unidad} "
            f"por año (R² = {t['r2']:.2f}; correlación de Spearman con el año = {t['rho']:.2f}).")

    
    def _objetivo1(df: pd.DataFrame, estado: str) -> None:
    st.subheader("Migración geográfica de los focos más graves")
    clase = st.select_slider("Tamaño mínimo para considerar un incendio «grave»", options=list(CLASES_GRAVES),
                             value="F", format_func=CLASES_GRAVES.get, key=f"clase_{estado}")
    graves = ind.focos_graves(df, estado, clase)
    if graves.empty:
        st.info("No hay incendios de esa clase en el estado seleccionado.")
        return
    cent = ind.centroides_por_periodo(graves)
    mov = ind.desplazamiento(cent)
    c1, c2 = st.columns(2)
    c1.metric("Incendios graves analizados", f"{len(graves):,}")
    if mov:
        c2.metric(f"Desplazamiento del centro ({mov['desde']} → {mov['hasta']})", f"{mov['km']:.0f} km",
                  f"hacia el {mov['direccion_ns']} y el {mov['direccion_eo']}", delta_color="off")
    st.caption("El centro de cada periodo es el promedio de las coordenadas ponderado por la superficie quemada.")
    st.dataframe(cent.round(3))
    columnas = st.columns(len(cent))
    for col, (periodo, sub) in zip(columnas, graves.groupby("periodo")):
        with col:
            st.caption(f"{periodo} · {len(sub)} incendios")
            st.map(sub, latitude="LATITUDE", longitude="LONGITUDE")
    with st.expander("Centro de los focos graves año por año"):
        anual = ind.centroides_por_anio(graves)
        st.line_chart(anual[["latitud_centro"]])
        st.line_chart(anual[["longitud_centro"]])
        st.caption("Los años con pocos incendios graves son ruidosos; la tabla por periodo es más estable.")



def render():
    st.header("Análisis de resultados")
    st.info("Sección preparada para incorporar los resultados obtenidos del procesamiento de la base de datos.")
    st.markdown("""**Indicadores por desarrollar:** frecuencia anual y estacional, duración de incendios, distribución geográfica de focos graves y superficie afectada según causa de origen.

Los resultados y gráficos se incorporarán una vez que estén disponibles los datos procesados y validados.""")
