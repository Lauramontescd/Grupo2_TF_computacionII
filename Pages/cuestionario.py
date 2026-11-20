import re
import duckdb
import pandas as pd
import streamlit as st


@st.cache_resource
def get_connection() -> duckdb.DuckDBPyConnection:
    token = st.secrets["MOTHERDUCK_ORIGINAL"]
    db = st.secrets.get("MOTHERDUCK_OG", "my_db")

    return duckdb.connect(f"md:{db}?motherduck_token={token}")


@st.cache_data(ttl=600)
def run_query(sql: str) -> pd.DataFrame:
    con = get_connection()
    return con.sql(sql).df()


def preparar_sql_duckdb(sql: str) -> str:
    expresion_juliana = "(DATE '1970-01-01' + INTERVAL (DISCOVERY_DATE - 2440587.5) DAY)::DATE"
    return re.sub(
        r"\bdate\s*\(\s*DISCOVERY_DATE\s*\)",
        expresion_juliana,
        sql,
        flags=re.IGNORECASE,
    )


def render() -> None:
    st.title("CUESTIONARIO DE ANALISIS DE DATOS")

    st.subheader("Pregunta 3: Causas de Fin de Semana")
    st.write("Algunas causas de incendio están ligadas al ocio y deberían concentrarse en sábados y domingos. Se quiere comprobar con la fecha de descubrimiento.")
    st.write("Cuenta los incendios por causa y tipo de día (fin de semana o laborable) y obtén ambos tipos en  una misma fila cruzando ese resultado consigo mismo. Como hay cinco días laborables y dos de fin de semana, la comparación se hace con la razón diaria: incendios de fin de semana divididos entre dos, sobre incendios laborables divididos entre cinco.")
    st.write("Muestra solo las causas con al menos 20.000 incendios en total. Para cada una indica los incendios de cada tipo de día, el porcentaje ocurrido en fin de semana, la razón diaria, el porcentaje que representan sus  incendios entre las causas mostradas y su puesto según la razón diaria, de mayor a menor. Ordena por puesto.")
    
    default_sql = """WITH TotalesPorCausa AS (
        -- se calculan los incendios de fin de semana, laborables y total por causa
        SELECT 
            STAT_CAUSE_DESCR AS Causa,
            SUM(CASE WHEN strftime('%w', date(DISCOVERY_DATE)) IN ('0', '6') THEN 1 ELSE 0 END) AS Incendios_FDS,
            SUM(CASE WHEN strftime('%w', date(DISCOVERY_DATE)) NOT IN ('0', '6') THEN 1 ELSE 0 END) AS Incendios_Laborables,
            COUNT(*) AS Total_Incendios
        FROM fires
        WHERE DISCOVERY_DATE IS NOT NULL 
          AND STAT_CAUSE_DESCR IS NOT NULL
        GROUP BY STAT_CAUSE_DESCR
        HAVING COUNT(*) >= 20000
    ),
    CalculosBase AS (
        -- se calculan porcentajes individuales, razón diaria y total acumulado
        SELECT 
            Causa,
            Incendios_FDS,
            Incendios_Laborables,
            Total_Incendios,
            ROUND((Incendios_FDS * 100.0) / Total_Incendios, 2) AS Pct_FinDeSemana,
            ROUND((Incendios_FDS / 2.0) / (Incendios_Laborables / 5.0), 2) AS Razon_Diaria,
            SUM(Total_Incendios) OVER () AS Total_Grupo
        FROM TotalesPorCausa
    )
    SELECT 
        --  mayor a menor según razón diaria
        RANK() OVER (ORDER BY Razon_Diaria DESC) AS Puesto,
        Causa,
        Incendios_FDS,
        Incendios_Laborables,
        Total_Incendios,
        Pct_FinDeSemana,
        Razon_Diaria,
        -- Porcentaje de esta causa sobre el total del grupo filtrado (>= 20.000)
        ROUND((Total_Incendios * 100.0) / Total_Grupo, 2) AS Pct_Causas
    FROM CalculosBase
    ORDER BY Puesto ASC;"""

    sql_query = st.text_area(
        "Consulta SQL",
        value=default_sql,
        height=340,
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        execute_clicked = st.button("Ejecutar", type="primary")
    with col2:
        if st.button("Limpiar caché"):
            run_query.clear()
            st.toast("Caché de consultas limpiada")

    if "cuestionario_query_result" not in st.session_state:
        st.session_state.cuestionario_query_result = None

    if execute_clicked:
        clean_sql = sql_query.strip()
        if not clean_sql:
            st.warning("Escribe una consulta SQL antes de ejecutar.")
        else:
            try:
                sql_ejecutable = preparar_sql_duckdb(clean_sql)
                with st.spinner("Ejecutando consulta..."):
                    st.session_state.cuestionario_query_result = run_query(sql_ejecutable)
            except Exception as e:
                st.error(f"Error en la consulta: {e}")

    if st.session_state.cuestionario_query_result is not None:
        df = st.session_state.cuestionario_query_result
        st.caption(f"Filas: {len(df)} | Columnas: {len(df.columns)}")
        st.dataframe(df, use_container_width=True)