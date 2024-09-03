# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 11:12:18 2023
@author: alonso.flores
"""

# Importación de librerías necesarias
import traceback
import os
import sys
import pandas as pd
import re
from datetime import datetime
import numpy as np
import openpyxl
import warnings
import funciones as func  # Se importa un módulo personalizado llamado Funciones

warning_messages = [
    "Data Validation extension is not supported and will be removed",
    "The default value of regex will change from True to False in a future version.",
]
for message in warning_messages:
    warnings.filterwarnings("ignore", message=message)
class PlanillaRevisor:

    def __init__(
        self, primer_año, último_año, primer_mes_primer_año, último_mes_último_año
    ):
        self.primer_año = primer_año
        self.último_año = último_año
        self.primer_mes_primer_año = primer_mes_primer_año
        self.último_mes_último_año = último_mes_último_año
        self.pares_lista = func.ConversionDatos().generar_pares(
            primer_año, último_año, primer_mes_primer_año, último_mes_último_año
        )

    def run(self):
        # Wrap your main code in a try/except block
        try:
            print("Python version:", sys.version)
            print("openpyxl version:", openpyxl.__version__)
            print("pandas version:", pd.__version__)

            # Deshabilitar temporalmente las advertencias
            # warnings.filterwarnings("ignore")

            self.process_files()
        except Exception as e:
            # This will print the type, value, and traceback of the exception
            traceback.print_exc()

    def process_files(self):

        # Procesar cada par de años y meses
        for par in self.pares_lista:
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

                # Obtener las hojas del archivo
                sheet_names = xls.sheet_names

                # Obtener el nombre de la empresa
                nombre_empresa = re.findall(r"FIFC_(.*?)_RCUT", file_name)

                # todo Dataframe Hoja 'Detalle-Clientes L'
                
                df_detalle_clientes_libres = pd.read_excel(
                    xls,
                    sheet_name="Detalle-Clientes L",
                    engine="openpyxl",
                    header=None,
                )

                df_detalle_clientes_libres = func.ObtencionDatos().obtencion_Tablas(df_detalle_clientes_libres, 11, 2)
                Columnas_energía = df_detalle_clientes_libres.columns[9:]

                df_detalle_clientes_libres[Columnas_energía] = df_detalle_clientes_libres[Columnas_energía].replace({0: np.nan})
                df_detalle_clientes_libres[Columnas_energía] = df_detalle_clientes_libres[Columnas_energía].replace({np.nan: None})
                df_detalle_clientes_libres[Columnas_energía] = df_detalle_clientes_libres[Columnas_energía].replace({None: np.nan})
                df_detalle_clientes_libres = df_detalle_clientes_libres.dropna(subset=Columnas_energía, how="all")

                df_detalle_clientes_libres[Columnas_energía] = df_detalle_clientes_libres[Columnas_energía].replace({np.nan: ""})

                # Procesar columnas numéricas para reemplazar '.' con ','
                # Convertir nombres de columnas de fecha
                timestamps = df_detalle_clientes_libres.columns[9:]
                df_detalle_clientes_libres.columns.values[9:] = [
                    datetime.strftime(timestamp, "%d-%m-%Y") for timestamp in timestamps
                ]

                # Seleccionar columnas relevantes y derretir el dataframe
                selected_columns = df_detalle_clientes_libres.columns[:9].tolist()

                df_detalle_clientes_libres = pd.melt(
                    df_detalle_clientes_libres,
                    id_vars=selected_columns,
                    var_name="Mes Consumo",
                    value_name="Energía [kWh]",
                )
                # Filtrar filas con valores no nulos
                df_detalle_clientes_libres = df_detalle_clientes_libres[(~df_detalle_clientes_libres["Energía [kWh]"].isnull()) & (df_detalle_clientes_libres["Energía [kWh]"] != "")]
                df_detalle_clientes_libres["Energía [kWh]"] = (
                    df_detalle_clientes_libres["Energía [kWh]"].astype(str).str.replace(".", ",", regex=False)
                )

                # Reemplazar valor SISTEMA por Sistema
                df_detalle_clientes_libres["Zonal"] = (
                    df_detalle_clientes_libres["Zonal"]
                    .astype(str)
                    .str.replace(r"\bSISTEMA\b", "Sistema", regex=True)
                )

                # Agregar columnas
                df_detalle_clientes_libres = df_detalle_clientes_libres.assign(mes_repartición=mes_rep)
                df_detalle_clientes_libres = df_detalle_clientes_libres.assign(Empresa_Planilla=nombre_empresa[0])

                 # Convertir a mayúsculas
                df_detalle_clientes_libres["Empresa_Planilla"] = df_detalle_clientes_libres["Empresa_Planilla"].str.upper()
                df_detalle_clientes_libres["Recaudador"] = df_detalle_clientes_libres["Recaudador"].str.upper()

                df_detalle_clientes_libres["Empresa_Planilla_Recauda_Cliente"] = np.where(
                    df_detalle_clientes_libres["Recaudador"] == df_detalle_clientes_libres["Empresa_Planilla"], 1, 0
                )
               
                # Revisor para ver que el suministrador informa al recaudador
                df_detalle_clientes_libres["Energía [kWh]"] = df_detalle_clientes_libres["Energía [kWh]"].replace(["-", ""], np.nan)
                df_detalle_clientes_libres["Energía [kWh]"] = pd.to_numeric(
                    df_detalle_clientes_libres["Energía [kWh]"].astype(str).str.replace(",", "."),
                    errors="coerce",
                )
                # df_detalle_clientes_libres["Energía [kWh]"] = df_detalle_clientes_libres["Energía [kWh]"].str.replace(",", ".").astype(float)
                df_detalle_clientes_libres["Recaudador No Informado"] = np.where(
                    (df_detalle_clientes_libres["Energía [kWh]"] > 0) & (df_detalle_clientes_libres["Energía [kWh]"].isin(["", "-"])),
                    1,
                    0,
                )
                df_detalle_clientes_libres["Energía [kWh]"] = (
                    df_detalle_clientes_libres["Energía [kWh]"].astype(str).str.replace(".", ",", regex=False)
                )

                # Eliminar filas con valores nulos en las columnas Barra, Clave y Suministrador
                df_detalle_clientes_libres.dropna(subset=["Barra", "Clave", "Suministrador"], inplace=True)
                # Agregar el dataframe a la lista
                dataframes.append(df_detalle_clientes_libres)

                # todo Dataframe Hoja 'Detalle- Nvs Clientes L'
                df_detalle_nuevos_clientes_libres = pd.read_excel(
                    xls,
                    sheet_name="Detalle-Nvs Clientes L",
                    engine="openpyxl",
                    header=None,
                )
                df_detalle_nuevos_clientes_libres = func.ObtencionDatos().obtencion_Tablas(df_detalle_nuevos_clientes_libres, 11, 2)
                Columnas_energía = df_detalle_nuevos_clientes_libres.columns[9:]
                df_detalle_nuevos_clientes_libres[Columnas_energía] = df_detalle_nuevos_clientes_libres[Columnas_energía].replace({0: np.nan})
                df_detalle_nuevos_clientes_libres[Columnas_energía] = df_detalle_nuevos_clientes_libres[Columnas_energía].replace(
                    {np.nan: None}
                )
                df_detalle_nuevos_clientes_libres[Columnas_energía] = df_detalle_nuevos_clientes_libres[Columnas_energía].replace(
                    {None: np.nan}
                )
                df_detalle_nuevos_clientes_libres = df_detalle_nuevos_clientes_libres.dropna(subset=Columnas_energía, how="all")
                df_detalle_nuevos_clientes_libres[Columnas_energía] = df_detalle_nuevos_clientes_libres[Columnas_energía].replace(
                    {np.nan: ""}
                )

                # Procesar columnas numéricas para reemplazar '.' con ','
                for column in df_detalle_nuevos_clientes_libres.columns[9:]:
                    df_detalle_nuevos_clientes_libres[column] = (
                        df_detalle_nuevos_clientes_libres[column].astype(str).str.replace(".", ",", regex=False)
                    )

                # Convertir nombres de columnas de fecha
                timestamps = df_detalle_nuevos_clientes_libres.columns[9:]
                df_detalle_nuevos_clientes_libres.columns.values[9:] = [
                    datetime.strftime(timestamp, "%d-%m-%Y") for timestamp in timestamps
                ]

                # Seleccionar columnas relevantes y derretir el dataframe
                columnas_melt = df_detalle_nuevos_clientes_libres.columns[:9].tolist()

                df_detalle_nuevos_clientes_libres = pd.melt(
                    df_detalle_nuevos_clientes_libres,
                    id_vars=columnas_melt,
                    var_name="Mes Consumo",
                    value_name="Energía [kWh]",
                )

                # Filtrar filas con valores no nulos
                df_detalle_nuevos_clientes_libres = df_detalle_nuevos_clientes_libres[
                    (~df_detalle_nuevos_clientes_libres["Energía [kWh]"].isnull())
                    & (df_detalle_nuevos_clientes_libres["Energía [kWh]"] != "")
                ]

                df_detalle_nuevos_clientes_libres["Zonal"] = (
                    df_detalle_nuevos_clientes_libres["Zonal"]
                    .astype(str)
                    .str.replace(r"\bSISTEMA\b", "Sistema", regex=True)
                )

                df_detalle_nuevos_clientes_libres = df_detalle_nuevos_clientes_libres.assign(mes_repartición=mes_rep)
                df_detalle_nuevos_clientes_libres = df_detalle_nuevos_clientes_libres.assign(Empresa_Planilla=nombre_empresa[0])

                df_detalle_nuevos_clientes_libres["Empresa_Planilla_Recauda_Cliente"] = np.where(
                    df_detalle_nuevos_clientes_libres["Recaudador"] == df_detalle_nuevos_clientes_libres["Empresa_Planilla"], 1, 0
                )
                df_detalle_nuevos_clientes_libres["Empresa_Planilla_Recauda_Cliente"] = np.where(
                    df_detalle_nuevos_clientes_libres["Recaudador"] == df_detalle_nuevos_clientes_libres["Empresa_Planilla"], 1, 0
                )

                # Revisor para ver que el suministrador informa al recaudador
                df_detalle_nuevos_clientes_libres["Energía [kWh]"] = (
                    df_detalle_nuevos_clientes_libres["Energía [kWh]"].str.replace(",", ".").astype(float)
                )
                df_detalle_nuevos_clientes_libres["Recaudador No Informado"] = np.where(
                    (df_detalle_nuevos_clientes_libres["Energía [kWh]"] > 0)
                    & (df_detalle_nuevos_clientes_libres["Energía [kWh]"].isin(["", "-"])),
                    1,
                    0,
                )
                df_detalle_nuevos_clientes_libres["Energía [kWh]"] = (
                    df_detalle_nuevos_clientes_libres["Energía [kWh]"].astype(str).str.replace(".", ",")
                )

                # Eliminar filas con valores nulos en las columnas Barra, Clave y Suministrador
                df_detalle_nuevos_clientes_libres.dropna(subset=["Barra", "Clave", "Suministrador"], inplace=True)

                # Agregar el dataframe a la lista
                dataframes_Nvs.append(df_detalle_nuevos_clientes_libres)

                # todo Dataframe Hoja 'Formulario-Clientes L'

                df_formulario_clientes_libres = pd.read_excel(
                    xls,
                    sheet_name="Formulario-Clientes L",
                    engine="openpyxl",
                    header=None,
                )
                df_formulario_clientes_libres = func.ObtencionDatos().obtencion_Tablas(df_formulario_clientes_libres, 19, 3)

                # Procesar datos de Clientes Libres
                df_formulario_clientes_libres_energia = df_formulario_clientes_libres.iloc[:, :11]
                df_formulario_clientes_libres_energia = df_formulario_clientes_libres_energia[
                    (~df_formulario_clientes_libres_energia["Observación"].isnull())
                    & (df_formulario_clientes_libres_energia["Observación"] != "")
                ]

                df_formulario_clientes_libres_energia[
                    ["Cargo [$/kWh]", "Recaudación [$]", "Energía facturada [kWh]"]
                ] = df_formulario_clientes_libres_energia[
                    ["Cargo [$/kWh]", "Recaudación [$]", "Energía facturada [kWh]"]
                ].astype(
                    str
                )

                df_formulario_clientes_libres_energia["Cargo [$/kWh]"] = (
                    df_formulario_clientes_libres_energia["Cargo [$/kWh]"]
                    .astype(str)
                    .str.replace(".", ",", regex=False)
                )

                df_formulario_clientes_libres_energia["Energía facturada [kWh]"] = (
                    df_formulario_clientes_libres_energia["Energía facturada [kWh]"]
                    .astype(str)
                    .str.replace(".", ",", regex=False)
                )

                df_formulario_clientes_libres_energia["Recaudación [$]"] = (
                    df_formulario_clientes_libres_energia["Recaudación [$]"]
                    .astype(str)
                    .str.replace(".", ",", regex=False)
                )

                df_formulario_clientes_libres_energia = df_formulario_clientes_libres_energia.assign(mes_repartición=mes_rep)
                df_formulario_clientes_libres_energia = df_formulario_clientes_libres_energia.assign(Recaudador=nombre_empresa[0])

                # Revisor de Formulario Clientes Libres
                df_formulario_clientes_libres_revision = df_formulario_clientes_libres.iloc[:, 15:18]
                df_formulario_clientes_libres_revision = df_formulario_clientes_libres_revision[
                    (~df_formulario_clientes_libres_revision["Observación"].isnull())
                    & (df_formulario_clientes_libres_revision["Observación"] != "")
                ]
                df_formulario_clientes_libres_revision = df_formulario_clientes_libres_revision.assign(mes_repartición=mes_rep)
                df_formulario_clientes_libres_revision = df_formulario_clientes_libres_revision.assign(Recaudador=nombre_empresa[0])

                df_formulario_clientes_libres_revision["Observación"] = (
                    df_formulario_clientes_libres_revision["Observación"]
                    .astype(str)
                    .str.replace(".", ",", regex=False)
                )

                # todo Intentar leer la hoja 'Formulario-Clientes R' si existe
                # Dataframe Hoja 'Formulario-Clientes R'

                df_formulario_clientes_regulados_energia = None  # Inicializar a None
                df_formulario_clientes_regulados_revision = None  # Inicializar a None

                if "Formulario-Clientes R" in sheet_names:
                    df_formulario_clientes_regulados = pd.read_excel(
                        xls,
                        sheet_name="Formulario-Clientes R",
                        engine="openpyxl",
                        header=None,
                    )
                    df_formulario_clientes_regulados = func.ObtencionDatos().obtencion_Tablas(df_formulario_clientes_regulados, 19, 3)

                    # Procesar datos de Clientes Regulados
                    df_formulario_clientes_regulados_energia = df_formulario_clientes_regulados.iloc[:, :11]

                    df_formulario_clientes_regulados_energia = df_formulario_clientes_regulados_energia.assign(mes_repartición=mes_rep)
                    df_formulario_clientes_regulados_energia = df_formulario_clientes_regulados_energia.assign(Recaudador=nombre_empresa[0])

                    # Columnas a string
                    df_formulario_clientes_regulados_energia[
                        ["Cargo [$/kWh]", "Recaudación [$]", "Energía facturada [kWh]"]
                    ] = df_formulario_clientes_regulados_energia[
                        ["Cargo [$/kWh]", "Recaudación [$]", "Energía facturada [kWh]"]
                    ].astype(
                        str
                    )

                    df_formulario_clientes_regulados_energia["Cargo [$/kWh]"] = (
                        df_formulario_clientes_regulados_energia["Cargo [$/kWh]"].astype(str).str.replace(".", ",")
                    )
                    df_formulario_clientes_regulados_energia["Energía facturada [kWh]"] = (
                        df_formulario_clientes_regulados_energia["Energía facturada [kWh]"]
                        .astype(str)
                        .str.replace(".", ",")
                    )
                    df_formulario_clientes_regulados_energia["Recaudación [$]"] = (
                        df_formulario_clientes_regulados_energia["Recaudación [$]"].astype(str).str.replace(".", ",")
                    )

                    dataframes_regulados.append(
                        df_formulario_clientes_regulados_energia[
                            (df_formulario_clientes_regulados_energia["Segmento"] == "Nacional")
                            & ~(
                                df_formulario_clientes_regulados_energia["Energía facturada [kWh]"].isnull()
                                | df_formulario_clientes_regulados_energia["Energía facturada [kWh]"]
                                == 0
                            )
                        ]
                    )

                    df_formulario_clientes_regulados_energia = df_formulario_clientes_regulados_energia[
                        (~df_formulario_clientes_libres_energia["Observación"].isnull())
                        & (df_formulario_clientes_regulados_energia["Observación"] != "")
                    ]

                    df_formulario_clientes_regulados_revision = df_formulario_clientes_regulados.iloc[:, 14:22]
                    # si existe columns llamada Observación_2 cambiar el nombre a Observación
                    if "Observación_2" in df_formulario_clientes_regulados_revision.columns:
                        df_formulario_clientes_regulados_revision = df_formulario_clientes_regulados_revision.rename(columns={"Observación_2": "SSCC"})

                    df_formulario_clientes_regulados_revision = df_formulario_clientes_regulados_revision[
                        (~df_formulario_clientes_regulados_revision["Observación"].isnull())
                        & (df_formulario_clientes_regulados_revision["Observación"] != "")
                    ]

                    df_formulario_clientes_regulados_revision = df_formulario_clientes_regulados_revision.assign(mes_repartición=mes_rep)
                    df_formulario_clientes_regulados_revision = df_formulario_clientes_regulados_revision.assign(Recaudador=nombre_empresa[0])

                    df_formulario_clientes_regulados_revision["Nacional"] = (
                        df_formulario_clientes_regulados_revision["Nacional"].astype(str).str.replace(".", ",")
                    )

                    df_formulario_clientes_regulados_revision["Exenciones Peajes de Inyección"] = (
                        df_formulario_clientes_regulados_revision["Exenciones Peajes de Inyección"]
                        .astype(str)
                        .str.replace(".", ",")
                    )

                    df_formulario_clientes_regulados_revision["Pago Peajes de Retiros"] = (
                        df_formulario_clientes_regulados_revision["Pago Peajes de Retiros"]
                        .astype(str)
                        .str.replace(".", ",")
                    )

                    df_formulario_clientes_regulados_revision["Zonal"] = (
                        df_formulario_clientes_regulados_revision["Zonal"].astype(str).str.replace(".", ",")
                    )

                    df_formulario_clientes_regulados_revision["SSCC"] = (
                        df_formulario_clientes_regulados_revision["SSCC"].astype(str).str.replace(".", ",")
                    )

                    df_formulario_clientes_regulados_revision["Dedicado"] = (
                        df_formulario_clientes_regulados_revision["Dedicado"].astype(str).str.replace(".", ",")
                    )

                    dataframes_regulados_E.append(df_formulario_clientes_regulados_energia)
                    dataframes_regulados_R.append(df_formulario_clientes_regulados_revision)

                    del df_formulario_clientes_regulados, df_formulario_clientes_regulados_energia, df_formulario_clientes_regulados_revision

                # Agregar dataframes a las listas correspondientes
                dataframes_libres_E.append(df_formulario_clientes_libres_energia)
                dataframes_libres_R.append(df_formulario_clientes_libres_revision)

                # Close excel file
                xls.close

                # Eliminar dataframes para liberar memoria
                del df_detalle_clientes_libres, df_formulario_clientes_libres_energia, df_formulario_clientes_libres_revision

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


""" # Usage:
revisor = PlanillaRevisor(2023, 2023, 11, 12)
revisor.run()         """
