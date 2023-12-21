import pandas as pd
import funciones as fc

# Carpeta de salida
carpeta_salida = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Balance-Recaudación\\"

# Carpeta de recaudación
carpeta_recaudación = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Recaudación\\Revisión Histórica\\"

# Carpeta de energía
carpeta_energia = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\\02 Repartición\Balances\\Listados de Clientes\\Retiros Históricos Clientes\\"

# Fecha inicio y fin de la revisión
primer_año = 2023
primer_mes_primer_año = 10

último_año = 2023
último_mes_último_año = 10

# Genera una lista de pares de años y meses
pares_lista = fc.ConversionDatos().generar_pares(
    primer_año, último_año, primer_mes_primer_año, último_mes_último_año
)

# Archivo de recaudación
df_energia = pd.read_csv(
    carpeta_energia + "Retiros_Históricos_Clientes_L.csv",
    sep=";",
    encoding="UTF-8",
)

# Nueva columna concateando columnas Barra, Clave y Suministrador_Final
df_energia["Barra-Clave-Suministrador-Mes"] = (
    df_energia["Barra"].astype(str)
    + "-_-"
    + df_energia["Clave"].astype(str)
    + "-_-"
    + df_energia["Suministrador_final"].astype(str)
    + "-_-"
    + df_energia["Mes"].astype(str)
)

# change column name Medidas_2 to Energía Balance [kWh] and make all values negative
df_energia["Medida 2"] = df_energia["Medida 2"].str.replace(",",".").astype(float)
df_energia["Medida 2"] = df_energia["Medida 2"] * -1
df_energia.rename(columns={"Medida 2": "Energía Balance [kWh]"}, inplace=True)

# Mantain only column Barra-Clave-Suministrador-Mes and Energía Balance [kWh]
df_energia = df_energia[["Barra-Clave-Suministrador-Mes", "Energía Balance [kWh]"]]

df_recaudacion = pd.read_csv(
    carpeta_recaudación
    + "BDD Clientes Históricos.csv",
    sep=";",
    encoding="UTF-8",
)

# filtrar solo las empresas que recaudan
df_recaudacion = df_recaudacion[df_recaudacion["Empresa_Planilla_Recauda_Cliente"] == 1]

df_recaudacion["Barra-Clave-Suministrador-Mes"] = (
    df_recaudacion["Barra"].astype(str)
    + "-_-"
    + df_recaudacion["Clave"].astype(str)
    + "-_-"
    + df_recaudacion["Recaudador"].astype(str)
    + "-_-"
    + df_recaudacion["Mes Consumo"].astype(str)
)

# Mantain only column Barra-Clave-Suministrador-Mes and Energía [kWh]
df_recaudacion = df_recaudacion[["Barra-Clave-Suministrador-Mes", "Energía [kWh]"]]

# Add column Energía [kWh] from df_recaudación into
# df_energía by column Barra-Clave-Suministrador-Mes. Conservar Columna Barra-Clave-Suministrador-Mes
df_combinado = pd.merge(
    df_energia,
    df_recaudacion[["Barra-Clave-Suministrador-Mes", "Energía [kWh]"]],
    on="Barra-Clave-Suministrador-Mes",
    how="left",
).reset_index(drop=True)

print(df_energia["Barra-Clave-Suministrador-Mes"].unique())
print(df_recaudacion["Barra-Clave-Suministrador-Mes"].unique())
print(df_combinado["Barra-Clave-Suministrador-Mes"])

# change column name Energía [kWh] to Energía Recaudada [kWh] and make all values negative
df_combinado.rename(columns={"Energía [kWh]": "Energía Declarada [kWh]"}, inplace=True)

df_combinado["Energía Balance [kWh]"] = (
    df_combinado["Energía Balance [kWh]"]
    .astype(str)
    .str.replace(",", ".")
    .astype(float)
)

df_combinado["Energía Declarada [kWh]"] = (
    df_combinado["Energía Declarada [kWh]"]
    .astype(str)
    .str.replace(",", ".")
    .astype(float)
)

# New Column difference between Energía Balance [kWh] and Energía Recaudada [kWh]
df_combinado["Diferencia Energía [kWh]"] = (
    df_combinado["Energía Balance [kWh]"] - df_combinado["Energía Declarada [kWh]"]
)

# New Column percentage between Energía Balance [kWh] and Energía Recaudada [kWh]
df_combinado["% Diferencia Energía"] = (
    df_combinado["Energía Balance [kWh]"] - df_combinado["Energía Declarada [kWh]"]
) / df_combinado["Energía Balance [kWh]"]

# New Column if df_combinado["Energía Balance [kWh]"] is 0 or nan then "Clave Obsoleta", else if df_combinado["Energía Balance [kWh]"] is not 0 or nan and df_combinado["Diferencia Energía [kWh]"] is 0 or nan then "Clave no informada en RCUT", if df_combinado["% Diferencia Energía"] is greater than 0.05 then "Diferencia Energía con Diferencias", else "Diferencia Energía sin Diferencias"

df_combinado["Tipo"] = df_combinado.apply(
    lambda x: "Clave Obsoleta"
    if pd.isna(x["Energía Balance [kWh]"]) or x["Energía Balance [kWh]"] == 0
    else (
        "Clave no informada en RCUT"
        if pd.isna(x["Diferencia Energía [kWh]"])
        else (
            "Diferencia Energía con Diferencias"
            if x["% Diferencia Energía"] > 0.05
            else "Diferencia Energía sin Diferencias"
        )
    ),
    axis=1,
)

# Split
df_combinado["Barra"] = df_combinado["Barra-Clave-Suministrador-Mes"].str.split(
    "-_-", expand=True
)[0]
df_combinado["Clave"] = df_combinado["Barra-Clave-Suministrador-Mes"].str.split(
    "-_-", expand=True
)[1]
df_combinado["Suministrador"] = df_combinado["Barra-Clave-Suministrador-Mes"].str.split(
    "-_-", expand=True
)[2]

a = 5
