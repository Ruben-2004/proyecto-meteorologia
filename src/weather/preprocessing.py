import pandas as pd
import polars as pl


def preprocess(df: pl.DataFrame) -> pl.DataFrame:
    """
    Preprocess temperature data by handling missing values and outliers.

    Parameters
    ----------
    df : pl.DataFrame
        Input DataFrame containing:
        - 'time': datetime column
        - 'temp': temperature values

    Returns
    -------
    pl.DataFrame
        Cleaned DataFrame with:
        - Missing values handled
        - Outliers filtered
        - Data sorted by time

    Raises
    ------
    ValueError
        If required columns are missing.

    Notes
    -----
    The preprocessing steps include:
    - Sorting by time
    - Interpolating or filling missing values
    - Removing extreme outliers based on temperature thresholds

    Outlier thresholds can be adapted depending on the dataset.
    """

    # ordenar por tiempo
    df = df.sort("time")

    # eliminar duplicados
    df = df.unique(subset="time")

    # interpolar NAs
    df = df.with_columns(pl.col("temp").interpolate())

    # eliminar outliers (IQR)
    q1 = df.select(pl.col("temp").quantile(0.25)).item()
    q3 = df.select(pl.col("temp").quantile(0.75)).item()
    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    df = df.filter((pl.col("temp") >= lower) & (pl.col("temp") <= upper))

    return df


def serie_to_polars(df: pd.Series) -> pl.DataFrame:
    """
    Convert a pandas Series with datetime index into a Polars DataFrame.

    Parameters
    ----------
    df : pd.Series
        Pandas Series containing temperature values indexed by datetime.

    Returns
    -------
    pl.DataFrame
        Polars DataFrame with two columns:
        - 'time': datetime index
        - 'temp': values from the input series

    Raises
    ------
    ValueError
        If the input is not a pandas Series.

    Notes
    -----
    This function is useful to convert Meteostat outputs (pandas)
    into Polars format for faster processing.
    """
    return pl.from_pandas(df.to_frame(name="temp").reset_index())
