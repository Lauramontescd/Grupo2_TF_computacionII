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
    
def render():
    st.header("Análisis de resultados")
    st.info("Sección preparada para incorporar los resultados obtenidos del procesamiento de la base de datos.")
    st.markdown("""**Indicadores por desarrollar:** frecuencia anual y estacional, duración de incendios, distribución geográfica de focos graves y superficie afectada según causa de origen.

Los resultados y gráficos se incorporarán una vez que estén disponibles los datos procesados y validados.""")
