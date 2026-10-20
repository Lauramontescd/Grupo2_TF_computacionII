import streamlit as st 

st.html("<style>.stApp, .stApp * { color: white !important; background-color: #0E1117; font-family: Arial, sans-serif; }</style>")

st.title ("“Transformación y comportamiento de los incendios forestales en California, Texas y Oregon  (1992-2015).”")
st.header ("Capítulo 3 (Marco Metodológico)")

opcion_seleccionada = st.selectbox ("Seleccionar sección", ["Tipo y Nivel de la Investigación", "Población y Unidad de Análisis"])

if opcion_seleccionada == "Tipo y Nivel de la Investigación":
    st.subheader ("Tipo y Nivel de la Investigación")
    st.write ("El presente estudio se enmarca en un enfoque cuantitativo, fundamentado en el procesamiento numérico y estadístico de registros masivos de incendios forestales.")
    st.write (" En cuanto a su nivel y diseño, la investigación es de carácter descriptivo y longitudinal retrospectivo. Es descriptiva porque busca especificar las características, tendencias y comportamientos de los incendios sin manipular deliberadamente las variables; y es longitudinal retrospectiva dado que analiza una ventana temporal histórica de 24 años (comprendida entre el 1 de enero de 1992 y el 31 de diciembre de 2015), permitiendo observar la evolución temporal, estacional y espacial de los eventos en los estados de California, Texas y Oregón.")

if opcion_seleccionada == "Población y Unidad de Análisis":
    st.subheader ("Población y Unidad de Análisis")
    st.markdown ("a- oblación: Está constituida por el conjunto total de registros de incendios forestales ocurridos en los Estados Unidos de América y recopilados en la base de datos oficial FPA_FOD_20170508 (Fire Program Analysis Fire-Occurrence Database), la cual abarca más de 1.88 millones de eventos a nivel nacional para el periodo 1992-2015.")
    st.markdown ("b- Unidad de Análisis: Se delimita específicamente a los registros correspondientes a los estados de California, Texas y Oregón. Por tratarse de un análisis censal de los registros oficiales disponibles en dichos estados dentro del periodo de estudio, no se requiere el cálculo de una muestra probabilística, procesando la totalidad de los eventos reportados para las tres entidades federativas seleccionadas.")
    





