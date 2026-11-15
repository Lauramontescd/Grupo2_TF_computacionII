# Diccionario de datos

Descripción de las tablas y columnas de la base **normalizada** (`normalizada.sqlite`) con la que se analiza la evolución temporal y espacial de los incendios en California, Oregón y Texas entre 1992 y 2015.

- **Fuente:** base `FPA_FOD_20170508` (Kaggle), registro de incendios de Estados Unidos, tabla plana `Fires` con 1.880.465 filas y 39 columnas.
- **Alcance de la base normalizada:** 167.215 incendios de CA, OR y TX con hora de descubrimiento registrada (ver la sección de limpieza en `02_Limpieza.sql`).
- **Esquema:** tercera forma normal, con una tabla principal (`fire_event`) y dos catálogos (`cause` y `county`).

## 1. Relaciones

| Tabla | Llave primaria | Llaves foráneas |
| --- | --- | --- |
| `fire_event` | `FOD_ID` | `STAT_CAUSE_CODE` → `cause`; (`STATE`, `FIPS_CODE`) → `county` |
| `cause` | `STAT_CAUSE_CODE` | — |
| `county` | (`STATE`, `FIPS_CODE`) | — |

Un incendio tiene una causa y un condado; una causa o un condado pueden aparecer en muchos incendios. Un mismo `FIPS_CODE` se repite en estados distintos, por eso la llave de `county` es compuesta.

## 2. Tabla `fire_event` (167.215 filas)

Un registro por incendio.

| Columna | Tipo | Descripción | Valores en la base |
| --- | --- | --- | --- |
| `FOD_ID` | entero | Identificador único del incendio. Es la clave que se usa para identificar un registro. | Sin nulos ni repetidos |
| `FPA_ID` | texto | Identificador del registro en la fuente original. No es único: hay 167.214 valores distintos en 167.215 filas. | Sin nulos |
| `DISCOVERY_DATE` | fecha (`AAAA-MM-DD`) | Fecha en que se descubrió el incendio. | 1992-01-01 a 2015-12-31; sin nulos |
| `DISCOVERY_DOY` | entero | Día del año de `DISCOVERY_DATE`. | 1 a 366; sin nulos |
| `DISCOVERY_TIME` | hora (`HH:MM:00`) | Hora de descubrimiento. Es el criterio por el que se conservaron los registros: se eliminaron los que no la tenían. | 00:00:00 a 23:59:00; sin nulos |
| `CONT_DATE` | fecha (`AAAA-MM-DD`) | Fecha de contención del incendio. Cuando faltaba se imputó con la fecha de descubrimiento (ver notas). | 1992-01-01 a 2016-01-01; sin nulos |
| `CONT_DOY` | entero | Día del año de contención. | 1 a 368; sin nulos |
| `CONT_TIME` | hora (`HH:MM:00`) | Hora de contención. Cuando faltaba se imputó con el promedio de su clase de tamaño (ver notas). | Sin nulos; 20.344 filas con formato dañado (ver notas) |
| `FIRE_SIZE` | decimal | Tamaño del incendio, en **acres**. | 0,001 a 558.198,3; sin nulos |
| `FIRE_SIZE_CLASS` | texto (1 letra) | Clase de tamaño: A hasta 0,25 acres; B de 0,26 a 9,9; C de 10 a 99,9; D de 100 a 299; E de 300 a 999; F de 1.000 a 4.999; G de 5.000 o más. | A, B, C, D, E, F, G |
| `LATITUDE` | decimal | Latitud del punto de origen, en grados. | 25,84 a 46,23 |
| `LONGITUDE` | decimal | Longitud del punto de origen, en grados (negativa: oeste). | -124,54 a -93,52 |
| `STATE` | texto (2 letras) | Estado: CA, OR o TX. | CA 110.217; OR 42.722; TX 14.276 |
| `FIPS_CODE` | texto (3 dígitos) | Código FIPS del condado dentro del estado. `000` marca condado desconocido. | 241 valores distintos; `000` en 80.764 filas (48,3 %) |
| `STAT_CAUSE_CODE` | entero | Código de la causa del incendio (1 a 13). | Ver `cause` |

Distribución por clase de tamaño: A 99.570; B 51.726; C 9.769; D 2.446; E 1.680; F 1.275; G 749.

## 3. Tabla `cause` (13 filas)

Catálogo de causas estadísticas.

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `STAT_CAUSE_CODE` | texto (2) | Código de la causa. En la copia revisada de la base está guardado como texto; en `fire_event` es entero, por eso al unir las tablas se convierte con `CAST`. |
| `STAT_CAUSE_DESCR` | texto | Nombre de la causa en inglés, tal como viene en la fuente. |

