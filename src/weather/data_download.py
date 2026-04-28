from datetime import datetime

import geopandas as gpd
import meteostat as ms
import pandas as pd
from pyproj import Transformer

ms.config.block_large_requests = False


def get_meteostat(
    start: datetime = datetime(2010, 1, 1),
    end: datetime = datetime(2022, 12, 31, 23, 59),
) -> tuple[list[pd.Series]]:

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
