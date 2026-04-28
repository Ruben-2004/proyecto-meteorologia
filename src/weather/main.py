from datetime import datetime

import meteostat as ms
import pandas as pd

# módulos del proyecto
from data_download import get_corine, get_meteostat
from features import build_final_df
from land_use import classify_land, create_buffers, intersect_land, land_use_percentage
from models import prepare_data, train_models
from preprocessing import preprocess, serie_to_polars
from uhi_calculation import calcular_uhi_pl, resumen_completo_uhi
from visualizations import decomposition, plot_correlation, plot_day_night, plot_uhi

# ------------------------


def main():

    print("🚀 Starting UHI analysis pipeline...")

    # ------------------------
    # 1. CONFIGURACIÓN
    # ------------------------

    ciudades = [
        "Madrid",
        "Barcelona",
        "Sevilla",
        "Zaragoza",
        "Bilbao",
        "Coruña",
        "Santander",
        "Tenerife",
    ]

    point_mad = ms.Point(40.416944, -3.703333)
    point_bcn = ms.Point(41.358343, 2.132798)
    point_sev = ms.Point(37.394104, -5.984400)
    point_zar = ms.Point(41.653531, -0.880645)
    point_bil = ms.Point(43.264409, -2.929773)
    point_cor = ms.Point(43.348043, -8.361744)
    point_san = ms.Point(43.458945, -3.830064)
    point_tnf = ms.Point(28.460128, -16.271544)
    puntos = [
        point_mad,
        point_bcn,
        point_sev,
        point_zar,
        point_bil,
        point_cor,
        point_san,
        point_tnf,
    ]
    start = datetime(2010, 1, 1)
    end = datetime(2022, 12, 31, 23, 59)

    corine_path = "data/U2018_CLC2018_V2020_20u1.gpkg"

    # ------------------------
    # 2. DESCARGA DE DATOS
    # ------------------------

    print("📥 Downloading meteorological data...")
    urbanas, rurales = get_meteostat(start, end)

    print("📥 Loading CORINE data...")
    clc = get_corine(corine_path)

    # ------------------------
    # 3. PREPROCESAMIENTO
    # ------------------------

    print("🧹 Preprocessing data...")

    urbanas_pl = [preprocess(serie_to_polars(df)) for df in urbanas]

    rurales_pl = [preprocess(serie_to_polars(df)) for df in rurales]

    # ------------------------
    # 4. CÁLCULO UHI
    # ------------------------

    print("🌡️ Calculating UHI...")

    uhis = [calcular_uhi_pl(urb, rur) for urb, rur in zip(urbanas_pl, rurales_pl)]

    uhi_results = []
    for ciudad, df in zip(ciudades, uhis):
        res = resumen_completo_uhi(df)

        uhi_results.append(
            {
                "ciudad": ciudad,
                "uhi_medio": res["uhi_medio"],
                "uhi_dia": res["uhi_dia"],
                "uhi_noche": res["uhi_noche"],
            }
        )

    uhi_df = pd.DataFrame(uhi_results)

    # ------------------------
    # 5. LAND USE (CORINE)
    # ------------------------

    print("🌍 Computing land use...")

    buffers = create_buffers(puntos, ciudades, radius=5000)
    intersections = intersect_land(buffers, clc)
    intersections["categoria"] = intersections["Code_18"].apply(classify_land)
    land_use_df = land_use_percentage(intersections)

    # ------------------------
    # 6. FEATURES FINALES
    # ------------------------

    print("🧩 Building feature table...")

    poblaciones = [
        3_280_000,
        1_620_000,
        690_000,
        675_000,
        345_000,
        245_000,
        173_000,
        209_000,
    ]
    altitud_urb = [609, 4, 34, 263, 42, 58, 64, 64]
    altitud_rur = [607, 250, 87, 539, 513, 97, 6, 632]

    df_final = build_final_df(
        uhis,
        ciudades,
        poblaciones,
        altitud_urb,
        altitud_rur,
        puntos,
        urbanas_pl,
        rurales_pl,
        land_use_df,
    )

    print(df_final.head())

    # ------------------------
    # 7. REGRESIÓN
    # ------------------------

    print("📈 Running regression models...")

    X_train, X_test, y_train, y_test = prepare_data(df_final)

    r_2, coefs = train_models(X_train, X_test, y_train, y_test)

    print(f"Linear R²: {r_2['Lineal']:.3f}")
    print(f"Ridge R²: {r_2['Ridge']:.3f}")
    print(f"Lasso R²: {r_2['Lasso']:.3f}")

    # coeficientes
    print("\n📊 Linear coefficients:")
    print(coefs)

    # ------------------------
    # 8. VISUALIZACIÓN
    # ------------------------

    print("📊 Generating plots...")

    start = datetime(2020, 1, 1)
    end = datetime(2022, 12, 31, 23, 59)

    plot_uhi(uhis, ciudades)
    plot_day_night(uhi_df)
    decomposition(start, end)
    plot_correlation(df_final)

    print("✅ Pipeline completed successfully!")


# ------------------------

if __name__ == "__main__":
    main()
