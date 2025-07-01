# Creador Listado Clientes

import pandas as pd
import zipfile
import pandas as pd
import zipfile
import xlrd
import funciones as fc
from datetime import datetime
from dateutil.relativedelta import relativedelta
import openpyxl
import os
import interfaz as gui
import sys
import warnings

warnings.filterwarnings("ignore", category=pd.errors.DtypeWarning)

class CreadorListaClientesBalance:
    """
    Esta clase se encarga de procesar y organizar los datos de clientes individuales
    a partir de archivos ZIP. El objetivo principal es obtener los datos de los clientes
    que aparecen en los balances de energía mensuales, para luego guardar los resultados
    en un archivo Excel.

    Atributos:
    lista_meses (list): Lista de meses a procesar.
    ruta_homologa_propietarios (str): Ruta del archivo de homologación de propietarios.
    ruta_control_versiones (str): Ruta del archivo de control de versiones.
    ruta_retiros_historicos_L (str): Ruta del archivo de retiros históricos de clientes libres.
    ruta_retiros_historicos_R (str): Ruta del archivo de retiros históricos de clientes regulados.
    ruta_registro_cambios_empresas (str): Ruta del archivo de registro de cambios de empresas.
    ruta_registro_cambios_clientes_L (str): Ruta del archivo de registro de cambios de clientes libres.
    ruta_registro_cambios_clientes_R (str): Ruta del archivo de registro de cambios de clientes regulados.
    lista_balance_fisico (list): Lista de nombres de hojas de balance físico.
    rutas_posibles (list): Lista de rutas posibles en los archivos ZIP.
    
    Métodos:
    get_dataframes(): Carga los archivos de homologación de propietarios y control de versiones.
    procesar_meses(mes): Procesa los datos de los clientes para un mes específico.
    run(): Ejecuta el programa.


    """
    def __init__(self,lista_meses):

        """
        Inicializa los atributos de la clase. 

        Atributos:
        lista_meses (list): Lista de meses a procesar.
        ruta_homologa_propietarios (str): Ruta del archivo de homologación de propietarios.
        ruta_control_versiones (str): Ruta del archivo de control de versiones.
        ruta_retiros_historicos_L (str): Ruta del archivo de retiros históricos de clientes libres.
        ruta_retiros_historicos_R (str): Ruta del archivo de retiros históricos de clientes regulados.
        ruta_registro_cambios_empresas (str): Ruta del archivo de registro de cambios de empresas.
        ruta_registro_cambios_clientes_L (str): Ruta del archivo de registro de cambios de clientes libres.
        ruta_registro_cambios_clientes_R (str): Ruta del archivo de registro de cambios de clientes regulados.
        lista_balance_fisico (list): Lista de nombres de hojas de balance físico.
        rutas_posibles (list): Lista de rutas posibles en los archivos ZIP.

        Devuelve:
        None
        """
        #! Month Selection
        self.lista_meses = lista_meses    
        # ? Paths inputs
        self.ruta_homologa_propietarios = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\02 Repartición\Balances\Homologaciones\Homologacion_Propietarios_Balance_Fisico.xlsx"
        self.ruta_control_versiones = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Balances\Versiones_Balances.xlsx"
        self.ruta_retiros_historicos_L = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Retiros Históricos Clientes\Retiros_Históricos_Clientes_L.csv"
        self.ruta_retiros_historicos_R = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Retiros Históricos Clientes\Retiros_Históricos_Clientes_R.csv"
        self.ruta_registro_cambios_empresas = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Registro de Cambios\Registro_de_Cambios_Empresas.csv"
        self.ruta_registro_cambios_clientes_L = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Registro de Cambios\Registro_de_Cambios_Clientes_Libres.csv"
        self.ruta_registro_cambios_clientes_R = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Registro de Cambios\Registro_de_Cambios_Clientes_Regulados.csv"


        # Listado de posibles nombres de hojas de balance físico y rutas posibles en los archivos ZIP
        self.lista_balance_fisico = [
            "REVISION_NORTE_",
            "REVISION_NORTE_DX_",
            "REVISION_CENTRO_",
            "REVISION_SUR_",
            "REVISION_SUR_DX_",
            "REVISION_DX_SUR_",
            "REVISION_RES_DX_SUR_",
            "REVISION_RES_DX_NORTE_",
            "REVISION_RES_SUR_DX_",
            "REVISION_RES_SUR_",
            "REVISION_RES_NORTE_DX_",
            "REVISION_RES_NORTE_DX",
            "REVISION_DX_NORTE_",
            "REVISION_RES_NORTE_",
            "REVISION_TFE_RES_NORTE_DX_",
            "Balance_B01D_",
        ]
        self.rutas_posibles = [
            "01 Resultados/02 Balance Físico/",
            "01 Resultados/01 Balance de Energía/02 Balance Físico/",
            "01 Resultados/01 Resultados/01 Balance de Energía/02 Balance Físico/",
            "01 Resultados/",
        ]

