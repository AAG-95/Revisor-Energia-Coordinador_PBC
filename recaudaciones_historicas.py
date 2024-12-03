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


class ProcesadorRecaudacionesHistoricas:
    """
    Esta clase se encarga de procesar los datos de recaudación histórica de clientes libres y regulados
    a partir de archivos CSV. El objetivo principal es cargar los datos de los archivos CSV, procesarlos
    y organizarlos en un solo archivo CSV que contenga la información histórica de recaudación de los
    clientes libres y regulados. Finalmente, el resultado se guarda en un archivo CSV.

    Atributos:
    -----------
    primer_año: El año inicial para el procesamiento
    último_año: El año final para el procesamiento
    primer_mes_primer_año: El mes inicial del primer año
    último_mes_último_año: El mes final del último año
    pares_lista: Lista de pares de año y mes
    carpeta_entrada: Carpeta de entrada donde se almacenan los archivos de recaudación para revisión

    Métodos:
    -----------
    procesamiento_datos: Procesa los datos de recaudación histórica
    actualizador_recaudacion_historica: Actualiza los archivos históricos
        
    """
    def __init__(self, primer_año, último_año, primer_mes_primer_año, último_mes_último_año):
        # Inicialización de los parámetros de rango temporal para la recaudación histórica
        self.primer_año = primer_año  # Año inicial para el procesamiento
        self.primer_mes_primer_año = primer_mes_primer_año  # Mes inicial del primer año
        self.último_año = último_año  # Año final para el procesamiento
        self.último_mes_último_año = último_mes_último_año  # Mes final del último año
        
        # Genera una lista de pares de año y mes desde el primer año y mes hasta el último año y mes
        self.pares_lista = func.ConversionDatos().generar_pares(
            primer_año, 
            último_año, 
            primer_mes_primer_año, 
            último_mes_último_año
        )
        
        # Carpeta de entrada donde se almacenan los archivos de recaudación para revisión
        self.carpeta_entrada = rf"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Recaudación\\"
        
        # Inicialización de los DataFrames vacíos para almacenar diferentes tipos de datos
        self.dataframe_clientes_libres = []  # Lista que almacenará los datos de clientes libres
        self.dataframe_clientes_regulados = []  # Lista que almacenará los datos de clientes regulados
        self.dataframe_observaciones = []  # Lista para almacenar observaciones
        self.dataframe_revisor_clientes_L = []  # Lista para almacenar datos del revisor de clientes libres
        self.dataframe_revisor_clientes_R = []  # Lista para almacenar datos del revisor de clientes regulados
        
        # Lista para almacenar los meses que serán revisados en la repartición
        self.meses_rep = []

    def procesamiento_datos(self):
        """
        Procesa los datos de recaudación histórica
        """
        # Itera sobre cada par de año y mes en la lista de pares
        for par in self.pares_lista:
            # ? Registro Mensual de Clientes Libres
            # Leer el archivo CSV de clientes
            df_clientes_L = pd.read_csv(
                self.carpeta_entrada
                + "Revisiones Mensuales\\BDD_"
                + str(par[1])
                + "\\"
                + "Clientes_"
                + str(par[1])
                + ".csv",
                encoding="UTF-8",
                sep=";",
                header=0,
            )

            # Marcar los clientes como no nuevos
            df_clientes_L["Cliente Nuevo"] = 0

            # Leer el archivo CSV de nuevos clientes
            df_nvs_clientes_L = pd.read_csv(
                self.carpeta_entrada
                + "Revisiones Mensuales\\BDD_"
                + str(par[1])
                + "\\"
                + "Clientes Nuevos_"
                + str(par[1])
                + ".csv",
                encoding="UTF-8",
                sep=";",
                header=0,
            )

            # Marcar los nuevos clientes como nuevos
            df_nvs_clientes_L["Cliente Nuevo"] = 1

            # Concatenar los DataFrames de clientes y nuevos clientes
            df_clientes_L_total = pd.concat(
                [df_clientes_L, df_nvs_clientes_L], ignore_index=True
            )

            # Eliminar filas con valores nulos en las columnas Barra, Clave y Suministrador
            df_clientes_L_total.dropna(
                subset=["Barra", "Clave", "Suministrador"], inplace=True
            )

            # Parsear la cadena de fecha en formato 'YYYY-MM-DD'
            df_clientes_L_total["mes_repartición"] = pd.to_datetime(
                df_clientes_L_total["mes_repartición"]
            )

            # Reformatear la fecha a 'DD-MM-YYYY'
            df_clientes_L_total["mes_repartición"] = df_clientes_L_total["mes_repartición"].dt.strftime("%m-%d-%Y")

            # Agregar el DataFrame resultante a la lista dataframe_clientes_libres
            self.dataframe_clientes_libres.append(df_clientes_L_total)

            # ? Registro Mensual de Clientes Regulados

            # Leer el archivo CSV de formularios de clientes regulados
            df_clientes_R = pd.read_csv(
                self.carpeta_entrada
                + "Revisiones Mensuales\\BDD_"
                + str(par[1])
                + "\\"
                + "Formularios Clientes Regulados_"
                + str(par[1])
                + ".csv",
                encoding="UTF-8",
                sep=";",
                header=0,
            )

            # Convertir la columna "Mes de consumo" a formato datetime y luego a string con formato "%m-%d-%Y"
            df_clientes_R["Mes de consumo"] = pd.to_datetime(
                df_clientes_R["Mes de consumo"]
            ).dt.strftime("%d-%m-%Y")

            # Convertir la columna "mes_repartición" a formato datetime y luego a string con formato "%m-%d-%Y"
            df_clientes_R["mes_repartición"] = pd.to_datetime(
                df_clientes_R["mes_repartición"]
            ).dt.strftime("%m-%d-%Y")

            # Agregar el DataFrame resultante a la lista dataframe_clientes_regulados
            self.dataframe_clientes_regulados.append(df_clientes_R)
            
            # ? Registro Mensual de Observaciones
            df_observaciones_clientes_L = pd.read_csv(
                self.carpeta_entrada
                + "Revisiones Mensuales\\BDD_"
                + str(par[1])
                + "\\"
                + "Observaciones Clientes Libres_"
                + str(par[1])
                + ".csv",
                encoding="UTF-8",
                sep=";",
                header=0,
            )

            # Agregar la columna "Tipo Cliente" con el valor "L" para indicar que son clientes libres
            df_observaciones_clientes_L["Tipo Cliente"] = "L"

            # Leer el archivo CSV de observaciones de clientes regulados
            df_observaciones_clientes_R = pd.read_csv(
                self.carpeta_entrada
                + "Revisiones Mensuales\\BDD_"
                + str(par[1])
                + "\\"
                + "Observaciones Clientes Regulados_"
                + str(par[1])
                + ".csv",
                encoding="UTF-8",
                sep=";",
                header=0,
            )

            # Agregar la columna "Tipo Cliente" con el valor "R" para indicar que son clientes regulados
            df_observaciones_clientes_R["Tipo Cliente"] = "R"

            # Concatenar los DataFrames de observaciones de clientes libres y regulados
            df_observaciones_total = pd.concat(
                [df_observaciones_clientes_L, df_observaciones_clientes_R],
                ignore_index=True,
            )

            # Convertir la columna "Mes de consumo" a formato datetime y luego a string con formato "%m-%d-%Y"
            df_observaciones_total["Mes de consumo"] = pd.to_datetime(
                df_observaciones_total["Mes de consumo"]
            )

            # Reformatear la fecha a 'DD-MM-YYYY'
            df_observaciones_total["Mes de consumo"] = df_observaciones_total["Mes de consumo"].dt.strftime("%m-%d-%Y")

            # Convertir la columna "mes_repartición" a formato datetime y luego a string con formato "%m-%d-%Y"
            df_observaciones_total["mes_repartición"] = pd.to_datetime( df_observaciones_total["mes_repartición"])

            # Reformatear la fecha a 'DD-MM-YYYY'
            df_observaciones_total["mes_repartición"] = df_observaciones_total["mes_repartición"].dt.strftime("%m-%d-%Y")

            # Agregar el DataFrame resultante a la lista dataframe_observaciones
            self.dataframe_observaciones.append(df_observaciones_total)

            # ? Registro Mensual de Clientes Libres
            # Leer el archivo CSV de revisor de clientes libres
            df_revisor_clientes_L = pd.read_csv(
                self.carpeta_entrada
                + "Revisiones Mensuales\\BDD_"
                + str(par[1])
                + "\\"
                + "Revisor Clientes Libres_"
                + str(par[1])
                + ".csv",
                encoding="UTF-8",
                sep=";",
                header=0,
            )
            
            # Convertir la columna "mes_repartición" a formato datetime y luego a string con formato "%m-%d-%Y"
            df_revisor_clientes_L["mes_repartición"] = pd.to_datetime(
                df_revisor_clientes_L["mes_repartición"]
            )

            # Reformatear la fecha a 'DD-MM-YYYY'    
            df_revisor_clientes_L["mes_repartición"] = df_revisor_clientes_L["mes_repartición"].dt.strftime("%m-%d-%Y")

            # Agregar el DataFrame resultante a la lista dataframe_revisor_clientes_L
            self.dataframe_revisor_clientes_L.append(df_revisor_clientes_L)

            # ? Registro Mensual de Revisor de Clientes Regulados
            # Leer el archivo CSV de revisor de clientes regulados
            df_revisor_clientes_R = pd.read_csv(
                self.carpeta_entrada
                + "Revisiones Mensuales\\BDD_"
                + str(par[1])
                + "\\"
                + "Revisor Clientes Regulados_"
                + str(par[1])
                + ".csv",
                encoding="UTF-8",
                sep=";",
                header=0,
            ) 
            
            # Convertir la columna "mes_repartición" a formato datetime y luego a string con formato "%m-%d-%Y"
            self.dataframe_revisor_clientes_R.append(df_revisor_clientes_R)

            # Convertir la columna "mes_repartición" a formato datetime y luego a string con formato "%m-%d-%Y"
            mes_rep = datetime.strptime(df_clientes_R["mes_repartición"].unique()[0], "%m-%d-%Y")

            # Reformatear la fecha a 'DD-MM-YYYY'
            mes_rep = mes_rep.strftime("%d-%m-%Y")

            # Agregar el mes a la lista meses_rep
            self.meses_rep.append(mes_rep)

        #! Dataframes históricos

        # Lista de nombres de archivos
        self.lista_nombre_archivos = [
            "BDD Clientes Libres Históricos.csv",
            "BDD Clientes Regulados Históricos.csv",
            "BDD Observaciones Históricas.csv",
            "BDD Revisor Clientes L Históricos.csv",
            #"BDD Revisor Clientes R Históricos.csv",
        ]

        # Lista de DataFrames históricos
        self.lista_df_historicos = [None for i in range(5)]
        lista_valores_mes = []

        # Leer los archivos históricos si existen
        for idx, nombre_archivo in enumerate(self.lista_nombre_archivos):
            # Verificar si el archivo existe
            if os.path.isfile(
                self.carpeta_entrada + "Revisión Histórica\\" + nombre_archivo
            ):
                # Leer el archivo CSV
                self.lista_df_historicos[idx] = pd.read_csv(
                    self.carpeta_entrada + "Revisión Histórica\\" + nombre_archivo,
                    sep=";",
                    encoding="UTF-8",
                    header=0,
                )
                # Convertir la columna "mes_repartición" a formato datetime y luego a string con formato "%m-%d-%Y"
                self.lista_df_historicos[idx]["mes_repartición"] = pd.to_datetime(
                    self.lista_df_historicos[idx]["mes_repartición"]
                )
                # Reformatear la fecha a 'DD-MM-YYYY'
                self.lista_df_historicos[idx]["mes_repartición"] = self.lista_df_historicos[idx][
                    "mes_repartición"
                ].dt.strftime("%m-%d-%Y")
                # Obtener los valores únicos de la columna "mes_repartición"
                valores_mes = (
                    self.lista_df_historicos[idx]["mes_repartición"]
                    .unique()
                )
                # Agregar los valores únicos a la lista lista_valores_mes
                lista_valores_mes.append(valores_mes)
            else:
                # Imprimir un mensaje si el archivo no existe
                print(f"No Existe {nombre_archivo} en: {self.carpeta_entrada}")
                self.lista_df_historicos[idx] = pd.DataFrame()
                if idx == 0:
                    valores_mes = []
                    lista_valores_mes.append(valores_mes)

        #! Unión de Dataframes
        # Verificar si el mes de cada df de mes ya se encuentra en el histórico
        lista_dataframes_mes_analizado = [
            self.dataframe_clientes_libres,
            self.dataframe_clientes_regulados,
            self.dataframe_observaciones,
            self.dataframe_revisor_clientes_L,
            #self.dataframe_revisor_clientes_R,
        ]

        # Verificar si el mes de cada df de mes ya se encuentra en el histórico, si no, se incorpora
        for idx, (lista_dataframe, nombre_archivo) in enumerate(
            zip(lista_dataframes_mes_analizado, self.lista_nombre_archivos)
        ):
            print(f"Actualización archivo {nombre_archivo}")

            for i, mes_rep in zip(lista_dataframe, self.meses_rep):
                # Verificar que el dataframe no esté vacío
                df_vacio = False
                meses_unicos = i["mes_repartición"].unique()

                if len(meses_unicos) > 0:
                    
                    # Change the date string format to 'MM-DD-YYYY'
                    i["mes_repartición"] = i["mes_repartición"].apply(lambda x: datetime.strptime(x, "%m-%d-%Y"))

                    i["mes_repartición"] = i["mes_repartición"].dt.strftime("%d-%m-%Y")

                    # Format the date as 'DD-MM-YYYY'
                    mes_df = i["mes_repartición"].unique()[0]

                else:
                    df_vacio = True

                # Verificar si el mes de cada df de mes ya se encuentra en el histórico
                if mes_df in lista_valores_mes[idx] or df_vacio:
                    print(
                        f"El mes {mes_rep} ya se encuentra en el en el histórico de la {nombre_archivo} o es un dataframe vacío"
                    )
                else:
                    print(
                        f"Se incorpora el mes {mes_df} en el histórico de la {nombre_archivo}"
                    )
                    self.lista_df_historicos[idx] = pd.concat(
                        [self.lista_df_historicos[idx], i]
                    )
                    

    def actualizador_recaudacion_historica(self):
        """
        Actualiza los archivos históricos
        """
        # Actualizar los archivos históricos
        #! Salida de archivo retiros históricos
        carpeta_salida = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Recaudación\\Revisión Histórica\\"

        for variable, nombre_archivo in zip(
            self.lista_df_historicos, self.lista_nombre_archivos
        ):
            variable.to_csv(
                carpeta_salida + nombre_archivo, sep=";", encoding="UTF-8", index=False
            )
    def run(self):
        self.procesamiento_datos()
        self.actualizador_recaudacion_historica()
        print("Process completed successfully")


