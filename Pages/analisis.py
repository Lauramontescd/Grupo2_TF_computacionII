import duckdb
from duckdb import df
import streamlit as st
import numpy as np
import pandas as pd

import indicators as ind
from data import NOMBRES_ESTADO, cargar_incendios

@st.cache_resource
def get_connection() -> duckdb.DuckDBPyConnection:
    token = st.secrets["MOTHERDUCK_TOKEN"]
    db = st.secrets.get("MOTHERDUCK_DB", "NOR_BD")
   
    return duckdb.connect(f"md:{db}?motherduck_token={token}")


@st.cache_data(ttl=600)  
def run_query(sql: str) -> pd.DataFrame:
    con = get_connection()
    return con.sql(sql).df()

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

        st.markdown(" ### Análisis de resultados")

        Analisis_objetivo1 = {
            "CA": "Entre 1992 y 2015 se registraron 956 incendios graves (de 1.000 acres o más) en California. Al comparar el primer periodo (1992–1999) con el más reciente (2008–2015), el centro geográfico de estos focos se desplazó 193 km hacia el noroeste. Además, el impacto creció notablemente: los grandes incendios aumentaron de 307 a 335 y la superficie quemada casi se duplicó, pasando de 2,42 a 4,38 millones de acres.",
            "OR": "Entre 1992 y 2015 se registraron 585 incendios graves (de 1.000 acres o más) en Oregón. Al comparar el primer periodo (1992–1999) con el más reciente (2008–2015), el centro geográfico de estos focos se desplazó apenas 55 km hacia el sureste, manteniendo una ubicación muy estable. Sin embargo, su magnitud creció de forma constante: los grandes incendios aumentaron de 143 a 232 y la superficie quemada más que se triplicó, pasando de 1,06 a 3,87 millones de acres.",
            "TX": "Entre 1992 y 2015 se registraron 483 incendios graves (de 1.000 acres o más) en Texas. Al comparar el primer periodo (1992–1999) con el más reciente (2008–2015), el centro geográfico de estos focos se desplazó 325 km hacia el noroeste. Además, el impacto creció de forma drástica en el último periodo: los grandes incendios se multiplicaron casi por siete, pasando de 55 a 378, y la superficie quemada se disparó de 186.717 acres a más de 3,5 millones de acres.",
        } 

        st.info(Analisis_objetivo1.get(estado, "Análisis en proceso"))


