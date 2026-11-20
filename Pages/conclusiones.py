import streamlit as st

import indicators as ind
from data import cargar_incendios


def render():
    st.header("Conclusiones")
    st.write("Cifras resumen por estado, calculadas a partir de los datos. Cada columna es la pendiente de una "
             "regresión lineal sobre los años 1992–2015 (cambio por año), salvo las dos últimas.")
    resumen = ind.resumen_estados(cargar_incendios())
    resumen.index = resumen.index.map({"CA": "California", "OR": "Oregón", "TX": "Texas"})
    st.dataframe(resumen.round(2))
    st.caption("Redacta aquí las conclusiones de cada objetivo con estas cifras y las de la sección Análisis.")

    with st.container(border=True):
        st.image("https://i.pinimg.com/236x/1a/18/89/1a188994454f7da73f229f775cf8801a.jpg", use_container_width=True, caption="Como se sintieron los parciales del semestre", width=250)
