# Creador Listado Clientes

import pandas as pd
import zipfile
import pandas as pd
import zipfile
import xlrd
import Funciones as fc
from datetime import datetime
from dateutil.relativedelta import relativedelta
import openpyxl
import os

#! Month Selection

# Open data from a ZIP file Abril-2020-R03D-1.zip in \\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Balances\Balances de Energía\Archivos Fuente\2020

mes = "Nov22"
mes_fecha = fc.convertir_fecha(mes)
mes_numeral = "2211"

# Get previous month from mes_fecha
mes_anterior = mes_fecha - relativedelta(months=1)


#! Main Program
# Path to Homologacion_Propietarios_Balance_Fisico.xlsx
ruta_homologa_propietarios = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\02 Repartición\Balances\Homologaciones\Homologacion_Propietarios_Balance_Fisico.xlsx"

# Path to Homologacion Listado Clientes
ruta_registro_cambios = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Registro de Cambios\Registro_de_Cambios_Empresas.csv"

# Path to ZIP file, balance fisico
zip_path = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Balances\Balances de Energía\Archivos Fuente\2022\Nov2022-B01D.zip"

# Get dataframe from ruta_homologa_propietarios sheet 'Homologa'
df_homologa_propietarios = pd.read_excel(
    ruta_homologa_propietarios, sheet_name="Homologa"
)

# List of sheets to read from ZIP file
lista_balance_fisico = [
    "REVISION_NORTE_",
    "REVISION_NORTE_DX_",
    "REVISION_SUR_",
    "REVISION_SUR_DX_",
]

listado_clientes = []
listado_clientes_R = []
listado_clientes_L = []

# List of possible file paths
file_paths = [
    "01 Resultados/02 Balance Físico/",
    "01 Resultados/01 Balance de Energía/02 Balance Físico/",
]

correct_path = None

with zipfile.ZipFile(zip_path) as myzip:
    for i in lista_balance_fisico:
        print(i)

        for path in file_paths:
            try:
                with myzip.open(path + i + mes_numeral + ".xls") as myfile:
                    df_balance_fisico = pd.read_excel(myfile)
                    print(f"File exists at {path}")
                    correct_path = path  # store the correct path
                    break  # if file is found and opened successfully, break the loop
            except KeyError:
                continue  # if file is not found, continue to the next path

        with myzip.open(
            correct_path + i + mes_numeral + ".xls"
        ) as myfile:
            df_balance_fisico = pd.read_excel(
                myfile, sheet_name="Balance por Barra", header=None
            )

            # Seleted table from sheet Balance por Barra
            df_clientes = fc.obtencion_tablas_clientes(df_balance_fisico, 6, 2, 17)

            # Change Nombre_2 to Barra
            df_clientes.rename(columns={"Nombre_2": "Barra"}, inplace=True)
            # Change (0/1)_2 into Medidas 2 and (0/1)_3 into Medidas 3
            df_clientes.rename(
                columns={"(0/1)_2": "Medidas 2", "(0/1)_3": "Medidas 3"}, inplace=True
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


# Get database from ruta_registro_cambios
df_registro_cambios = pd.read_csv(ruta_registro_cambios, sep=";")

# Change column mes_fecha to datetime, example input 1-08-2020
df_registro_cambios["Mes"] = pd.to_datetime(df_registro_cambios["Mes"], dayfirst=True)

# Filter month column from df_registro_cambios with mes_anterior
df_registro_cambios_mes_anterior = df_registro_cambios[
    df_registro_cambios["Mes"] == mes_anterior
]

# Get Values that are in df_clientes_unique and not in df_registro_cambios_mes_anterior
df_nuevas_empresas = df_clientes_unique[
    ~df_clientes_unique["Suministrador_final"].isin(
        df_registro_cambios_mes_anterior["Suministrador_final"]
    )
]

# Empresas Eliminadas
df_empresas_eliminadas = df_registro_cambios_mes_anterior[
    ~df_registro_cambios_mes_anterior["Suministrador_final"].isin(
        df_clientes_unique["Suministrador_final"]
    )
]

# Column of df to list
print(
    "Empresas nuevas mes_fecha Actual:",
    df_nuevas_empresas["Suministrador_final"].to_list(),
)
print(
    "Empresas eliminadas respecto a mes_fecha Anterior:",
    df_empresas_eliminadas["Suministrador_final"].to_list(),
)

# Concatenate df_registro_cambios_mes_anterior with df_clientes_unique
df_registro_cambios_final = pd.concat(
    [df_registro_cambios_mes_anterior, df_clientes_unique]
)


#! Output of program
# Path to save output
ruta_salida = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes"

# Open an excel file to start saving dataframe each sheet
with pd.ExcelWriter(
    ruta_salida + "\\" + "Retiros_" + str(mes) + ".xlsx", engine="openpyxl"
) as writer:
    # Write each dataframe to a different worksheet.
    df_clientes.to_excel(writer, sheet_name="Listado_Clientes", index=False)

    df_clientes_R.to_excel(writer, sheet_name="Listado_Clientes_R", index=False)

    df_clientes_L.to_excel(writer, sheet_name="Listado_Clientes_L", index=False)


# Get database
# Comparador con proceso del mes_fecha pasado
