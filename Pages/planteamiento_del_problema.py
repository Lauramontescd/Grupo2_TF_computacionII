import streamlit as st 

st.html("<style>.stApp, .stApp * { color: white !important; background-color: #0E1117; font-family: Arial, sans-serif; }</style>")


st.title ("“Transformación y comportamiento de los incendios forestales en California, Texas y Oregon  (1992-2015).”")
st.header ("Capítulo 1") 

opcion_seleccionada = st.selectbox ("selecciona una parte del trabajo", ["planteamiento del problema", "justificacion", "objetivos de investigación"])

if opcion_seleccionada == "planteamiento del problema":
    st.subheader ("planteamiento del problema")
    st.write ("A lo largo de los años, estudios previos han documentado que, entre 1992 y 2015, los incendios en Estados Unidos aumentaron de tamaño y sus temporadas se alargaron. No obstante, dichos estudios suelen concentrarse en análisis territoriales aislados, (3. A. L. Westerling, Extensión de las temporadas de incendios en el Oeste de EE. UU. “Westerling, A. L. (2016). Increasing western US forest wildfire activity: sensitivity to changes in the timing of spring. Philosophical Transactions of the Royal Society B: Biological Sciences, 371(1696), 20150178.”), dejando un vacío sobre el comportamiento específico a escala estatal. Apoyándose en los avances teóricos y empíricos de estos antecedentes, surge la necesidad de estudiar de manera dirigida la evolución del comportamiento del fuego dentro de California, Texas y Oregón, tres estados caracterizados por geografías, climas y realidades humanas particulares.")
    st.write ("Al procesar directamente la base de datos FPA_FOD_20170508, creada con anterioridad por la investigadora y ecóloga espacial del Servicio Forestal de los Estados Unidos (USDA Forest Service) Karen Short, y sus variables, se plantean las siguientes preguntas de investigación:")
    st.markdown ("1- ¿Cómo es la migración geográfica en los focos más graves de los incendios en los estados de California, Texas y Oregón entre 1992 y 2015?")
    st.markdown ("2- ¿Cuál es el cambio de la duración promedio de los incendios en California, Texas y Oregón entre 1992 y 2015?")
    st.markdown ("3-¿Cómo varía la frecuencia anual y/o estacional de los incendios?")
    st.markdown ("4- ¿Cuál es la tendencia de la duración promedio en el periodo 1992 y 2015 en los estados de California, Texas y Oregon?")
    st.markdown ("5- ¿Cuál es la severidad de los incendios dependiendo de su causa de origen?")

if opcion_seleccionada == "justificacion":
    st.subheader ("Justificación")
    st.write ("Los incendios forestales constituyen uno de los fenómenos de mayor impacto ambiental, económico y social en Estados Unidos. Cada año, millones de acres son afectados, con consecuencias que van desde la pérdida de biodiversidad y degradación del suelo. Esta investigación analiza  la evolución de dichos incendios entre el periodo de 1992 y 2015 el cual  ofrece una ventana de 24 años que permite observar cambios significativos en el comportamiento de los incendios en los estados de California, Texas y Oregón, tres estados seleccionados por criterios de representatividad geográfica, volumen de datos  y contraste en sus condiciones climáticas y de vegetación. A través de un enfoque descriptivo la investigación no busca comparar los estados entre sí, sino identificar tendencias temporales de cada uno, aportando evidencia que contribuya a la compresión del comportamiento histórico del fuego al ofrecer un panorama claro de cómo ha evolucionado el riesgo en cada región estudiada.")


if opcion_seleccionada == "objetivos de investigación":
    st.subheader ("objetivos de investigación")

if opcion_seleccionada == "objetivos de investigación":
    st.subheader ("objetivo general") 
    st.markdown ("**Objetivo general:** Analizar la evolución temporal y espacial de los incendios en los estados de California, Texas y Oregon de Estados Unidos  entre 1992 y 2015, evaluando cambios en la duración de temporadas de incendios, la duración promedio de los incendios, la migración geográfica de los focos más graves y el perfil del terreno afectado.")

if opcion_seleccionada == "objetivos de investigación":
    st.subheader ("objetivos especificos")
    st.markdown ("**Objetivos específicos:**")
    st.markdown ("1- Describir la migración geográfica de los incendios en los estados de California, Texas y Oregon en los focos más graves entre 1992 y 2015.")
    st.markdown ("2- Evaluar el cambio de la duración promedio de incendios en California, Texas y Oregón entre 1992 y 2015.")
    st.markdown ("3- Cuantificar la variación en la frecuencia anual y/o estacional de los incendios evaluando el alargamiento de la temporada.")
    st.markdown ("4- Analizar la tendencia de la duración promedio en el periodo 1992 y 2015 en los estados de California, Texas y Oregon.")
    st.markdown ("5- Determinar la severidad de los incendios dependiendo de su causa de origen natural o humano.")
