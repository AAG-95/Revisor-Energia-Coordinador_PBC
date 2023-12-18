import pandas as pd
import funciones as fc

# Carpeta de salida
carpeta_salida = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Balance-Recaudación\\"

# Carpeta de recaudación
carpeta_recaudación = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Recaudación\\"

# Carpeta de energía
carpeta_energia = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\\02 Repartición\Balances\\Listados de Clientes\\"

# Fecha inicio y fin de la revisión
primer_año = 2023
primer_mes_primer_año = 10

último_año = 2023
último_mes_último_año = 10

# Genera una lista de pares de años y meses
pares_lista = fc.ConversionDatos().generar_pares(
    primer_año, último_año, primer_mes_primer_año, último_mes_último_año
)

for par in pares_lista:
    mes_rep = fc.ConversionDatos().convertir_numeral_datetime(par[1])

    # Archivo de recaudación
    df_energia = pd.read_excel(
        carpeta_energia + "Retiros_" + str(par[1]) + ".xlsx",
        sheet_name="Listado_Clientes_L",
        engine="openpyxl",
        header=0,
    )

    # Nueva columna concateando columnas Barra, Clave y Suministrador_Final
    df_energia["Barra-Clave-Suministrador-Mes"] = (
        df_energia["Barra"].astype(str)
        + "-_-"
        + df_energia["Clave"].astype(str)
        + "-_-"
        + df_energia["Suministrador_final"].astype(str)
        
    )

    df_recaudacion = pd.read_csv(
        carpeta_recaudación
        + "BDD_"
        + str(par[1])
        + "\\"
        + "Revisor_Clientes"
        + str(par[1])
        + ".csv",
        sep=";",
        encoding="latin1",
    )

    # filtrar solo las empresas que recaudan
    df_recaudacion = df_recaudacion[
        df_recaudacion["Empresa_Planilla_Recauda_Cliente"] == 1
    ]


    df_recaudacion["Barra-Clave-Suministrador-Mes"] = (
        df_recaudacion["Barra"].astype(str)
        + "-_-"
        + df_recaudacion["Clave"].astype(str)
        + "-_-"
        + df_recaudacion["Recaudador"].astype(str)
        
    )
    
    # Add column Energía [kWh] from df_recaudación into 
    # df_energía by column Barra-Clave-Suministrador-Mes. Conservar Columna Barra-Clave-Suministrador-Mes
    df_combinado = pd.merge(df_energia, df_recaudacion[["Barra-Clave-Suministrador-Mes", "Energía [kWh]"]], on="Barra-Clave-Suministrador-Mes", how="left")

    print(df_energia["Barra-Clave-Suministrador-Mes"].unique())
    print(df_recaudacion["Barra-Clave-Suministrador-Mes"].unique())
    print(df_combinado["Barra-Clave-Suministrador-Mes"])


    a = 5
