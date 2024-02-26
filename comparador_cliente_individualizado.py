import pandas as pd
import funciones as fc
import numpy as np

class ComparadorClienteIndividualizado:
    def __init__(self):
        
        # Carpeta de energía
        self.carpeta_salida = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Balance-Recaudación\\"
        
        self.carpeta_sistemas = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\\02 Repartición\\Revisiones\\Revisión Recaudación\\"

    def cargar_datos_clientes_ind(self):
        df_clientes_ind = pd.read_excel(
            self.carpeta_sistemas + "Revisores RCUT.xlsm",
            sheet_name="Clientes Indiv. Vigentes",
            header=None,
            engine="openpyxl",
        )

        df_clientes_ind = fc.ObtencionDatos().obtencion_Tablas(df_clientes_ind, 5, 4)


        df_clientes_ind = df_clientes_ind[
            [
                "Cliente (Balance de Energía)",
                "Clave (Balance de Energía)",
                "RUT Cliente",
                "Suministrador",
                "Empresa Cliente",
                "Suministrador",
                "Tipo Cliente",
                "Suscripción",
                "Inicio",
                "Termino"
            ]
        ]

        # Current day time 
        dia_actual = pd.Timestamp.now()
        df_clientes_ind["Fecha Actual"] = dia_actual

        df_clientes_ind["Fecha Actual"] = pd.to_datetime(df_clientes_ind["Fecha Actual"])
        df_clientes_ind["Termino"] = pd.to_datetime(df_clientes_ind["Termino"])

        #Diferencia de fechas entre columna Termino y Fecha Actual
        df_clientes_ind["Días para termino de contrato"] = (df_clientes_ind["Termino"] - df_clientes_ind["Fecha Actual"]).dt.days

        # Sort by smaller Días para termino de contrato
        df_clientes_ind = df_clientes_ind.sort_values(by=["Días para termino de contrato"], ascending=True).reset_index(drop=True)
        
        df_clientes_ind.to_csv(self.carpeta_salida + "df_clientes_ind.csv", sep=";", encoding="UTF-8", index=False)

    def run(self):
        self.cargar_datos_clientes_ind()
            