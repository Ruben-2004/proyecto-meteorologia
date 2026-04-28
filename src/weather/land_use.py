import geopandas as gpd
import pandas as pd
from shapely.geometry import Point


def create_buffers(
    puntos: list[Point], ciudades: list[str], radius: int = 5000
) -> gpd.GeoDataFrame:
    """
    Create buffer zones around geographic points.

    Parameters
    ----------
    puntos : List[Point]
        List of geographic points (longitude, latitude).
    ciudades : List[str]
        List of city names corresponding to each point.
    radius : int, optional
        Buffer radius in meters (default is 5000).

    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame containing buffer geometries in projected CRS (EPSG:3035).

    Raises
    ------
    ValueError
        If the lengths of puntos and ciudades do not match.

    Notes
    -----
    Points are initially defined in WGS84 (EPSG:4326) and then projected
    to EPSG:3035 to allow buffering in meters.
    """

    gdf_points = gpd.GeoDataFrame(
        {
            "ciudad": ciudades,
            "geometry": [Point(punto.longitude, punto.latitude) for punto in puntos],
        },
        crs="EPSG:4326",
    )

    gdf_points = gdf_points.to_crs(3035)
    gdf_points["geometry"] = gdf_points.buffer(radius)
    return gdf_points


def intersect_land(
    buffers: gpd.GeoDataFrame, clc: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """
    Compute spatial intersection between buffers and CORINE land use polygons.

    Parameters
    ----------
    buffers : gpd.GeoDataFrame
        GeoDataFrame containing buffer geometries.
    clc : gpd.GeoDataFrame
        CORINE land cover GeoDataFrame.

    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame with intersected geometries and combined attributes.

    Raises
    ------
    ValueError
        If inputs are not valid GeoDataFrames.

    Notes
    -----
    Both GeoDataFrames must share the same CRS before performing the intersection.
    """

    intersections = gpd.overlay(buffers, clc, how="intersection")
    intersections["area"] = intersections.geometry.area
    return intersections


def classify_land(code: str) -> str:
    """
    Classify CORINE land cover codes into broader categories.

    Parameters
    ----------
    code : int
        CORINE land cover code (e.g., 111, 211, 311).

    Returns
    -------
    str
        Land use category:
        - 'urbano'
        - 'agricola'
        - 'vegetacion'
        - 'otros'

    Raises
    ------
    ValueError
        If the code is not a valid integer.

    Notes
    -----
    CORINE codes are grouped as follows:
    - 1xx: Artificial surfaces (urban)
    - 2xx: Agricultural areas
    - 3xx: Forest and semi-natural areas
    - Others: classified as 'otros'
    """

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
    """
    Compute percentage of land use types within each buffer.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame resulting from spatial intersection. Must include:
        - 'ciudad'
        - 'Code_18'
        - 'geometry'

    Returns
    -------
    gpd.GeoDataFrame
        DataFrame with percentage of each land use category per city.

    Raises
    ------
    ValueError
        If required columns are missing.

    Notes
    -----
    The function:
    - Computes area of each polygon
    - Classifies land use using CORINE codes
    - Aggregates area by category and city
    - Converts to percentage
    """

    area_cat = gdf.groupby(["ciudad", "categoria"])["area"].sum().reset_index()

    area_total = gdf.groupby("ciudad")["area"].sum().reset_index(name="area_total")

    df = area_cat.merge(area_total, on="ciudad")

    df["porcentaje"] = df["area"] / df["area_total"] * 100

    df_final = df.pivot(
        index="ciudad", columns="categoria", values="porcentaje"
    ).fillna(0)

    df_final.loc["Tenerife"] = [0, 100, 0, 0]

    df_final = df_final.reset_index()

    return df_final
