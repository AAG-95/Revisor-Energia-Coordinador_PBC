# Creador Listado Clientes

import pandas as pd
import zipfile
import pandas as pd
import zipfile
import xlrd
import Funciones as fc

# Open data from a ZIP file Abril-2020-R03D-1.zip in \\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Balances\Balances de Energía\Archivos Fuente\2020

mes = "Ago20"
mes = fc.convertir_fecha(mes)
mes_numeral= "2008"

# Path to Homologacion_Propietarios_Balance_Fisico.xlsx
ruta_homologa_propietarios = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\02 Repartición\Balances\Homologaciones\Homologacion_Propietarios_Balance_Fisico.xlsx"

# Get dataframe from ruta_homologa_propietarios sheet 'Homologa'
df_homologa_propietarios = pd.read_excel(
    ruta_homologa_propietarios, sheet_name="Homologa"
)

lista_balance_fisico= ["REVISION_NORTE_","REVISION_NORTE_DX_","REVISION_SUR_", "REVISION_SUR_DX_"]

listado_clientes = []
listado_clientes_R = []
listado_clientes_L = []

zip_path = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Balances\Balances de Energía\Archivos Fuente\2020\Ago20_R01D-2.zip"
with zipfile.ZipFile(zip_path) as myzip:
    for i in lista_balance_fisico:
        print(i)
        with myzip.open(
            "01 Resultados/02 Balance Físico/"+ i + mes_numeral + ".xls"
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
            df_clientes["Mes"] = mes

            # Drop Rows from column df_clientes['Nombre'] that contains 'TOTAL' or NaN
            df_clientes = df_clientes[df_clientes["Nombre"] != "TOTAL"]
            df_clientes = df_clientes[df_clientes["Nombre"] != "NaN"]

            # From Column Tipo filter 'R', 'L' or 'L_D'
            retiros_clientes = df_clientes[
                df_clientes["Tipo"].isin(["R", "L", "L_D"])
            ]
           
           
    

            # Merge dataframe df_clientes with df_homologa_propietarios based in column Propietario from both df
            retiros_clientes = pd.merge(
                retiros_clientes, df_homologa_propietarios, on="Propietario", how="left"
            )

            # Check if Column Suministrador_final has NaN, if Column has NaN, print this row and end program
            if retiros_clientes["Suministrador_final"].isnull().values.any():
                print("Columnas con NaN en Suministrador_Final")
                print(df_clientes[df_clientes["Suministrador_final"].isnull()])
                exit()

            # retiros divided in R and L   
            retiros_clientes_R = retiros_clientes[retiros_clientes["Tipo"].isin(["R"])]

            retiros_clientes_L = retiros_clientes[retiros_clientes["Tipo"].isin(["L", "L_D"])]
                
            listado_clientes.append(retiros_clientes)
            listado_clientes_R.append(retiros_clientes_R)
            listado_clientes_L.append(retiros_clientes_L)



df_clientes = pd.concat(listado_clientes)
df_clientes_R = pd.concat(listado_clientes_R) 
df_clientes_L = pd.concat(listado_clientes_L)  


