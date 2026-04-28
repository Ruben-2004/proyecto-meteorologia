import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import polars as pl
import pytest
from shapely.geometry import Point

from src.weather.data_download import get_corine, get_meteostat
from src.weather.features import build_final_df
from src.weather.land_use import (
    classify_land,
    create_buffers,
    intersect_land,
)
from src.weather.models import prepare_data, train_models
from src.weather.preprocessing import preprocess, serie_to_polars
from src.weather.uhi_calculation import calcular_uhi_pl, resumen_completo_uhi
from src.weather.visualizations import (
    decomposition,
    plot_correlation,
    plot_day_night,
    plot_uhi,
)


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

        from datetime import datetime

        import meteostat as ms

        uhi_df = [
            pl.DataFrame(
                {
                    "ciudad": ["Madrid", "Barcelona"],
                    "uhi": [2.5, 1.8],
                    "time": [
                        datetime(2022, 12, 12, 00, 00),
                        datetime(2022, 12, 15, 00, 00),
                    ],
                }
            ),
            pl.DataFrame(
                {
                    "ciudad": ["Madrid", "Barcelona"],
                    "uhi": [2.5, 1.8],
                    "time": [
                        datetime(2022, 12, 3, 00, 00),
                        datetime(2022, 12, 18, 00, 00),
                    ],
                }
            ),
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

        assert X_train.shape[0] == 2, "shape should be 2"
        assert len(y_train) == 2, "len should be 2"

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
                "uhi_medio": [1.0, 2.0, 3.0],
                "uhi_dia": [1.0, 2.0, 3.0],
            }
        )

        X_train, X_test, y_train, y_test = prepare_data(df)

        models = train_models(X_train, X_test, y_train, y_test)

        assert models is not None

    def test_invalid_input(self):
        with pytest.raises(Exception):
            train_models(None, None)


# ------------------------
# serie_to_polars
# ------------------------


class TestSerieToPolars:
    def test_happy_path(self):
        df = pd.DataFrame(
            {
                "time": pd.date_range("2020-01-01", periods=5, freq="D"),
                "temp": [1, 2, 3, 4, 5],
            }
        ).set_index("time")

        result = serie_to_polars(df["temp"])

        assert isinstance(result, pl.DataFrame)
        assert "temp" in result.columns
        assert "time" in result.columns

    def test_edge_empty_series(self):
        s = pd.Series(dtype=float)

        result = serie_to_polars(s)

        assert isinstance(result, pl.DataFrame)
        assert result.shape[0] == 0

    def test_invalid_input(self):
        with pytest.raises(Exception):
            serie_to_polars(None)


# ------------------------
# preprocess
# ------------------------


class TestPreprocess:
    def test_happy_path(self):
        df = pl.DataFrame(
            {
                "time": pd.date_range("2020-01-01", periods=6, freq="D"),
                "temp": [1, 2, None, 4, 5, 6],
            }
        )

        result = preprocess(df)

        assert isinstance(result, pl.DataFrame)
        assert "temp" in result.columns
        assert result.shape[0] > 0

    def test_missing_column(self):
        df = pl.DataFrame({"time": [1, 2, 3]})

        with pytest.raises(Exception):
            preprocess(df)


# ------------------------
# calcular_uhi_pl
# ------------------------


class TestCalcularUHI:
    def test_happy_path(self):
        urb = pl.DataFrame({"time": [1, 2, 3], "temp": [20, 21, 22]})

        rur = pl.DataFrame({"time": [1, 2, 3], "temp": [18, 19, 20]})

        result = calcular_uhi_pl(urb, rur)

        assert "uhi" in result.columns
        assert result["uhi"][0] == 2

    def test_edge_empty(self):
        urb = pl.DataFrame({"time": [], "temp": []})
        rur = pl.DataFrame({"time": [], "temp": []})

        result = calcular_uhi_pl(urb, rur)

        assert result.shape[0] == 0

    def test_missing_column(self):
        urb = pl.DataFrame({"time": [1, 2, 3]})  # falta temp
        rur = pl.DataFrame({"time": [1, 2, 3], "temp": [1, 2, 3]})

        with pytest.raises(Exception):
            calcular_uhi_pl(urb, rur)


# ------------------------
# resumen_completo_uhi
# ------------------------


class TestResumenCompletoUHI:
    def test_happy_path(self):
        df = pl.DataFrame(
            {
                "time": pd.date_range("2020-01-01", periods=24, freq="D"),
                "temp_urb": [20] * 24,
                "temp_rur": [18] * 24,
                "uhi": [2] * 24,
            }
        )

        result = resumen_completo_uhi(df)

        assert "uhi_medio" in result
        assert "uhi_dia" in result
        assert "uhi_noche" in result

    def test_edge_single_value(self):
        df = pl.DataFrame(
            {
                "time": [pd.Timestamp("2020-01-01 12:00")],
                "temp_urb": [20],
                "temp_rur": [18],
                "uhi": [2],
            }
        )

        result = resumen_completo_uhi(df)

        assert result["uhi_medio"] == 2

    def test_missing_uhi_column(self):
        df = pl.DataFrame({"time": [1, 2, 3], "temp_urb": [1, 2, 3]})

        with pytest.raises(Exception):
            resumen_completo_uhi(df)


class TestPlotCorrelation:
    def test_happy_path(self):
        df = pd.DataFrame(
            {
                "uhi_noche": [1, 2, 3],
                "urbano": [10, 20, 30],
                "vegetacion": [50, 40, 30],
                "ciudad": ["A", "B", "C"],
            }
        )

        plot_correlation(df)

        assert plt.gcf() is not None
        plt.close()

    def test_invalid_input(self):
        with pytest.raises(Exception):
            plot_correlation(None)


# ------------------------
# plot_day_night
# ------------------------


class TestPlotDayNight:
    def test_happy_path(self):
        df = pd.DataFrame(
            {"uhi_dia": [1, 2, 3], "uhi_noche": [2, 3, 4], "ciudad": ["A", "B", "C"]}
        )

        plot_day_night(df)

        assert plt.gcf() is not None
        plt.close()

    def test_edge_single_city(self):
        df = pd.DataFrame({"uhi_dia": [1], "uhi_noche": [2], "ciudad": ["A"]})

        plot_day_night(df)

        assert plt.gcf() is not None
        plt.close()

    def test_invalid_input(self):
        with pytest.raises(Exception):
            plot_day_night(None)


# ------------------------
# plot_uhi
# ------------------------


class TestPlotUHI:
    def test_happy_path(self):
        df = [
            pl.DataFrame(
                {
                    "time": pd.date_range("2020-01-01", periods=5, freq="D"),
                    "uhi": [1, 2, 3, 2, 1],
                }
            )
        ]

        plot_uhi(df, ["TestCity"])

        assert plt.gcf() is not None
        plt.close()

    def test_missing_column(self):
        df = pl.DataFrame({"time": [1, 2, 3]})

        with pytest.raises(Exception):
            plot_uhi(df, "TestCity")


class TestDecomposition:
    def test_decompose(self):
        from datetime import datetime

        start = datetime(2018, 1, 1)
        end = datetime(2022, 12, 31, 23, 59)
        decomposition(start, end)

        assert plt.gcf() is not None
        plt.close()
