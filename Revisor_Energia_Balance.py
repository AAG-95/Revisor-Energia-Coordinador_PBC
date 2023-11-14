# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 11:12:18 2023
@author: alonso.flores
"""

# Importación de librerías necesarias
import os
import pandas as pd
import re
from datetime import datetime
import numpy as np
import openpyxl
import warnings
import Funciones as func  # Se importa un módulo personalizado llamado Funciones

# Versiones de las librerías utilizadas
# python version: 3.9.13
# openpyxl version: 3.0.10
# pandas version: 1.4.4

# Deshabilitar temporalmente las advertencias
warnings.filterwarnings("ignore")

# Carpeta salida de archivos
carpeta_salida = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Diferencias\\2023\\Revisión Neomas Diferencias 2023\\Balance de Energía\\"

# Definición de variables de año y mes
primer_año = 2023
último_año = 2023
primer_mes_primer_año = 1
último_mes_último_año = 7


# Genera una lista de pares de años y meses
pares_lista = func.generar_pares(
    primer_año, último_año, primer_mes_primer_año, último_mes_último_año
)

# Usar segundo valor de la tupla para crear una lista de meses
fechas = [i[1] for i in pares_lista]

carpeta_entrada = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\2023\Balances\\"
# Lista para almacenar los nombres de los archivos encontrados
archivos = []


# Obtener la lista de archivos en la carpeta
entries = os.scandir(carpeta_entrada)

# Buscar archivos que cumplan ciertos criterios en la carpeta
for val in entries:
    count = 0  # Contador de archivos encontrados
    if (
        val.is_file()
        and any(str(word) in val.name for word in fechas)
        and (
            "Retiro" in val.name
        )  # Check if any word from the list is in the file name
        and not val.name.startswith("~$")
    ):
        count += 1
        archivos.append(val.name)

# Empresas a analizar
#empresas_analizadas = ["ENGIE", "ANDINA"]
empresas_analizadas = ["NEOMAS"]
# Listas para almacenar los dataframes resultantes
dataframes = []  # Datos Clientes Libres

# Procesar cada par de años y meses
for i in archivos:
    archivo_excel = carpeta_entrada + i
    df = pd.read_excel(archivo_excel, sheet_name="Retiros", engine="openpyxl",header=None)
    df = func.obtencion_Tablas(df, 1, 1)

    # Identify columns with NaN names
    nan_columns = [col for col in df.columns if pd.isna(col)]

    # Remove columns with NaN names
    df = df.drop(columns=nan_columns)
    dataframes.append(df)
    df["Medida 1"] = df["Medida 1"].astype(str).str.replace(".", ",", regex=False)
    df["Medida 2"] = df["Medida 2"].astype(str).str.replace(".", ",", regex=False)
    df["Medida 3"] = df["Medida 3"].astype(str).str.replace(".", ",", regex=False)
    df = df[df["Suministrador_final"].isin(empresas_analizadas)]
    print(df)

func.process_data(carpeta_salida, dataframes, "Retiros_NEOMAS", "")
