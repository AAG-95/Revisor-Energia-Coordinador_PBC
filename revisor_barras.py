# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 15:26:54 2022

@author: alonso.flores
"""

#!/usr/bin/env python
# coding: utf-8

# In[2]:
# Librerias a importar
import xlwings as xw  # librería que permite trabajar excel con python
import pandas as pd  # librería que permite la manipulación y tratamiento de datos
import csv  # librería que permite leer y guardar archivos csv
import datetime as dt
import numpy as np

# In[3]:
BDD_Zonal_Frecuente = r"C:/Registro Energia/BDD_Zonal_Frecuente_Barra.csv"
BDD_Zonal_Base = r"C:/Registro Energia/BDD_Base.csv"
BDD_Zonal_Repetido = r"C:/Registro Energia/BDD_Zonal_Repetido_Barra.csv"

carpeta = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Revisiones\Revisión Recaudación\BDD Revisión Recaudación\\"

# todo Dataframe Hoja 'Detalle-Clientes L'

df_clientes = pd.read_csv(
    carpeta + "Revisor_Clientes_resultado.csv",
    sep=",",
    encoding="UTF-8",
    header=0,
)

sitemas_unicos = df_clientes["Zonal"].unique()
nivel_tension_unicos = df_clientes["Nivel Tensión Zonal"].unique()

# Replace 0, . na, . and - as Nan
df_clientes["Zonal"] = df_clientes["Zonal"].replace(
    ["0", ".", "na", "NaN", "-"], np.nan
)

# make every value in the column upper case
df_clientes["Zonal"] = df_clientes["Zonal"].str.upper()

sitemas_unicos = df_clientes["Zonal"].unique()

df_clientes["Zonal_Nivel"] = (
    df_clientes["Zonal"] + "_" + df_clientes["Nivel Tensión Zonal"]
)

""" 
df_clientes_nvs = pd.read_csv(
    carpeta + "Revisor Clientes Libres_resultado.csv",
    sep=",",
    encoding="latin1",
    header=None,
)

if df_clientes_nvs:
    df_clientes_total = pd.concat([df_clientes, df_clientes_nvs])
else:
    df_clientes_total = df_clientes """

df_clientes_total = df_clientes


barras = df_clientes_total.groupby("Barra")["Zonal_Nivel"].apply(
    lambda x: x.value_counts().idxmax() if not x.value_counts().empty else None
).reset_index()

# Split Zonal_Nivel column by _ in two columns
barras[["Zonal", "Nivel Tensión Zonal"]] = barras[
    "Zonal_Nivel"
].str.split("_", expand=True)

barras = barras.drop(columns=["Zonal_Nivel"])



lista_sistema = ["SISTEMA A", "SISTEMA B", "SISTEMA C", "SISTEMA D", "SISTEMA E", "SISTEMA F", np.nan, "NaN", "nan", "na"]

lista_nivel_tension = ["220", "154", "110", "66", "33", "44", "23", "Tx < 25", np.nan, "NaN", "nan", "na"]

barras = barras[(barras["Zonal"].isin(lista_sistema) | barras["Zonal"].isna())]

barras = barras[(barras["Nivel Tensión Zonal"].isin(lista_nivel_tension) | barras["Nivel Tensión Zonal"].isna())]

barras.to_csv(carpeta + "Sistema_por_Barra.csv", sep=";", encoding="latin1", index=False)



""" 


# Direcciones (Actualizar este bloque de codigos)
Lista = []
Meses = [
    "Abr21",
    "Ago21",
    "Ago22",
    "Dic21",
    "Ene21",
    "Feb21",
    "Jul21",
    "Jul22",
    "Jun21",
    "Jun22",
    "Mar21",
    "May21",
    "May22",
    "Nov21",
    "Oct21",
    "Sep21",
    "Sep22",
]
Largo = 0

for i in Meses:
    Datos_Mes = (
        r"C:/Registro Energia/Revisión_" + i + ".xlsx"
    )  # Actualizar dirección de archivo xlsx a mes de recaudación actual

    # Uso de librería xlwings para ir a buscar los datos de recaudación en la planilla xlsx del mes actual (planilla guardada en Datos_Mes)
    R_mes = xw.Book(
        Datos_Mes
    )  # Se abre planilla de recaudación usando la librería xlwings para poder trabajar con ella
    Recaudacion_mes = R_mes.sheets[
        "Datos"
    ]  # se selecciona la hoja '3_Recaudación' desde la planilla de recaudación del mes actual
    Ultima_fila_mes = (
        Recaudacion_mes["A2"].expand("down").last_cell.row
    )  # Desde la casilla Q6 (casilla donde comienzan a registrare los datos buscados), se busca la última fila que tiene datos (diferente a "blanco")
    Ultima_celda_mes = "Q" + str(
        Ultima_fila_mes
    )  # Se selecciona la ultima celda, la cual se ubica en la última columna (AI en este caso) y última fila
    Rango_ultimo_mes = (
        "A1" + ":" + Ultima_celda_mes
    )  # Se obtiene el rango completo de datos del mes actual (considerando el encabezado)
    Datos_Nuevo_Mes = Recaudacion_mes.range(
        Rango_ultimo_mes
    )  # Se guardan los datos de recaudación en el rango específico en una variable

    df = Datos_Nuevo_Mes.options(
        pd.DataFrame, header=1, index=False, expand="table"
    ).value  # Se guardan los valores de recaudación del mes actual en un dataframe de pandas
    columns = [
        "Zonal",
        "Barra",
        "Cliente Individualizado",
        "Recaudador",
        "Nivel Tensión Zonal",
        "Mes de Facturación",
    ]
    df = pd.DataFrame(df, columns=columns)
    df = df[df.Zonal.notnull()]
    Lista.append(df)
    Largo = Largo + len(df)
    R_mes.save()  # Se guarda la planilla de recaudación del mes actual
    R_mes.close()  # Se cierra la planilla de recaudación del mes actual

BDD = pd.concat(Lista)
BDD.to_csv(
    BDD_Zonal_Base, encoding="latin1", index=True, sep=";"
)  # Finalmente se guardan los datos unidos del mes actual más los anteriores en un CSV, con codificación 'latin1' y separados por ';'

Zonal = BDD.groupby("Barra").agg(pd.Series.mode)
Zonal.to_csv(
    BDD_Zonal_Frecuente, encoding="latin1", index=True, sep=";"
)  # Finalmente se guardan los datos unidos del mes actual más los anteriores en un CSV, con codificación 'latin1' y separados por ';'

Repetidos = BDD.groupby("Barra").agg(["unique"])
Repetidos.to_csv(
    BDD_Zonal_Repetido, encoding="latin1", index=True, sep=";"
)  # Finalmente se guardan los datos unidos del mes actual más los anteriores en un CSV, con codificación 'latin1' y separados por ';'
 """
