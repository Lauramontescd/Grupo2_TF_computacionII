/* ============================================================================
 * SCRIPT 2: CREACIÓN DEL ESQUEMA DENORMALIZADO
----------------------------------------------------------------------------
PROYECTO: Evolución Temporal y Espacial de los Incendios en California, Texas y Oregón (1992-2015)
BASE DE DATOS: SQLite (FPA_FOD_20170508)

PROPÓSITO:
Este script consolida la información en una única estructura denormalizada 
que integra los datos clave de fechas, ubicación y causas junto con la 
tabla de hechos, optimizando el rendimiento de las consultas analíticas 
al evitar la necesidad de múltiples JOINS.

Para la población de las tablas se unieron e insertaron los datos directamente 
de la base limpia y normalizada, partiendo de las tablas de normalización ya establecidas.
 */

-- 1: garantiza la activación de claves foráneas (en caso de aún no tenerlas activadas)

PRAGMA foreign_keys = ON;

-- Creación de las tablas de dimensión

-- DIMENSIÓN: FECHA (dim_date)
-- Justificación: Agrupa todos los componentes temporales del incendio (Anio, mes, día, horas, e
-- información de contención) a partir de la fecha de descubrimiento, generando una clave primaria 
-- corrida (date_id en formato DDMMYYYY). Al separarla, se evita duplicar metadatos de tiempo en 
-- cada registro de la tabla principal  y se facilita el análisis estandarizado por periodos.

CREATE TABLE dim_date (
    date_id TEXT PRIMARY KEY,       
    year INTEGER,                      
    month INTEGER,                    
    day INTEGER,
    DISCOVERY_DOY INTEGER,
    DISCOVERY_TIME TEXT,
    CONT_DATE TEXT,
    CONT_DOY INTEGER,
    CONT_TIME TEXT
);

-- DIMENSIÓN: UBICACIÓN (location)
-- Justificación: El código de ubicación (FIPS_CODE) y el estado (STATE) definen el contexto 
-- geográfico donde ocurrió el incendio. Al crear su propia tabla, se evita que los nombres de 
-- los estados y condados se repitan millones de veces, optimizando el espacio y centralizando la 
-- información espacial.

CREATE TABLE dim_location (
    location_id TEXT PRIMARY KEY,
    FIPS_CODE TEXT,
    STATE TEXT
);

-- DIMENSIÓN: CAUSA (cause)
-- Justificación: El código de causa (STAT_CAUSE_CODE) especifica la descripción (STAT_CAUSE_DESCR)
-- de la causa por la que se generó el incendio. Al crear su propia tabla, se evita que aparezca alguna
-- de las causas posibles varias veces.

CREATE TABLE dim_cause (
    STAT_CAUSE_CODE INTEGER PRIMARY KEY,
    STAT_CAUSE_DESCR TEXT
);

-- TABLA DE HECHOS: INCENDIOS (fact_fires)
-- Justificación: Almacena las métricas cuantitativas y transaccionales del estudio (como el tamaño del
-- incendio FIRE_SIZE y las coordenadas LATITUDE y LONGITUDE), junto con las claves foráneas que conectan
-- con las dimensiones de fecha, ubicación y causa. Al aislar las mediciones numéricas y las referencias
-- aquí, se evita duplicar atributos descriptivos y se centraliza el núcleo transaccional para las consultas
-- de análisis.