| Código | Descripción | Incendios | Grupo usado en el análisis |
| --- | --- | --- | --- |
| 1 | Lightning (rayo) | 52.472 | Natural |
| 2 | Equipment Use (uso de equipos) | 15.979 | Humana |
| 3 | Smoking (fumadores) | 4.452 | Humana |
| 4 | Campfire (fogata) | 14.206 | Humana |
| 5 | Debris Burning (quema de residuos) | 12.732 | Humana |
| 6 | Railroad (ferrocarril) | 547 | Humana |
| 7 | Arson (incendio provocado) | 15.433 | Humana |
| 8 | Children (niños) | 3.606 | Humana |
| 9 | Miscellaneous (varios) | 30.408 | Humana |
| 10 | Fireworks (fuegos artificiales) | 1.072 | Humana |
| 11 | Powerline (línea eléctrica) | 2.165 | Humana |
| 12 | Structure (estructura) | 210 | Humana |
| 13 | Missing/Undefined (sin determinar) | 13.933 | Sin determinar |

## 4. Tabla `county`

Catálogo de condados.

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `STATE` | texto (2) | Estado al que pertenece el condado. |
| `FIPS_CODE` | texto (3) | Código FIPS del condado dentro del estado. |
| `FIPS_NAME` | texto | Nombre del condado. Se tomó con `MAX(FIPS_NAME)` por cada pareja (`STATE`, `FIPS_CODE`). |

El código `000` (condado desconocido) existe en `fire_event` pero **no** está en `county`. Por eso el análisis es por estado y no une esta tabla.

## 5. Variables derivadas en la aplicación

La aplicación (`data.py`) calcula estas columnas a partir de las anteriores. No se guardan en la base.

| Variable | Cómo se obtiene | Para qué se usa |
| --- | --- | --- |
| `anio` | Año de `DISCOVERY_DATE` | Eje temporal de los gráficos |
| `mes` | Mes de `DISCOVERY_DATE` | Distribución mensual |
| `doy` | `DISCOVERY_DOY` | Duración de la temporada |
| `periodo` | 1992-1999, 2000-2007 o 2008-2015, según el año | Mapas, centros de focos graves y distribuciones |
| `grupo_causa` | Código 1 = Natural; 13 = Sin determinar; 2 a 12 = Humana | Objetivo 5 |
| `duracion_dias` | `CONT_DATE` menos `DISCOVERY_DATE`, en días | Duración tal como está guardada |
| `duracion_corregida` | Duración recuperada con `CONT_DOY - 2 - DISCOVERY_DOY` en los casos alterados (ver notas) | Objetivo 2 |

## 6. Notas de calidad

- **Registros conservados.** De 392.659 incendios de CA, OR y TX en la fuente, quedaron 167.215 (42,6 %): los que tenían hora de descubrimiento. La proporción conservada no es uniforme entre estados, clases de tamaño ni causas, por lo que el número de incendios por año describe los incendios con hora registrada y no el total real.
- **Fecha de contención imputada.** Cuando faltaba, `CONT_DATE` se imputó con la fecha de descubrimiento (y `CONT_DOY` con su día del año); si la hora imputada cruzaba la medianoche se sumó un día. Por eso `CONT_DATE` llega a 2016-01-01 y `CONT_DOY` llega a 368.
- **Duraciones alteradas.** En unos 20.000 incendios de varios días con datos reales, la fecha de contención aparece como "descubrimiento + 1 día" y `CONT_DOY` desplazado en 2 días. `CONT_DOY` conserva el dato original y permite recuperar la duración real; la corrección coincide con la fuente cruda en 147.618 de 147.633 incendios con fecha real.
- **Hora de contención.** 20.344 filas (12,2 %), las que tuvieron hora imputada, tienen `CONT_TIME` con formato dañado (por ejemplo `21::4:00`). Por eso la duración se mide en días y no se usa `CONT_TIME` en ningún cálculo.
- **Condado desconocido.** El 48,3 % de los incendios tiene `FIPS_CODE` = `000`. Es la razón por la que el análisis se hace por estado.

## 7. Cómo comprobar las cifras

```sql
SELECT COUNT(*) FROM fire_event;                                    -- 167215
SELECT STATE, COUNT(*) FROM fire_event GROUP BY STATE;              -- CA 110217, OR 42722, TX 14276
SELECT FIRE_SIZE_CLASS, COUNT(*) FROM fire_event GROUP BY 1;        -- A..G
SELECT COUNT(*) FROM fire_event WHERE FIPS_CODE = '000';            -- 80764
SELECT c.STAT_CAUSE_DESCR, COUNT(*)
FROM fire_event e JOIN cause c ON c.STAT_CAUSE_CODE = CAST(e.STAT_CAUSE_CODE AS TEXT)
GROUP BY 1;                                                         -- 13 causas
```
