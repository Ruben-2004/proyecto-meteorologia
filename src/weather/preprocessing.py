import polars as pl
import pandas as pd

def preprocess(df: pl.DataFrame) -> pl.DataFrame:

    # ordenar por tiempo
    df = df.sort("time")

    # eliminar duplicados
    df = df.unique(subset="time")

    # interpolar NAs
    df = df.with_columns(
        pl.col("temp").interpolate()
    )

    # eliminar outliers (IQR)
    q1 = df.select(pl.col("temp").quantile(0.25)).item()
    q3 = df.select(pl.col("temp").quantile(0.75)).item()
    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    df = df.filter(
        (pl.col("temp") >= lower) & (pl.col("temp") <= upper)
    )

    return df


def serie_a_polars(df: pd.Series) -> pl.DataFrame:
    return pl.from_pandas(
        df.to_frame(name="temp").reset_index()
    )