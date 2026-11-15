import numpy as np
import pandas as pd

from data import ORDEN_CLASES 

PERIODOS = [("1992-1999", 1992, 1999), ("2000-2007", 2000, 2007), ("2008-2015", 2008, 2015)]
MINIMO_POR_ANIO = 30  


def _estado(df: pd.DataFrame, estado: str) -> pd.DataFrame:
    return df[df["estado"] == estado]


def periodo_de(anio: int) -> str:
    for etiqueta, ini, fin in PERIODOS:
        if ini <= anio <= fin:
            return etiqueta
    return "otro"


def tendencia(x, y) -> dict:
    """Pendiente por unidad de x (mínimos cuadrados), R² y correlación de Spearman (sobre rangos)."""
    s = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(s) < 3 or s["y"].nunique() < 2:
        return {"pendiente": np.nan, "r2": np.nan, "rho": np.nan}
    pendiente = np.polyfit(s["x"], s["y"], 1)[0]
    r = np.corrcoef(s["x"], s["y"])[0, 1]
    rho = s["x"].rank().corr(s["y"].rank())
    return {"pendiente": float(pendiente), "r2": float(r**2), "rho": float(rho)}


def focos_graves(df: pd.DataFrame, estado: str, clase_minima: str = "F") -> pd.DataFrame:
    """Incendios de clase >= clase_minima (F = 1.000 acres o más) con su periodo."""
    clases = ORDEN_CLASES[ORDEN_CLASES.index(clase_minima):]
    d = _estado(df, estado)
    d = d[d["FIRE_SIZE_CLASS"].isin(clases)].copy()
    d["periodo"] = d["anio"].map(periodo_de)
    return d


def _centroides(graves: pd.DataFrame, por: str) -> pd.DataFrame:
    """Centro geográfico ponderado por superficie quemada."""
    g = graves.assign(plat=graves["LATITUDE"] * graves["FIRE_SIZE"],
                      plon=graves["LONGITUDE"] * graves["FIRE_SIZE"])
    a = g.groupby(por).agg(incendios=("FOD_ID", "size"), superficie_acres=("FIRE_SIZE", "sum"),
                           plat=("plat", "sum"), plon=("plon", "sum"))
    a["latitud_centro"] = a["plat"] / a["superficie_acres"]
    a["longitud_centro"] = a["plon"] / a["superficie_acres"]
    return a.drop(columns=["plat", "plon"])


def centroides_por_periodo(graves: pd.DataFrame) -> pd.DataFrame:
    return _centroides(graves, "periodo")


def centroides_por_anio(graves: pd.DataFrame) -> pd.DataFrame:
    return _centroides(graves, "anio")


def distancia_km(lat1, lon1, lat2, lon2) -> float:
    """Distancia entre dos puntos (fórmula de Haversine)."""
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon1) / 2) ** 2
    return float(2 * 6371.0088 * np.arcsin(np.sqrt(a)))


def desplazamiento(cent: pd.DataFrame) -> dict:
    """Movimiento del centro entre el primer y el último periodo."""
    if len(cent) < 2:
        return {}
    a, b = cent.iloc[0], cent.iloc[-1]
    dlat = b["latitud_centro"] - a["latitud_centro"]
    dlon = b["longitud_centro"] - a["longitud_centro"]
    return {
        "km": distancia_km(a["latitud_centro"], a["longitud_centro"], b["latitud_centro"], b["longitud_centro"]),
        "direccion_ns": "norte" if dlat > 0 else "sur",
        "direccion_eo": "este" if dlon > 0 else "oeste",
        "desde": cent.index[0], "hasta": cent.index[-1],
    }


def duracion_anual(df: pd.DataFrame, estado: str, columna: str = "duracion_corregida") -> pd.DataFrame:
    d = _estado(df, estado)
    g = d.groupby("anio")[columna]
    return pd.DataFrame({
        "incendios": g.size(),
        "media_dias": g.mean(),
        "mediana_dias": g.median(),
        "p90_dias": g.quantile(0.9),
        "pct_mas_de_1_dia": (d[columna] > 1).groupby(d["anio"]).mean() * 100,
    })


def frecuencia_anual(df: pd.DataFrame, estado: str) -> pd.Series:
    return _estado(df, estado).groupby("anio").size().rename("incendios")


def perfil_mensual(df: pd.DataFrame, estado: str) -> pd.DataFrame:
    """% de los incendios de cada periodo que ocurre en cada mes (filas = mes)."""
    d = _estado(df, estado).assign(periodo=lambda x: x["anio"].map(periodo_de))
    t = d.groupby(["mes", "periodo"]).size().unstack("periodo", fill_value=0)
    return (t / t.sum() * 100).reindex(range(1, 13), fill_value=0)


