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
    def __init__(
        self, primer_año,  último_año,primer_mes_primer_año, último_mes_último_año
    ):
        self.primer_año = primer_año
        self.primer_mes_primer_año = primer_mes_primer_año
        self.último_año = último_año
        self.último_mes_último_año = último_mes_último_año
        self.pares_lista = func.ConversionDatos().generar_pares(
            primer_año, último_año, primer_mes_primer_año, último_mes_último_año
        )
        self.carpeta_entrada = rf"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Recaudación\\"
        self.dataframe_clientes_libres = []
        self.dataframe_clientes_regulados = []
        self.dataframe_observaciones = []
        self.dataframe_revisor_clientes_L = []
        self.dataframe_revisor_clientes_R = []
        self.meses_rep = []

    def procesamiento_datos(self):
        for par in self.pares_lista:

            # ? Registro Mensual de Clientes Libres
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

            df_clientes_L["Cliente Nuevo"] = 0

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

            df_nvs_clientes_L["Cliente Nuevo"] = 1

            df_clientes_L_total = pd.concat(
                [df_clientes_L, df_nvs_clientes_L], ignore_index=True
            )

            # Eliminar filas con valores nulos en las columnas Barra, Clave y Suministrador
            df_clientes_L_total.dropna(
                subset=["Barra", "Clave", "Suministrador"], inplace=True
            )

            # Parse the date string in 'YYYY-MM-DD' format
            df_clientes_L_total["mes_repartición"] = pd.to_datetime(
                df_clientes_L_total["mes_repartición"], format="%Y-%m-%d"
            )

            # Reformat the date to 'DD-MM-YYYY'
            df_clientes_L_total["mes_repartición"] = df_clientes_L_total["mes_repartición"].dt.strftime("%d-%m-%Y")

            self.dataframe_clientes_libres.append(df_clientes_L_total)

            # ? Registro Mensual de Clientes Regulados

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

            df_clientes_R["Mes de consumo"] = pd.to_datetime(
                df_clientes_R["Mes de consumo"], format="%Y-%m-%d"
)

            df_clientes_R["Mes de consumo"] = df_clientes_R["Mes de consumo"].dt.strftime("%d-%m-%Y")

            df_clientes_R["mes_repartición"] = pd.to_datetime(
                df_clientes_R["mes_repartición"], format="%Y-%m-%d"
            )

            df_clientes_R["mes_repartición"] = df_clientes_R["mes_repartición"].dt.strftime("%d-%m-%Y")

            
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

            df_observaciones_clientes_L["Tipo Cliente"] = "L"

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

            df_observaciones_clientes_R["Tipo Cliente"] = "R"

            df_observaciones_total = pd.concat(
                [df_observaciones_clientes_L, df_observaciones_clientes_R],
                ignore_index=True,
            )

            df_observaciones_total["Mes de consumo"] = pd.to_datetime(
                df_observaciones_total["Mes de consumo"], format="%Y-%m-%d"
            )

            df_observaciones_total["Mes de consumo"] = df_observaciones_total["Mes de consumo"].dt.strftime("%d-%m-%Y")

            df_observaciones_total["mes_repartición"] = pd.to_datetime( df_observaciones_total["mes_repartición"], format="%Y-%m-%d")

            df_observaciones_total["mes_repartición"] = df_observaciones_total["mes_repartición"].dt.strftime("%d-%m-%Y")


            self.dataframe_observaciones.append(df_observaciones_total)

            # ? Registro Mensual de Clientes Libres
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
            
            df_revisor_clientes_L["mes_repartición"] = pd.to_datetime(
                df_revisor_clientes_L["mes_repartición"], format="%Y-%m-%d"
            )

            df_revisor_clientes_L["mes_repartición"] = df_revisor_clientes_L["mes_repartición"].dt.strftime("%d-%m-%Y")


            self.dataframe_revisor_clientes_L.append(df_revisor_clientes_L)

            # ? Registro Mensual de Revisor de Clientes Regulados
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
            # empty dataframe
           
            self.dataframe_revisor_clientes_R.append(df_revisor_clientes_R)

            # Parse the date string in 'YYYY-MM-DD' format
            mes_rep = datetime.strptime(df_clientes_R["mes_repartición"].unique()[0], "%d-%m-%Y")
            mes_rep = mes_rep.strftime("%d-%m-%Y")

            # Format the date as 'DD-MM-YYYY'
            
            self.meses_rep.append(mes_rep)

        #! Dataframes históricos

        self.lista_nombre_archivos = [
            "BDD Clientes Libres Históricos.csv",
            "BDD Clientes Regulados Históricos.csv",
            "BDD Observaciones Históricas.csv",
            "BDD Revisor Clientes L Históricos.csv",
            #"BDD Revisor Clientes R Históricos.csv",
        ]

        self.lista_df_historicos = [None for i in range(5)]
        lista_valores_mes = []

        for idx, nombre_archivo in enumerate(self.lista_nombre_archivos):

            if os.path.isfile(
                self.carpeta_entrada + "Revisión Histórica\\" + nombre_archivo
            ):
                self.lista_df_historicos[idx] = pd.read_csv(
                    self.carpeta_entrada + "Revisión Histórica\\" + nombre_archivo,
                    sep=";",
                    encoding="UTF-8",
                    header=0,
                )

                self.lista_df_historicos[idx]["mes_repartición"] = pd.to_datetime(
                    self.lista_df_historicos[idx]["mes_repartición"]
                )

                self.lista_df_historicos[idx]["mes_repartición"] = self.lista_df_historicos[idx][
                    "mes_repartición"
                ].dt.strftime("%m-%d-%Y")

                valores_mes = (
                    self.lista_df_historicos[idx]["mes_repartición"]
                    .unique()
                )
              
                
                lista_valores_mes.append(valores_mes)
            else:
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
                    # Parse the date string in 'YYYY-MM-DD' format
                    mes_df = datetime.strptime(
                        str(i["mes_repartición"].unique()[0]), "%d-%m-%Y"
                    )

                    # Format the date as 'DD-MM-YYYY'
                    mes_df = mes_df.strftime("%d-%m-%Y")

                    print("d")
                else:
                    df_vacio = True

                # Verificar si el mes de cada df de mes ya se encuentra en el histórico
                if mes_df in lista_valores_mes[idx] or df_vacio:
                    print(
                        f"El mes {mes_rep} ya se encuentra en el en el histórico de la {nombre_archivo} o es un dataframe vacío"
                    )
                else:
                    self.lista_df_historicos[idx] = pd.concat(
                        [self.lista_df_historicos[idx], i]
                    )
                    print(
                        f"Se incorpora el mes {mes_df} en el histórico de la {nombre_archivo}"
                    )

    def actualizador_recaudacion_historica(self):
        # Your existing code for saving the data goes here, but replace all variable references with self.variable

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


