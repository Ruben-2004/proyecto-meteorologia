import pandas as pd
import polars as pl
from meteostat import Point
from src.weather.uhi_calculation import resumen_completo_uhi


def build_final_df(
    uhis: list[pl.DataFrame],
    ciudades: list[str],
    poblaciones: list[int],
    altitud_urb: list[int],
    altitud_rur: list[int],
    puntos: list[Point],
    urbanas_pl: list[pl.DataFrame],
    rurales_pl: list[pl.DataFrame],
    land_use: pd.DataFrame,
) -> pd.DataFrame:
    resultados = []
    for uhi, ciudad, poblacion, alt_urb, alt_rur, point, temp_urb, temp_rur in zip(
        uhis,
        ciudades,
        poblaciones,
        altitud_urb,
        altitud_rur,
        puntos,
        urbanas_pl,
        rurales_pl,
    ):
        res = resumen_completo_uhi(uhi)

        resultados.append(
            {
                "ciudad": ciudad,
                "uhi_medio": res["uhi_medio"],
                "uhi_dia": res["uhi_dia"],
                "uhi_noche": res["uhi_noche"],
                "población": poblacion,
                "altitud urbana": alt_urb,
                "altitud rural": alt_rur,
                "latitud": point.latitude,
                "temp_urb": temp_urb.mean()["temp"][0],
                "temp_rur": temp_rur.mean()["temp"][0],
            }
        )

    df_res = pd.DataFrame(resultados)

    df_final = df_res.merge(pd.DataFrame(land_use))

    return df_final