def temporada_anual(df: pd.DataFrame, estado: str, p_ini: float = 0.05, p_fin: float = 0.95) -> pd.DataFrame:
    """Temporada = intervalo entre los percentiles p_ini y p_fin del día del año de descubrimiento."""
    d = _estado(df, estado)
    g = d.groupby("anio")["doy"]
    t = pd.DataFrame({"incendios": g.size(), "inicio_doy": g.quantile(p_ini), "fin_doy": g.quantile(p_fin)})
    t["largo_dias"] = t["fin_doy"] - t["inicio_doy"]
    t.loc[t["incendios"] < MINIMO_POR_ANIO, ["inicio_doy", "fin_doy", "largo_dias"]] = np.nan
    return t


def magnitud_anual(df: pd.DataFrame, estado: str) -> pd.DataFrame:
    d = _estado(df, estado)
    g = d.groupby("anio")["FIRE_SIZE"]
    return pd.DataFrame({
        "incendios": g.size(),
        "superficie_total_acres": g.sum(),
        "media_acres": g.mean(),
        "mediana_acres": g.median(),
        "p90_acres": g.quantile(0.9),
        "p99_acres": g.quantile(0.99),
        "maximo_acres": g.max(),
        "pct_100_acres_o_mas": (d["FIRE_SIZE"] >= 100).groupby(d["anio"]).mean() * 100,
    })


def clases_por_periodo(df: pd.DataFrame, estado: str) -> pd.DataFrame:
    """% de incendios en cada clase de tamaño (A-G) por periodo."""
    d = _estado(df, estado).assign(periodo=lambda x: x["anio"].map(periodo_de))
    t = d.groupby(["FIRE_SIZE_CLASS", "periodo"]).size().unstack("periodo", fill_value=0)
    return (t / t.sum() * 100).reindex(ORDEN_CLASES, fill_value=0)


def severidad_por_causa(df: pd.DataFrame, estado: str, nivel: str = "grupo_causa") -> pd.DataFrame:
    """nivel = 'grupo_causa' (natural / humana / sin determinar) o 'causa' (las 13 causas)."""
    d = _estado(df, estado)
    g = d.groupby(nivel)["FIRE_SIZE"]
    t = pd.DataFrame({
        "incendios": g.size(),
        "superficie_acres": g.sum(),
        "media_acres": g.mean(),
        "mediana_acres": g.median(),
        "p90_acres": g.quantile(0.9),
        "pct_100_acres_o_mas": (d["FIRE_SIZE"] >= 100).groupby(d[nivel]).mean() * 100,
        "pct_1000_acres_o_mas": (d["FIRE_SIZE"] >= 1000).groupby(d[nivel]).mean() * 100,
    })
    t.insert(1, "pct_incendios", t["incendios"] / t["incendios"].sum() * 100)
    t.insert(3, "pct_superficie", t["superficie_acres"] / t["superficie_acres"].sum() * 100)
    return t.sort_values("superficie_acres", ascending=False)


def superficie_anual_por_grupo(df: pd.DataFrame, estado: str) -> pd.DataFrame:
    d = _estado(df, estado)
    return d.pivot_table(index="anio", columns="grupo_causa", values="FIRE_SIZE", aggfunc="sum", fill_value=0)


def resumen_estados(df: pd.DataFrame, columna_duracion: str = "duracion_corregida") -> pd.DataFrame:
    filas = {}
    for estado in sorted(df["estado"].unique()):
        dur = duracion_anual(df, estado, columna_duracion)
        frec = frecuencia_anual(df, estado)
        temp = temporada_anual(df, estado)
        mag = magnitud_anual(df, estado)
        desp = desplazamiento(centroides_por_periodo(focos_graves(df, estado)))
        sev = severidad_por_causa(df, estado)
        filas[estado] = {
            "Cambio de la duración media (días/año)": tendencia(dur.index, dur["media_dias"])["pendiente"],
            "Cambio de la frecuencia (incendios/año)": tendencia(frec.index, frec)["pendiente"],
            "Cambio del largo de temporada (días/año)": tendencia(temp.index, temp["largo_dias"])["pendiente"],
            "Cambio del tamaño p90 (acres/año)": tendencia(mag.index, mag["p90_acres"])["pendiente"],
            "Cambio de la superficie anual (acres/año)": tendencia(mag.index, mag["superficie_total_acres"])["pendiente"],
            "Desplazamiento de focos graves (km)": desp.get("km", np.nan),
            "Superficie por causas naturales (%)": sev["pct_superficie"].get("Natural", np.nan),
        }
    return pd.DataFrame(filas).T