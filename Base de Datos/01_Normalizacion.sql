/* ============================================================================
   SCRIPT 1: CREACIÓN DEL ESQUEMA NORMALIZADO (3FN)
   ----------------------------------------------------------------------------
   PROYECTO:Evolución Temporal y Espacial de los Incendios en California, Texas y Oregón (1992-2015)
   BASE DE DATOS: SQLite (FPA_FOD_20170508)
   
   PROPÓSITO:
   La base original "Fires" contiene 1.8 millones de registros en una sola 
   tabla plana con 39 columnas. Muchos datos de texto (como el nombre del 
   condado o la descripción de la causa) se repiten millones de veces, 
   generando redundancia y haciendo las consultas lentas.
   
   Este script aplica la Tercera Forma Normal (3FN) dividiendo la tabla 
   original en un esquema de 3 tablas (Dimensiones y Hechos) enfocado 
   exclusivamente en las variables necesarias para el estudio.
   
   Para la poblacion de las tablas se insertaron los datos directamente de la 
   base original, utilizando especificamente la tabla Fires.
   ============================================================================ */


-- BLOQUE 1: TABLAS DE DIMENSIÓN 
-- ----------------------------------------------------------------------------

/* DIMENSIÓN: CAUSA (cause)
   Justificación: El código de causa (STAT_CAUSE_CODE) especifica la descripción 
   (STAT_CAUSE_DESCR) de la causa por la que se generó el incendio.
   Al crear su propia tabla, se evita que aparezca alguna de las 13 causas posibles 
   varias veces */

CREATE TABLE cause (
    STAT_CAUSE_CODE integer PRIMARY KEY,
    STAT_CAUSE_DESCR text
);

-- Poblamiento: Se extraen solo los valores únicos de la columna STAT_CAUSE_CODE,
-- se agrupan por el código. 

INSERT INTO cause (STAT_CAUSE_CODE, STAT_CAUSE_DESCR)
SELECT STAT_CAUSE_CODE, MAX(STAT_CAUSE_DESCR)
FROM Fires
WHERE STAT_CAUSE_CODE IS NOT NULL
GROUP BY STAT_CAUSE_CODE;


/* DIMENSIÓN: CONDADO (County)
   Justificación: El nombre del condado depende de la combinación de 
   Estado (STATE) y Código FIPS (FIPS_CODE). Se usa una llave primaria 
   compuesta porque un código FIPS se repite en diferentes estados. */

CREATE TABLE county (
    STATE varchar(2),
    FIPS_CODE varchar(10),
    FIPS_NAME text,
    PRIMARY KEY (STATE, FIPS_CODE)
);

-- Poblamiento: Se usa COALESCE para asignar '000' a los condados que no tienen
-- FIPS_CODE para garantizar que ningún incendio quede sin ubicación geográfica.
INSERT INTO county (STATE, FIPS_CODE, FIPS_NAME)
SELECT 
    STATE, 
    COALESCE(FIPS_CODE, '000'), 
    MAX(FIPS_NAME)
FROM Fires
WHERE STATE IS NOT NULL
GROUP BY STATE, COALESCE(FIPS_CODE, '000');



-- BLOQUE 2: TABLA DE HECHOS 
-- ----------------------------------------------------------------------------

/* TABLA DE HECHOS: FIRE_EVENT
   Justificación: Almacena el evento del incendio en sí. Contiene las métricas 
   (tamaño, latitud, longitud, fechas) y las llaves foráneas que conectan 
   con las dimensiones.*/

CREATE TABLE fire_event (
    FOD_ID integer PRIMARY KEY,
    FPA_ID text,
    DISCOVERY_DATE text,  
    DISCOVERY_DOY integer,
    DISCOVERY_TIME text,   
    CONT_DATE text,        
    CONT_DOY integer,
    CONT_TIME text,
    FIRE_SIZE float,
    FIRE_SIZE_CLASS varchar(2),
    LATITUDE float,
    LONGITUDE float,
    STATE varchar(2),
    FIPS_CODE varchar(10),
    STAT_CAUSE_CODE integer,
    FOREIGN KEY (STATE, FIPS_CODE) REFERENCES county(STATE, FIPS_CODE),
    FOREIGN KEY (STAT_CAUSE_CODE) REFERENCES cause(STAT_CAUSE_CODE)
);

-- Poblamiento: Se insertan los 1.8 millones de registros asegurando la coincidencia 
-- exacta del orden de las columnas.
INSERT INTO fire_event (
    FOD_ID, FPA_ID, DISCOVERY_DATE, DISCOVERY_DOY, DISCOVERY_TIME, 
    CONT_DATE, CONT_DOY, CONT_TIME, FIRE_SIZE, FIRE_SIZE_CLASS, 
    LATITUDE, LONGITUDE, STATE, FIPS_CODE, STAT_CAUSE_CODE
)
SELECT 
    FOD_ID, 
    FPA_ID, 
    date(DISCOVERY_DATE), 
    DISCOVERY_DOY,
    DISCOVERY_TIME,
    date(CONT_DATE),      
    CONT_DOY,
    CONT_TIME,
    FIRE_SIZE,
    FIRE_SIZE_CLASS,
    LATITUDE,
    LONGITUDE,
    STATE,
    COALESCE(FIPS_CODE, '000'), 
    CAST(STAT_CAUSE_CODE AS integer)
FROM Fires;


