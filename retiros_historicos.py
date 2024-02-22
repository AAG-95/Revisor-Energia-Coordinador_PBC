import pandas as pd
import glob
import funciones as fc
import os

ruta_balances_clientes_libres = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Retiros Mensuales"

ruta_balances_historicos_clientes_L = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Retiros Históricos Clientes"
ruta_balances_historicos_clientes_R = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Retiros Históricos Clientes"

# Path to Registro Cambio Clientes Libres
ruta_registro_cambios_clientes_L = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Registro de Cambios\Registro_de_Cambios_Clientes_Libres.csv"


# Path to Registro Cambio Clientes Reglados
ruta_registro_cambios_clientes_R = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Registro de Cambios\Registro_de_Cambios_Clientes_Regulados.csv"


# Definición de variables de año y mes
primer_año = 2020
primer_mes_primer_año = 1

último_año = 2020
último_mes_último_año = 2

# Genera una lista de pares de años y meses
pares_lista = fc.ConversionDatos().generar_pares(
    primer_año, último_año, primer_mes_primer_año, último_mes_último_año
)


#! Dataframes históricos Clientes Libres
if os.path.isfile(
    ruta_balances_historicos_clientes_L + "\Retiros_Históricos_Clientes_L.csv"
):

    df_historico_clientes_L = pd.read_csv(
        ruta_balances_historicos_clientes_L + "\Retiros_Históricos_Clientes_L.csv",
        sep=";",
        encoding="UTF-8",
    )
    valores_mes = df_historico_clientes_L["Mes"].unique()
else:
    print(
        f"No existe BDD de Retiros de Energía Histórica en: {ruta_balances_historicos_clientes_L}"
    )
    df_historico_clientes_L = pd.DataFrame()
    valores_mes = []

#! Dataframes históricos Clientes Regulados
if os.path.isfile(
    ruta_balances_historicos_clientes_R + "\Retiros_Históricos_Clientes_R.csv"
):

    df_historico_clientes_R = pd.read_csv(
        ruta_balances_historicos_clientes_R + "\Retiros_Históricos_Clientes_R.csv",
        sep=";",
        encoding="UTF-8",
    )
    valores_mes = df_historico_clientes_R["Mes"].unique()
else:
    print(
        f"No existe BDD de Retiros de Energía Histórica en: {ruta_balances_historicos_clientes_R}"
    )
    df_historico_clientes_R = pd.DataFrame()
    valores_mes = []


#! Listado meses Clientes L
# Convert values
dataframe_clientes_L = []
for pair in pares_lista:
    print(pair)
    i = pair[1]
    df_mes_clientes_L = pd.read_excel(
        ruta_balances_clientes_libres + f"\Retiros_{i}.xlsx",
        sheet_name="Listado_Clientes_L",
    )
    # Get first 18 columns
    df_mes_clientes_L = df_mes_clientes_L.iloc[:, :18]
    # Erase emprty rows
    df_mes_clientes_L = df_mes_clientes_L.dropna(how="all")
    dataframe_clientes_L.append(df_mes_clientes_L)


#! Listado meses Clientes R
# Convert values
dataframe_clientes_R = []
for pair in pares_lista:
    print(pair)
    i = pair[1]
    df_mes_clientes_R = pd.read_excel(
        ruta_balances_clientes_libres + f"\Retiros_{i}.xlsx",
        sheet_name="Listado_Clientes_L",
    )
    # Get first 18 columns
    df_mes_clientes_R = df_mes_clientes_R.iloc[:, :18]
    # Erase emprty rows
    df_mes_clientes_R = df_mes_clientes_R.dropna(how="all")
    dataframe_clientes_R.append(df_mes_clientes_R)


  # ? Update Registros Históricos Clientes Libres--------------------------------------------------------------
