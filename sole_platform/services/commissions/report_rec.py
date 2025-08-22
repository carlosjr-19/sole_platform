import os
import polars as pl
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.drawing.image import Image as Img
from openpyxl.styles import numbers
from flask import current_app

def limpiar_archivo_polars(df1: pl.DataFrame, df2: pl.DataFrame):

    # Mostrar totales
    total_df1 = df1.height
    total_df2 = df2.height

    print(f"Total en DataFrame 1: {total_df1}")
    print(f"Total en DataFrame 2: {total_df2}")

    # Obtener los sets de msisdn únicos
    msisdn_df1 = set(df1.select("msisdn").to_series().to_list())
    msisdn_df2 = set(df2.select("msisdn").to_series().to_list())

    # Números en df1 que no están en df2
    solo_en_df1 = msisdn_df1 - msisdn_df2

    # Números en df2 que no están en df1
    solo_en_df2 = msisdn_df2 - msisdn_df1

    # Filtrar los msisdn de df1 que empiezan con '1'
    msisdn_eliminados = df1.filter(pl.col("msisdn").cast(pl.Utf8).str.starts_with("1")).select("msisdn").to_series().to_list()

    # Eliminar esas filas del dataframe
    df1_limpio = df1.filter(~pl.col("msisdn").cast(pl.Utf8).str.starts_with("1"))

    print(f"Números eliminados de DataFrame 1 (por empezar con '1'): {msisdn_eliminados}")
    print(f"Total después de limpieza: {df1_limpio.height}")

    # Retornar resultados
    resultado = {
        "total_df1": df1_limpio.height,
        "total_df2": total_df2,
        "solo_en_df1": list(solo_en_df1),
        "solo_en_df2": list(solo_en_df2),
        "msisdn_eliminados": msisdn_eliminados,
        "df1_limpio": df1_limpio
    }

    return resultado