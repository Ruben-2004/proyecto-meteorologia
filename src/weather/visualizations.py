import matplotlib.pyplot as plt
import pandas as pd
import polars as pl
import seaborn as sns


def plot_uhi(df: list[pl.DataFrame], ciudades: list[str]) -> None:
    for i in range(len(df)):
        plt.plot(df[i]["uhi"])
        plt.title(f"UHI {ciudades[i]}")
        plt.show()


def plot_day_night(df: pd.DataFrame) -> None:
    df.set_index("ciudad").plot(kind="bar")
    plt.savefig("Uhi_dia_noche")
    plt.show()


def plot_correlation(df: pd.DataFrame) -> None:
    sns.heatmap(df.drop("ciudad", axis=1).corr(), annot=True)
    plt.show()
