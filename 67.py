import duckdb
import pandas as pd
import streamlit as st

st.set_page_config(page_title="MotherDuck + Streamlit", layout="wide")



@st.cache_resource
def get_connection() -> duckdb.DuckDBPyConnection:
    token = st.secrets["MOTHERDUCK_TOKEN"]
    db = st.secrets.get("MOTHERDUCK_DB", "my_db")
    # "md:" le indica a DuckDB que la base está en MotherDuck
    return duckdb.connect(f"md:{db}?motherduck_token={token}")


@st.cache_data(ttl=600)  # cachea resultados 10 minutos
def run_query(sql: str) -> pd.DataFrame:
    con = get_connection()
    return con.sql(sql).df()


# ---------------------------------------------------------------------------
# Interfaz
# ---------------------------------------------------------------------------
st.title("🦆 Explorador de MotherDuck")

try:
    con = get_connection()
    st.success("Conectado a MotherDuck")
except Exception as e:
    st.error(f"No se pudo conectar: {e}")
    st.stop()

# Listar tablas disponibles
tablas = run_query(
    """
    SELECT table_schema, table_name
    FROM information_schema.tables
    WHERE table_catalog = current_database()
    ORDER BY table_schema, table_name
    """
)

if tablas.empty:
    st.warning("La base de datos no tiene tablas.")
    st.stop()

tablas["completo"] = tablas["table_schema"] + "." + tablas["table_name"]

with st.sidebar:
    st.header("Tablas")
    tabla = st.selectbox("Elige una tabla", tablas["completo"])
    limite = st.slider("Filas a mostrar", 10, 5000, 100, step=10)

# Vista previa de la tabla seleccionada
st.subheader(f"Vista previa: `{tabla}`")
df = run_query(f"SELECT * FROM {tabla} LIMIT {limite}")
st.dataframe(df, use_container_width=True)

col1, col2 = st.columns(2)
col1.metric("Filas mostradas", len(df))
col2.metric(
    "Filas totales",
    int(run_query(f"SELECT COUNT(*) AS n FROM {tabla}")["n"].iloc[0]),
)

# Gráfico rápido con columnas numéricas
numericas = df.select_dtypes("number").columns.tolist()
if numericas:
    st.subheader("Gráfico rápido")
    y = st.multiselect("Columnas numéricas", numericas, default=numericas[:1])
    if y:
        st.line_chart(df[y])

# Consola SQL libre
st.subheader("Consulta SQL personalizada")
sql = st.text_area("Escribe tu consulta", f"SELECT * FROM {tabla} LIMIT 10")
if st.button("Ejecutar"):
    try:
        st.dataframe(run_query(sql), use_container_width=True)
    except Exception as e:
        st.error(f"Error en la consulta: {e}")