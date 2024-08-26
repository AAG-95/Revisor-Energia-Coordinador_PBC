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

    def cargar_datos_energia(self):
        self.df_energia = pd.read_csv(
            self.carpeta_energia + "Retiros_Históricos_Clientes_R.csv",
            sep=";",
            encoding="UTF-8",
        )
        self.df_energia["Suministrador-Mes"] = (
            self.df_energia["Suministrador_final"].astype(str)
            + "-_-"
            + self.df_energia["Mes"].astype(str)
        )
        self.df_energia["Medida 2"] = (
            self.df_energia["Medida 2"].str.replace(",", ".").astype(float)
        )
        self.df_energia["Medida 2"] = self.df_energia["Medida 2"] * -1
        self.df_energia.rename(
            columns={"Medida 2": "Energía Balance [kWh]"}, inplace=True
        )
        self.df_energia = self.df_energia[
            ["Suministrador-Mes", "Energía Balance [kWh]"]
        ]
        self.df_energia = (
            self.df_energia.groupby(["Suministrador-Mes"])
            .agg({"Energía Balance [kWh]": "sum"})
            .reset_index()
        )
        return self.df_energia

    def cargar_datos_recaudacion(self):
        self.df_recaudacion = pd.read_csv(
            self.carpeta_recaudacion + "BDD Clientes Regulados Históricos.csv",
            sep=";",
            encoding="UTF-8",
        )

        # Mantener Columnas Recaudador y Energía facturada [kWh]
        self.df_recaudacion = self.df_recaudacion[
            ["Recaudador", "Mes de consumo", "Energía facturada [kWh]"]
        ]

        # Columnas Mes de consumo de formato fecha d%m%Y
        self.df_recaudacion["Mes de consumo"] = pd.to_datetime(
            self.df_recaudacion["Mes de consumo"], format="%d-%m-%Y"
        ).dt.strftime("%d-%m-%Y")

        self.df_recaudacion["Suministrador-Mes"] = (
            self.df_recaudacion["Recaudador"].astype(str)
            + "-_-"
            + self.df_recaudacion["Mes de consumo"].astype(str)
        )

        self.df_recaudacion["Energía facturada [kWh]"] = (
            self.df_recaudacion["Energía facturada [kWh]"]
            .str.replace(",", ".")
            .replace("-", np.nan, regex=False)
            .replace("[^0-9.]", np.nan, regex=True)
            .replace("na", np.nan)
            .astype(float)
        )

        self.df_recaudacion = (
            self.df_recaudacion.groupby(["Suministrador-Mes"])
            .agg(
                {
                    "Energía facturada [kWh]": "sum",
                }
            )
            .reset_index()
        )

        # Filtrar Energia 0
        self.df_recaudacion = self.df_recaudacion[
            self.df_recaudacion["Energía facturada [kWh]"] > 0
        ]

        return self.df_recaudacion

    def combinar_datos(self):
        df_combinado_regulados = pd.merge(
            self.df_recaudacion,
            self.df_energia,
            on="Suministrador-Mes",
            how="left",
        ).reset_index(drop=True)

        # Separa Suministrador de Mes y elimina columna
        df_combinado_regulados["Suministrador"] = df_combinado_regulados[
            "Suministrador-Mes"
        ].apply(lambda x: x.split("-_-")[0])
        df_combinado_regulados["Mes"] = df_combinado_regulados[
            "Suministrador-Mes"
        ].apply(lambda x: x.split("-_-")[1])
        df_combinado_regulados.drop(columns=["Suministrador-Mes"], inplace=True)

        # Reordenar columnas
        df_combinado_regulados = df_combinado_regulados[
            ["Suministrador", "Mes", "Energía facturada [kWh]", "Energía Balance [kWh]"]
        ]

        # Eliminar decimales de Energía Balance y Energía Facturada
        df_combinado_regulados["Energía facturada [kWh]"] = (
            df_combinado_regulados["Energía facturada [kWh]"].fillna(0).astype(int)
        )

        df_combinado_regulados["Energía Balance [kWh]"] = (
            df_combinado_regulados["Energía Balance [kWh]"].fillna(0).astype(int)
        )

        # Diferencia Energía Balance Menos Facturada
        df_combinado_regulados["Diferencia Energía [kWh]"] = (
            df_combinado_regulados["Energía Balance [kWh]"]
            - df_combinado_regulados["Energía facturada [kWh]"]
        )

        # Diferencia Energía Balance Menos Facturada porcentual
        df_combinado_regulados["Diferencia Energía [%]"] = (
            df_combinado_regulados["Diferencia Energía [kWh]"]
            / df_combinado_regulados["Energía Balance [kWh]"]
        ) * 100
        df_combinado_regulados["Diferencia Energía [%]"] = df_combinado_regulados[
            "Diferencia Energía [%]"
        ].replace({np.inf: 100, -np.inf: 0})
        df_combinado_regulados["Diferencia Energía [%]"] = (
            df_combinado_regulados["Diferencia Energía [%]"].fillna(0).round(2)
        )

        df_combinado_regulados["Tipo"] = df_combinado_regulados.apply(
            lambda x: (
                "Suministrador No Informado En Mes"
                if x["Diferencia Energía [%]"] == 100
                else (
                    "Energía Facturada Sin Diferencias Mayores"
                    if abs(x["Diferencia Energía [%]"]) <= 20
                    else (
                        "Diferencia Energía con Diferencias Con Mayor Facturación"
                        if x["Diferencia Energía [%]"] < -20
                        else (
                            "Diferencia Energía con Diferencias Con Menor Facturación"
                            if x["Diferencia Energía [%]"] > 20
                            else "Other"  # You need to add an else condition here
                        )
                    )
                )
            ),
            axis=1,
        )

        df_combinado_regulados.to_csv(self.carpeta_salida + "df_revision_energia_regulados.csv", sep=";", encoding="UTF-8", index=False)

    def run(self):
        self.cargar_datos_energia()
        self.cargar_datos_recaudacion()
        self.combinar_datos()
        """ self.df_recaudacion["Recaudador"] = self.df_recaudacion["Recaudador"].apply(lambda x: pd.Series(x).mode()[0] if pd.Series(x).mode().size else None) """