# Verificar si el mes de cada df de mes ya se encuentra en el histórico
#! Unión de Dataframes
for df_clientes_L in dataframe_clientes_L:
    if os.path.isfile(
        ruta_balances_historicos_clientes_L + "\Retiros_Históricos_Clientes_L.csv"
    ):

        # Obtain Month unique in column Mes
        mes_fecha = pd.Timestamp(df_clientes_L["Mes"].unique()[0]).strftime("%m-%d-%Y")

        df_historico_clientes_L = pd.read_csv(
            ruta_balances_historicos_clientes_L + "\Retiros_Históricos_Clientes_L.csv",
            sep=";",
            encoding="UTF-8",
        )

        # If value in first row is
        # Convert column Mes to datetime with format datetime.datetime(2023, 9, 1, 0, 0)
        df_historico_clientes_L["Mes"] = pd.to_datetime(
            df_historico_clientes_L["Mes"]
        ).dt.strftime("%m-%d-%Y")
        df_clientes_L["Mes"] = pd.to_datetime(df_clientes_L["Mes"])

        print(df_historico_clientes_L["Mes"].unique().tolist())

        if mes_fecha not in df_historico_clientes_L["Mes"].unique().tolist():
            print(
                "Se actualiza el archivo Registro de Cambios Históricos Libre con registro mes: "
                + str(mes_fecha)
            )

            df_retiros_historico_L_final = pd.concat(
                [df_historico_clientes_L, df_clientes_L]
            )

            columnas_numericas = [
                "Medida 1",
                "(0/1)",
                "Medida 2",
                "(0/1).1",
                "Medida 3",
                "(0/1).2",
                "Error",
                "Cálculo",
            ]  # replace with your column names

            # Replace "." with "," in the selected columns
            for column in columnas_numericas:
                df_retiros_historico_L_final[column] = (
                    df_retiros_historico_L_final[column]
                    .astype(str)
                    .str.replace(".", ",")
                )

            df_retiros_historico_L_final["Mes"] = df_retiros_historico_L_final[
                "Mes"
            ].dt.strftime("%m-%d-%Y")
            # Rewrite df_registro_cambios_empresas_final into ruta_registro_cambios_Empresas
            df_retiros_historico_L_final.to_csv(
                ruta_balances_historicos_clientes_L
                + "\Retiros_Históricos_Clientes_L.csv",
                sep=";",
                index=False,
            )

            # ? Update and save Registro Cambios Clientes
            df_registro_cambios_clientes_L = df_retiros_historico_L_final.reset_index(
                drop=True
            )

            df_registro_cambios_clientes_L = df_registro_cambios_clientes_L[
                ["Nombre", "Clave", "Suministrador_final", "Mes"]
            ]

            df_registro_cambios_clientes_L["Nombre_Cliente_Actual_Para_Clave"] = (
                df_registro_cambios_clientes_L.sort_values("Mes")
                .groupby("Clave")["Nombre"]
                .transform("last")
            )

            df_registro_cambios_clientes_L["Mes_Actual_De_Nombre_Cliente"] = (
                df_registro_cambios_clientes_L.sort_values("Mes")
                .groupby("Clave")["Mes"]
                .transform("last")
            )

            # Replaces Na column with -
            df_registro_cambios_clientes_L["Nombre"] = df_registro_cambios_clientes_L[
                "Nombre"
            ].fillna("-")

            # Replace whitespace with a special character
            cols = ["Nombre", "Clave", "Suministrador_final"]
            for col in cols:
                df_registro_cambios_clientes_L[col] = df_registro_cambios_clientes_L[
                    col
                ].str.replace(" ", "##_#")

            # Perform your operations
            df_registro_cambios_clientes_L = (
                df_registro_cambios_clientes_L.drop_duplicates(subset=cols, keep="last")
            )

            # Replaces Na column with -
            df_registro_cambios_clientes_L["Nombre"] = df_registro_cambios_clientes_L[
                "Nombre"
            ].fillna("-")

            df_registro_cambios_clientes_L = df_registro_cambios_clientes_L.dropna(
                subset=["Nombre", "Clave", "Suministrador_final"]
            )

            df_registro_cambios_clientes_L = (
                df_registro_cambios_clientes_L.drop_duplicates(
                    subset=["Nombre", "Clave", "Suministrador_final"], keep="last"
                )
            )

            # Replace the special character back to whitespace
            for col in cols:
                df_registro_cambios_clientes_L[col] = df_registro_cambios_clientes_L[
                    col
                ].str.replace("##_#", " ")

            df_registro_cambios_clientes_L.rename(
                columns={"Nombre": "Cliente"}, inplace=True
            )

            df_registro_cambios_clientes_L.to_csv(
                ruta_registro_cambios_clientes_L, sep=";", index=False, encoding="UTF-8"
            )
        else:
            print(
                "Revisar Base De Datos de Clientes Libres Históricos, el Mes Actual"
                + mes_fecha
                + " ya fue actualizado anteriormente"

            )
  # ? Update Registros Históricos Clientes Regulados--------------------------------------------------------------

