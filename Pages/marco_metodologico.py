import streamlit as st
import pandas as pd

def render():


    st.header ("Capítulo 3 (Marco Metodológico)")

    opcion_seleccionada = st.selectbox ("SELECCIONAR SECCIÓN", ["TIPO Y NIVEL DE LA INVESTIGACIÓN", "POBLACIÓN Y UNIDAD DE ANÁLISIS", "OPERACIONALIZACIÓN DE VARIABLES","PROCESAMIENTO DE LOS DATOS"])

    if opcion_seleccionada == "TIPO Y NIVEL DE LA INVESTIGACIÓN":
        st.subheader ("TIPO Y NIVEL DE LA INVESTIGACIÓN")
        st.write ("El presente estudio se enmarca en un enfoque cuantitativo, fundamentado en el procesamiento numérico y estadístico de registros masivos de incendios forestales.")
        st.write (" En cuanto a su nivel y diseño, la investigación es de carácter descriptivo y longitudinal retrospectivo. Es descriptiva porque busca especificar las características, tendencias y comportamientos de los incendios sin manipular deliberadamente las variables; y es longitudinal retrospectiva dado que analiza una ventana temporal histórica de 24 años (comprendida entre el 1 de enero de 1992 y el 31 de diciembre de 2015), permitiendo observar la evolución temporal, estacional y espacial de los eventos en los estados de California, Texas y Oregón.")

    if opcion_seleccionada == "POBLACIÓN Y UNIDAD DE ANÁLISIS":
        st.subheader ("POBLACIÓN Y UNIDAD DE ANÁLISIS")
        st.markdown ("a- Población: Está constituida por el conjunto total de registros de incendios forestales ocurridos en los Estados Unidos de América y recopilados en la base de datos oficial FPA_FOD_20170508 (Fire Program Analysis Fire-Occurrence Database), la cual abarca más de 1.88 millones de eventos a nivel nacional para el periodo 1992-2015.")
        st.markdown ("b- Unidad de Análisis: Se delimita específicamente a los registros correspondientes a los estados de California, Texas y Oregón. Por tratarse de un análisis censal de los registros oficiales disponibles en dichos estados dentro del periodo de estudio, no se requiere el cálculo de una muestra probabilística, procesando la totalidad de los eventos reportados para las tres entidades federativas seleccionadas.")


    if opcion_seleccionada == "OPERACIONALIZACIÓN DE VARIABLES":
        st.subheader("OPERACIONALIZACIÓN DE VARIABLES")
        st.write("A continuación se identifican y clasifican las variables claves contenidas en el modelo de datos construido, utilizadas para dar respuesta a las preguntas de investigación. Se detalla la operacionalización de las variables, especificando su definición, naturaleza estadística y su correspondencia técnica con los campos originales de la base de datos recopilada.")

        datos_variables = [
            {"Dimensión": "Temporalidad", "Variable/Indicador": "Año del incendio", "Naturaleza": "Cuantitativa discreta", "Campo en el Modelo": "FIRE_YEAR", "Medidas Aplicables": "Frecuencias absolutas"},
            {"Dimensión": "Temporalidad", "Variable/Indicador": "Fecha del descubrimiento del incendio", "Naturaleza": "Cuantitativa discreta", "Campo en el Modelo": "DISCOVERY_DATE", "Medidas Aplicables": "Frecuencias por mes/día "},
            {"Dimensión": "Temporalidad", "Variable/Indicador": "Fecha de contención del incendio", "Naturaleza": "Cuantitativa discreta", "Campo en el Modelo": "CONT_DATE", "Medidas Aplicables": "Frecuencias, media aritmética"},
            {"Dimensión": "Geografía", "Variable/Indicador": "Estado", "Naturaleza": "Cualitativa nominal", "Campo en el Modelo": "STATE", "Medidas Aplicables": "Frecuencias absolutas y relativas"},
            {"Dimensión": "Geografía", "Variable/Indicador": "Condado", "Naturaleza": "Cualitativa nominal", "Campo en el Modelo": "COUNTY", "Medidas Aplicables": "Frecuencias, moda, ranking "},
            {"Dimensión": "Geografía", "Variable/Indicador": "Latitud", "Naturaleza": "Cuantitativa continua", "Campo en el Modelo": "LATITUDE", "Medidas Aplicables": "Media, mínimo, máximo, rango"},
            {"Dimensión": "Geografía", "Variable/Indicador": "Longitud", "Naturaleza": "Cuantitativa continua", "Campo en el Modelo": "LONGITUDE", "Medidas Aplicables": "Media, mínimo, máximo, rango"},
            {"Dimensión": "Magnitud", "Variable/Indicador": "Acres quemados", "Naturaleza": "Cuantitativa continua", "Campo en el Modelo": "FIRE_SIZE", "Medidas Aplicables": "Media, mediana, desviación estándar, cuartiles"},
            {"Dimensión": "Magnitud", "Variable/Indicador": "Tamaño del incendio por letras", "Naturaleza": "Cualitativa ordinal", "Campo en el Modelo": "FIRE_SIZE_CLASS", "Medidas Aplicables": "Frecuencias y frecuencias acumuladas"},
            {"Dimensión": "Causa", "Variable/Indicador": "Causa de origen del incendio", "Naturaleza": "Cualitativa nominal", "Campo en el Modelo": "STAT_CAUSE_DESCR", "Medidas Aplicables": "Frecuencias absolutas y relativas"},
        ]

        df_variables = pd.DataFrame(datos_variables)
        st.dataframe(df_variables, hide_index=True, width="stretch")

    if opcion_seleccionada == "PROCESAMIENTO DE LOS DATOS":
        st.subheader("PROCESAMIENTO DE LOS DATOS")
        st.write(
            "El tratamiento de la información se llevó a cabo mediante el lenguaje SQL a través de la herramienta Dbeaver como una base de datos con formato sqlite que después fue convertida a un formato duckdb para su consumo en el aplicativo del streamlit y el dashboard, realizado en power bi para la visualización de los resultados. El proceso se realizó en las siguientes etapas:"
        )

        st.markdown("### Normalización")
        st.write(
            "Para la creación del modelo de datos se aplicó un proceso de normalización (hasta la Tercera Forma Normal o 3FN) sobre la tabla original denormalizada, la cual contenía 39 columnas y 1.8 millones de registros. El objetivo principal de esta etapa fue eliminar la redundancia de la información, optimizar el espacio de almacenamiento y garantizar la integridad de los datos antes de realizar el análisis estadístico."
        )
        st.write(
            "Como resultado de este proceso, la estructura se dividió en un esquema relacional compuesto por tres tablas: dos tablas categóricas y una tabla principal"
        )
        st.markdown(
            "- **Tabla de causas (`cause`):** Se extrajo el catálogo de las 13 causas de origen del incendio. Al aislar la descripción de la causa en su propia tabla, se evitó repetir cadenas de texto extensas (como \"Lightning\" o \"Debris Burning\") millones de veces en la tabla principal.\n"
            "- **Tabla de condados (`county`):** Se construyó un catálogo geográfico utilizando una llave primaria compuesta por el estado (`STATE`) y el identificador FIPS (`FIPS_CODE`), ya que este código no es único a nivel nacional por sí solo.\n"
            "- **Tabla principal (`fire_event`):** Es la tabla central del modelo y almacena los registros válidos. En ella se conservan las características propias de cada evento, como el tamaño del incendio, la ubicación geográfica (latitud y longitud), y las variables temporales (fecha y hora de descubrimiento y contención). Esta tabla se conecta con las dimensiones mediante llaves foráneas."
        )
        st.write(
            "Durante el diseño del nuevo esquema, también se realizó una selección de variables. Se descartaron las columnas de la tabla original que no aportaban información relevante para los objetivos del estudio como los identificadores de sistemas de reporte, datos de agencias específicas o nombres de complejos, también se descartó aquellas variables que presentaban una cantidad crítica de valores nulos. Al conservar únicamente las variables de interés (causas, ubicación, temporalidad y magnitud), se construyó un modelo más ligero, enfocado y eficiente para el análisis del estudio."
        )

        st.markdown("### Limpieza")
        st.write(
            "Una vez estructurada la base de datos, se procedió a la fase de limpieza y depuración de registros. En primer lugar, se evaluó la calidad de las variables temporales. Se identificó que un 47% de los datos originales carecía de la hora de descubrimiento del incendio. Dado que esta variable es fundamental para calcular la duración de los incendios y no fue posible imputar sin introducir un sesgo significativo en los resultados, se tomó la decisión metodológica de eliminar dichos registros incompletos."
        )
        st.write(
            "Para los registros restantes que tenían fecha de descubrimiento pero no fecha de contención se realizó una imputación calculando el promedio de duración de los incendios por el tamaño de clase de los mismos, para proceder a sumar dichos promedios a la hora de descubrimiento de los registros con fecha de contención faltante, para así imputar la fecha y día en que se contuvo el evento."
        )
        st.write(
            "Posteriormente, y en concordancia con los alcances de la investigación, se aplicó un filtro geográfico para conservar únicamente los incendios ocurridos en los estados de California, Texas y Oregón. Tras este proceso de depuración, la muestra final quedó constituida por un total de 167,215 registros válidos."
        )

        st.markdown("### Denormalización")
        st.write(
            "Tras finalizar el proceso de limpieza y normalización, se aplicó una estrategia de denormalización con el fin de optimizar el rendimiento en la manipulación de los datos. Esto consistió en consolidar la información clave de las tablas (`cause`), (`county`) y (`fire_event`) en un conjunto unificado para dar inicio a la siguiente etapa."
                )
        st.write(
            "El punto de partida de este proceso consistió en la definición formal del nivel de granularidad del modelo de datos. Se estableció que cada registro (fila) de la base de datos representa un evento individual e independiente de incendio forestal. A partir de esta unidad mínima de información, cada entidad queda caracterizada por un conjunto de atributos espacio-temporales y descriptivos clave, tales como la fecha y hora de inicio, la causa confirmada del siniestro, la ubicación geográfica exacta, la superficie afectada y los recursos desplegados para su atención. Esta granularidad atómica asegura la flexibilidad necesaria para realizar análisis detallados y posteriores agregaciones multidimensionales (por región, periodo de tiempo o tipo de causa) sin perder la trazabilidad de los datos originales."
                )
        st.write(
            "Como siguiente paso en la estructuración del modelo, se procedió a la creación de las tablas de dimensión. Estas tablas tienen como propósito almacenar los atributos descriptivos y cualitativos que otorgan contexto al análisis, permitiendo segmentar y filtrar los registros principales a partir de categorías clave."
        )
        st.markdown(
            "- **DIMENSIÓN: UBICACIÓN (`dim_location`):** Agrupa todos los datos de ubicación geográfica del incendio, como el estado, condado y código FIPS. Para evitar redundancia, se creó una clave primaria única para cada uno de los datos de la tabla."
        )
        st.write(
            "- **DIMENSIÓN: FECHA (`dim_date`):** Agrupa todos los componentes temporales del incendio, (año, mes, día, hora, información de contención, etc). Para crear la clave primaria de esta dimensión, se extrajeron los datos de la columna (`CONT_DATE`) (fecha de contención), juntando año, mes y día como tipo de dato (`TEXT`) para crear una clave primaria única para cada uno de los registros, evitando así los datos duplicados."
            )
        st.write(
            "- **DIMENSIÓN: CAUSA (`dim_cause`):** Agrupa los datos de la causa del incendio junto con su código, siendo este la clave primaria de la tabla."
        )
        st.write(
            "- **TABLA DE HECHOS (`fact_fires`):** Además de su clave primaria (`FOD_ID`), contiene información general de la base de datos, como sus fechas y horas de descubrimiento y contención, tamaño, clase y las claves foráneas hacia cada una de las dimensiones. "
        )
        st.write(
            "Finalmente se realiza un proceso de poblamiento de tablas, usando de base las tablas normalizadas para llevar los datos a las nuevas tablas creadas."
        )

    with st.container(border=True):
        st.image("https://images3.memedroid.com/images/UPLOADED947/669b46ef728e7.jpeg", use_container_width=True, caption="Chapu maltratado y sobreexplotado por no sacar la app.py de la carpeta streamlit", width=250)





