import pandas as pd
import glob
import funciones as fc
import os

ruta_balances_clientes_libres = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Retiros Mensuales"

ruta_balances_historicos_clientes_L = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Retiros Históricos Clientes"

# Definición de variables de año y mes
primer_año = 2020
primer_mes_primer_año = 1

último_año = 2023
último_mes_último_año = 10

# Genera una lista de pares de años y meses
pares_lista = fc.ConversionDatos().generar_pares(
    primer_año, último_año, primer_mes_primer_año, último_mes_último_año
)


#! Dataframes históricos
if os.path.isfile(ruta_balances_historicos_clientes_L + "\Retiros_Históricos_Clientes_L.csv"):

    df_historico = pd.read_csv(ruta_balances_historicos_clientes_L + "\Retiros_Históricos_Clientes_L.csv", sep=";", encoding = "UTF-8" )
    valores_mes = df_historico["Mes"].unique()
else:
    print(f"No existe BDD de Retiros de Energía Histórica en: {ruta_balances_historicos_clientes_L}")
    df_historico = pd.DataFrame()
    valores_mes = []



#! Listado meses 
# Convert values
dataframe = []
for pair in pares_lista:
    print(pair)
    i = pair[1]
    df_mes = pd.read_excel(ruta_balances_clientes_libres + f"\Retiros_{i}.xlsx", sheet_name="Listado_Clientes_L")
    # Get first 18 columns
    df_mes = df_mes.iloc[:, :18]
    # Erase emprty rows
    df_mes = df_mes.dropna(how="all")
    dataframe.append(df_mes)
    


# Verificar si el mes de cada df de mes ya se encuentra en el histórico
#! Unión de Dataframes
for i in dataframe:
    mes = str(i["Mes"].unique()[0]) 
    if mes in valores_mes:
        print(f"El mes {mes} ya se encuentra en el histórico del balance de energía")
    else: 
        # List of columns where you want to replace the character
        columnas_numericas = ['Medida 1','(0/1)','Medida 2','(0/1).1','Medida 3','(0/1).2','Error','Cálculo']  # replace with your column names

        # Replace "." with "," in the selected columns
        for column in columnas_numericas:
            i[column] = i[column].astype(str).str.replace(".", ",")
         

        df_historico = pd.concat([df_historico, i])
        print(f"Se incorpora el mes {mes} en el histórico del balance de energía")

#! Salida de archivo retiros históricos        
ruta_salida = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Retiros Históricos Clientes"

df_historico.to_csv(
    ruta_salida + "\\" + "Prueba_Históricos_Clientes_L" + ".csv",
    sep=";", encoding="UTF-8", index=False)
