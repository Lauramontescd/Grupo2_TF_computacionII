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
    st.subheader("Pregunta 1: Variación de la Superficie Quemada en el Último Año")
    st.write(
        "Se quiere saber en qué estados creció más la superficie quemada en el último año "
        "de la base respecto del año anterior. Calcula por estado y año (FIRE_YEAR) la cantidad "
        "de incendios y la superficie quemada de los dos últimos años disponibles, sin escribir "
        "esos años en la consulta. Obtén ambos años en una misma fila cruzando ese resultado "
        "consigo mismo y calcula la variación porcentual de la superficie. Solo participan los "
        "estados con datos en los dos años."
    )
    st.write(
        "Muestra los estados cuya superficie del último año sea mayor o igual que la media de "
        "ese valor entre los estados participantes. Para cada uno indica su puesto según la "
        "variación (de mayor a menor), los incendios del último año, la superficie del año anterior, "
        "la del último año, la variación porcentual y el porcentaje que representa su superficie "
        "del último año sobre la de todos los estados participantes. Ordena por puesto."
    )

    default_sql_p1 = """
WITH resumen_anual AS (
    SELECT 
        STATE,
        FIRE_YEAR,
        COUNT(*) AS total_incendios,
        SUM(FIRE_SIZE) AS area_quemada
    FROM Fires
    WHERE FIRE_YEAR IN (
        SELECT DISTINCT FIRE_YEAR 
        FROM Fires 
        ORDER BY FIRE_YEAR DESC 
        LIMIT 2
    )
    GROUP BY STATE, FIRE_YEAR
),
metricas_comparadas AS (
    SELECT 
        act.STATE AS estado,
        act.total_incendios AS incendios_ultimo_anio,
        ant.area_quemada AS sup_anterior,
        act.area_quemada AS sup_actual,
        ((act.area_quemada - ant.area_quemada) / ant.area_quemada) * 100.0 AS cambio_pct,
        RANK() OVER (
            ORDER BY ((act.area_quemada - ant.area_quemada) / ant.area_quemada) DESC
        ) AS ranking,
        AVG(act.area_quemada) OVER () AS promedio_nacional,
        (act.area_quemada / SUM(act.area_quemada) OVER ()) * 100.0 AS aporte_total_pct
    FROM resumen_anual act
    INNER JOIN resumen_anual ant 
        ON act.STATE = ant.STATE 
        AND act.FIRE_YEAR = ant.FIRE_YEAR + 1
)
SELECT 
    ranking AS Puesto,
    estado AS Estado,
    incendios_ultimo_anio AS Incendios_Ultimo_Anio,
    ROUND(sup_anterior, 2) AS Superficie_Anio_Anterior,
    ROUND(sup_actual, 2) AS Superficie_Ultimo_Anio,
    ROUND(cambio_pct, 2) AS Variacion_Porcentual,
    ROUND(aporte_total_pct, 2) AS Porcentaje_Sobre_Total
FROM metricas_comparadas
WHERE sup_actual >= promedio_nacional
ORDER BY ranking ASC;
"""


    sql_query_p1 = st.text_area(
        "Consulta SQL",
        value=default_sql_p1,
        height=340,
        key="sql_p1",
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        execute_clicked_p1 = st.button("Ejecutar", type="primary", key="btn_exec_p1")
    with col2:
        if st.button("Limpiar caché", key="btn_clear_p1"):
            run_query.clear()
            st.toast("Caché de consultas limpiada")

    if "cuestionario_query_result_p1" not in st.session_state:
        st.session_state.cuestionario_query_result_p1 = None

    if execute_clicked_p1:
        clean_sql_p1 = sql_query_p1.strip()
        if not clean_sql_p1:
            st.warning("Escribe una consulta SQL antes de ejecutar.")
        else:
            try:
                sql_ejecutable_p1 = preparar_sql_duckdb(clean_sql_p1)
                with st.spinner("Ejecutando consulta..."):
                    st.session_state.cuestionario_query_result_p1 = run_query(sql_ejecutable_p1)
            except Exception as e:
                st.error(f"Error en la consulta: {e}")

    if st.session_state.cuestionario_query_result_p1 is not None:
        df_p1 = st.session_state.cuestionario_query_result_p1
        st.caption(f"Filas: {len(df_p1)} | Columnas: {len(df_p1.columns)}")
        st.dataframe(df_p1, width="stretch", hide_index=True)

    st.subheader("Pregunta 2: Pirámide de Clases de Tamaño")
    st.write("Los incendios se clasifican por tamaño en siete clases, de la A (los más pequeños) a la G (los más grandes). Se quiere ver cómo se reparten los incendios y la superficie entre ellas.")
    st.write("Para cada clase calcula la cantidad de incendios y la superficie quemada. Calcula también el porcentaje acumulado de incendios desde la clase más pequeña hasta esa clase, y el porcentaje de la superficie total que corresponde a esa clase y a todas las mayores; ambos porcentajes se calculan sobre el total de la base.")
    st.write("Agrega en cada fila la clase inmediatamente superior, obtenida cruzando el resultado consigo mismo, y cuántos incendios hay de la clase por cada incendio de la clase superior. La última clase debe aparecer con esos dos valores vacíos. Ordena por clase.")

    sql_p2 = st.text_area(
        "Consulta SQL - Pregunta 2",
        value="""WITH ResumenClases AS (
    SELECT 
        FIRE_SIZE_CLASS,
        COUNT(*) AS Cantidad_Incendios,
        SUM(FIRE_SIZE) AS Superficie_Quemada
    FROM Fires
    WHERE FIRE_SIZE_CLASS IS NOT NULL
    GROUP BY FIRE_SIZE_CLASS
),
Calculos AS (
    SELECT 
        FIRE_SIZE_CLASS,
        Cantidad_Incendios,
        Superficie_Quemada,
        CASE FIRE_SIZE_CLASS 
            WHEN 'A' THEN 1 WHEN 'B' THEN 2 WHEN 'C' THEN 3 WHEN 'D' THEN 4 
            WHEN 'E' THEN 5 WHEN 'F' THEN 6 WHEN 'G' THEN 7 
        END AS Orden,
        (Cantidad_Incendios * 100.0) / SUM(Cantidad_Incendios) OVER () AS Porcentaje_Incendios,
        (SUM(Cantidad_Incendios) OVER (ORDER BY FIRE_SIZE_CLASS ASC) * 100.0) / SUM(Cantidad_Incendios) OVER () AS Porcentaje_Acumulado_Incendios,
        (SUM(Superficie_Quemada) OVER (ORDER BY FIRE_SIZE_CLASS DESC) * 100.0) / SUM(Superficie_Quemada) OVER () AS Porcentaje_Superficie_Mayores
    FROM ResumenClases
)
SELECT 
    c.FIRE_SIZE_CLASS AS "Clase de Tamaño",
    c.Cantidad_Incendios AS "Cantidad de Incendios",
    ROUND(c.Porcentaje_Incendios, 2) AS "Porcentaje Incendios",
    ROUND(c.Porcentaje_Acumulado_Incendios, 2)  AS "Porcentaje Acumulado",
    ROUND(c.Porcentaje_Superficie_Mayores, 2)  AS "Porcentaje Superficie (Mayores)",
    c2.FIRE_SIZE_CLASS AS "Clase Superior",
    c2.Cantidad_Incendios AS "Incendios Clase Superior"
FROM Calculos c
LEFT JOIN Calculos c2 ON c2.Orden = c.Orden + 1
ORDER BY c.FIRE_SIZE_CLASS ASC;
""",
        height=320,
        key="sql_p2",
    )

    if st.button("Ejecutar", type="primary", key="btn_p2"):
        if not sql_p2.strip():
            st.warning("Escribe una consulta SQL antes de ejecutar.")
        else:
            try:
                sql_ejecutable_p2 = preparar_sql_duckdb(sql_p2.strip())
                with st.spinner("Ejecutando consulta..."):
                    df_p2 = run_query(sql_ejecutable_p2)
                st.caption(f"Filas: {len(df_p2)} | Columnas: {len(df_p2.columns)}")
                st.dataframe(df_p2, use_container_width=True)
            except Exception as e:
                st.error(f"Error en la consulta: {e}")

    st.divider()

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
    with st.container(border=True):
         st.image("https://i.pinimg.com/736x/f5/52/28/f55228345af8a36e75aa939ac16a0348.jpg", use_container_width=True, caption="Aziel, Juan y Laura con 0 horas de sueño", width=250)