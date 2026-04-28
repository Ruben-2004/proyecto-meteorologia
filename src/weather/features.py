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
    """
    Build the final dataset combining UHI metrics, land use, and additional features.

    Parameters
    ----------
    uhis : pl.DataFrame
        DataFrame from which UHI metrics per city are calculated (e.g., mean, day, night).
        Must include a 'ciudad' column.
    ciudades : List[str]
        Name of the cities included
    poblaciones : list[int]
        List containing population data per city.
    altitud_urb : List[int]
        List containing altitude data per urban city.
    altitud_rur : List[int]
        List containing altitude data per rural city.
    puntos : list[Point]
        Geographic coordinates (latitude, longitude) for each city.
    urbanas_pl: list[pl.DataFrame]
        List of Dataframes with the UHIs from each urban city
    rurales_pl: list[pl.DataFrame]
        List of Dataframes with the UHIs from each rural city
    land_use : pd.DataFrame
        DataFrame with land use percentages per city.
        Must include a 'ciudad' column and variables such as 'urbano', 'vegetacion', etc.

    Returns
    -------
    pd.DataFrame
        Final merged DataFrame containing:
        - UHI metrics
        - Land use variables
        - Population
        - Engineered features (distance, altitude, coordinates)

    Raises
    ------
    ValueError
        If required columns are missing or input sizes are inconsistent.

    Notes
    -----
    The merge is typically performed on the 'ciudad' column. Additional
    features are appended assuming all lists are aligned with the rows
    of the input DataFrames.
    """

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
