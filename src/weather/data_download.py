from datetime import datetime

import geopandas as gpd
import meteostat as ms
import pandas as pd
from pyproj import Transformer

ms.config.block_large_requests = False


def get_meteostat(
    start: datetime = datetime(2010, 1, 1),
    end: datetime = datetime(2022, 12, 31, 23, 59),
) -> tuple[list[pd.Series], list[pd.Series]]:
    """
    Download hourly temperature data from Meteostat for multiple locations.

    Parameters
    ----------
        List of Meteostat Point objects representing locations.
    start : datetime
        Start date.
    end : datetime
        End date.

    Returns
    -------
    Tuple[List[pd.Series], List[pd.Series]]
        Two lists:
        - Urban station temperature series
        - Rural station temperature series

    Raises
    ------
    ValueError
        If the date format is invalid.
    RuntimeError
        If data retrieval fails.

    Notes
    -----
    This function assumes that for each point, both an urban and a rural
    station are available. Returned data are typically pandas Series
    indexed by datetime.
    """

    urbanas = []
    rurales = []

    id_urb = ["08221", "08181", "08391", "08160", "08025", "08001", "08023", "60025"]
    id_rur = ["08227", "LELL0", "08397", "LEHC0", "08080", "08002", "08021", "60015"]

    for urb, rur in zip(id_urb, id_rur):
        urbanas.append(ms.hourly(ms.Station(id=urb), start, end).fetch()["temp"])
        rurales.append(ms.hourly(ms.Station(id=rur), start, end).fetch()["temp"])

    return (urbanas, rurales)


def get_corine(
    path: str = "data/U2018_CLC2018_V2020_20u1.gpkg", crs: int = 3035
) -> gpd.GeoDataFrame:
    """
    Load CORINE Land Cover data from a file.

    Parameters
    ----------
    path : str
        Path to the CORINE file (e.g., .gpkg).
    crs : int | None, optional
        Proyection to use. If None, the default crs is used.

    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame containing CORINE land use polygons with attributes.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the file cannot be read or contains no valid layers.

    Notes
    -----
    The dataset is typically large, so it is recommended to use bounding
    boxes or filters to limit memory usage.
    """

    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3035", always_xy=True)

    xmin, ymin = transformer.transform(-10, 35)
    xmax, ymax = transformer.transform(5, 44)

    bbox_3035 = (xmin, ymin, xmax, ymax)

    clc = gpd.read_file(
        path,
        layer="U2018_CLC2018_V2020_20u1",
        bbox=bbox_3035,
        columns=["Code_18", "geometry"],
    ).to_crs(crs)

    return clc
