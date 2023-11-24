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
import entrada_datos_gui_clientes as gui

#! Month Selection
ventana = gui.VentanaIngresoDatos()
ventana.iniciar()
mes = ventana.visualizador()

# Open data from a ZIP file Abril-2020-R03D-1.zip in \\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Balances\Balances de Energía\Archivos Fuente\2020

#mes = "Ene2020"
# Lista Meses a Evaluar
# Split mes into list by comma
lista_meses = [x.strip() for x in mes.split(", ")] 

#! Main Program
#? Paths inputs
# Path to Homologacion_Propietarios_Balance_Fisico.xlsx
ruta_homologa_propietarios = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\02 Repartición\Balances\Homologaciones\Homologacion_Propietarios_Balance_Fisico.xlsx"

# Path to Control de Versiones
ruta_control_versiones = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Balances\Versiones_Balances.xlsx"

# Listado de Clientes Histórico
ruta_retiros_historicos_L = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Registro Histórico Clientes\Retiros_históricos_Clientes_L.csv"

# Path to Registro Cambio Empresas
ruta_registro_cambios_empresas = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Registro de Cambios\Registro_de_Cambios_Empresas.csv"

# Path to Registro Cambio Clientes
ruta_registro_cambios_clientes = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Registro de Cambios\Registro_de_Cambios_Clientes.csv"


#? Get Propietarios Names as they are in the Balance Físico
# Get dataframe from ruta_homologa_propietarios sheet 'Homologa'
df_homologa_propietarios = pd.read_excel(
    ruta_homologa_propietarios, sheet_name="Homologa"
)

#? Get Versión
# Get dataframe from ruta_control_versiones sheet 'Versiones' 
df_control_versiones = pd.read_excel(ruta_control_versiones, sheet_name="Versiones", header=None)

df_control_versiones = fc.ObtencionDatos().obtencion_tablas_clientes(df_control_versiones, 5, 8, 9)

#? Listado de Posibles Archivos y Rutas
# List of sheets to read from ZIP file
lista_balance_fisico = [
    "REVISION_NORTE_",
    "REVISION_NORTE_DX_",
    "REVISION_CENTRO_",
    "REVISION_SUR_",
    "REVISION_SUR_DX_",
]

# List of possible file paths
rutas_posibles = [
    "01 Resultados/02 Balance Físico/",
    "01 Resultados/01 Balance de Energía/02 Balance Físico/",
    "01 Resultados/01 Resultados/01 Balance de Energía/02 Balance Físico/"
]

