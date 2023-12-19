import pandas as pd
import glob
import funciones as fc
import os

ruta_balances_clientes_libres = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes"

ruta_balances_historicos_clientes_L = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Registro Histórico Clientes"

# Definición de variables de año y mes
primer_año = 2023
primer_mes_primer_año = 1

último_año = 2023
último_mes_último_año = 7

# Genera una lista de pares de años y meses
pares_lista = fc.ConversionDatos().generar_pares(
    primer_año, último_año, primer_mes_primer_año, último_mes_último_año
)

#! Listado meses 
# Convert values
dataframe = []
for pair in pares_lista:
    
    i = pair[1]
    df_mes = pd.read_excel(ruta_balances_clientes_libres + f"\Retiros_{i}.xlsx", sheet_name="Listado_Clientes_L")
    # Get first 18 columns
    df_mes = df_mes.iloc[:, :18]
    # Erase emprty rows
    df_mes = df_mes.dropna(how="all")
    dataframe.append(df_mes)
    
#! Dataframes históricos
if os.path.isfile(ruta_balances_historicos_clientes_L + "\Retiros_Históricos_Clientes_L.csv"):

    df_historico = pd.read_csv(ruta_balances_historicos_clientes_L + "\Retiros_Históricos_Clientes_L.csv", sep=";", encoding = "UTF-8" )
else:
    print(f"File does not exist: {ruta_balances_historicos_clientes_L}")
    df_histórico = pd.DataFrame()

valores_mes = df_historico["Mes"].unique()

# Verificar si el mes de cada df de mes ya se encuentra en el histórico

#! Unión de Dataframes
for i in dataframe:
    mes = i["Mes"].unique()[0]
    if mes in valores_mes:
        print(f"El mes {mes} ya se encuentra en el histórico")
    else: 
        df_historico = pd.concat([df_historico, i])
            
ruta_salida = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes"

df_historico.to_excel(
    ruta_salida + "\\" + "Prueba_Históricos_Clientes_L" + ".xlsx",
    engine="openpyxl",
    index=False,
)
