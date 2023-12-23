import pandas as pd
import funciones as fc
import numpy as np
import pandas as pd
import funciones as fc
import numpy as np


class ComparadorRecaudacionEnergia:
    def __init__(self):
        # Carpeta de salida
        self.carpeta_salida = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Balance-Recaudación\\"
        # Carpeta de recaudación
        self.carpeta_recaudacion = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Recaudación\\Revisión Histórica\\"
        # Carpeta de energía
        self.carpeta_energia = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\\02 Repartición\Balances\\Listados de Clientes\\Retiros Históricos Clientes\\"
        # Fecha inicio y fin de la revisión
        self.primer_año = 2023
        self.primer_mes_primer_año = 10
        self.último_año = 2023
        self.último_mes_último_año = 10

    def generar_pares(self):
        pares_lista = fc.ConversionDatos().generar_pares(
            self.primer_año, self.último_año, self.primer_mes_primer_año, self.último_mes_último_año
        )
        return pares_lista

    def cargar_datos_energia(self):
        df_energia = pd.read_csv(
            self.carpeta_energia + "Retiros_Históricos_Clientes_L.csv",
            sep=";",
            encoding="UTF-8",
        )
        df_energia["Barra-Clave-Suministrador-Mes"] = (
            df_energia["Barra"].astype(str)
            + "-_-"
            + df_energia["Clave"].astype(str)
            + "-_-"
            + df_energia["Suministrador_final"].astype(str)
            + "-_-"
            + df_energia["Mes"].astype(str)
        )
        df_energia["Medida 2"] = df_energia["Medida 2"].str.replace(",", ".").astype(float)
        df_energia["Medida 2"] = df_energia["Medida 2"] * -1
        df_energia.rename(columns={"Medida 2": "Energía Balance [kWh]"}, inplace=True)
        df_energia = df_energia[["Barra-Clave-Suministrador-Mes", "Energía Balance [kWh]"]]
        df_energia = df_energia.groupby(["Barra-Clave-Suministrador-Mes"]).agg(
            {"Energía Balance [kWh]": "sum"}
        ).reset_index()
        return df_energia

    def cargar_datos_recaudacion(self):
        df_recaudacion = pd.read_csv(
            self.carpeta_recaudacion + "BDD Clientes Libres Históricos.csv",
            sep=";",
            encoding="UTF-8",
        )
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
        df_recaudacion["Energía [kWh]"] = df_recaudacion["Energía [kWh]"].str.replace(",", ".").replace("-", np.nan, regex=False).replace("[^0-9.]", np.nan, regex=True).replace("na", np.nan).astype(float)
        df_recaudacion = df_recaudacion.groupby(["Barra-Clave-Suministrador-Mes"]).agg(
            {"Energía [kWh]": "sum", "mes_repartición": lambda x: list(x)}
        ).reset_index()
        return df_recaudacion

    def combinar_datos(self, df_energia, df_recaudacion):
        df_combinado = pd.merge(
            df_energia,
            df_recaudacion[["Barra-Clave-Suministrador-Mes", "Energía [kWh]", "mes_repartición"]],
            on="Barra-Clave-Suministrador-Mes",
            how="left",
        ).reset_index(drop=True)
        df_combinado.rename(columns={"Energía [kWh]": "Energía Declarada [kWh]"}, inplace=True)
        df_combinado["Energía Balance [kWh]"] = df_combinado["Energía Balance [kWh]"].astype(str).str.replace(",", ".").astype(float)
        df_combinado["Diferencia Energía [kWh]"] = df_combinado["Energía Balance [kWh]"] - df_combinado["Energía Declarada [kWh]"]
        df_combinado["% Diferencia Energía"] = df_combinado["Diferencia Energía [kWh]"] / df_combinado["Energía Balance [kWh]"]
        df_combinado["Tipo"] = df_combinado.apply(
            lambda x: "Clave Obsoleta" if pd.isna(x["Energía Balance [kWh]"]) or x["Energía Balance [kWh]"] == 0 else (
                "Clave no informada en RCUT" if pd.isna(x["Diferencia Energía [kWh]"]) else (
                    "Diferencia Energía con Diferencias" if x["% Diferencia Energía"] > 0.05 else "Diferencia Energía sin Diferencias"
                )
            ),
            axis=1,
        )
        df_combinado[["Barra", "Clave", "Suministrador", "Mes Consumo"]] = df_combinado["Barra-Clave-Suministrador-Mes"].str.split("-_-", expand=True)
        df_combinado = df_combinado[[
            "Barra",
            "Clave",
            "Suministrador",
            "Mes Consumo",
            "mes_repartición",
            "Energía Balance [kWh]",
            "Energía Declarada [kWh]",
            "Diferencia Energía [kWh]",
            "% Diferencia Energía",
            "Tipo",
        ]]
        return df_combinado