for mes in lista_meses:
    
    # Convert mes to datetime
    mes_fecha = fc.ConversionDatos().convertir_fecha(mes)
    mes_numeral = fc.ConversionDatos().convertir_fecha_numeral(mes)

    # Get previous month from mes_fecha
    mes_anterior = mes_fecha - relativedelta(months=1)
    
    # Get Value from column Versiones when mes fecha match value in column Mes
    version = df_control_versiones.loc[df_control_versiones["Mes"] == mes_fecha, "Versión"].iloc[0]

    # Path to ZIP file, Balance Físico
    ruta_zip = rf"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Balances\Balances de Energía\Archivos Fuente\20{mes_numeral[:2]}\{mes}-{version}.zip"

    #? Dataframes a guardar
    listado_clientes = []
    listado_clientes_R = []
    listado_clientes_L = []
    ruta_correcta = None
   
    print("Mes a evaluar: " + str(mes) + " // Versión a evaluar: " + str(version))

    with zipfile.ZipFile(ruta_zip) as myzip:
        for i in lista_balance_fisico:
            print("Archivo " + i +  " Analizado en "+ str(mes) + ":", end='')

            for path in rutas_posibles:
                try:
                    with myzip.open(path + i + mes_numeral + ".xls") as myfile:
                        df_balance_fisico = pd.read_excel(myfile)
                        print(f" Ruta en ZIP EXISTE con {path}")
                        ruta_correcta = path   # store the correct path
                        break  # if file is found and opened successfully, break the loop
                except KeyError:
                    continue  # if file is not found, try the next path
            else:
                print(f" Ruta NO EXISTE para {i}")
                continue  # if file is not found for any path, move on to the next i

            with myzip.open(
                ruta_correcta + i + mes_numeral + ".xls"
            ) as myfile:
                df_balance_fisico = pd.read_excel(
                    myfile, sheet_name="Balance por Barra", header=None
                )

                # Replace (0/1) in other columns
                df_balance_fisico.iloc[:,11] = df_balance_fisico.iloc[:,11].replace("(0/1)", "(0/1).1")
                df_balance_fisico.iloc[:,13] = df_balance_fisico.iloc[:,13].replace("(0/1)", "(0/1).2")

                # Seleted table from sheet Balance por Barra
                df_clientes = fc.ObtencionDatos().obtencion_tablas_clientes(df_balance_fisico, 6, 2, 17)

                # Drop Column names N if it exists
                df_clientes = df_clientes.drop(columns="N")

                # Change Nombre_2 to Barra
                df_clientes.rename(columns={"Nombre_2": "Barra"}, inplace=True)
                # Change (0/1)_2 into Medidas 2 and (0/1)_3 into Medidas 3
                df_clientes.rename(
                    columns={"(0/1)_2": "Medida 2", "(0/1)_3": "Medida 3"}, inplace=True
                )

                # If values is found in column Barra, replace all nan values in bottom rows from same column with that value and stop when find another value
                df_clientes["Barra"] = df_clientes["Barra"].ffill()

                # Add month column
                df_clientes["Mes"] = mes_fecha

                # Drop Rows from column df_clientes['Nombre'] that contains 'TOTAL' or NaN
                df_clientes = df_clientes[df_clientes["Nombre"] != "TOTAL"]
                df_clientes = df_clientes[df_clientes["Nombre"] != "NaN"]

                # From Column Tipo filter 'R', 'L' or 'L_D'
                retiros_clientes = df_clientes[df_clientes["Tipo"].isin(["R", "L", "L_D"])]

                # Merge dataframe df_clientes with df_homologa_propietarios based in column Propietario from both df
                retiros_clientes = pd.merge(
                    retiros_clientes, df_homologa_propietarios, on="Propietario", how="left"
                )

                # Check if Column Suministrador_final has NaN, if Column has NaN, print this row and end program
                if retiros_clientes["Suministrador_final"].isnull().values.any():
                    print("Columnas con NaN en Suministrador_Final al no coincidir con Propietario:")
                    print(retiros_clientes[retiros_clientes["Suministrador_final"].isnull()]["Propietario"].to_list())
                    exit()

                # retiros divided in R and L
                retiros_clientes_R = retiros_clientes[retiros_clientes["Tipo"].isin(["R"])]

                retiros_clientes_L = retiros_clientes[
                    retiros_clientes["Tipo"].isin(["L", "L_D"])
                ]

                listado_clientes.append(retiros_clientes)
                listado_clientes_R.append(retiros_clientes_R)
                listado_clientes_L.append(retiros_clientes_L)
            
            

    # Concatenate all dataframes from listado_clientes
    df_clientes = pd.concat(listado_clientes)
    df_clientes_R = pd.concat(listado_clientes_R)
    df_clientes_L = pd.concat(listado_clientes_L)

    # Get unique values from df_clientes
    df_clientes_unique = df_clientes.drop_duplicates(subset=["Suministrador_final"])
    # Get only column Suministrador_final and mes_fecha
    df_clientes_unique = df_clientes_unique[["Suministrador_final", "Mes"]]

    # order by column Suministrador_final alfabetically
    df_clientes_unique = df_clientes_unique.sort_values(by=["Suministrador_final"])

    # Get database from ruta_registro_cambios_empresas
    df_registro_cambios_empresas = pd.read_csv(ruta_registro_cambios_empresas, sep=";")

    # Change column mes_fecha to datetime, example input 1-08-2020
    df_registro_cambios_empresas["Mes"] = pd.to_datetime(df_registro_cambios_empresas["Mes"], dayfirst=True)

    # Filter month column from df_registro_cambios_empresas with mes_anterior
    df_registro_cambios_empresas_mes_anterior = df_registro_cambios_empresas[
        df_registro_cambios_empresas["Mes"] == mes_anterior
    ]

    # Get Values that are in df_clientes_unique and not in df_registro_cambios_empresas_mes_anterior
    df_nuevas_empresas = df_clientes_unique[
        ~df_clientes_unique["Suministrador_final"].isin(
            df_registro_cambios_empresas_mes_anterior["Suministrador_final"]
        )
    ]

    # Empresas Eliminadas
    df_empresas_eliminadas = df_registro_cambios_empresas_mes_anterior[
        ~df_registro_cambios_empresas_mes_anterior["Suministrador_final"].isin(
            df_clientes_unique["Suministrador_final"]
        )
    ]

    # Column of df to list
    print(
        "Empresas nuevas Mes Actual:",
        df_nuevas_empresas["Suministrador_final"].to_list(),
    )
    print(
        "Empresas eliminadas respecto a Mes Anterior:",
        df_empresas_eliminadas["Suministrador_final"].to_list(),
    )


    #! Output of program
    #? Update Registro Cambios Empresas
    # If mes is not in registro_cambios by column Mes, add Columns Mes and Suministrador_final of df_clientes into registro_cambios
    if mes_fecha not in df_registro_cambios_empresas["Mes"].to_list():
        print("Se actualiza el archivo Registro de Cambios con registro mes " + str(mes_fecha))
        df_registro_cambios_empresas_final = pd.concat(
            [df_registro_cambios_empresas, df_clientes_unique[["Suministrador_final", "Mes"]]]
        )

        # Rewrite df_registro_cambios_empresas_final into ruta_registro_cambios_empresas
        df_registro_cambios_empresas_final.to_csv(
            ruta_registro_cambios_empresas, sep=";", index=False
        )
    
    #? Update Registros Históricos
    df_historico_clientes_L = pd.read_csv(ruta_retiros_historicos_L, sep=";", encoding='latin1')

    #If value in first row is
    # Convert column Mes to datetime with format datetime.datetime(2023, 9, 1, 0, 0)
    df_historico_clientes_L["Mes"] = pd.to_datetime(df_historico_clientes_L["Mes"])

    if mes_fecha  in df_historico_clientes_L["Mes"].unique().tolist():
        print("Se actualiza el archivo Registro de Cambios con registro mes " + str(mes_fecha))
       
        df_retiros_historico_L_final = pd.concat(
            [df_historico_clientes_L, df_clientes_L]
        )

        """  # Rewrite df_registro_cambios_empresas_final into ruta_registro_cambios_Empresas
        df_retiros_historico_L_final.to_csv(
            ruta_retiros_historicos_L, sep=";", index=False
        )
         """
        #? Update and save Registro Cambios Clientes

        df_registro_cambios_clientes = df_retiros_historico_L_final[['Nombre', 'Clave', 'Suministrador_final', 'Mes']].drop_duplicates(subset=['Nombre', 'Clave', 'Suministrador_final'])
        
        df_registro_cambios_clientes['Clave_Actual'] = df_registro_cambios_clientes.sort_values('Mes').reset_index(drop=True).groupby('Clave')['Nombre'].transform('last')

        df_registro_cambios_clientes['Mes_Actual'] = df_registro_cambios_clientes.sort_values('Mes').reset_index(drop=True).groupby('Clave')['Mes'].transform('last')
        
        df_registro_cambios_clientes.rename(columns={'Nombre': 'Cliente'} )

        df_registro_cambios_clientes.to_csv(
            ruta_registro_cambios_clientes, sep=";", index=False
        )
       

    # Path to save output Listado de Clientes
    ruta_salida = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes"

    # Open an excel file to start saving dataframe each sheet
    with pd.ExcelWriter(
        ruta_salida + "\\" + "Retiros_" + str(mes_numeral) + ".xlsx", engine="openpyxl"
    ) as writer:
        # Write each dataframe to a different worksheet.
        df_clientes.to_excel(writer, sheet_name="Listado_Clientes", index=False)

        df_clientes_R.to_excel(writer, sheet_name="Listado_Clientes_R", index=False)

        df_clientes_L.to_excel(writer, sheet_name="Listado_Clientes_L", index=False)

    del listado_clientes, listado_clientes_R, listado_clientes_L
   
