# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 11:12:18 2023
@author: alonso.flores
"""

# Importación de librerías necesarias
import os
import sys
import pandas as pd
import re
from datetime import datetime
import pandas as pd
import re
import numpy as np
import openpyxl
import warnings
import funciones as func  # Se importa un módulo personalizado llamado Funciones

# Definición de variables de año y mes
primer_año = 2020
primer_mes_primer_año = 6
último_año = 2020
último_mes_último_año = 10

# Genera una lista de pares de años y meses
pares_lista = func.ConversionDatos().generar_pares(
    primer_año, último_año, primer_mes_primer_año, último_mes_último_año
)

carpeta_entrada = rf"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Recaudación\\"

# Convert values
dataframe = []

for par in pares_lista:
    df_clientes_L = pd.read_csv(carpeta_entrada + "Revisiones Mensuales\\BDD_" + str(par[1]) +"\\" + "Revisor_Clientes" + str(par[1]) + ".csv" , encoding="UTF-8", sep=";")

    df_nvs_clientes_L = pd.read_csv(carpeta_entrada + "Revisiones Mensuales\\BDD_" + str(par[1]) +"\\" + "Revisor_Clientes_Nuevos" + str(par[1]) + ".csv" , encoding="UTF-8", sep=";")

    df_clientes_L_total = pd.concat([df_clientes_L, df_nvs_clientes_L], ignore_index=True)

    dataframe.append(df_clientes_L_total)

    df_nvs_clientes_L =1 

#! Dataframes históricos
if os.path.isfile(carpeta_entrada + "BDD_Clientes_Histórica.csv"):

    df_historico = pd.read_csv(carpeta_entrada + "BDD_Clientes_Histórica.csv", sep=";", encoding = "UTF-8" )
    valores_mes = df_historico["mes_repartición"].unique()
else:
    print(f"No Existe BDD de Recaudación Histórica en: {carpeta_entrada}")
    df_historico = pd.DataFrame()
    valores_mes = []

# Verificar si el mes de cada df de mes ya se encuentra en el histórico
#! Unión de Dataframes
for i in dataframe:
    mes = str(i["mes_repartición"].unique()[0])
    if mes in valores_mes:
        print(f"El mes {mes} ya se encuentra en el histórico de la Recaudación")
    else: 

        df_historico = pd.concat([df_historico, i])
        print(f"Se incorpora el mes {mes} en el histórico de la Recaudación")


#! Salida de archivo retiros históricos        
ruta_salida = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Registro Histórico Clientes"