def _objetivo2(df: pd.DataFrame, estado: str) -> None:
    st.subheader("Cambio de la duración promedio de los incendios")
    usar = st.checkbox("Usar la duración corregida (recomendado)", value=True, key=f"corr_{estado}",
                       help="En ~20.000 incendios multi-día la limpieza reemplazó la fecha de contención por "
                            "«descubrimiento + 1 día». La columna CONT_DOY conserva el dato original y permite recuperarlo.")
    columna = "duracion_corregida" if usar else "duracion_dias"
    d = ind.duracion_anual(df, estado, columna)
    serie = df.loc[df["estado"] == estado, columna]
    c1, c2 = st.columns(2)
    c1.metric("Duración media (días)", f"{serie.mean():.2f}")
    c2.metric("Duran más de 1 día", f"{(serie > 1).mean() * 100:.1f} %")
    st.line_chart(d[["media_dias"]])
    st.write(_frase(ind.tendencia(d.index, d["media_dias"]), "la duración media", "días"))
    st.caption("La duración se mide en días completos entre la fecha de descubrimiento y la de contención. "
               "La distribución tiene cola larga, por eso se reporta también el percentil 90.")
    st.dataframe(d.round(2))


    Analisis_objetivo2 = {
        "CA": "Entre 1992 y 2015, los incendios registrados en California tuvieron una duración media de 1,05 días, y solo el 5,2 % logró extenderse por más de una jornada. Al observar la evolución anual del promedio, se evidencia una aumento leve, sin tendencia lineal clara respecto a los 1990’s (donde el promedio rondaba los 0,5 días), pasando a estabilizarse cerca de 1,0 día a partir del año 2000. Además, destacan dos picos atípicos muy marcados en 1999 (alrededor de 3,6 días) y 2008 (cerca de 4,4 días), 1999 es un efecto de 4 valores extremos y 2008 un año de incendios largos y difíciles de contener.",
        "OR": "Entre 1992 y 2015, los incendios registrados en Oregón presentaron una duración media de 1,68 días, y un 15,0 % logró extenderse por más de una jornada, triplicando la proporción observada en California. Al observar la evolución anual, se aprecia una clara tendencia creciente: mientras en los años noventa el promedio se mantenía por debajo de 1,5 días, a partir del año 2000 los tiempos de contención aumentaron de forma irregular pero creciente. Destacan especialmente tres picos críticos en 2002 (cerca de 3,5 días), 2011 (alrededor de 2,8 días) y 2014 (superando los 4,2 días), reflejando incendios forestales cada vez más persistentes.",
        "TX": "Entre 1992 y 2015, los incendios registrados en Texas tuvieron una duración media de 0,58 días, siendo los de más rápida extinción entre los tres estados analizados, aunque un 7,1 % logró superar el día de duración. Al observar la evolución anual, se distingue un crecimiento gradual desde los años noventa (con promedios menores a 0,5 días) hasta alcanzar un máximo pronunciado en 2006 (cerca de 1,9 días) y otros repuntes entre 2008 y 2009 (alrededor de 1,1 días). Sin embargo, desde 2012 los tiempos de contención volvieron a descender y se estabilizaron por debajo de los 0,4 días.",
    }

    st.info(Analisis_objetivo2.get(estado, "Análisis en proceso"))


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

     st.markdown("### Análisis de resultados")
     
     Analisis_objetivo3 = {
         
             "CA": "Entre 1992 y 2015, el número de incendios registrados en California muestra una tendencia clara al crecimiento, aumentando en promedio 193,76 incendios por año (R² = 0,56; correlación de Spearman = 0,73). Al observar la evolución anual en el gráfico de barras, se distingue un salto notable a partir de 2011: mientras que entre 1992 y 2010 los registros solían mantenerse entre los 2.500 y 5.000 eventos anuales, en el tramo final (2011–2015) superaron frecuentemente los 7.000 a 8.800 incendios al año, reflejando tanto una mayor actividad como una posiblemente mejor cobertura en el registro horario reciente.",
             "OR": "Entre 1992 y 2015, el número de incendios registrados en Oregón muestra una tendencia prácticamente estable, con un leve aumento promedio de apenas 14,07 incendios por año (R² = 0,04; correlación de Spearman = 0,14). Al observar el gráfico de barras, se aprecia que la frecuencia anual permanece de forma irregular sin un crecimiento sostenido a largo plazo, moviéndose habitualmente entre los 1.000 y 2.500 eventos por año. Solo destacan repuntes puntuales al inicio de la serie en 1992 (más de 2.600 registros) y en los años finales de 2013 a 2015, alcanzando su máximo histórico en 2014 con cerca de 3.000 incendios.",
             "TX": "Entre 1992 y 2015, el número de incendios registrados en Texas presenta una tendencia creciente de 59,07 incendios por año (R² = 0,32; correlación de Spearman = 0,83). Sin embargo, el gráfico de barras muestra un cambio en la captura de datos a partir de 2009: mientras entre 1992 y 2008 los registros anuales casi nunca superaban los 500 eventos, 2009–2011 supera los 1.300; después, entre 600 y 1.000, alcanzando un pico extraordinario en 2011 con más de 3.500 incendios (coincidiendo con una sequía histórica y una posiblemente mayor cobertura de reporte horario).",
         }
     
     st.info(Analisis_objetivo3.get(estado, "Análisis en proceso"))
     

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

     st.header("ANÁLISIS DE RESULTADOS")
          
     Analisis_objetivo4 = {
         
             "CA": "Entre 1992 y 2015, la superficie quemada anual en California muestra una tendencia creciente, aumentando en promedio 17.869 acres por año (R² = 0,16; correlación de Spearman = 0,34). A diferencia de Texas donde un solo año concentra casi todo el daño, en California se observa una actividad destructiva recurrente y escalonada: destacan temporadas muy severas en 1999 (cerca de 750.000 acres), 2003 (casi 960.000 acres), 2007 (superando el millón de acres) y un máximo histórico en 2008 con más de 1,2 millones de acres quemados, manteniéndose en niveles altos entre 2012 y 2015.",
             "OR": "Entre 1992 y 2015, la superficie quemada anual en Oregón muestra una tendencia creciente, aumentando en promedio 17.869 acres por año (R² = 0,16; correlación de Spearman = 0,34). A diferencia de otros estados donde un solo año domina todo el registro, en Oregón se observa una actividad destructiva recurrente y escalonada: destacan temporadas muy severas en 1999 (cerca de 750.000 acres), 2003 (casi 960.000 acres), 2007 (superando el millón de acres) y un máximo histórico en 2008 con más de 1,2 millones de acres quemados, manteniéndose en niveles altos entre 2012 y 2015.",
             "TX": "Entre 1992 y 2015, la superficie quemada anual en Texas presenta un aumento promedio de 25.237 acres por año (R² = 0,09; correlación de Spearman = 0,51). El bajo valor de R² demuestra que el daño no crece de forma uniforme, sino concentrado en episodios extremos de sequía: mientras que en la mayoría de los años la superficie afectada fue mínima, destacan dos eventos catastróficos en 2006 (cerca de 1 millón de acres) y especialmente en 2011, año que concentra la mayor devastación del periodo con casi 3 millones de acres quemados.",
        }
          
     st.info(Analisis_objetivo4.get(estado, "Análisis en proceso"))



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

    st.header("ANÁLISIS DE RESULTADOS")
         
    Analisis_objetivo5 = {
             
            "CA": "Entre 1992 y 2015, de los 110.217 incendios registrados en California, las causas humanas dominan tanto en frecuencia como en extensión total, representando el 66,74% de los eventos (73.561 incendios) y el 58,44% de la superficie quemada (6.716.612,27 acres). Sin embargo, las causas naturales muestran una severidad individual notablemente mayor: aunque solo equivalen al 21,87% de los siniestros (24.100 incendios), concentran el 34,73% del área afectada (3.991.232,10 acres), lo que evidencia que los incendios originados por rayos tienden a alcanzar una magnitud promedio mucho más destructiva que los provocados por actividad humana, mientras que las causas sin determinar aportan el 11,39% de los casos y el 6,83% de los acres quemados.",
            "OR": "A diferencia de los otros estados analizados, en Oregón (42.722 incendios registrados entre 1992 y 2015) las causas naturales lideran ampliamente tanto en ocurrencia como en impacto territorial. Los incendios originados por rayos representan el 62,02% del total de eventos (26.496 incendios) y son responsables del 85,87% de toda la superficie quemada (7.049.636 acres), lo que demuestra una severidad extrema por evento. En contraste, aunque las causas humanas generan el 36,10% de los focos (15.422 incendios), apenas explican el 13,52% del área devastada (1.110.284,37 acres), mientras que los siniestros de origen sin determinar tienen una incidencia marginal con el 1,88% de los casos y el 0,60% de la superficie afectada.",
            "TX": "En Texas (14.276 incendios registrados entre 1992 y 2015), se observa la mayor preponderancia de la actividad humana como detonante de incendios forestales, concentrando el 82,85% de los eventos (11.827 incendios) y el 60,87% de la superficie total quemada (3.219.032,86 acres). No obstante, al evaluar la severidad relativa, tanto los incendios naturales como los de causa sin determinar presentan un impacto desproporcionado respecto a su frecuencia: las causas naturales representan apenas el 13,14% de los siniestros (1.876 incendios) pero abarcan el 23,77% de los acres quemados (1.257.202,87 acres), mientras que los eventos sin determinar, con solo el 4,01% de los casos (573 incendios), explican el 15,35% de la superficie afectada (811.706,81 acres), evidenciando una alta extensión promedio en estos dos últimos grupos.",
            }
         
    st.info(Analisis_objetivo5.get(estado, "Análisis en proceso"))
              
    

def render() -> None:
    st.header("ANÁLISIS DE RESULTADOS")
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

    with st.container(border=True):
        st.image("https://content.imageresizer.com/images/memes/House-On-Fire-meme-7.jpg", use_container_width=True, caption="La casa de Oliver misteriosamente después de las 6:00PM", width=250)
