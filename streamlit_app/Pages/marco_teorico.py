import streamlit as st

def render():


    st.header ("Capítulo 2 (Marco Teórico)") 

    opcion_seleccionada = st.selectbox ("SELECCIONAR SECCIÓN", ["ANTECEDENTES", "BASES TEÓRICAS", "MÉTODOS ESTADÍSTICOS"])

    if opcion_seleccionada == "ANTECEDENTES":
        st.subheader ("ANTECEDENTES")
        st.write ("La base de datos utilizada en esta investigación, FPA_FOD_20170508, fue desarrollada por Short (2014) como una base espacial de incendios ocurridos en Estados Unidos. Integra los registros de reporte de incendios de agencias federales, estatales y locales en un formato homogéneo. La versión empleada en este trabajo corresponde a la actualización publicada por Short (2017), que abarca el periodo 1992-2015 e incluye aproximadamente 1,88 millones de registros con información sobre la fecha de descubrimiento, la fecha de contención, la causa, el tamaño, el estado y las coordenadas geográficas de cada incendio. Esta base se ha convertido en una de las fuentes de referencia para estudiar el comportamiento histórico del fuego en el país, lo que sustenta su uso en el presente estudio.")
   
        st.subheader ("Antecedentes a escala nacional y del oeste de Estados Unidos")
        st.write ("Diversos estudios han documentado un aumento de la actividad de incendios en las últimas décadas. Westerling et al. (2006) encontraron que, desde mediados de los años ochenta, aumentó de forma marcada la frecuencia de grandes incendios forestales en el oeste de Estados Unidos, junto con un alargamiento de la temporada y de la duración de los incendios grandes. Lo asociaron al calentamiento y al deshielo temprano de primavera. De manera consistente, Dennison et al. (2014) analizaron el periodo 1984-2011 y reportaron aumentos significativos en el número y la superficie de los grandes incendios en gran parte del oeste del país.")
        st.write ("En una escala más amplia, Jolly et al. (2015) evidenciaron que la duración de la temporada de clima propicio para incendios se alargó en una proporción considerable de la superficie terrestre entre 1979 y 2013, incluido el oeste de Estados Unidos. Por su parte, Abatzoglou y Williams (2016) atribuyeron parte del aumento del área quemada en los bosques del oeste a la mayor aridez del combustible asociada al cambio climático de origen antropogénico.")

        st.subheader ("Antecedentes sobre las causas humanas y naturales")
        st.write ("Balch et al. (2017) utilizaron la misma base de datos empleada en este trabajo (FPA-FOD) y concluyeron que la gran mayoría de los incendios en Estados Unidos son iniciados por personas, que esto amplía el periodo del año en que ocurren incendios y que la distribución de las causas varía entre regiones. Este antecedente es el más cercano a la presente investigación, pues relaciona el comportamiento del fuego con su origen humano o natural, aspecto que se aborda en el objetivo sobre severidad según la causa.")

        st.subheader ("Antecedentes por estado")
        st.markdown ("**Antecedentes por estado:**")
        st.markdown ("1- California: Syphard et al. (2007) analizaron la influencia humana en los regímenes de fuego de California y mostraron que factores como la densidad poblacional y el desarrollo urbano inciden en la frecuencia de los incendios. Keeley y Syphard (2019) distinguieron entre incendios dominados por el combustible, característicos del norte del estado, e incendios dominados por el viento, asociados a los vientos de Santa Ana en el sur. Williams et al. (2019) vincularon el aumento del área quemada en verano en California con el calentamiento observado.")
        st.markdown ("2- Oregón: Reilly et al. (2017) estudiaron los patrones de extensión y severidad del fuego en los bosques del noroeste del Pacífico entre 1985 y 2010, y señalaron la influencia de la sequía y de los rayos como factores relevantes en la región.")
        st.markdown ("3- Texas: En ausencia de estudios, puede redactarse así: en la literatura revisada no se identificaron análisis que describan la evolución temporal del fuego en Texas con los mismos indicadores aplicados a otros estados, lo que refuerza la necesidad de estudiarlo.")

        st.subheader ("Vacío de investigación")
        st.write ("Los antecedentes revisados muestran que existe evidencia sólida de un aumento en el tamaño de los incendios y de un alargamiento de las temporadas, pero se concentran principalmente en promedios nacionales, en el oeste del país o en análisis regionales aislados. Son escasos los trabajos que describan, estado por estado, la evolución de la duración de las temporadas, de la duración de los incendios, de la ubicación de los focos más graves y de la severidad según el origen del fuego. Este vacío justifica el estudio de California, Texas y Oregón entre 1992 y 2015, con los datos de FPA_FOD_20170508.")

    if opcion_seleccionada == "BASES TEÓRICAS":
        st.subheader ("BASES TEÓRICAS")
        st.write ("En este capítulo se desarrollan los conceptos y fundamentos estadísticos para realizar el análisis necesario para cubrir los objetivos planteados anteriormente. Se abordarán conceptos como que es incendio, como se ocasiona y las medidas fundamentales para la estadística descriptiva.")
        st.write ("Estos conceptos son necesarios para comprender la metodología y resultados de análisis de estudio y asociarlo a los incendios de la investigación.")

        st.subheader ("¿Que es un incendio? ")
        st.write ("Un incendio es un fuego grande que se propaga de forma descontrolada, destruyendo materiales, estructuras o terrenos naturales que no estaban destinados a quemarse.")

        st.subheader (" Patrón  de incendios")
        st.write ("Es el patrón histórico, cíclico y característico en el que ocurren los incendios en un ecosistema determinado a lo largo del tiempo.")
        st.write ("En lugar de analizar un incendio individual, esto describe cómo se comporta el fuego típicamente en una región durante décadas o siglos. Sus principales características son:")
        st.markdown ("a- Frecuencia: Cada cuánto tiempo se quema una zona (intervalo de retorno del fuego).")
        st.markdown ("b- Estacionalidad: es la variación regular y predecible que experimenta una variable a lo largo de periodos de tiempo fijos, habitualmente menores o iguales a un año. ")
        st.markdown ("c-  Severidad: El grado de impacto ecológico y mortalidad de la vegetación que el fuego suele causar.")
        st.markdown ("d- Tamaño e Intensidad: Qué tan grandes son los incendios promedio y cuánta energía liberan sus llamas.")

        st.subheader ("¿Por qué se generan los incendios? ")
        st.write ("Un incendio forestal se genera cuando coinciden combustible seco (hojas, ramas, pasto), oxígeno y una fuente de calor (chispa).")
        st.write ("La chispa inicial ocurre por dos razones:")
        st.markdown ("a- Causas Humanas: Son la mayoría. Ocurren por descuidos (fogatas o colillas mal apagadas), fallas en cables eléctricos, quemas agrícolas descontroladas o incendios provocados.")
        st.markdown ("b- Causas Naturales: La principal es la caída de rayos, sobre todo durante tormentas eléctricas secas (con viento pero sin lluvia).")
        st.write ("El fuego se descontrola y se convierte en un gran incendio si encuentra mucho terreno seco por culpa del calor, la sequía prolongada y vientos fuertes que propagan las llamas rápido.")

        st.subheader ("¿Cuales son las temporadas de incendio en Texas, Oregón y California?")
        st.write ("Las temporadas de incendios en estos tres estados varían según sus climas locales, tipos de vegetación y patrones meteorológicos lo que lo distribuye de la siguiente manera:")
        st.markdown ("1.California")
        st.write ("El riesgo en California es constante, pero presenta dos picos muy marcados según la región:")
        st.markdown ("a- Norte de California: Su temporada alta suele comenzar en junio o julio y se extiende hasta octubre o noviembre. Se alimenta del calor extremo del verano que seca la vegetación densa de los bosques.")
        st.markdown ("b-Sur de California: Comienza un poco antes, en mayo o junio, y se prolonga hasta octubre. Sin embargo, la etapa más destructiva suele ocurrir en otoño (septiembre a noviembre) debido a la llegada de los vientos de Santa Ana, que propagan el fuego de forma explosiva.")

        st.markdown ("2. Texas")
        st.write ("Texas cuenta con una dinámica única, ya que tiene dos temporadas de picos críticos bien diferenciadas en el año:")
        st.markdown ("a- Temporada de letargo (Invierno/Primavera): Ocurre de febrero a abril. El frío seca los pastizales (hierba curada por la helada) y los frentes fríos traen vientos fuertes combinados con muy baja humedad, provocando incendios que avanzan muy rápido")
        st.markdown ("b-Temporada de verano: Ocurre de agosto a octubre. Es provocada por el calor extremo del verano y los periodos prolongados de sequía que deshidratan la vegetación.")

        st.markdown ("3. Oregón")
        st.write ("Al estar en el noroeste del Pacífico, su temporada está fuertemente ligada al ciclo del deshielo y las lluvias veraniegas:")
        st.markdown ("a- Temporada general: Tradicionalmente abarca de mediados de mayo hasta finales de septiembre o principios de octubre (cuando llegan las primeras lluvias otoñales).")
        st.markdown ("b- Pico de la temporada: Se concentra de julio a septiembre. Durante estos meses de verano, el calor evapora la humedad de los densos bosques de coníferas y las tormentas eléctricas secas (rayos sin lluvia) suelen desatar los incendios más grandes y severos del estado.")

        st.subheader ("Agencias de incendios")
        st.write ("Las agencias contra incendios en Estados Unidos son un grupo institucional y descentralizado de organismos gubernamentales, entidades civiles y corporaciones normativas dedicadas de forma integral a la prevención, regulación, combate y mitigación de los efectos del fuego en todo el territorio nacional. A diferencia de los modelos centralizados de otros países, este ecosistema opera de manera unificada bajo un protocolo de coordinación interagencial que fusiona la respuesta urbana de emergencia, el control de incendios forestales en millones de hectáreas de terrenos públicos y la gestión logística federal. El propósito fundamental de esta red es salvar vidas humanas, proteger la infraestructura civil y preservar los recursos naturales.")
        st.write ("Algunas de las principales agencias son:")

        st.markdown ("1. . FS (Forest Service / Servicio Forestal)")
        st.write ("Es una agencia del gobierno federal que pertenece al Departamento de Agricultura de EE. UU. (USDA). Es el organismo más grande e importante en el combate de incendios forestales.")
        st.write ("Esta  Administra y protege 193 millones de acres de bosques públicos y praderas nacionales. Tienen su propio ejército de bomberos forestales, camiones especializados, helicópteros y aviones cisterna. Cuando escuchas en las noticias que hay un incendio gigantesco en la naturaleza de EE. UU.")

        st.markdown ("2. BLM (Bureau of Land Management / Oficina de Administración de Tierras)")
        st.write (" Es una agencia federal que pertenece al Departamento del Interior de EE. UU. A  diferencia del Forest Service (que cuida bosques densos), el BLM gestiona tierras públicas que suelen ser desiertos, pastizales, cuencas y zonas de matorrales (especialmente en el oeste del país y Alaska). Tienen un papel crítico en la prevención de incendios mediante la eliminación de maleza seca y coordinan brigadas de bomberos de respuesta rápida para evitar que los fuegos en zonas desérticas o llanuras se salgan de control.")

        st.markdown ("FEMA (Federal Emergency Management Agency / Agencia Federal para la Gestión de Emergencias)")
        st.write ("Es la agencia federal de seguridad nacional encargada de responder a grandes desastres y catástrofes (huracanes, terremotos e incendios masivos). ")
        st.write ("Los empleados de FEMA no se ponen trajes de bombero ni apagan las llamas directamente. Su función es financiera y logística. Cuando un incendio forestal se vuelve incontrolable y destruye vecindarios enteros (superando la capacidad de los bomberos locales), el Presidente declara un **Estado de Desastre** y FEMA interviene. Ellos envían millones de dólares en ayuda, coordinan refugios para los evacuados, pagan los equipos de rescate de otros estados y ayudan económicamente a las familias a reconstruir sus casas.")

    if opcion_seleccionada == "MÉTODOS ESTADÍSTICOS":
        st.subheader ("Estadística Descriptiva Univariante")
        st.write ("La estadística descriptiva univariante se centra en el análisis de datos, haciendo uso de herramientas para describir, tabular, representar y visualizar el comportamiento de una variable.")

        st.subheader ("Medidas de Posición")
        st.write ("Las medidas de posición, también llamadas fractiles o cuantiles, son utilizadas para facilitar la localización de un dato respecto de un conjunto de ellos. Para este estudio, se utilizarán:")
        st.markdown ("a- Cuartiles: Valores que dividen la serie en 4 partes iguales, cada una de ellas con un 25 % de los datos.")
        st.markdown ("$$Q_k = L_i + \left[ \frac{\frac{k \cdot n}{4} - F_{i-1}}{f_i} \right] \cdot c$$")
        st.markdown ("b-Mediana: Promedio no matemático que divide a la serie de datos de un estudio, en dos partes iguales, que representan cada una el 50% de los datos.")
        st.markdown ("$$\text{Me} = L_i + \left[ \frac{\frac{n}{2} - F_{i-1}}{f_i} \right] \cdot c$$")

        st.subheader ("Medidas de Tendencia Central")
        st.write ("Son casos especiales de las medidas de posición, debido a su ubicación en la zona cntral de la distribución. Estas medidas, también son denominadas promedios.")
        st.markdown ("a-Media Aritmética: Es el valor resultante más **presentativo** de la serie de datos, el punto de equilibrio, el centro de gravedad de la serie.")
        st.markdown ("$$\bar{x} = \frac{\sum_{i=1}^{n} x_i}{n}$$")

        st.markdown ("b- Mediana: Promedio no matemático que divide a la serie de datos de un estudio, en dos partes iguales, que representan cada una el 50% de los datos.")
        st.markdown ("$$\text{Me} = L_i + \left[ \frac{\frac{n}{2} - F_{i-1}}{f_i} \right] \cdot c$$")

        st.markdown ("b- Moda: Es un promedio no matemático representado por el valor con mayor frecuencia en la serie de datos.")
        st.markdown ("$$\text{Mo} = L_i + \left[ \frac{f_{i} - f_{i-1}}{(f_{i} - f_{i-1}) + (f_{i} - f_{i+1})} \right] \cdot c$$")

        st.subheader ("Medidas de Dispersión")
        st.write ("Tienen por objeto medir la magnitud de los desvíos de los valores de la variable con respecto al valor central de la distribución, es decir, definen cuán semejante o cuán distinto son cada uno de los valores, de la variable con respecto al valor central.")
        st.markdown ("a- Rango Intercuartílico: constituye la máxima diferencia posible entre dos valores entre el 50% de los datos centrales.")
        st.markdown ("$$RI = Q_3 - Q_1$$")

        st.markdown ("b- Varianza: Es el promedio cuadrático de los desvíos de los datos respecto de la mdia aritmética.")
        st.markdown ("$$s^2 = \frac{\sum_{i=1}^{n} (x_i - \bar{x})^2}{n-1}$$")

        st.markdown ("c-Desviación Típica: Es la raíz cuadrada positiva de la varianza. Constituye el índice de dispersión más usado y más confiable.")
        st.markdown ("$$s = \sqrt{\frac{\sum_{i=1}^{n} (x_i - \bar{x})^2}{n-1}}$$")

        st.markdown ("d- Coeficiente de Variación de Pearson: Es el cociente entre la desviación estándar y la media aritmética, multiplicado por cien. Es el coeficiente de dispersión relativa de más amplio uso.")
        st.markdown ("$$CV = \frac{s}{\bar{x}} \cdot 100$$")





