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
import numpy as np
import openpyxl
import warnings
import funciones as func  # Se importa un módulo personalizado llamado Funciones


# Versiones de las librerías utilizadas
# python version: 3.9.13
# openpyxl version: 3.0.10
# pandas version: 1.4.4

print("Python version:", sys.version)
print("openpyxl version:", openpyxl.__version__)
print("pandas version:", pd.__version__)

# Deshabilitar temporalmente las advertencias
# warnings.filterwarnings("ignore")
warnings.filterwarnings(
    "ignore", message="Data Validation extension is not supported and will be removed"
)

warnings.filterwarnings('ignore', 'The default value of regex will change from True to False in a future version.')

# Definición de variables de año y mes
primer_año = 2020
primer_mes_primer_año = 6
último_año = 2023
último_mes_último_año = 12

# Genera una lista de pares de años y meses
pares_lista = func.ConversionDatos().generar_pares(
    primer_año, último_año, primer_mes_primer_año, último_mes_último_año
)

# Procesar cada par de años y meses
for par in pares_lista:
    mes_rep = func.ConversionDatos().convertir_numeral_datetime(par[1])

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
    dataframes = []  # Datos Clientes Libre s
    dataframes_Nvs = []  # Datos Clientes Libres
    dataframes_regulados = []  # Datos Clientes Regulados
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

        # Load the Excel file
        xls = pd.ExcelFile(excel_file_path)

        # Get the sheet names
        sheet_names = xls.sheet_names

        # Obtener el nombre de la empresa
        nombre_empresa = re.findall(r"FIFC_(.*?)_RCUT", file_name)

        # todo Dataframe Hoja 'Detalle-Clientes L'
        df = pd.read_excel(
            excel_file_path,
            sheet_name="Detalle-Clientes L",
            engine="openpyxl",
            header=None,
        )

        df = func.ObtencionDatos().obtencion_Tablas(df, 11, 2)
        Columnas_energía = df.columns[9:]

        df[Columnas_energía] = df[Columnas_energía].replace({0: np.nan})

        df[Columnas_energía] = df[Columnas_energía].replace({np.nan: None})
        df[Columnas_energía] = df[Columnas_energía].replace({None: np.nan})
        df = df.dropna(subset=Columnas_energía, how="all")

        df[Columnas_energía] = df[Columnas_energía].replace({np.nan: ""})

        # Procesar columnas numéricas para reemplazar '.' con ','
        # Convertir nombres de columnas de fecha
        timestamps = df.columns[9:]
        df.columns.values[9:] = [
            datetime.strftime(timestamp, "%d-%m-%Y") for timestamp in timestamps
        ]

        # Seleccionar columnas relevantes y derretir el dataframe
        selected_columns = df.columns[:9].tolist()

        df = pd.melt(
            df,
            id_vars=selected_columns,
            var_name="Mes Consumo",
            value_name="Energía [kWh]",
        )
        # Filtrar filas con valores no nulos
        df = df[(~df["Energía [kWh]"].isnull()) & (df["Energía [kWh]"] != "")]
        df["Energía [kWh]"] = (
            df["Energía [kWh]"].astype(str).str.replace(".", ",", regex=False)
        )

        # Reemplazar valor SISTEMA por Sistema
        df["Zonal"] = (
            df["Zonal"].astype(str).str.replace(r"\bSISTEMA\b", "Sistema", regex=True)
        )

        # Agregar columnas
        df = df.assign(mes_repartición=mes_rep)
        df = df.assign(Empresa_Planilla=nombre_empresa[0])

        df["Empresa_Planilla_Recauda_Cliente"] = np.where(
            df["Recaudador"] == df["Empresa_Planilla"], 1, 0
        )

        # Revisor para ver que el suministrador informa al recaudador 
        df["Energía [kWh]"] = df["Energía [kWh]"].replace('-', np.nan)
        df["Energía [kWh]"] = df["Energía [kWh]"].str.replace(",", ".").astype(float)
        df["Recaudador No Informado"] = np.where((df["Energía [kWh]"] > 0) & (df["Energía [kWh]"].isin(["", "-"])), 1, 0)
        df["Energía [kWh]"] = df["Energía [kWh]"].astype(str).replace('.', ',')
        

        # Eliminar filas con valores nulos en las columnas Barra, Clave y Suministrador
        df.dropna(subset=["Barra", "Clave", "Suministrador"], inplace=True)
        # Agregar el dataframe a la lista
        dataframes.append(df)

        # todo Dataframe Hoja 'Detalle- Nvs Clientes L'
        df_Nvs = pd.read_excel(
            excel_file_path,
            sheet_name="Detalle-Nvs Clientes L",
            engine="openpyxl",
            header=None,
        )
        df_Nvs = func.ObtencionDatos().obtencion_Tablas(df_Nvs, 11, 2)
        Columnas_energía = df_Nvs.columns[9:]
        df_Nvs[Columnas_energía] = df_Nvs[Columnas_energía].replace({0: np.nan})
        df_Nvs[Columnas_energía] = df_Nvs[Columnas_energía].replace({np.nan: None})
        df_Nvs[Columnas_energía] = df_Nvs[Columnas_energía].replace({None: np.nan})
        df_Nvs = df_Nvs.dropna(subset=Columnas_energía, how="all")
        df_Nvs[Columnas_energía] = df_Nvs[Columnas_energía].replace({np.nan: ""})

        # Procesar columnas numéricas para reemplazar '.' con ','
        for column in df_Nvs.columns[9:]:
            df_Nvs[column] = (
                df_Nvs[column].astype(str).str.replace(".", ",", regex=False)
            )

        # Convertir nombres de columnas de fecha
        timestamps = df_Nvs.columns[9:]
        df_Nvs.columns.values[9:] = [
            datetime.strftime(timestamp, "%d-%m-%Y") for timestamp in timestamps
        ]

        # Seleccionar columnas relevantes y derretir el dataframe
        columnas_melt = df_Nvs.columns[:9].tolist()

        df_Nvs = pd.melt(
            df_Nvs,
            id_vars=columnas_melt,
            var_name="Mes Consumo",
            value_name="Energía [kWh]",
        )

        # Filtrar filas con valores no nulos
        df_Nvs = df_Nvs[
            (~df_Nvs["Energía [kWh]"].isnull()) & (df_Nvs["Energía [kWh]"] != "")
        ]

        df_Nvs["Zonal"] = (
            df_Nvs["Zonal"]
            .astype(str)
            .str.replace(r"\bSISTEMA\b", "Sistema", regex=True)
        )

        df_Nvs = df_Nvs.assign(mes_repartición=mes_rep)
        df_Nvs = df_Nvs.assign(Empresa_Planilla=nombre_empresa[0])

        df_Nvs["Empresa_Planilla_Recauda_Cliente"] = np.where(
            df_Nvs["Recaudador"] == df_Nvs["Empresa_Planilla"], 1, 0
        )
        df_Nvs["Empresa_Planilla_Recauda_Cliente"] = np.where(
            df_Nvs["Recaudador"] == df_Nvs["Empresa_Planilla"], 1, 0
        )
        
        # Revisor para ver que el suministrador informa al recaudador

        df_Nvs["Energía [kWh]"] = df_Nvs["Energía [kWh]"].str.replace(",", ".").astype(float)
        df_Nvs["Recaudador No Informado"] = np.where((df_Nvs["Energía [kWh]"] > 0) & (df_Nvs["Energía [kWh]"].isin(["", "-"])), 1, 0)
        df_Nvs["Energía [kWh]"] = df_Nvs["Energía [kWh]"].astype(str).replace('.', ',')   
     

        # Eliminar filas con valores nulos en las columnas Barra, Clave y Suministrador
        df_Nvs.dropna(subset=["Barra", "Clave", "Suministrador"], inplace=True)

        # Agregar el dataframe a la lista
        dataframes_Nvs.append(df_Nvs)

        # todo Dataframe Hoja 'Formulario-Clientes L'

        df_FCL = pd.read_excel(
            excel_file_path,
            sheet_name="Formulario-Clientes L",
            engine="openpyxl",
            header=None,
        )
        df_FCL = func.ObtencionDatos().obtencion_Tablas(df_FCL, 19, 3)

        # Procesar datos de Clientes Libres
        df_FCL_E = df_FCL.iloc[:, :11]
        df_FCL_E = df_FCL_E[
            (~df_FCL_E["Observación"].isnull()) & (df_FCL_E["Observación"] != "")
        ]

        df_FCL_E[
            ["Cargo [$/kWh]", "Recaudación [$]", "Energía facturada [kWh]"]
        ] = df_FCL_E[
            ["Cargo [$/kWh]", "Recaudación [$]", "Energía facturada [kWh]"]
        ].astype(
            str
        )

        df_FCL_E["Cargo [$/kWh]"] = (
            df_FCL_E["Cargo [$/kWh]"].astype(str).str.replace(".", ",")
        )

        df_FCL_E["Energía facturada [kWh]"] = (
            df_FCL_E["Energía facturada [kWh]"].astype(str).str.replace(".", ",")
        )

        df_FCL_E["Recaudación [$]"] = (
            df_FCL_E["Recaudación [$]"].astype(str).str.replace(".", ",")
        )

        df_FCL_E = df_FCL_E.assign(mes_repartición=mes_rep)
        df_FCL_E = df_FCL_E.assign(Recaudador=nombre_empresa[0])

        # Revisor de Formulario Clientes Libres
        df_FCL_R = df_FCL.iloc[:, 15:18]
        df_FCL_R = df_FCL_R[
            (~df_FCL_R["Observación"].isnull()) & (df_FCL_R["Observación"] != "")
        ]
        df_FCL_R = df_FCL_R.assign(mes_repartición=mes_rep)
        df_FCL_R = df_FCL_R.assign(Recaudador=nombre_empresa[0])

        df_FCL_R["Observación"] = (
            df_FCL_R["Observación"].astype(str).str.replace(".", ",")
        )

        # todo Intentar leer la hoja 'Formulario-Clientes R' si existe
        # Dataframe Hoja 'Formulario-Clientes R'
        df_FCR = None  # Inicializar a None
        df_FCR_E = None  # Inicializar a None
        df_FCR_R = None  # Inicializar a None

        if "Formulario-Clientes R" in sheet_names:
            df_FCR = pd.read_excel(
                excel_file_path,
                sheet_name="Formulario-Clientes R",
                engine="openpyxl",
                header=None,
            )
            df_FCR = func.ObtencionDatos().obtencion_Tablas(df_FCR, 19, 3)

            # Procesar datos de Clientes Regulados
            df_FCR_E = df_FCR.iloc[:, :11]
           
            df_FCR_E = df_FCR_E.assign(mes_repartición=mes_rep)
            df_FCR_E = df_FCR_E.assign(Recaudador=nombre_empresa[0])

            # Columnas a string
            df_FCR_E[
                ["Cargo [$/kWh]", "Recaudación [$]", "Energía facturada [kWh]"]
            ] = df_FCR_E[
                ["Cargo [$/kWh]", "Recaudación [$]", "Energía facturada [kWh]"]
            ].astype(
                str
            )

            df_FCR_E["Cargo [$/kWh]"] = (
                df_FCR_E["Cargo [$/kWh]"].astype(str).str.replace(".", ",")
            )
            df_FCR_E["Energía facturada [kWh]"] = (
                df_FCR_E["Energía facturada [kWh]"].astype(str).str.replace(".", ",")
            )
            df_FCR_E["Recaudación [$]"] = (
                df_FCR_E["Recaudación [$]"].astype(str).str.replace(".", ",")
            )

            dataframes_regulados.append(df_FCR_E[(df_FCR_E["Segmento"] == "Nacional") & (df_FCR_E["Energía facturada [kWh]"].isnull() | df_FCR_E["Energía facturada [kWh]"] == 0)])

            df_FCR_E = df_FCR_E[
                (~df_FCL_E["Observación"].isnull()) & (df_FCR_E["Observación"] != "")
            ]

            df_FCR_R = df_FCR.iloc[:, 14:22]
            # si existe columns llamada Observación_2 cambiar el nombre a Observación
            if "Observación_2" in df_FCR_R.columns:
                df_FCR_R = df_FCR_R.rename(columns={"Observación_2": "SSCC"})

            df_FCR_R = df_FCR_R[
                (~df_FCR_R["Observación"].isnull()) & (df_FCR_R["Observación"] != "")
            ]

            df_FCR_R = df_FCR_R.assign(mes_repartición=mes_rep)
            df_FCR_R = df_FCR_R.assign(Recaudador=nombre_empresa[0])

            df_FCR_R["Nacional"] = (
                df_FCR_R["Nacional"].astype(str).str.replace(".", ",")
            )

            df_FCR_R["Exenciones Peajes de Inyección"] = (
                df_FCR_R["Exenciones Peajes de Inyección"]
                .astype(str)
                .str.replace(".", ",")
            )

            df_FCR_R["Pago Peajes de Retiros"] = (
                df_FCR_R["Pago Peajes de Retiros"].astype(str).str.replace(".", ",")
            )

            df_FCR_R["Zonal"] = df_FCR_R["Zonal"].astype(str).str.replace(".", ",")

            df_FCR_R["SSCC"] = df_FCR_R["SSCC"].astype(str).str.replace(".", ",")

            df_FCR_R["Dedicado"] = (
                df_FCR_R["Dedicado"].astype(str).str.replace(".", ",")
            )

            dataframes_regulados_E.append(df_FCR_E)
            dataframes_regulados_R.append(df_FCR_R)

            del df_FCR, df_FCR_E, df_FCR_R

        # Agregar dataframes a las listas correspondientes
        dataframes_libres_E.append(df_FCL_E)
        dataframes_libres_R.append(df_FCL_R)

        # Eliminar dataframes para liberar memoria
        del df, df_FCL_E, df_FCL_R

    # Define the list of dataframes and corresponding output file names
    dataframes_list = [
        (dataframes, "Clientes_"),
        (dataframes_Nvs, "Clientes Nuevos_"),
        (dataframes_libres_E, "Observaciones Clientes Libres_"),
        (dataframes_libres_R, "Revisor Clientes Libres_"),
        (dataframes_regulados, "Formularios Clientes Regulados_"), 
        (dataframes_regulados_E, "Observaciones Clientes Regulados_"),
        (dataframes_regulados_R, "Revisor Clientes Regulados_"),
    ]

    # Process the dataframes and save the results
    for df, filename in dataframes_list:
        print(filename)
        # Carpeta salida de archivos
        carpeta_salida = rf"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Recaudación\\Revisiones Mensuales\\"

        # Create Folder in carpeta_Salida with name "BDD"
        if not os.path.exists(carpeta_salida + "BDD"):
            os.makedirs(carpeta_salida + "BDD_" + str(par[1]), exist_ok=True)
        else:
            sys.exit("La carpeta BDD_" + str(par[1]) + "ya existe")

        func.ProcesamientosDeDatos().process_data(
            carpeta_salida + "BDD_" + str(par[1]) + "\\", df, filename, par
        )

    # Eliminar los dataframes para liberar memoria
    del dataframes_list
    # Eliminar los dataframes para liberar memoria
    del (
        dataframes,
        dataframes_Nvs,
        dataframes_libres_E,
        dataframes_libres_R,
        dataframes_regulados, 
        dataframes_regulados_E,
        dataframes_regulados_R,
    )
