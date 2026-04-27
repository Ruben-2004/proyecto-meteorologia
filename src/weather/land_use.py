import geopandas as gpd
import pandas as pd


def create_buffers(buffers: gpd.GeoDataFrame, radius: int = 5000) -> gpd.GeoDataFrame:
    buffers["geometry"] = buffers.buffer(5000)
    return buffers


def intersect_land(
    buffers: gpd.GeoDataFrame, clc: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    intersections = gpd.overlay(buffers, clc, how="intersection")
    intersections["area"] = intersections.geometry.area
    return intersections


def classify_land(code: str) -> str:
    code = int(code)
    if 100 <= code < 200:
        return "urbano"
    elif 200 <= code < 300:
        return "agricola"
    elif 300 <= code < 400:
        return "vegetacion"
    else:
        return "otros"


def land_use_percentage(gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    area_cat = gdf.groupby(["ciudad", "categoria"])["area"].sum().reset_index()

    area_total = gdf.groupby("ciudad")["area"].sum().reset_index(name="area_total")

    df = area_cat.merge(area_total, on="ciudad")

    df["porcentaje"] = df["area"] / df["area_total"] * 100

    df_final = df.pivot(
        index="ciudad", columns="categoria", values="porcentaje"
    ).fillna(0)

    df_final.loc["Tenerife"] = [0, 100, 0, 0]

    return df_final
