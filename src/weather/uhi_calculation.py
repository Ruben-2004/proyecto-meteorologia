import polars as pl


def calcular_uhi_pl(urb: pl.DataFrame, rur: pl.DataFrame) -> pl.DataFrame:
    """
    Calcula el Urban Heat Island (UHI) alineando dos series temporales.

    Parámetros
    ----------
    urb : pl.DataFrame
        DataFrame con columnas ["time", "temp"] (estación urbana)
    rur : pl.DataFrame
        DataFrame con columnas ["time", "temp"] (estación rural)

    Returns
    -------
    pl.DataFrame
        DataFrame con columnas:
        ["time", "temp_urb", "temp_rur", "uhi"]
    """

    # Renombrar columnas para evitar conflictos
    urb = urb.rename({"temp": "temp_urb"})
    rur = rur.rename({"temp": "temp_rur"})

    # Join temporal (solo tiempos comunes)
    df = urb.join(rur, on="time", how="inner")

    # Calcular UHI
    df = df.with_columns(
        (pl.col("temp_urb") - pl.col("temp_rur")).alias("uhi")
    )

    df = df.drop(['temp_urb', 'temp_rur'])

    # Ordenar por tiempo (por seguridad)
    df = df.sort("time")

    return df


def resumen_completo_uhi(df: pl.DataFrame) -> dict:
    """
    Calcula métricas completas del UHI a partir de un dataframe con:
    ["time", "temp_urb", "temp_rur", "uhi"]
    """

    # UHI medio total
    uhi_medio = df.select(pl.col("uhi").mean()).item()

    # UHI día (10-18)
    uhi_dia = df.filter(
        (pl.col("time").dt.hour() >= 10) &
        (pl.col("time").dt.hour() <= 18)
    ).select(pl.col("uhi").mean()).item()

    # UHI noche (22-06)
    uhi_noche = df.filter(
        (pl.col("time").dt.hour() >= 22) |
        (pl.col("time").dt.hour() <= 6)
    ).select(pl.col("uhi").mean()).item()

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
        "uhi_mes": uhi_mes
    }
