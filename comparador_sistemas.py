import pandas as pd
import funciones as fc
import numpy as np

class ComparadorSistemas:
    def __init__(self):
        # Carpeta de salida
        self.carpeta_salida = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Balance-Recaudación\\"
        # Carpeta de recaudación
        self.carpeta_recaudacion = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Recaudación\\Revisión Histórica\\"
        # Carpeta de energía
        self.carpeta_sistemas = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\\02 Repartición\\Revisiones\\Revisión Recaudación\\"
  

    def cargar_datos_sistemas(self):
        df_sistemas = pd.read_excel(
            self.carpeta_sistemas + "Revisores RCUT.xlsm",
            sheet_name="Sistemas Zonales vigentes Clien", header=None, engine="openpyxl")
        

        df_sistemas = fc.ObtencionDatos().obtencion_Tablas(df_sistemas, 5, 6)

        # Mantain Barra, Zonal (RE244 2019) and Sistema (RE244 2019) and Nivel Tensión Zonal (según Barra)
        df_sistemas = df_sistemas[["Barra", "Zonal (RE244 2019)", "Sistema (RE244 2019)", "Nivel Tensión Zonal (según Barra)"]]

        return df_sistemas

