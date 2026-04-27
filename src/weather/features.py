from uhi_calculation import resumen_completo_uhi
import pandas as pd
import polars as pl
from typing import List
from meteostat import Point

def build_final_df(uhis: List[pl.DataFrame], ciudades: List[str], poblaciones: List[int], altitud_urb: List[int], altitud_rur: List[int], puntos: List[Point], urbanas_pl: List[pl.DataFrame], rurales_pl: List[pl.DataFrame]) -> pd.DataFrame:
    resultados = []
    for uhi, ciudad, poblacion, alt_urb, alt_rur, point, temp_urb, temp_rur in zip(uhis, ciudades, poblaciones, altitud_urb, altitud_rur, puntos, urbanas_pl, rurales_pl):
        res = resumen_completo_uhi(uhi)

        resultados.append({
        "ciudad": ciudad,
        "uhi_medio": res["uhi_medio"],
        "uhi_dia": res["uhi_dia"],
        "uhi_noche": res["uhi_noche"],
        "población": poblacion,
        "altitud urbana": alt_urb,
        "altitud rural": alt_rur,
        'latitud': point.latitude,
        'temp_urb': temp_urb.mean()['temp'][0],
        'temp_rur': temp_rur.mean()['temp'][0]
    })
        
    return pd.DataFrame(resultados)