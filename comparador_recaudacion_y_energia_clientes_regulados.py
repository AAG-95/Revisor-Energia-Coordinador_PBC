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
        df_energia = pd.read_csv(
            self.carpeta_energia + "Retiros_Históricos_Clientes_R.csv",
            sep=";",
            encoding="UTF-8",
        )
        df_energia["Suministrador-Mes"] = (
            df_energia["Suministrador_final"].astype(str)
            + "-_-" 
            + df_energia["Mes"].astype(str)
        )
        df_energia["Medida 2"] = (
            df_energia["Medida 2"].str.replace(",", ".").astype(float)
        )
        df_energia["Medida 2"] = df_energia["Medida 2"] * -1
        df_energia.rename(columns={"Medida 2": "Energía Balance [kWh]"}, inplace=True)
        df_energia = df_energia[
            ["Suministrador-Mes", "Energía Balance [kWh]" ]
        ]
        df_energia = (
            df_energia.groupby(["Suministrador-Mes"])
            .agg({"Energía Balance [kWh]": "sum"
                    })
            .reset_index()
        )
        return df_energia
    

    def cargar_datos_recaudacion(self):
        df_recaudacion = pd.read_csv(
            self.carpeta_recaudacion + "BDD Clientes Regulados Históricos.csv",
            sep=";",
            encoding="UTF-8",
        )

        # Mantener Columnas Recaudador y Energía facturada [kWh]
        df_recaudacion = df_recaudacion[
            ["Recaudador", "Mes de consumo", "Energía facturada [kWh]"]
        ]
        
        # Columnas Mes de consumo de formato fecha d%m%Y
        df_recaudacion["Mes de consumo"] = pd.to_datetime(df_recaudacion["Mes de consumo"], format='%Y-%m-%d %H:%M:%S').dt.strftime('%d-%m-%Y')

        df_recaudacion["Suministrador-Mes"] = (
            df_recaudacion["Recaudador"].astype(str)
            + "-_-"
            + df_recaudacion["Mes de consumo"].astype(str)
        )
       
        df_recaudacion["Energía facturada [kWh]"] = (
            df_recaudacion["Energía facturada [kWh]"]
            .str.replace(",", ".")
            .replace("-", np.nan, regex=False)
            .replace("[^0-9.]", np.nan, regex=True)
            .replace("na", np.nan)
            .astype(float)
        )

       
        df_recaudacion = (
            df_recaudacion.groupby(["Suministrador-Mes"])
            .agg(
                {
                   "Energía facturada [kWh]": "sum",
                }
            )
            .reset_index()
        )

        # Filtrar Energia 0
        df_recaudacion = df_recaudacion[df_recaudacion["Energía facturada [kWh]"] > 0]
        
        return df_recaudacion

    def combinar_datos(self, df_energia, df_recaudacion):
        df_combinado_regulados = pd.merge(
            df_recaudacion,
            df_energia,
            on="Suministrador-Mes",
            how="left",
        ).reset_index(drop=True)

        # Separa Suministrador de Mes y elimina columna
        df_combinado_regulados["Suministrador"] = df_combinado_regulados["Suministrador-Mes"].apply(lambda x: x.split("-_-")[0])
        df_combinado_regulados["Mes"] = df_combinado_regulados["Suministrador-Mes"].apply(lambda x: x.split("-_-")[1])
        df_combinado_regulados.drop(columns=["Suministrador-Mes"], inplace=True)

        # Reordenar columnas
        df_combinado_regulados = df_combinado_regulados[
            ["Suministrador", "Mes", "Energía facturada [kWh]", "Energía Balance [kWh]"]
        ]
        
        # Eliminar decimales de Energía Balance y Energía Facturada
        df_combinado_regulados["Energía facturada [kWh]"] = df_combinado_regulados["Energía facturada [kWh]"].fillna(0).astype(int)

        df_combinado_regulados["Energía Balance [kWh]"] = df_combinado_regulados["Energía Balance [kWh]"].fillna(0).astype(int)

        #Diferencia Energía Balance Menos Facturada
        df_combinado_regulados["Diferencia Energía [kWh]"] = df_combinado_regulados["Energía Balance [kWh]"] - df_combinado_regulados["Energía facturada [kWh]"]

        # Diferencia Energía Balance Menos Facturada porcentual
        df_combinado_regulados["Diferencia Energía [%]"] = ((df_combinado_regulados["Diferencia Energía [kWh]"] / df_combinado_regulados["Energía Balance [kWh]"]) * 100)
        df_combinado_regulados["Diferencia Energía [%]"] = df_combinado_regulados["Diferencia Energía [%]"].replace([np.inf, -np.inf], 100)
        df_combinado_regulados["Diferencia Energía [%]"] = df_combinado_regulados["Diferencia Energía [%]"].fillna(0).round(2)

        """ df_recaudacion["Recaudador"] = df_recaudacion["Recaudador"].apply(lambda x: pd.Series(x).mode()[0] if pd.Series(x).mode().size else None) """

        return df_combinado_regulados
        