#! Main Program
    def get_dataframes(self):
        """
        Carga los archivos de homologación de propietarios y control de versiones.
        """

        # ? Obtener Nombre de Propietarios
        # Obtener dataframe de self.ruta_homologa_propietarios en la hoja 'Homologa'
        self.df_homologa_propietarios = pd.read_excel(
            self.ruta_homologa_propietarios, sheet_name="Homologa"
        )

        # ? Obtener Versiones de Balance
        # Obtener dataframe de self.ruta_control_versiones en la hoja 'Versiones'
        self.df_control_versiones = pd.read_excel(
            self.ruta_control_versiones, sheet_name="Versiones", header=None
        )

        # Obtener columnas 5, 8 y 9 de self.df_control_versiones
        self.df_control_versiones = fc.ObtencionDatos().obtencion_tablas_clientes(
            self.df_control_versiones, 5, 8, 9
        )

    def procesar_meses(self,mes):
        
            # Convert mes to datetime
            mes_fecha = fc.ConversionDatos().convertir_fecha(mes)
            mes_numeral = fc.ConversionDatos().convertir_fecha_numeral(mes)

            # Obteniendo mes anterior
            mes_anterior = pd.to_datetime(mes_fecha - relativedelta(months=1)).strftime('%d-%m-%Y')
            mes_fecha = mes_fecha.strftime('%d-%m-%Y')

            # Obtener versión de control de versiones
            version = self.df_control_versiones.loc[
            pd.to_datetime(self.df_control_versiones["Mes"]).dt.strftime('%d-%m-%Y') == mes_fecha, "Versión"
            ].iloc[0]

            # Ruta al archivo ZIP
            ruta_zip = rf"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Balances\Balances de Energía\Archivos Fuente\20{mes_numeral[:2]}\{mes}-{version}.zip"

            # ? Dataframes a guardar
            listado_clientes = [] # Listado de Clientes L y R
            listado_clientes_R = [] # Listado de Clientes R
            listado_clientes_L = [] # Listado de Clientes L
            ruta_correcta = None # Ruta correcta en ZIP

            print("Mes a evaluar: " + str(mes) + " // Versión a evaluar: " + str(version))

            #  Abrir archivo ZIP
            with zipfile.ZipFile(ruta_zip) as myzip:
                for i in self.lista_balance_fisico:
                    print("Archivo " + i + " Analizado en " + str(mes) + ":", end="")
                    # Para cada ruta posible en ZIP
                    for path in self.rutas_posibles:
                       
                        try:
                            print(f" Ruta en ZIP: {path}", end="")
                            with myzip.open(path + i + mes_numeral + ".xlsx") as myfile:
                                df_balance_fisico = pd.read_excel(myfile)
                                print(f" Ruta en ZIP EXISTE con {path}")
                                ruta_correcta = path # Guardar la ruta correcta
                                break  # Si se encuentra el archivo, salir del loop
                        except KeyError:
                            continue  # Si no se encuentra el archivo, probar con la siguiente ruta
                    else:
                        print(f" Ruta NO EXISTE para {i}")
                        continue  # Si no se encuentra el archivo, probar con el siguiente archivo

                    with myzip.open(ruta_correcta + i + mes_numeral + ".xlsx") as myfile:
                        df_balance_fisico = pd.read_excel(
                            myfile, sheet_name="Balance Físico", header=None
                        )

                        '''
                        # Obtener columnas 6, 2 y 17 de df_balance_fisico
                        df_balance_fisico.iloc[:, 11] = df_balance_fisico.iloc[:, 11].replace(
                            "(0/1)", "(0/1).1"
                        )
                        df_balance_fisico.iloc[:, 13] = df_balance_fisico.iloc[:, 13].replace(
                            "(0/1)", "(0/1).2"
                        )
                        '''


                        # Obtener fila 6 y columnas 2 a 17 de df_balance_fisico
                        df_clientes = fc.ObtencionDatos().obtencion_tablas_clientes(
                            df_balance_fisico, 1, 1, 25
                        )

                        '''
                        # Eliminar
                        df_clientes = df_clientes.drop(columns="N")

                        # Cambiar nombre de columnas
                        df_clientes.rename(columns={"Nombre_2": "Barra"}, inplace=True)

                        # Cambiar nombre de columnas
                        df_clientes.rename(
                            columns={"(0/1)_2": "Medida 2", "(0/1)_3": "Medida 3"}, inplace=True
                        )

                        # Si la columna Barra tiene NaN, rellenar con el valor de la fila anterior
                        df_clientes["Barra"] = df_clientes["Barra"].ffill()
                        '''
                        # Agregar Columna Mes
                        df_clientes["Mes"] = mes_fecha

                        '''
                        # Botar filas con NaN en columnas Nombre y Tipo
                        df_clientes = df_clientes[df_clientes["Nombre"] != "TOTAL"]
                        df_clientes = df_clientes[df_clientes["Nombre"] != "NaN"]
                        '''


                        #Cambiar nombre de "nombre_corto" a "Propietario" para realizar las homologaciones
                        df_clientes = df_clientes.rename(columns={"nombre_corto": "Propietario"})


                        # Si la columna Tipo tiene R, L o L_D, guardar en listado_clientes
                        retiros_clientes = df_clientes[
                            df_clientes["tipo_medidor"].isin(["R", "L", "L_D"])
                        ]


                        # Junta la columna Propietario con la homologación de propietarios
                        retiros_clientes = pd.merge(
                            retiros_clientes,
                            self.df_homologa_propietarios,
                            on="Propietario",
                            how="left",
                        )

                        # Cambiar de vuelta "Propietario" a "nombre_corto" en retiros_clientes
                        retiros_clientes = retiros_clientes.rename(columns={"Propietario": "nombre_corto"})


                        # Verificar si hay NaN en la columna Suministrador_final
                        if retiros_clientes["Suministrador_final"].isnull().values.any():
                            print(
                                "Columnas con NaN en Suministrador_Final al no coincidir con Propietario:"
                            )
                            print(
                                retiros_clientes[
                                    retiros_clientes["Suministrador_final"].isnull()
                                ]["Propietario"].to_list()
                            )
                            sys.exit()

                        # Reemplazar NaN en columnas Empresa y Suministrador_final por "Sin Información"
                        retiros_clientes_R = retiros_clientes[
                            retiros_clientes["tipo_medidor"].isin(["R"])
                        ]

                        retiros_clientes_L = retiros_clientes[
                            retiros_clientes["tipo_medidor"].isin(["L", "L_D"])
                        ]

                        # Guardar en listado_clientes_R y listado_clientes_L
                        listado_clientes.append(retiros_clientes)
                        listado_clientes_R.append(retiros_clientes_R)
                        listado_clientes_L.append(retiros_clientes_L)

            # ? Concatenar Columnas
            # Concatenar listado_clientes, listado_clientes_R y listado_clientes_L
            df_clientes = pd.concat(listado_clientes)
            df_clientes_R = pd.concat(listado_clientes_R)
            df_clientes_L = pd.concat(listado_clientes_L)

            # ? Reordenar Columnas
            
            '''
            # Obtener columnas de df_clientes
            cols = df_clientes_L.columns.tolist()

            # Alternar columnas Propietario y Suministrador_final
            indice_propietario = cols.index("nombre_corto")
            indice_suministrador = cols.index("Suministrador_final")

            # Alternar columnas Propietario y Suministrador_final
            cols[indice_propietario], cols[indice_suministrador] = cols[indice_suministrador], cols[indice_propietario]

            # Reasignar columnas a df_clientes_L
            df_clientes_L = df_clientes_L[cols]
            '''

            orden_columnas = [
                "barra",
                "nivel_tension",
                "nombre_medidor",
                "clave_medidor",
                "Suministrador_final",
                "propietario_medidor",
                "rut",
                "numero_linea",
                "calificacion_linea",
                "linea_barra_inicial",
                "linea_nivel_tension_inicial",
                "linea_barra_final",
                "linea_nivel_tension_final",
                "medida1", "flag1",
                "medida2", "flag2",
                "medida2a", "flag2a",
                "medida3", "flag3",
                "error",
                "tipo_medidor",
                "calculo",
                "zona",
                "Mes",
                "nombre_corto"
            ]
            
            df_clientes_L = df_clientes_L[orden_columnas]

            #Ordenar por "barra" y "nivel_tension"
            df_clientes_L = df_clientes_L.sort_values(["barra", "nivel_tension"], ascending=[True, True])


            #! Salida-----------------------------------------------------------------

            # ? Actualizar Registro Cambios Empresas-------------------------------------------------
            # Obtener Valores Unicos df_clientes
            df_clientes_unique = df_clientes.drop_duplicates(subset=["Suministrador_final"])
            # Obtener solo columna Suministrador_final y mes_fecha
            df_clientes_unique = df_clientes_unique[["Suministrador_final", "Mes"]]

            # Ordenar por Suministrador_final
            df_clientes_unique = df_clientes_unique.sort_values(by=["Suministrador_final"])

            # Obtener Registro Cambios Empresas
            df_registro_cambios_empresas = pd.read_csv(self.ruta_registro_cambios_empresas, sep=";")

            # Cambiar formato de Mes a dd-mm-YYYY
            df_registro_cambios_empresas["Mes"] = pd.to_datetime(
                df_registro_cambios_empresas["Mes"]
            ).dt.strftime('%m-%d-%Y')

            # Filtrar mes_anterior
            df_registro_cambios_empresas_mes_anterior = df_registro_cambios_empresas[
                df_registro_cambios_empresas["Mes"] == mes_anterior
            ]

            # Obtener Empresas Nuevas
            df_nuevas_empresas = df_clientes_unique[
                ~df_clientes_unique["Suministrador_final"].isin(
                    df_registro_cambios_empresas_mes_anterior["Suministrador_final"]
                )
            ]

            # Obtener Empresas Eliminadas
            df_empresas_eliminadas = df_registro_cambios_empresas_mes_anterior[
                ~df_registro_cambios_empresas_mes_anterior["Suministrador_final"].isin(
                    df_clientes_unique["Suministrador_final"]
                )
            ]

            # Imprimir Empresas Nuevas y Eliminadas
            print(
                "Empresas nuevas Mes Actual:",
                df_nuevas_empresas["Suministrador_final"].to_list(),
            )
            print(
                "Empresas eliminadas respecto a Mes Anterior:",
                df_empresas_eliminadas["Suministrador_final"].to_list(),
            )
        
            # Actualizar Registro Cambios Empresas
            if mes_fecha not in list(df_registro_cambios_empresas["Mes"].unique()):
            
                print(
                    "Se actualiza el archivo Registro de Cambios de Empresas Existentes con registro mes: "
                    + str(mes_fecha)
                )


                df_registro_cambios_empresas_final = pd.concat(
                    [
                        df_registro_cambios_empresas,
                        df_clientes_unique[["Suministrador_final", "Mes"]],
                    ]
                ) # Concatenar df_registro_cambios_empresas y df_clientes_unique

                # Guardar en archivo CSV
                df_registro_cambios_empresas_final.to_csv(
                    self.ruta_registro_cambios_empresas, sep=";", index=False
                )
            else:
                print(
                    "Revisar Base De Datos de Registro de Cambios de Empresas, el Mes Actual ya fue actualizado anteriormente"
                )
                        
            # Ruta de salida
            ruta_salida = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Retiros Mensuales"

            # Abrir archivo Excel
            with pd.ExcelWriter(
                ruta_salida + "\\" + "Retiros_" + str(mes_numeral) + ".xlsx", engine="openpyxl"
            ) as writer:
                # Escibir en Excel los dataframes
                df_clientes.to_excel(writer, sheet_name="Listado_Clientes", index=False)

                df_clientes_R.to_excel(writer, sheet_name="Listado_Clientes_R", index=False)

                df_clientes_L.to_excel(writer, sheet_name="Listado_Clientes_L", index=False)

            print("Se actualiza el archivo de Listado de Clientes del mes: " + str(mes_fecha))

            del listado_clientes, listado_clientes_R, 
            listado_clientes_L

    def run(self):
        self.get_dataframes()
        for mes in self.lista_meses:
            self.procesar_meses(mes)

if __name__ == "__main__":
    client_list_creator = CreadorListaClientesBalance()
    client_list_creator.run()  
    