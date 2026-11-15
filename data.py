"""Acceso y preparación de los datos de incendios (base normalizada en MotherDuck)."""
import os

import duckdb
import numpy as np
import pandas as pd
import streamlit as st

NOMBRES_ESTADO = {"CA": "California", "OR": "Oregón", "TX": "Texas"}
ORDEN_CLASES = list("ABCDEFG")  

CONSULTA = """
SELECT CAST(e.FOD_ID AS INTEGER)           AS FOD_ID,
       CAST(e.DISCOVERY_DATE AS DATE)      AS DISCOVERY_DATE,
       CAST(e.CONT_DATE AS DATE)           AS CONT_DATE,
       CAST(e.CONT_DOY AS INTEGER)         AS CONT_DOY,
       CAST(e.FIRE_SIZE AS DOUBLE)         AS FIRE_SIZE,
       e.FIRE_SIZE_CLASS,
       CAST(e.LATITUDE AS DOUBLE)          AS LATITUDE,
       CAST(e.LONGITUDE AS DOUBLE)         AS LONGITUDE,
       year(CAST(e.DISCOVERY_DATE AS DATE))  AS anio,
       month(CAST(e.DISCOVERY_DATE AS DATE)) AS mes,
       CAST(e.DISCOVERY_DOY AS INTEGER)    AS doy,
       e.STATE                             AS estado,
       CAST(e.STAT_CAUSE_CODE AS INTEGER)  AS codigo_causa,
       c.STAT_CAUSE_DESCR                  AS causa
FROM fire_event e
JOIN cause c ON CAST(c.STAT_CAUSE_CODE AS INTEGER) = CAST(e.STAT_CAUSE_CODE AS INTEGER)
"""


def conectar():
    """Conexión a MotherDuck. El token y el nombre de la base se leen de los secretos de
    Streamlit (.streamlit/secrets.toml), nunca del código ni del repositorio."""
    try:
        token = st.secrets["MOTHERDUCK_TOKEN"]
        base = st.secrets["MOTHERDUCK_DB"]
    except (KeyError, FileNotFoundError):
        raise RuntimeError(
            "Faltan MOTHERDUCK_TOKEN y MOTHERDUCK_DB en .streamlit/secrets.toml."
        ) from None
    os.environ["motherduck_token"] = token
    return duckdb.connect(f"md:{base}")


def grupo_de_causa(codigo: int) -> str:
    """1 = rayo (natural); 13 = sin determinar; 2-12 = origen humano."""
    if codigo == 1:
        return "Natural"
    if codigo == 13:
        return "Sin determinar"
    return "Humana"


def preparar(df: pd.DataFrame) -> pd.DataFrame:
    """Tipos correctos y columnas derivadas. Función pura (no depende de Streamlit)."""
    df = df.copy()
    for col in ["anio", "mes", "doy", "CONT_DOY", "codigo_causa"]:
        df[col] = df[col].astype("int64")
    df["DISCOVERY_DATE"] = pd.to_datetime(df["DISCOVERY_DATE"])
    df["CONT_DATE"] = pd.to_datetime(df["CONT_DATE"])
    df["nombre_estado"] = df["estado"].map(NOMBRES_ESTADO)
    df["grupo_causa"] = df["codigo_causa"].map(grupo_de_causa)

    df["duracion_dias"] = (df["CONT_DATE"] - df["DISCOVERY_DATE"]).dt.days

    desfase = df["CONT_DOY"] - df["CONT_DATE"].dt.dayofyear
    real = df["CONT_DOY"] - 2 - df["doy"]
    corregir = (df["duracion_dias"] == 1) & desfase.between(1, 299) & (real >= 0)
    df["duracion_corregida"] = np.where(corregir, real, df["duracion_dias"])
    return df


@st.cache_data(show_spinner="Cargando incendios…")
def cargar_incendios() -> pd.DataFrame:
    con = conectar()
    try:
        df = con.execute(CONSULTA).df()
    finally:
        con.close()
    return preparar(df)