from datetime import datetime

import matplotlib.pyplot as plt
import meteostat as ms
import pandas as pd
import polars as pl
import seaborn as sns
from statsmodels.tsa.seasonal import seasonal_decompose


def plot_uhi(df: list[pl.DataFrame], ciudades: list[str]) -> None:
    """
    Plot UHI time series for a given city.

    Parameters
    ----------
    df : list[pl.DataFrame]
        List of DataFrames containing:
        - 'time': datetime
        - 'uhi': UHI values
    ciudad : List[str]
        Name of the cities (used in the title).

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If required columns are missing.

    Notes
    -----
    The function displays a time series of UHI values and
    saves the figure.
    """

    for i in range(len(df)):
        plt.plot(df[i]["uhi"])
        plt.title(f"UHI {ciudades[i]}")
        plt.savefig("Uhis")
        plt.show()


def decomposition(start: datetime, end: datetime) -> None:
    """
    Plot seasonal decomposition for a given city.

    Parameters
    ----------
    start : datetime
        Date to start the data
    end : datetime
        Date to end the data

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If required dates are missing.

    Notes
    -----
    The function displays a seasonal decomposition of UHI values
    and saves the figure.
    """

    dal = ms.daily(ms.Station(id="08181"), start, end).fetch()["temp"]
    desc = seasonal_decompose(dal, model="a", period=365)
    desc.plot()
    plt.savefig("Descomposicion")
    plt.show()


def plot_day_night(df: pd.DataFrame) -> None:
    """
    Plot comparison between daytime and nighttime UHI values.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing:
        - 'ciudad'
        - 'uhi_dia'
        - 'uhi_noche'

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If required columns are missing.

    Notes
    -----
    The function creates a bar plot comparing UHI during day and night
    for each city and saves the figure.
    """

    df.set_index("ciudad").plot(kind="bar")
    plt.savefig("Uhi_dia_noche")
    plt.show()


def plot_correlation(df: pd.DataFrame) -> None:
    """
    Plot a correlation matrix of numerical variables.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing numerical variables.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If the input DataFrame is invalid or empty.

    Notes
    -----
    The function:
    - Computes correlation matrix
    - Displays it as a heatmap
    - Saves the figure

    Only numeric columns are considered.
    """

    sns.heatmap(df.drop("ciudad", axis=1).corr(), annot=True)
    plt.savefig("Heatmap")
    plt.show()
