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
    st.subheader("Pregunta 4: Megaincendios simultáneos")
    st.write("Un megaincendio es un incendio de la clase de tamaño más alta (clase G, de 5.000 acres o más). Cuando varios se declaran casi a la vez en un mismo estado, los recursos de extinción se saturan.")
    st.write("Forma todas las parejas de megaincendios distintos del mismo estado cuyas fechas de descubrimiento difieran en tres días o menos. Cada pareja debe contarse una sola vez: el primer incendio es el descubierto antes y, si ambos se descubrieron el mismo día, el de menor identificador.")
    st.write("Para cada estado muestra la cantidad de parejas, la cantidad de megaincendios que tiene y los datos de la pareja de mayor superficie conjunta: nombre, fecha de descubrimiento y superficie de cada incendio, días entre ambos y superficie conjunta. Si un incendio no tiene nombre, indícalo con el texto '(sin nombre)'. Muestra los diez estados con más parejas, de mayor a menor.")

    default_sql_p4 = """WITH megaincendios AS (

    SELECT
        FOD_ID,
        STATE                                                     AS estado,
        COALESCE(NULLIF(TRIM(FIRE_NAME), ''), '(sin nombre)')     AS nombre,
        date(DISCOVERY_DATE)                                      AS fecha_descubrimiento,
        CAST(julian(date(DISCOVERY_DATE)) + 0.5 AS INTEGER)    AS dia_juliano,
        FIRE_SIZE                                                 AS superficie,
        COUNT(*) OVER (PARTITION BY STATE)                        AS cantidad_megaincendios
    FROM Fires
    WHERE FIRE_SIZE_CLASS = 'G'
),
parejas AS (

    SELECT
        a.estado,
        a.cantidad_megaincendios,
        a.FOD_ID                            AS id_a,
        b.FOD_ID                            AS id_b,
        a.nombre                            AS nombre_a,
        a.fecha_descubrimiento              AS fecha_a,
        a.superficie                        AS superficie_a,
        b.nombre                            AS nombre_b,
        b.fecha_descubrimiento              AS fecha_b,
        b.superficie                        AS superficie_b,
        b.dia_juliano - a.dia_juliano       AS dias_entre_ambos,
        a.superficie + b.superficie         AS superficie_conjunta
    FROM megaincendios AS a
    JOIN megaincendios AS b
      ON  b.estado = a.estado
      AND b.dia_juliano BETWEEN a.dia_juliano AND a.dia_juliano + 3
      AND (b.dia_juliano > a.dia_juliano OR b.FOD_ID > a.FOD_ID)
),
ranking AS (

    SELECT
        parejas.*,
        COUNT(*)     OVER (PARTITION BY estado)                                  AS cantidad_parejas,
        ROW_NUMBER() OVER (PARTITION BY estado
                           ORDER BY superficie_conjunta DESC, id_a, id_b)        AS posicion
    FROM parejas
)
SELECT
    estado                    AS "Estado",
    cantidad_parejas          AS "Cantidad de parejas",
    cantidad_megaincendios    AS "Cantidad de megaincendios",
    nombre_a                  AS "Nombre del primer incendio",
    fecha_a                   AS "Fecha de descubrimiento del primero",
    superficie_a              AS "Superficie del primero (acres)",
    nombre_b                  AS "Nombre del segundo incendio",
    fecha_b                   AS "Fecha de descubrimiento del segundo",
    superficie_b              AS "Superficie del segundo (acres)",
    dias_entre_ambos          AS "Días entre ambos",
    superficie_conjunta       AS "Superficie conjunta (acres)"
FROM ranking
WHERE posicion = 1
  AND estado IN (
        SELECT estado
        FROM ranking
        WHERE posicion = 1
        ORDER BY cantidad_parejas DESC, estado
        LIMIT 10)
ORDER BY cantidad_parejas DESC, estado;"""
    
    sql_query_p4 = st.text_area(
            "Consulta SQL",
            value=default_sql_p4,
            height=340,
            key="sql_p4",
        )
    
    col1, col2 = st.columns([1, 5])
    with col1:
            execute_clicked_p4 = st.button("Ejecutar", type="primary", key="btn_exec_p4")
    with col2:
            if st.button("Limpiar caché", key="btn_clear_p4"):
                run_query.clear()
                st.toast("Caché de consultas limpiada")
    
    if "cuestionario_query_result_p4" not in st.session_state:
            st.session_state.cuestionario_query_result_p4 = None
    
    if execute_clicked_p4:
            clean_sql_p4 = sql_query_p4.strip()
            if not clean_sql_p4:
                st.warning("Escribe una consulta SQL antes de ejecutar.")
            else:
                try:
                    sql_ejecutable_p4 = preparar_sql_duckdb(clean_sql_p4)
                    with st.spinner("Ejecutando consulta..."):
                        st.session_state.cuestionario_query_result_p4 = run_query(sql_ejecutable_p4)
                except Exception as e:
                    st.error(f"Error en la consulta: {e}")

    if st.session_state.cuestionario_query_result_p4 is not None:
            df_p4 = st.session_state.cuestionario_query_result_p4
            st.caption(f"Filas: {len(df_p4)} | Columnas: {len(df_p4.columns)}")
            st.dataframe(df_p4, use_container_width=True, hide_index=True)

    st.subheader("Pregunta 5: Trimestre Crítico de Cada Estado")
    st.write("La temporada de incendios no es igual en todos los estados, y puede cruzar el fin de año (por ejemplo, de diciembre a febrero).")
    st.write("Suma los incendios de todos los años por estado y mes de la fecha de descubrimiento. Considera el año como circular: hay doce ventanas posibles de tres meses consecutivos, identificadas por su mes de inicio, y las que empiezan en noviembre y diciembre continúan en enero y febrero. Para cada estado encuentra la ventana con más incendios; si dos empatan, la de menor mes de inicio.")
    st.write("Incluye solo los estados con incendios en los doce meses y cuyo total de incendios sea mayor o igual que la media de los totales por estado. Muestra el total de incendios del estado, el mes de inicio y el mes de fin de la ventana, los incendios de la ventana, el porcentaje que representan sobre el total del estado, si la ventana cruza el fin de año ('si' o 'no') y el puesto del estado según ese porcentaje, de mayor a menor. Ordena por ese puesto.")

    default_sql_p5 = """WITH ventanas_por_estado AS (
    SELECT
        m1.STATE AS estado,
        totales.total_estado AS total_incendios,
        m1.mes AS mes_inicio,
        m3.mes AS mes_fin,
        (m1.cant + m2.cant + m3.cant) AS suma_3_meses,
        CASE
            WHEN m1.mes IN (11, 12) THEN 'si'
            ELSE 'no'
        END AS cruza_anio,
        (m1.cant + m2.cant + m3.cant) * 100.0 / totales.total_estado AS pct_total
    FROM (
        SELECT
            STATE,
            CAST(strftime(date(DISCOVERY_DATE), '%m') AS INT) AS mes,
            COUNT(*) AS cant
        FROM Fires
        WHERE DISCOVERY_DATE IS NOT NULL
          AND STATE IS NOT NULL
        GROUP BY STATE, mes
    ) m1
    INNER JOIN (
        SELECT
            STATE,
            CAST(strftime(date(DISCOVERY_DATE), '%m') AS INT) AS mes,
            COUNT(*) AS cant
        FROM Fires
        WHERE DISCOVERY_DATE IS NOT NULL
          AND STATE IS NOT NULL
        GROUP BY STATE, mes
    ) m2
        ON m1.STATE = m2.STATE
        AND m2.mes = CASE WHEN m1.mes = 12 THEN 1 ELSE m1.mes + 1 END
    INNER JOIN (
        SELECT
            STATE,
            CAST(strftime(date(DISCOVERY_DATE), '%m') AS INT) AS mes,
            COUNT(*) AS cant
        FROM Fires
        WHERE DISCOVERY_DATE IS NOT NULL
          AND STATE IS NOT NULL
        GROUP BY STATE, mes
    ) m3
        ON m1.STATE = m3.STATE
        AND m3.mes = CASE
            WHEN m1.mes = 11 THEN 1
            WHEN m1.mes = 12 THEN 2
            ELSE m1.mes + 2
        END
    INNER JOIN (
        SELECT
            STATE,
            COUNT(*) AS total_estado,
            COUNT(DISTINCT CAST(strftime(date(DISCOVERY_DATE), '%m') AS INT)) AS meses_activos
        FROM Fires
        WHERE DISCOVERY_DATE IS NOT NULL
          AND STATE IS NOT NULL
        GROUP BY STATE
        HAVING meses_activos = 12
    ) totales
        ON m1.STATE = totales.STATE
    WHERE totales.total_estado >= (
        SELECT AVG(conteo)
        FROM (
            SELECT COUNT(*) AS conteo
            FROM Fires
            WHERE STATE IS NOT NULL
            GROUP BY STATE
        )
    )
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY m1.STATE
        ORDER BY (m1.cant + m2.cant + m3.cant) DESC, m1.mes ASC
    ) = 1
)
SELECT
    RANK() OVER (ORDER BY pct_total DESC) AS "Puesto",
    estado AS "Estado",
    total_incendios AS "Total de Incendios",
    mes_inicio AS "Mes de Inicio",
    mes_fin AS "Mes de Fin",
    suma_3_meses AS "Incendios de la Ventana",
    ROUND(pct_total, 2) AS "Porcentaje sobre el Total (%)",
    cruza_anio AS "Cruza Fin de Año"
FROM ventanas_por_estado
ORDER BY "Puesto" ASC, "Estado" ASC;"""

    sql_query_p5 = st.text_area(
        "Consulta SQL",
        value=default_sql_p5,
        height=340,
        key="sql_p5",
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        execute_clicked_p5 = st.button("Ejecutar", type="primary", key="btn_exec_p5")
    with col2:
        if st.button("Limpiar caché", key="btn_clear_p5"):
            run_query.clear()
            st.toast("Caché de consultas limpiada")

    if "cuestionario_query_result_p5" not in st.session_state:
        st.session_state.cuestionario_query_result_p5 = None

    if execute_clicked_p5:
        clean_sql_p5 = sql_query_p5.strip()
        if not clean_sql_p5:
            st.warning("Escribe una consulta SQL antes de ejecutar.")
        else:
            try:
                sql_ejecutable_p5 = preparar_sql_duckdb(clean_sql_p5)
                with st.spinner("Ejecutando consulta..."):
                    st.session_state.cuestionario_query_result_p5 = run_query(sql_ejecutable_p5)
            except Exception as e:
                st.error(f"Error en la consulta: {e}")

    if st.session_state.cuestionario_query_result_p5 is not None:
        df_p5 = st.session_state.cuestionario_query_result_p5
        st.caption(f"Filas: {len(df_p5)} | Columnas: {len(df_p5.columns)}")
        st.dataframe(df_p5, use_container_width=True, hide_index=True)

    with st.container(border=True):
         st.image("https://i.pinimg.com/736x/f5/52/28/f55228345af8a36e75aa939ac16a0348.jpg", use_container_width=True, caption="Aziel, Juan y Laura con 0 horas de sueño", width=250)

    