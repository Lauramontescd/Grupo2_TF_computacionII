import streamlit as st

import indicators as ind
from data import cargar_incendios


CONCLUSIONES_ESTADO = {
    "CA": {
        "nombre": "California",
        "graves": "956",
        "graves_delta": "307 → 335 por periodo",
        "desplazamiento": "193 km",
        "direccion": "hacia el noroeste",
        "duracion": "1,05 días",
        "mas_1_dia": "5,2 % > 1 día",
        "frecuencia": "+193,76 / año",
        "causa_principal": "66,7 % Humana",
        "texto": (
            "Entre 1992 y 2015 se registraron 110.217 incendios en California, de los cuales 956 fueron graves "
            "(1.000 acres o más). Al comparar el primer periodo (1992–1999) con el más reciente (2008–2015), los "
            "grandes incendios subieron de 307 a 335, el centro geográfico se desplazó 193 km hacia el noroeste y la "
            "superficie quemada casi se duplicó, pasando de 2,42 a 4,38 millones de acres. En cuanto a los tiempos de "
            "contención, la duración media fue de 1,05 días: mientras en los años noventa rondaba los 0,5 días, desde "
            "el año 2000 se estabilizó cerca de 1,0 día, con picos atípicos muy marcados en 1999 (3,6 días) y 2008 "
            "(más de 4,5 días). Además, la frecuencia anual mostró un fuerte crecimiento de 193,76 incendios por año, "
            "superando los 7.000 a 8.800 eventos anuales entre 2011 y 2015. Por su parte, la superficie quemada anual "
            "aumentó en promedio 17.869 acres por año, con temporadas severas recurrentes en 1999, 2003, 2007 y un "
            "máximo histórico en 2008 con más de 1,2 millones de acres. Finalmente, las causas humanas dominan tanto "
            "en cantidad (66,74 % de los casos) como en extensión (58,44 % del área), aunque los incendios provocados "
            "por rayos (21,87 %) alcanzan una severidad individual mucho mayor."
        ),
    },
    "OR": {
        "nombre": "Oregón",
        "graves": "585",
        "graves_delta": "143 → 232 por periodo",
        "desplazamiento": "55 km",
        "direccion": "hacia el sureste",
        "duracion": "1,68 días",
        "mas_1_dia": "15,0 % > 1 día",
        "frecuencia": "+14,07 / año",
        "causa_principal": "62,0 % Natural",
        "texto": (
            "Entre 1992 y 2015 se registraron 42.722 incendios en Oregón, incluyendo 585 incendios graves. A diferencia "
            "de California y Texas, el centro geográfico de sus focos graves se mantuvo muy estable, desplazándose "
            "apenas 55 km hacia el sureste; sin embargo, su magnitud creció de forma constante: los grandes incendios "
            "aumentaron de 143 a 232 y la superficie quemada más que se triplicó, pasando de 1,06 a 3,87 millones de "
            "acres. También presentó los tiempos de contención más largos de todo el estudio, con una media de 1,68 "
            "días y un 15,0 % de incendios que superaron una jornada de duración, destacando picos críticos en 2002 "
            "(cerca de 3,5 días), 2011 (2,8 días) y 2014 (más de 4,2 días). En cuanto a la frecuencia anual, el número "
            "de incendios se mantuvo prácticamente estable (+14,07 incendios por año), moviéndose de forma irregular "
            "entre 1.000 y 2.500 eventos anuales con un máximo cercano a 3.000 en 2014, mientras la superficie quemada "
            "anual creció 17.869 acres por año. Además, es el único estado donde las causas naturales (rayos) lideran "
            "ampliamente tanto en ocurrencia (62,02 % de los siniestros) como en impacto territorial, concentrando el "
            "85,87 % de toda la superficie quemada."
        ),
    },
    "TX": {
        "nombre": "Texas",
        "graves": "483",
        "graves_delta": "55 → 378 por periodo",
        "desplazamiento": "325 km",
        "direccion": "hacia el noroeste",
        "duracion": "0,58 días",
        "mas_1_dia": "7,1 % > 1 día",
        "frecuencia": "+59,07 / año",
        "causa_principal": "Predominio humano",
        "texto": (
            "Entre 1992 y 2015 se registraron 483 incendios graves en Texas, protagonizando la transformación espacial "
            "más drástica de los tres estados: en el último periodo (2008–2015), los grandes incendios se multiplicaron "
            "casi por siete (pasando de 55 a 378), la superficie quemada se disparó de 186.717 acres a más de 3,5 "
            "millones y su centro geográfico se desplazó 325 km hacia el noroeste. En relación con la duración, tuvo "
            "la extinción más rápida con una media de 0,58 días (y 7,1 % mayores a una jornada); tras alcanzar un pico "
            "en 2006 (cerca de 1,9 días) y repuntes entre 2008 y 2009, los tiempos volvieron a bajar y se estabilizaron "
            "por debajo de los 0,4 días desde 2010. Por otro lado, la frecuencia creció en promedio 59,07 incendios por "
            "año con un salto marcado desde 2009, alcanzando más de 3.500 eventos en 2011. La superficie quemada anual "
            "(+25.237 acres por año) no creció de forma uniforme, sino concentrada en episodios extremos de sequía como "
            "2006 (cerca de 1 millón de acres) y especialmente 2011, cuando se devastaron casi 3 millones de acres, con "
            "un claro predominio de las causas vinculadas a la actividad humana."
        ),
    },
}


