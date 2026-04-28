import geopandas as gpd
import pandas as pd
import polars as pl
import pytest
from shapely.geometry import Point, Polygon

from src.weather.data_download import get_corine, get_meteostat
from src.weather.features import build_final_df
from src.weather.land_use import (
    classify_land,
    create_buffers,
    intersect_land,
    land_use_percentage,
)
from src.weather.models import prepare_data, train_models


class TestGetCorine:
    def test_corine(self):

        result = get_corine()

        assert result is not None, "Dataset not imported"
        assert len(result) == 284222, "Dataset not imported correctly"
        assert "geometry" in result.columns, "Geometry not imported correctly"


class TestGetMeteostat:
    def test_happy_path(self):
        from datetime import datetime

        start = datetime(2022, 12, 1)
        end = datetime(2022, 12, 31, 23, 59)

        urbanas, rurales = get_meteostat(start, end)

        assert len(urbanas) == 8, "Urbanas not imported correctly"
        assert len(rurales) == 8, "Rurales not imported correctly"


class TestBuildFinalDF:
    def test_happy_path(self):

        import meteostat as ms

        uhi_df = [
            pl.DataFrame({"ciudad": ["Madrid", "Barcelona"], "uhi_noche": [2.5, 1.8]}),
            pl.DataFrame({"ciudad": ["Madrid", "Barcelona"], "uhi_noche": [2.5, 1.8]}),
        ]

        ciudades = ["Madrid", "Barcelona"]
        land_use_df = pd.DataFrame(
            {
                "ciudad": ["Madrid", "Barcelona"],
                "urbano": [70, 60],
                "vegetacion": [10, 20],
                "otros": [0, 0],
                "agricola": [20, 20],
            }
        )

        poblacion = [3_000_000, 1_600_000]

        point_mad = ms.Point(40.416944, -3.703333)
        point_bcn = ms.Point(41.358343, 2.132798)
        puntos = [point_mad, point_bcn]
        altitud_urb = [100, 50]
        altitud_rur = [10, 24]

        urbanas_pl = [
            pl.DataFrame({"ciudad": ["Madrid", "Barcelona"], "temp": [2.5, 1.8]}),
            pl.DataFrame({"ciudad": ["Madrid", "Barcelona"], "temp": [2.5, 1.8]}),
        ]

        rurales_pl = [
            pl.DataFrame({"ciudad": ["Madrid", "Barcelona"], "temp": [2.5, 1.8]}),
            pl.DataFrame({"ciudad": ["Madrid", "Barcelona"], "temp": [2.5, 1.8]}),
        ]

        df = build_final_df(
            uhi_df,
            ciudades,
            poblacion,
            altitud_urb,
            altitud_rur,
            puntos,
            urbanas_pl,
            rurales_pl,
            land_use_df,
        )

        assert isinstance(df, pd.DataFrame), "Data is not a Dataframe"
        assert "uhi_noche" in df.columns, "Data not imported correctly"
        assert "urbano" in df.columns, "Data not imported correctly"


class TestClassifyLand:
    def test_happy_path(self):
        assert classify_land("111") == "urbano", '111 should return "urbano"'

    def test_edge_boundary(self):
        assert classify_land("199") == "urbano", '199 should return "urbano"'
        assert classify_land("200") == "agricola", '200 should return "agricola"'

    def test_invalid_input(self):
        assert classify_land("-1") == "otros", '-1 should return "otros"'


# ------------------------
# create_buffers
# ------------------------


class TestCreateBuffers:
    def test_happy_path(self):
        from meteostat import Point

        puntos = [Point(-3.7, 40.4)]
        ciudades = ["Madrid"]

        gdf = create_buffers(puntos, ciudades, radius=1000)

        assert isinstance(gdf, gpd.GeoDataFrame)
        assert gdf.shape[0] == 1

    def test_edge_empty(self):
        gdf = create_buffers([], [], radius=1000)

        assert gdf.shape[0] == 0

    def test_mismatch_lengths(self):
        puntos = [Point(-3.7, 40.4)]
        ciudades = ["Madrid", "Barcelona"]

        with pytest.raises(Exception):
            create_buffers(puntos, ciudades)


# ------------------------
# intersect_land
# ------------------------


