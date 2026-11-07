ATTACH DATABASE 'normalizada.sqlite' AS norm;


-- --- dimensiones -----------------------------------------------------------

CREATE TABLE dim_location (
    location_id TEXT PRIMARY KEY,      
    FIPS_CODE   VARCHAR NOT NULL,
    STATE       VARCHAR NOT NULL,
    state_name  VARCHAR NOT NULL,
    county_name VARCHAR NOT NULL
);
-- los 348 condados reales de los estados presentes en los datos
INSERT INTO dim_location (location_id, FIPS_CODE, STATE, state_name, county_name)
SELECT c.STATE || c.FIPS_CODE, c.FIPS_CODE, c.STATE,
       CASE c.STATE WHEN 'CA' THEN 'California' WHEN 'OR' THEN 'Oregon'
                    WHEN 'TX' THEN 'Texas' ELSE c.STATE END,
       c.FIPS_NAME
FROM norm.county c
WHERE c.STATE IN (SELECT DISTINCT STATE FROM norm.fire_event);

-- el marcador de condado desconocido, que county no contiene
INSERT INTO dim_location (location_id, FIPS_CODE, STATE, state_name, county_name)
SELECT DISTINCT e.STATE || e.FIPS_CODE, e.FIPS_CODE, e.STATE,
       CASE e.STATE WHEN 'CA' THEN 'California' WHEN 'OR' THEN 'Oregon'
                    WHEN 'TX' THEN 'Texas' ELSE e.STATE END,
       'Unknown'
FROM norm.fire_event e
WHERE e.STATE || e.FIPS_CODE NOT IN (SELECT location_id FROM dim_location);

CREATE TABLE dim_cause (
    STAT_CAUSE_CODE INTEGER PRIMARY KEY,
    STAT_CAUSE_DESCR VARCHAR
);
INSERT INTO dim_cause
SELECT CAST(STAT_CAUSE_CODE AS INTEGER), STAT_CAUSE_DESCR
FROM norm.cause ORDER BY 1;

-- dim_date: una fila por fecha, SOLO con atributos de la fecha 
CREATE TABLE dim_date (
    date_id       TEXT PRIMARY KEY,      
    full_date     TEXT    NOT NULL UNIQUE,  
    year          INTEGER NOT NULL,
    quarter       INTEGER NOT NULL,
    month         INTEGER NOT NULL,
    month_name    TEXT    NOT NULL,
    day           INTEGER NOT NULL,
    day_of_week   INTEGER NOT NULL,     
    day_name      TEXT    NOT NULL,
    is_weekend    INTEGER NOT NULL,
    DISCOVERY_DOY INTEGER NOT NULL      
);
-- Calendario 
INSERT INTO dim_date
WITH RECURSIVE
  rango(ini, fin) AS (
    SELECT MIN(d), MAX(d) FROM (
      SELECT DISCOVERY_DATE AS d FROM norm.fire_event
      UNION SELECT CONT_DATE FROM norm.fire_event WHERE CONT_DATE IS NOT NULL)),
  dias(f) AS (
    SELECT ini FROM rango
    UNION ALL SELECT date(f, '+1 day') FROM dias, rango WHERE f < rango.fin)
SELECT strftime('%Y%m%d', f), f,
       CAST(strftime('%Y', f) AS INTEGER),
       (CAST(strftime('%m', f) AS INTEGER) + 2) / 3,
       CAST(strftime('%m', f) AS INTEGER),
       CASE CAST(strftime('%m', f) AS INTEGER)
            WHEN 1 THEN 'January' WHEN 2 THEN 'February' WHEN 3 THEN 'March'
            WHEN 4 THEN 'April' WHEN 5 THEN 'May' WHEN 6 THEN 'June'
            WHEN 7 THEN 'July' WHEN 8 THEN 'August' WHEN 9 THEN 'September'
            WHEN 10 THEN 'October' WHEN 11 THEN 'November' ELSE 'December' END,
       CAST(strftime('%d', f) AS INTEGER),
       CASE CAST(strftime('%w', f) AS INTEGER) WHEN 0 THEN 7
            ELSE CAST(strftime('%w', f) AS INTEGER) END,
       CASE CAST(strftime('%w', f) AS INTEGER)
            WHEN 0 THEN 'Sunday' WHEN 1 THEN 'Monday' WHEN 2 THEN 'Tuesday'
            WHEN 3 THEN 'Wednesday' WHEN 4 THEN 'Thursday' WHEN 5 THEN 'Friday'
            ELSE 'Saturday' END,
       CASE WHEN strftime('%w', f) IN ('0','6') THEN 1 ELSE 0 END,
       CAST(strftime('%j', f) AS INTEGER)
FROM dias;


-- --- hecho -----------------------------------------------------------------

CREATE TABLE fact_fires (
    FOD_ID INTEGER PRIMARY KEY,
    FPA_ID TEXT,
    dim_date_id TEXT,            
    DISCOVERY_DATE TEXT,          
    dim_location_id TEXT,
    dim_cause_id INTEGER,
    FIRE_SIZE FLOAT,
    FIRE_SIZE_CLASS VARCHAR,
    LATITUDE FLOAT,
    LONGITUDE FLOAT,
    DISCOVERY_TIME TIME,
    CONT_DATE DATE,
    cont_date_id TEXT,        
    CONT_DOY INTEGER,
    CONT_TIME TIME,

    FOREIGN KEY (dim_date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (cont_date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (dim_location_id) REFERENCES dim_location(location_id),
    FOREIGN KEY (dim_cause_id) REFERENCES dim_cause(STAT_CAUSE_CODE)
);

INSERT INTO fact_fires
SELECT
    e.FOD_ID, e.FPA_ID,
    strftime('%Y%m%d', e.DISCOVERY_DATE),
    e.DISCOVERY_DATE,
    e.STATE || e.FIPS_CODE,
    CAST(e.STAT_CAUSE_CODE AS INTEGER),
    e.FIRE_SIZE, e.FIRE_SIZE_CLASS, e.LATITUDE, e.LONGITUDE,
    e.DISCOVERY_TIME, e.CONT_DATE,
    strftime('%Y%m%d', e.CONT_DATE),
    e.CONT_DOY, e.CONT_TIME
FROM norm.fire_event e;

DETACH DATABASE norm;
VACUUM;
