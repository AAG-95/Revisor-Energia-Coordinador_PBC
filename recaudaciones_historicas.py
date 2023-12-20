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
último_mes_último_año = 8

# Genera una lista de pares de años y meses
pares_lista = func.ConversionDatos().generar_pares(
    primer_año, último_año, primer_mes_primer_año, último_mes_último_año
)

carpeta_entrada = rf"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Recaudación\\"

# Convert values
dataframe_clientes = []
dataframe_observaciones = []
dataframe_revisor_clientes_L = []
dataframe_revisor_clientes_R = []
meses_rep = []

for par in pares_lista:

    #? Histórico de Clientes
    df_clientes_L = pd.read_csv(carpeta_entrada + "Revisiones Mensuales\\BDD_" + str(par[1]) +"\\" + "Clientes_" + str(par[1]) + ".csv" , encoding="UTF-8", sep=";", header=0)

    df_nvs_clientes_L = pd.read_csv(carpeta_entrada + "Revisiones Mensuales\\BDD_" + str(par[1]) +"\\" + "Clientes_Nuevos_" + str(par[1]) + ".csv" , encoding="UTF-8", sep=";", header=0)

    df_clientes_L_total = pd.concat([df_clientes_L, df_nvs_clientes_L], ignore_index=True)
    

    dataframe_clientes.append(df_clientes_L_total)
    
    #? Histórico de Observaciones
    df_observaciones_clientes_L = pd.read_csv(carpeta_entrada + "Revisiones Mensuales\\BDD_" + str(par[1]) +"\\" + "Observaciones Clientes Libres_" + str(par[1]) + ".csv" , encoding="UTF-8", sep=";", header=0)

    df_observaciones_clientes_L["Tipo Cliente"] = "L"

    df_observaciones_clientes_R = pd.read_csv(carpeta_entrada + "Revisiones Mensuales\\BDD_" + str(par[1]) +"\\" + "Observaciones Clientes Regulados_" + str(par[1]) + ".csv" , encoding="UTF-8", sep=";", header=0)

    df_observaciones_clientes_R["Tipo Cliente"] = "R"

    df_observaciones_total = pd.concat([df_observaciones_clientes_L, df_observaciones_clientes_R], ignore_index=True)
    
    dataframe_observaciones.append(df_observaciones_total)

    #? Histórico de Revisor de Clientes Libres
    df_revisor_clientes_L = pd.read_csv(carpeta_entrada + "Revisiones Mensuales\\BDD_" + str(par[1]) +"\\" + "Revisor Clientes Libres_" + str(par[1]) + ".csv" , encoding="UTF-8", sep=";", header=0)

    dataframe_revisor_clientes_L.append(df_revisor_clientes_L)

    #? Histórico de Revisor de Clientes Regulados
    df_revisor_clientes_R = pd.read_csv(carpeta_entrada + "Revisiones Mensuales\\BDD_" + str(par[1]) +"\\" + "Revisor Clientes Regulados_" + str(par[1]) + ".csv" , encoding="UTF-8", sep=";", header=0)

    dataframe_revisor_clientes_R.append(df_revisor_clientes_R)
    
    mes_rep = str(df_clientes_L["mes_repartición"].unique()[0])
    meses_rep.append(mes_rep)

#! Dataframes históricos
    
lista_nombre_archivos = ["BDD Clientes Históricos.csv", "BDD Observaciones Históricas.csv", "BDD Revisor Clientes L Históricos.csv", "BDD Revisor Clientes R Históricos.csv"]

lista_df_historicos = [None for i in range(4)]

for idx, nombre_archivo in enumerate(lista_nombre_archivos):
    print(carpeta_entrada + "Revisión Histórica\\"+ nombre_archivo)
    if os.path.isfile(carpeta_entrada + "Revisión Histórica\\"+ nombre_archivo):
        lista_df_historicos[idx] = pd.read_csv(carpeta_entrada + "Revisión Histórica\\"+ nombre_archivo, sep=";", encoding = "UTF-8", header=0 )
        if idx == 0:
            valores_mes = lista_df_historicos[idx]["mes_repartición"].unique()
    else:
        print(f"No Existe {nombre_archivo} en: {carpeta_entrada}")
        lista_df_historicos[idx] = pd.DataFrame()
        if idx == 0:
            valores_mes = []


#! Unión de Dataframes
# Verificar si el mes de cada df de mes ya se encuentra en el histórico
lista_dataframes_mes_analizado = [dataframe_clientes, dataframe_observaciones, dataframe_revisor_clientes_L, dataframe_revisor_clientes_R]

lista_nombre_archivos = ["BDD Clientes Históricos.csv", "BDD Observaciones Históricas.csv", "BDD Revisor Clientes L Históricos.csv", "BDD Revisor Clientes R Históricos.csv"]

# Verificar si el mes de cada df de mes ya se encuentra en el histórico, si no, se incorpora
for idx, (lista_dataframe, nombre_archivo) in enumerate(zip(lista_dataframes_mes_analizado, lista_nombre_archivos)):
    print(f"Actualización archivo {nombre_archivo}")
    
    for i, mes_rep in zip(lista_dataframe, meses_rep):
        # Verificar que el dataframe no esté vacío
        meses_unicos = i["mes_repartición"].unique()
        if len(meses_unicos) > 0 :
            mes_df = str(i["mes_repartición"].unique()[0])
        else:
            print(len(meses_unicos))
            df_vacio = True
           
        # Verificar si el mes de cada df de mes ya se encuentra en el histórico            
        if mes_df in valores_mes or df_vacio:
            print(f"El mes {mes_rep} ya se encuentra en el en el histórico de la {nombre_archivo} o es un dataframe vacío")
        else: 
            lista_df_historicos[idx] = pd.concat([lista_df_historicos[idx], i])
            print(f"Se incorpora el mes {mes_df} en el histórico de la {nombre_archivo}")

#! Salida de archivo retiros históricos        
carpeta_salida = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Recaudación\\Revisión Histórica\\" 

for variable, nombre_archivo in zip(lista_df_historicos, lista_nombre_archivos):
    variable.to_csv(carpeta_salida + nombre_archivo, sep=";", encoding="UTF-8", index=False)