class TestIntersectLand:
    def test_happy_path(self):
        buffers = gpd.GeoDataFrame(
            {"ciudad": ["A"], "geometry": [Point(0, 0).buffer(1)]}, crs="EPSG:4326"
        )

        clc = gpd.GeoDataFrame(
            {"Code_18": [111], "geometry": [Point(0, 0).buffer(1)]}, crs="EPSG:4326"
        )

        result = intersect_land(buffers, clc)

        assert isinstance(result, gpd.GeoDataFrame)
        assert len(result) > 0

    def test_edge_no_overlap(self):
        buffers = gpd.GeoDataFrame(
            {"ciudad": ["A"], "geometry": [Point(0, 0).buffer(1)]}, crs="EPSG:4326"
        )

        clc = gpd.GeoDataFrame(
            {"Code_18": [111], "geometry": [Point(100, 100).buffer(1)]}, crs="EPSG:4326"
        )

        result = intersect_land(buffers, clc)

        assert len(result) == 0

    def test_invalid_input(self):
        with pytest.raises(Exception):
            intersect_land(None, None)


# ------------------------
# land_use_percentage
# ------------------------


class TestLandUsePercentage:
    def test_happy_path(self):
        gdf = gpd.GeoDataFrame(
            {
                "ciudad": ["A", "B"],
                "categoria": ["otros", "urbano"],
                "area": [100, 520],
                "geometry": [
                    Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                    Polygon([(0, 0), (2, 0), (2, 2), (0, 2)]),
                ],
            },
            crs="EPSG:4326",
        )

        result = land_use_percentage(gdf)

        assert "ciudad" in result.columns
        assert len(result) == 1

    def test_edge_empty(self):
        gdf = gpd.GeoDataFrame(
            {"ciudad": [], "categoria": [], "area": [], "geometry": []}, crs="EPSG:4326"
        )

        result = land_use_percentage(gdf)

        assert len(result) == 0

    def test_invalid_input(self):
        with pytest.raises(Exception):
            land_use_percentage(None)


# ------------------------
# prepare_data
# ------------------------


class TestPrepareData:
    def test_happy_path(self):
        df = pd.DataFrame(
            {
                "ciudad": ["A", "B", "C"],
                "uhi_noche": [1.0, 2.0, 3.0],
                "urbano": [10, 20, 30],
                "vegetacion": [50, 40, 30],
                "uhi_medio": [1.0, 2.0, 3.0],
                "uhi_dia": [1.0, 2.0, 3.0],
            }
        )

        X_train, X_test, y_train, y_test = prepare_data(df)

        assert X_train.shape[0] == 3
        assert len(y_train) == 3

    def test_edge_single_row(self):
        df = pd.DataFrame(
            {
                "ciudad": ["A"],
                "uhi_noche": [1.0],
                "urbano": [10],
                "vegetacion": [50],
                "uhi_medio": [1.0],
                "uhi_dia": [1.0],
            }
        )

        X_train, X_test, y_train, y_test = prepare_data(df)

        assert X_train.shape[0] == 1

    def test_missing_target(self):
        df = pd.DataFrame({"urbano": [10, 20]})

        with pytest.raises(Exception):
            prepare_data(df)


# ------------------------
# train_models
# ------------------------


class TestTrainModels:
    def test_happy_path(self):
        df = pd.DataFrame(
            {
                "ciudad": ["A", "B", "C"],
                "uhi_noche": [1.0, 2.0, 3.0],
                "urbano": [10, 20, 30],
                "vegetacion": [50, 40, 30],
            }
        )

        X_train, X_test, y_train, y_test = prepare_data(df)

        models = train_models(X_train, X_test, y_train, y_test)

        assert models is not None

    def test_edge_small_dataset(self):
        df = pd.DataFrame(
            {
                "ciudad": ["A", "B"],
                "uhi_noche": [1.0, 2.0],
                "urbano": [10, 20],
                "vegetacion": [50, 40],
            }
        )

        X_train, X_test, y_train, y_test = prepare_data(df)

        models = train_models(X_train, X_test, y_train, y_test)

        assert models is not None

    def test_invalid_input(self):
        with pytest.raises(Exception):
            train_models(None, None)
