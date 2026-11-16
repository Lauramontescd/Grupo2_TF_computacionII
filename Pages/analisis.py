from duckdb import df
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


def _objetivo2(df: pd.DataFrame, estado: str) -> None:
    st.subheader("Cambio de la duración promedio de los incendios")
    usar = st.checkbox("Usar la duración corregida (recomendado)", value=True, key=f"corr_{estado}",
                       help="En ~20.000 incendios multi-día la limpieza reemplazó la fecha de contención por "
                            "«descubrimiento + 1 día». La columna CONT_DOY conserva el dato original y permite recuperarlo.")
    columna = "duracion_corregida" if usar else "duracion_dias"
    d = ind.duracion_anual(df, estado, columna)
    serie = df.loc[df["estado"] == estado, columna]
    c1, c2, c3 = st.columns(3)
    c1.metric("Duración media (días)", f"{serie.mean():.2f}")
    c2.metric("Mediana (días)", f"{serie.median():.0f}")
    c3.metric("Duran más de 1 día", f"{(serie > 1).mean() * 100:.1f} %")
    st.line_chart(d[["media_dias"]])
    st.write(_frase(ind.tendencia(d.index, d["media_dias"]), "la duración media", "días"))
    st.caption("La duración se mide en días completos entre la fecha de descubrimiento y la de contención. "
               "La distribución tiene cola larga (la mediana es casi siempre 0 días), por eso se reporta también el percentil 90.")
    st.dataframe(d.round(2))

def _objetivo3(df: pd.DataFrame, estado: str) -> None:
     st.subheader("Frecuencia anual y estacional; duración de la temporada")
     frec = ind.frecuencia_anual(df, estado)
     st.bar_chart(frec)
     st.write(_frase(ind.tendencia(frec.index, frec), "el número de incendios registrados", "incendios"))
     temp = ind.temporada_anual(df, estado)
     st.markdown("**Duración de la temporada** = días entre el percentil 5 y el percentil 95 de la fecha de descubrimiento de cada año.")
     st.line_chart(temp[["largo_dias"]])
     st.write(_frase(ind.tendencia(temp.index, temp["largo_dias"]), "la duración de la temporada", "días", 1))
     st.markdown("**Distribución mensual (% de los incendios de cada periodo)**")
     st.line_chart(ind.perfil_mensual(df, estado))
     st.warning("Los conteos corresponden a los incendios que tienen hora de descubrimiento registrada; "
                "esa proporción varía por año y estado (en Texas es muy baja). Interpreta la tendencia del número de "
                "incendios con cautela; el largo de la temporada y el perfil mensual dependen menos de ese efecto.")
     st.dataframe(temp.round(1))

def _objetivo4(df: pd.DataFrame, estado: str) -> None:
     st.subheader("Evolución de la magnitud de los incendios")
     m = ind.magnitud_anual(df, estado)
     st.markdown("**Superficie quemada por año (acres)**")
     st.bar_chart(m["superficie_total_acres"])
     st.write(_frase(ind.tendencia(m.index, m["superficie_total_acres"]), "la superficie quemada anual", "acres", 0))
     st.markdown("**Tamaño típico y grande (acres): promedio y percentil 90**")
     st.line_chart(m[["media_acres", "p90_acres"]])
     st.write(_frase(ind.tendencia(m.index, m["p90_acres"]), "el tamaño del percentil 90", "acres"))
     st.markdown("**Reparto por clase de tamaño (% de incendios por periodo)**")
     st.dataframe(ind.clases_por_periodo(df, estado).round(1))
     st.caption("La distribución del tamaño tiene cola muy larga: unos pocos incendios concentran casi toda la superficie. "
                "Por eso se usan percentiles y totales, no solo el promedio.")
     st.dataframe(m.round(2))

def _objetivo5(df: pd.DataFrame, estado: str) -> None:
    st.subheader("Severidad de los incendios según su causa")
    st.caption("Natural = rayo (código 1). Humana = causas 2 a 12. Sin determinar = código 13. "
               "Severidad = tamaño del incendio (acres) y proporción de incendios grandes.")
    nivel = st.radio("Agrupar por", ["Grupo (natural / humana)", "Causa (13 categorías)"], horizontal=True, key=f"nivel_{estado}")
    sev = ind.severidad_por_causa(df, estado, "grupo_causa" if nivel.startswith("Grupo") else "causa")
    st.dataframe(sev.round(2))
    st.markdown("*Porcentaje de incendios vs. porcentaje de la superficie quemada*")
    st.bar_chart(sev[["pct_incendios", "pct_superficie"]])
    st.markdown("*Superficie quemada por año según el origen (acres)*")
    st.line_chart(ind.superficie_anual_por_grupo(df, estado))

def render() -> None:
    st.header("Análisis de resultados")
    df = cargar_incendios()
    estado = st.radio("Estado", list(NOMBRES_ESTADO), format_func=NOMBRES_ESTADO.get, horizontal=True)
    n = int((df["estado"] == estado).sum())
    st.caption(f"{n:,} incendios de {NOMBRES_ESTADO[estado]} con hora de descubrimiento registrada (1992–2015).")
    t1, t2, t3, t4, t5 = st.tabs(["1 · Focos graves", "2 · Duración", "3 · Frecuencia y temporada",
                                  "4 · Magnitud", "5 · Severidad por causa"])
    with t1:
        _objetivo1(df, estado)
    with t2:
        _objetivo2(df, estado)
    with t3:
        _objetivo3(df, estado)
    with t4:
        _objetivo4(df, estado)
    with t5:
        _objetivo5(df, estado)

def render():
    st.header("Análisis de resultados")
    st.info("Sección preparada para incorporar los resultados obtenidos del procesamiento de la base de datos.")
    st.markdown("""**Indicadores por desarrollar:** frecuencia anual y estacional, duración de incendios, distribución geográfica de focos graves y superficie afectada según causa de origen.

Los resultados y gráficos se incorporarán una vez que estén disponibles los datos procesados y validados.""")
    
