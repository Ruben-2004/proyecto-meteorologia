from datetime import datetime

import matplotlib.pyplot as plt
import meteostat as ms
import pandas as pd
import polars as pl
import seaborn as sns
from statsmodels.tsa.seasonal import seasonal_decompose


def plot_uhi(df: list[pl.DataFrame], ciudades: list[str]) -> None:
    for i in range(len(df)):
        plt.plot(df[i]["uhi"])
        plt.title(f"UHI {ciudades[i]}")
        plt.savefig("Uhis")
        plt.show()


def decomposition(start: datetime, end: datetime) -> None:
    dal = ms.daily(ms.Station(id="08181"), start, end).fetch()["temp"]
    desc = seasonal_decompose(dal, model="a", period=365)
    desc.plot()
    plt.savefig("Descomposicion")
    plt.show()


def plot_day_night(df: pd.DataFrame) -> None:
    df.set_index("ciudad").plot(kind="bar")
    plt.savefig("Uhi_dia_noche")
    plt.show()


def plot_correlation(df: pd.DataFrame) -> None:
    sns.heatmap(df.drop("ciudad", axis=1).corr(), annot=True)
    plt.savefig("Heatmap")
    plt.show()