def _resumen_por_estado(estado: str) -> None:
    datos = CONCLUSIONES_ESTADO[estado]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Incendios graves (Clase F+)", datos["graves"], datos["graves_delta"], delta_color="off")
    c2.metric("Desplazamiento del centro", datos["desplazamiento"], datos["direccion"], delta_color="off")
    c3.metric("Duración media", datos["duracion"], datos["mas_1_dia"], delta_color="off")
    c4.metric("Tendencia y origen", datos["frecuencia"], datos["causa_principal"], delta_color="off")
    st.info(datos["texto"])


def render() -> None:
    st.header("Conclusiones")

    st.subheader("Hallazgos por objetivo")
    st.markdown(
        "- **(Migración geográfica de los focos graves):** En los tres estados creció de forma "
        "notable la superficie quemada por incendios de 1.000 acres o más, aunque con comportamientos espaciales "
        "distintos. Mientras Oregón mantuvo sus focos concentrados en la misma región (desplazándose apenas 55 km "
        "hacia el sureste), California (193 km) y Texas (325 km) mostraron un claro corrimiento hacia el noroeste "
        "en el periodo 2008–2015, acompañado en Texas por un aumento casi siete veces mayor en la cantidad de eventos graves.\n"
        "- **(Duración y tiempos de contención):** La persistencia de los incendios responde a las "
        "características climáticas y forestales de cada estado. Oregón registró los tiempos más largos y una "
        "tendencia sostenida al aumento (1,68 días de media y 15,0 % mayores a un día), California se estabilizó "
        "alrededor de 1,0 día desde el año 2000 con picos extremos en 1999 y 2008, y Texas mantuvo la extinción "
        "más rápida (0,58 días), logrando reducir sus tiempos por debajo de 0,4 días a partir de 2010.\n"
        "- **(Frecuencia anual y estacionalidad):** California (+193,76 incendios/año) y Texas "
        "(+59,07 incendios/año) evidencian un crecimiento importante en el número de registros —impulsado en "
        "los últimos años tanto por una mayor actividad como por una mejor cobertura en el reporte horario—, "
        "mientras que Oregón conserva una frecuencia prácticamente estable (+14,07 incendios/año) sin tendencia "
        "creciente a largo plazo.\n"
        "- **(Tendencia de la superficie quemada):** El área devastada anualmente aumenta en los tres "
        "estados, pero bajo dos patrones diferentes: en California y Oregón (+17.869 acres/año) el daño se "
        "distribuye de forma recurrente y escalonada a través de varias temporadas severas (1999, 2003, 2007 y 2008), "
        "mientras que en Texas (+25.237 acres/año) el impacto se concentra en episodios puntuales de sequía extrema "
        "como 2006 y especialmente 2011.\n"
        "- **(Causas humanas frente a causas naturales):** El origen principal de los siniestros marca "
        "un fuerte contraste regional. En California (66,74 % de los casos y 58,44 % del área) y Texas predominan "
        "las igniciones provocadas por actividad humana, aunque los rayos generan incendios individuales más "
        "destructivos; en cambio, en Oregón las causas naturales lideran ampliamente con el 62,02 % de los eventos "
        "y el 85,87 % de toda la superficie quemada."
    )

    st.subheader("Resumen por estado")
    tab_ca, tab_or, tab_tx = st.tabs(["California", "Oregón", "Texas"])
    with tab_ca:
        _resumen_por_estado("CA")
    with tab_or:
        _resumen_por_estado("OR")
    with tab_tx:
        _resumen_por_estado("TX")

    st.subheader("Conclusión general")
    
    st.info("Entre 1992 y 2015, el problema de los incendios forestales en estos tres estados no creció solo porque haya más incendios, sino porque los incendios grandes son cada vez más fuertes y queman mucha más tierra. Ver hacia dónde se mueven los fuegos más graves, cuánto tiempo tardan en apagarse, qué tan seguido pasan y qué los provoca deja claro que cada estado necesita soluciones distintas: controlar los incendios causados por personas en California y Texas, y vigilar mejor los rayos y fuegos difíciles de apagar en Oregón.")

    with st.container(border=True):
        st.image("https://i.pinimg.com/236x/1a/18/89/1a188994454f7da73f229f775cf8801a.jpg", use_container_width=True, caption="Como se sintieron los parciales del semestre", width=250)
