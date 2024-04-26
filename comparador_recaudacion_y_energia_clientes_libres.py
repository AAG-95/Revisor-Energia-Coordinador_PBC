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
            self.carpeta_energia + "Retiros_Históricos_Clientes_L.csv",
            sep=";",
            encoding="UTF-8",
        )
        self.df_energia["Barra-Clave-Mes"] = (
            self.df_energia["Barra"].astype(str)
            + "-_-"
            + self.df_energia["Clave"].astype(str)
            + "-_-" 
            + self.df_energia["Mes"].astype(str)
        )
        self.df_energia["Medida 2"] = (
            self.df_energia["Medida 2"].str.replace(",", ".").astype(float)
        )
        self.df_energia["Medida 2"] = self.df_energia["Medida 2"] * -1
        self.df_energia.rename(columns={"Medida 2": "Energía Balance [kWh]"}, inplace=True)
        self.df_energia = self.df_energia[
            ["Barra-Clave-Mes", "Nombre", "Energía Balance [kWh]","Suministrador_final" ]
        ]
        self.df_energia = (
            self.df_energia.groupby(["Barra-Clave-Mes"])
            .agg({"Energía Balance [kWh]": "sum",
                    "Suministrador_final": lambda x: list(x)[0],
                    "Nombre": lambda x: list(x)[0]})
            .reset_index()
        )
        return self.df_energia

    def cargar_datos_recaudacion(self):
        self.df_recaudacion = pd.read_csv(
            self.carpeta_recaudacion + "BDD Clientes Libres Históricos.csv",
            sep=";",
            encoding="UTF-8",
        )

        # Filtrar dataframe para obtener empresas informantes que sean recaduador y revisar caso que no hay recaduador pero sí energía
        self.df_recaudacion = self.df_recaudacion[
            ~(
                (self.df_recaudacion["Empresa_Planilla_Recauda_Cliente"] == 0)
                & (self.df_recaudacion["Recaudador No Informado"] == 0)
            )
        ]
        
        self.df_recaudacion =  self.df_recaudacion[
            
                (self.df_recaudacion["Empresa_Planilla_Recauda_Cliente"] == 1)]

        self.df_recaudacion["Barra-Clave-Mes"] = (
            self.df_recaudacion["Barra"].astype(str)
            + "-_-"
            + self.df_recaudacion["Clave"].astype(str)
            + "-_-"
            + self.df_recaudacion["Mes Consumo"].astype(str)
        )

        self.df_recaudacion["Energía [kWh]"] = (
            self.df_recaudacion["Energía [kWh]"]
            .str.replace(",", ".")
            .replace("-", np.nan, regex=False)
            .replace("[^0-9.]", np.nan, regex=True)
            .replace("na", np.nan)
            .astype(float)
        )


        self.df_recaudacion = (
            self.df_recaudacion.groupby(["Barra-Clave-Mes"])
            .agg(
                {
                    "Energía [kWh]": "sum",
                    "Suministrador": lambda x: list(x)[0],
                    "Recaudador": lambda x: list(x)[-1],
                    "mes_repartición": lambda x: list(x),
                    "Recaudador No Informado": lambda x: list(x),
                }
            )
            .reset_index()
        )

        """ self.df_recaudacion["Recaudador"] = self.df_recaudacion["Recaudador"].apply(lambda x: pd.Series(x).mode()[0] if pd.Series(x).mode().size else None) """


        return self.df_recaudacion

    def combinar_datos(self):
        df_combinado_energia = pd.merge(
            self.df_energia,
            self.df_recaudacion[
                [
                    "Barra-Clave-Mes",
                    "Recaudador",
                    "Energía [kWh]",
                    "mes_repartición",
                    "Recaudador No Informado",
                ]
            ],
            on="Barra-Clave-Mes",
            how="left",
        ).reset_index(drop=True)
        
        df_combinado_energia.rename(
            columns={"Energía [kWh]": "Energía Declarada [kWh]"}, inplace=True
        )
        df_combinado_energia["Energía Balance [kWh]"] = (
            df_combinado_energia["Energía Balance [kWh]"]
            .astype(str)
            .str.replace(",", ".")
            .astype(float)
        )
        df_combinado_energia["Energía Balance [kWh]"] = df_combinado_energia[
            "Energía Balance [kWh]"
        ].fillna(0)
        df_combinado_energia["Energía Declarada [kWh]"] = df_combinado_energia[
            "Energía Declarada [kWh]"
        ].fillna(0)
        df_combinado_energia["Diferencia Energía [kWh]"] = (
            df_combinado_energia["Energía Balance [kWh]"]
            - df_combinado_energia["Energía Declarada [kWh]"]
        )
        df_combinado_energia["% Diferencia Energía"] = (
            df_combinado_energia["Diferencia Energía [kWh]"]
            / df_combinado_energia["Energía Balance [kWh]"]
        )
        df_combinado_energia["Tipo"] = df_combinado_energia.apply(
            lambda x: "Recaudador No Informado"
            if (np.array(x["Recaudador No Informado"]) == 1).any()
            or x["Recaudador No Informado"] == 1
            else (
                "Cliente Informado con Diferente Clave"
                if pd.isna(x["Energía Balance [kWh]"])
                or x["Energía Balance [kWh]"] == 0
                and x["Energía Declarada [kWh]"] > 0
                else (
                    "Clave Obsoleta"
                    if pd.isna(x["Energía Balance [kWh]"])
                    or x["Energía Balance [kWh]"] == 0
                    else (
                        "Clave no informada en RCUT"
                        if (
                            pd.isna(x["Energía Declarada [kWh]"])
                            or x["Energía Declarada [kWh]"] == 0
                        )
                        and x["Energía Balance [kWh]"] > 0
                        else (
                            "Diferencia Energía con Diferencias"
                            if abs(x["% Diferencia Energía"]) > 0.05
                            else "Diferencia Energía sin Diferencias"
                        )
                    )
                )
            ),
            axis=1,
        )

        df_combinado_energia[["Barra", "Clave", "Mes Consumo"]] = df_combinado_energia[
            "Barra-Clave-Mes"
        ].str.split("-_-", expand=True)

        # rename Suministrador_final to Suministrador
        df_combinado_energia = df_combinado_energia.rename(columns={"Suministrador_final": "Suministrador"})
        
        df_combinado_energia = df_combinado_energia[
            [
                "Barra",
                "Nombre",
                "Clave",
                "Suministrador",
                "Recaudador",
                "Mes Consumo",
                "mes_repartición",
                "Recaudador No Informado",
                "Energía Balance [kWh]",
                "Energía Declarada [kWh]",
                "Diferencia Energía [kWh]",
                "% Diferencia Energía",
                "Tipo",
            ]
        ]

        df_combinado_energia["Recaudador"] = np.where(df_combinado_energia["Recaudador"].isna() | (df_combinado_energia["Recaudador"] == ""), df_combinado_energia["Suministrador"], df_combinado_energia["Recaudador"])

        df_combinado_energia = df_combinado_energia.reset_index(drop=True)

        df_combinado_energia.to_csv(self.carpeta_salida + "df_revision_energia_libres.csv", sep=";", encoding="UTF-8", index=False)

        return df_combinado_energia

    def run(self):
        self.cargar_datos_energia()
        self.cargar_datos_recaudacion()
        self.combinar_datos()