for df_clientes_R in dataframe_clientes_R:
  
    if os.path.isfile(
        ruta_balances_historicos_clientes_R + "\Retiros_Históricos_Clientes_R.csv"
    ):
        # Obtain Month unique in column Mes
        mes_fecha = pd.Timestamp(df_clientes_R["Mes"].unique()[0]).strftime("%m-%d-%Y")
        df_historico_clientes_R = pd.read_csv(
            ruta_balances_historicos_clientes_R + "\Retiros_Históricos_Clientes_R.csv",
            sep=";",
            encoding="UTF-8",
        )

        # If value in first row is
        # Convert column Mes to datetime with format datetime.datetime(2023, 9, 1, 0, 0)
        df_historico_clientes_R["Mes"] = pd.to_datetime(
            df_historico_clientes_R["Mes"]
        ).dt.strftime("%m-%d-%Y")
        df_clientes_R["Mes"] = pd.to_datetime(df_clientes_R["Mes"])

        if mes_fecha not in df_historico_clientes_R["Mes"].unique().tolist():
            print(
                "Se actualiza el archivo Registro de Cambios Históricos Regulados con registro mes: "
                + str(mes_fecha)
            )

            df_retiros_historico_R_final = pd.concat(
                [df_historico_clientes_R, df_clientes_R]
            )

            columnas_numericas = [
                "Medida 1",
                "(0/1)",
                "Medida 2",
                "(0/1).1",
                "Medida 3",
                "(0/1).2",
                "Error",
                "Cálculo",
            ]  # replace with your column names

            # Replace "." with "," in the selected columns
            for column in columnas_numericas:
                df_retiros_historico_R_final[column] = (
                    df_retiros_historico_R_final[column]
                    .astype(str)
                    .str.replace(".", ",")
                )

            df_retiros_historico_R_final["Mes"] = pd.to_datetime(
                df_retiros_historico_R_final["Mes"]
            )
            df_retiros_historico_R_final["Mes"] = df_retiros_historico_R_final[
                "Mes"
            ].dt.strftime("%m-%d-%Y")
            # Rewrite df_registro_cambios_empresas_final into ruta_registro_cambios_Empresas
            df_retiros_historico_R_final.to_csv(
                ruta_balances_historicos_clientes_R
                + "\Retiros_Históricos_Clientes_R.csv",
                sep=";",
                index=False,
            )

            # ? Update and save Registro Cambios Clientes
            df_registro_cambios_clientes_R = df_retiros_historico_R_final.reset_index(
                drop=True
            )

            df_registro_cambios_clientes_R = df_registro_cambios_clientes_R[
                ["Nombre", "Clave", "Suministrador_final", "Mes"]
            ]

            df_registro_cambios_clientes_R["Nombre_Cliente_Actual_Para_Clave"] = (
                df_registro_cambios_clientes_R.sort_values("Mes")
                .groupby("Clave")["Nombre"]
                .transform("last")
            )

            df_registro_cambios_clientes_R["Mes_Actual_De_Nombre_Cliente"] = (
                df_registro_cambios_clientes_R.sort_values("Mes")
                .groupby("Clave")["Mes"]
                .transform("last")
            )

            # Replaces Na column with -
            df_registro_cambios_clientes_R["Nombre"] = df_registro_cambios_clientes_R[
                "Nombre"
            ].fillna("-")

            # Replace whitespace with a special character
            cols = ["Nombre", "Clave", "Suministrador_final"]
            for col in cols:
                df_registro_cambios_clientes_R[col] = df_registro_cambios_clientes_R[
                    col
                ].str.replace(" ", "##_#")

            # Perform your operations
            df_registro_cambios_clientes_R = (
                df_registro_cambios_clientes_R.drop_duplicates(subset=cols, keep="last")
            )

            # Replaces Na column with -
            df_registro_cambios_clientes_R["Nombre"] = df_registro_cambios_clientes_R[
                "Nombre"
            ].fillna("-")

            df_registro_cambios_clientes_R = df_registro_cambios_clientes_R.dropna(
                subset=["Nombre", "Clave", "Suministrador_final"]
            )

            df_registro_cambios_clientes_R = (
                df_registro_cambios_clientes_R.drop_duplicates(
                    subset=["Nombre", "Clave", "Suministrador_final"], keep="last"
                )
            )

            # Replace the special character back to whitespace
            for col in cols:
                df_registro_cambios_clientes_R[col] = df_registro_cambios_clientes_R[
                    col
                ].str.replace("##_#", " ")

            df_registro_cambios_clientes_R.rename(
                columns={"Nombre": "Cliente"}, inplace=True
            )

            df_registro_cambios_clientes_R.to_csv(
                ruta_registro_cambios_clientes_R, sep=";", index=False, encoding="UTF-8"
            )
        else:
            print(
                "Revisar Base De Datos de Clientes Regulados Históricos, el Mes Actual"
                + mes_fecha
                + " ya fue actualizado anteriormente"
            )

        """ df_historico = pd.concat([df_historico, i])
        print(f"Se incorpora el mes {mes} en el histórico del balance de energía") """


#! Salida de archivo retiros históricos
""" ruta_salida = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Retiros Históricos Clientes"
 """

""" df_historico.to_csv(
    ruta_salida + "\\" + "Retiros_Históricos_Clientes_L" + ".csv",
    sep=";", encoding="UTF-8", index=False)
 """
