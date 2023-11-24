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
import funciones as func  # Se importa un módulo personalizado llamado Funciones

# Versiones de las librerías utilizadas
# python version: 3.9.13
# openpyxl version: 3.0.10
# pandas version: 1.4.4

# Deshabilitar temporalmente las advertencias
warnings.filterwarnings("ignore")

# Carpeta salida de archivos
carpeta_salida = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Recaudación\\BDD Septiembre 2023\\"

# Definición de variables de año y mes
primer_año = 2023
último_año = 2023
primer_mes_primer_año = 9
último_mes_último_año = 9

# Genera una lista de pares de años y meses
pares_lista = func.generar_pares(
    primer_año, último_año, primer_mes_primer_año, último_mes_último_año
)

# Procesar cada par de años y meses
for par in pares_lista:
    count = 0  # Contador de archivos encontrados

    # Carpeta de entrada de archivos IFC por Carpeta
    carpeta = (
        r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\"
        + str(par[0])
        + "\\"
        + str(par[1])
        + "\\00 InfoRecibida\\IFC\\"
    ) 


    entries = os.scandir(carpeta)

    # Lista para almacenar los nombres de los archivos encontrados
    file_list = []

    # Listas para almacenar los dataframes resultantes
    dataframes = []  # Datos Clientes Libres
    dataframes_Nvs = []  # Datos Clientes Libres
    dataframes_regulados_E = []
    dataframes_regulados_R = []
    dataframes_libres_E = []
    dataframes_libres_R = []

    # Buscar archivos que cumplan ciertos criterios en la carpeta
    for val in entries:
        if (
            val.is_file()
            and ("VE" in val.name)
            and ("FIFC" in val.name)
            and not val.name.startswith("~$")
        ):
            count += 1
            file_list.append(val.name)

    # Procesar cada archivo encontrado
    for file_name in file_list:
        print(file_name)
        excel_file_path = carpeta + file_name
        
        # Obtener el nombre de la empresa
        nombre_empresa = re.findall(r"FIFC_(.*?)_RCUT", file_name)

        # todo Dataframe Hoja 'Detalle-Clientes L'
        df = pd.read_excel(
            excel_file_path, sheet_name="Detalle-Clientes L", engine="openpyxl", header=None
        )
        df = func.obtencion_Tablas(df, 11, 2)
        Columnas_energía = df.columns[9:]
        df[Columnas_energía] = df[Columnas_energía].replace({0: np.nan})
        df[Columnas_energía] = df[Columnas_energía].replace({np.nan: None})
        df[Columnas_energía] = df[Columnas_energía].replace({None: np.nan})
        df = df.dropna(subset=Columnas_energía, how="all")
        df[Columnas_energía] = df[Columnas_energía].replace({np.nan: ""})

        # Procesar columnas numéricas para reemplazar '.' con ','
        for column in df.columns[9:]:
            df[column] = df[column].astype(str).str.replace(".", ",", regex=False)

        

        # Convertir nombres de columnas de fecha
        timestamps = df.columns[9:]
        df.columns.values[9:] = [
            datetime.strftime(timestamp, "%d-%m-%Y") for timestamp in timestamps
        ]
        Mes_Rep = df.columns[9]
        df = df.assign(Mes_Repartición=Mes_Rep)

        # Seleccionar columnas relevantes y derretir el dataframe
        selected_columns = df.columns[:9].tolist() + [df.columns[-1]]
        df = pd.melt(
            df,
            id_vars=selected_columns,
            var_name="Mes Consumo",
            value_name="Energía [kWh]",
        )

        # Filtrar filas con valores no nulos
        df = df[(~df["Energía [kWh]"].isnull()) & (df["Energía [kWh]"] != "")]

        # Reemplazar valor SISTEMA por Sistema
        df["Zonal"] = df["Zonal"].str.replace(r"\bSISTEMA\b", "Sistema", regex=True)
        
        # Agregar columna Empresa
        df = df.assign(Empresa_Planilla=nombre_empresa[0])

        # Agregar el dataframe a la lista
        dataframes.append(df)

        # todo Dataframe Hoja 'Detalle- Nvs Clientes L'
        df_Nvs = pd.read_excel(
            excel_file_path, sheet_name="Detalle-Nvs Clientes L", engine="openpyxl", header=None
        )
        df_Nvs = func.obtencion_Tablas(df_Nvs, 11, 2)
        Columnas_energía = df_Nvs.columns[9:]
        df_Nvs[Columnas_energía] = df_Nvs[Columnas_energía].replace({0: np.nan})
        df_Nvs[Columnas_energía] = df_Nvs[Columnas_energía].replace({np.nan: None})
        df_Nvs[Columnas_energía] = df_Nvs[Columnas_energía].replace({None: np.nan})
        df_Nvs = df_Nvs.dropna(subset=Columnas_energía, how="all")
        df_Nvs[Columnas_energía] = df_Nvs[Columnas_energía].replace({np.nan: ""})

        # Procesar columnas numéricas para reemplazar '.' con ','
        for column in df_Nvs.columns[9:]:
            df_Nvs[column] = df_Nvs[column].astype(str).str.replace(".", ",", regex=False)

        

        # Convertir nombres de columnas de fecha
        timestamps = df_Nvs.columns[9:]
        df_Nvs.columns.values[9:] = [
            datetime.strftime(timestamp, "%d-%m-%Y") for timestamp in timestamps
        ]
        Mes_Rep = df_Nvs.columns[9]
        df_Nvs = df_Nvs.assign(Mes_Repartición=Mes_Rep)

        # Seleccionar columnas relevantes y derretir el dataframe
        selected_columns = df_Nvs.columns[:9].tolist() + [df_Nvs.columns[-1]]
        df_Nvs = pd.melt(
            df_Nvs,
            id_vars=selected_columns,
            var_name="Mes Consumo",
            value_name="Energía [kWh]",
        )

        # Filtrar filas con valores no nulos
        df_Nvs = df_Nvs[(~df_Nvs["Energía [kWh]"].isnull()) & (df_Nvs["Energía [kWh]"] != "")]

        # Reemplazar valor SISTEMA por Sistema
        df_Nvs["Zonal"] = df_Nvs["Zonal"].str.replace(r"\bSISTEMA\b", "Sistema", regex=True)
       
        # Agregar columna Empresa
        df_Nvs = df_Nvs.assign(Empresa_Planilla=nombre_empresa[0])
        
        # Agregar el dataframe a la lista
        dataframes_Nvs.append(df_Nvs)
        
        # todo Dataframe Hoja 'Formulario-Clientes L'

        df_FCL = pd.read_excel(
            excel_file_path, sheet_name="Formulario-Clientes L", engine="openpyxl", header=None
        )
        df_FCL = func.obtencion_Tablas(df_FCL, 19, 3)

        # Procesar datos de Clientes Libres

        df_FCL_E = df_FCL.iloc[:, :11]
        df_FCL_E = df_FCL_E[
            (~df_FCL_E["Observación"].isnull()) & (df_FCL_E["Observación"] != "")
        ]
        df_FCL_E = df_FCL_E.assign(Mes_Repartición=Mes_Rep)
        df_FCL_E = df_FCL_E.assign(Recaudador=nombre_empresa[0])

        # Procesar datos de Clientes Regulados
        df_FCL_R = df_FCL.iloc[:, 14:18]
        df_FCL_R = df_FCL_R[
            (~df_FCL_R["Observación"].isnull()) & (df_FCL_R["Observación"] != "")
        ]
        df_FCL_R = df_FCL_R.assign(Mes_Repartición=Mes_Rep)
        df_FCL_R = df_FCL_R.assign(Recaudador=nombre_empresa[0])

        # Dataframe Hoja 'Formulario-Clientes R'
        df_FCR_E = None  # Inicializar a None
        df_FCR_R = None  # Inicializar a None

        # todo Intentar leer la hoja 'Formulario-Clientes R' si existe
        try:
            df_FCR = pd.read_excel(
                excel_file_path, sheet_name="Formulario-Clientes R", engine="openpyxl", header=None
            )
            df_FCR = func.obtencion_Tablas(df_FCR, 19, 3)

            # Procesar datos de Clientes Regulados
            df_FCR_E = df_FCR.iloc[:, :11]
            df_FCR_E = df_FCR_E[
                (~df_FCL_E["Observación"].isnull()) & (df_FCR_E["Observación"] != "")
            ]
            df_FCR_E = df_FCR_E.assign(Mes_Repartición=Mes_Rep)
            df_FCR_E = df_FCR_E.assign(Recaudador=nombre_empresa[0])

            df_FCR_R = df_FCR.iloc[:, 14:22]
            df_FCR_R = df_FCR_R[
                (~df_FCR_R["Observación"].isnull()) & (df_FCR_R["Observación"] != "")
            ]
            df_FCR_R = df_FCR_R.assign(Mes_Repartición=Mes_Rep)
            df_FCR_R = df_FCR_R.assign(Recaudador=nombre_empresa[0])

        except:
            pass

        # Agregar dataframes a las listas correspondientes
        dataframes_libres_E.append(df_FCL_E)
        dataframes_libres_R.append(df_FCL_R)
        dataframes_regulados_E.append(df_FCR_E)
        dataframes_regulados_R.append(df_FCR_R)

        # Eliminar dataframes para liberar memoria
        del df, df_FCL_E, df_FCL_R, df_FCR_E, df_FCR_R

    # Procesar los dataframes y guardar los resultados
    func.process_data(carpeta_salida, dataframes, "Revisor_Clientes", par)

    func.process_data(carpeta_salida,  dataframes_Nvs, "Revisor_Clientes_Nuevos", par)
   

    func.process_data(
        carpeta_salida, dataframes_libres_E, "Observaciones Clientes Libres", par
    )
    func.process_data(
        carpeta_salida, dataframes_libres_R, "Revisor Clientes Libres", par
    )
    func.process_data(
        carpeta_salida, dataframes_regulados_E, "Observaciones Clientes Regulados", par
    )
    func.process_data(
        carpeta_salida, dataframes_regulados_R, "Revisor Clientes Regulados", par
    )

    # Eliminar los dataframes para liberar memoria
    del (
        dataframes,
        dataframes_Nvs,
        dataframes_libres_E,
        dataframes_libres_R,
        dataframes_regulados_E,
        dataframes_regulados_R,
    )
