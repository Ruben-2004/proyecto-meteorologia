import polars as pl


def calcular_uhi_pl(urb: pl.DataFrame, rur: pl.DataFrame) -> pl.DataFrame:
    """
    Compute the Urban Heat Island (UHI) effect using Polars DataFrames.

    Parameters
    ----------
    urb : pl.DataFrame
        Urban temperature data with columns:
        - 'time': datetime
        - 'temp': temperature values
    rur : pl.DataFrame
        Rural temperature data with columns:
        - 'time': datetime
        - 'temp': temperature values

    Returns
    -------
    pl.DataFrame
        DataFrame containing:
        - 'time': datetime
        - 'uhi': computed UHI (temp_urb - temp_rur)

    Raises
    ------
    ValueError
        If required columns are missing or inputs are invalid.

    Notes
    -----
    The function performs:
    - Inner join on 'time' to align both datasets
    - Column renaming to avoid conflicts
    - UHI computation as a new column

    Only timestamps present in both datasets are retained.
    """

    # Renombrar columnas para evitar conflictos
    urb = urb.rename({"temp": "temp_urb"})
    rur = rur.rename({"temp": "temp_rur"})

    # Join temporal (solo tiempos comunes)
    df = urb.join(rur, on="time", how="inner")

    # Calcular UHI
    df = df.with_columns((pl.col("temp_urb") - pl.col("temp_rur")).alias("uhi"))

    df = df.drop(["temp_urb", "temp_rur"])

    # Ordenar por tiempo (por seguridad)
    df = df.sort("time")

    return df


def resumen_completo_uhi(df: pl.DataFrame) -> dict:
    """
    Compute summary statistics of the UHI time series.

    Parameters
    ----------
    df : pl.DataFrame
        DataFrame containing:
        - 'time': datetime
        - 'uhi': UHI values

    Returns
    -------
    Dict[str, float]
        Dictionary with:
        - 'uhi_medio': mean UHI
        - 'uhi_dia': mean UHI during daytime
        - 'uhi_noche': mean UHI during nighttime

    Raises
    ------
    ValueError
        If required columns are missing.

    Notes
    -----
    Daytime and nighttime are defined based on hour:
    - Day: 10:00 - 18:00
    - Night: otherwise

    This split can be adjusted depending on the study.
    """

    # UHI medio total
    uhi_medio = df.select(pl.col("uhi").mean()).item()

    # UHI día (10-18)
    uhi_dia = (
        df.filter((pl.col("time").dt.hour() >= 10) & (pl.col("time").dt.hour() <= 18))
        .select(pl.col("uhi").mean())
        .item()
    )

    # UHI noche (22-06)
    uhi_noche = (
        df.filter((pl.col("time").dt.hour() >= 22) | (pl.col("time").dt.hour() <= 6))
        .select(pl.col("uhi").mean())
        .item()
    )

    # UHI por mes
    uhi_mes = (
        df.with_columns(pl.col("time").dt.month().alias("mes"))
        .group_by("mes")
        .agg(pl.col("uhi").mean().alias("uhi_medio"))
        .sort("mes")
    )

    return {
        "uhi_medio": uhi_medio,
        "uhi_dia": uhi_dia,
        "uhi_noche": uhi_noche,
        "uhi_mes": uhi_mes,
    }