CREATE TABLE fact_fires (
    FOD_ID INTEGER PRIMARY KEY,
    FPA_ID TEXT,
    dim_date_id TEXT,         
    DISCOVERY_DATE TEXT,      
    dim_location_id TEXT, 
    dim_cause_id INTEGER, 
    FIRE_SIZE REAL,
    LATITUDE REAL,
    LONGITUDE REAL,
    
    FOREIGN KEY (dim_date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (DISCOVERY_DATE) REFERENCES dim_date(date_id), 
    FOREIGN KEY (dim_location_id) REFERENCES dim_location(location_id),
    FOREIGN KEY (dim_cause_id) REFERENCES dim_cause(STAT_CAUSE_CODE)
);

-- hola esto es un separador


-- Poblamiento de dim_cause:
-- Justificación: Se extraen los códigos y descripciones desde la tabla fuente mediante SELECT DISTINCT.
-- Esto asegura una correspondencia unívoca y estricta entre cada STAT_CAUSE_CODE y su respectiva
-- descripción sin duplicar registros.

INSERT OR IGNORE INTO dim_cause (
    STAT_CAUSE_CODE,
    STAT_CAUSE_DESCR
)
SELECT DISTINCT 
    STAT_CAUSE_CODE,
    STAT_CAUSE_DESCR
FROM cause c;

-- sí, me estoy haciendo la chistosa en comentarios lol
  
-- Poblamiento de dim_date:
-- Justificación: Se extraen y transforman los componentes temporales directamente de DISCOVERY_DATE
-- mediante funciones de cadena (SUBSTR y CAST) para poblar los campos de año, mes, día y construir la
-- clave primaria corrida (date_id en formato DDMMYYYY). Se utiliza SELECT DISTINCT y un filtro IS NOT NULL
-- para asegurar registros de fecha únicos y consistentes.

INSERT OR IGNORE INTO dim_date (
    date_id,
    year,
    month,
    day,
    DISCOVERY_DOY,
    DISCOVERY_TIME,
    CONT_DATE,
    CONT_DOY,
    CONT_TIME
)
SELECT DISTINCT 
    SUBSTR(fe.DISCOVERY_DATE, 9, 2) || SUBSTR(fe.DISCOVERY_DATE, 6, 2) || SUBSTR(fe.DISCOVERY_DATE, 1, 4) AS date_id,
    CAST(SUBSTR(fe.DISCOVERY_DATE, 1, 4) AS INTEGER) AS year,
    CAST(SUBSTR(fe.DISCOVERY_DATE, 6, 2) AS INTEGER) AS month,
    CAST(SUBSTR(fe.DISCOVERY_DATE, 9, 2) AS INTEGER) AS day,
    fe.DISCOVERY_DOY,
    fe.DISCOVERY_TIME,
    fe.CONT_DATE,
    fe.CONT_DOY,
    fe.CONT_TIME
FROM fire_event fe
WHERE fe.DISCOVERY_DATE IS NOT NULL;

-- esto es una embolia que lo sepan

-- Poblamiento de dim_location:
-- Justificación: Se consolidan los datos geográficos únicos aplicando SELECT DISTINCT sobre los campos
-- FIPS_CODE y STATE de la fuente, descartando valores nulos. Esto garantiza que cada combinación geográfica
-- tenga una única entrada limpia asociada a su identificador.

INSERT OR IGNORE INTO dim_location (
    location_id, 
    state, 
    fips_code
)
SELECT DISTINCT 
    FIPS_CODE,        
    STATE,             
    FIPS_CODE          
FROM fire_event
WHERE FIPS_CODE IS NOT NULL;

-- dios mio me quiero matar

-- Poblamiento de fact_fires (Tabla de Hechos):
-- Justificación: Se cargan las métricas cuantitativas y los identificadores transaccionales 
-- (FOD_ID, FIRE_SIZE, LATITUDE, LONGITUDE) junto con las claves foráneas hacia las dimensiones.
-- Se implementa una subconsulta con GROUP BY FOD_ID para garantizar la unicidad de cada evento
-- de incendio y mantener la integridad relacional del modelo.

INSERT OR IGNORE INTO fact_fires (
    FOD_ID, 
    FPA_ID,
    dim_date_id,         
    DISCOVERY_DATE,      
    dim_location_id,
    dim_cause_id,
    FIRE_SIZE, 
    LATITUDE, 
    LONGITUDE
)
SELECT 
    f.FOD_ID, 
    f.FPA_ID, 
    SUBSTR(f.CONT_DATE, 9, 2) || SUBSTR(f.CONT_DATE, 6, 2) || SUBSTR(f.CONT_DATE, 1, 4),          
    SUBSTR(f.CONT_DATE, 9, 2) || SUBSTR(f.CONT_DATE, 6, 2) || SUBSTR(f.CONT_DATE, 1, 4),      
    f.FIPS_CODE,      
    f.STAT_CAUSE_CODE, 
    f.FIRE_SIZE, 
    f.LATITUDE, 
    f.LONGITUDE
FROM (
    SELECT FOD_ID, FPA_ID, CONT_DATE, FIPS_CODE, STAT_CAUSE_CODE, FIRE_SIZE, LATITUDE, LONGITUDE
    FROM fire_event
    WHERE CONT_DATE IS NOT NULL
    GROUP BY FOD_ID
) f;