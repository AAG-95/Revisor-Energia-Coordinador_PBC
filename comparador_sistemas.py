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

        self.sistemas_zonales_permitidos = [
            "SISTEMA A",
            "SISTEMA B",
            "SISTEMA C",
            "SISTEMA D",
            "SISTEMA E",
            "SISTEMA F",
        ]

        self.niveles_de_tension_permitidos = [
            "Tx < 25",
            "66",
            "110",
            "220",
            "154",
            "TX < 25",
            "44",
            "Tx < 66",
        ]

    def cargar_datos_sistemas(self):
        self.df_sistemas = pd.read_excel(
            self.carpeta_sistemas + "Revisores RCUT.xlsm",
            sheet_name="Sistemas Zonales vigentes Clien",
            header=None,
            engine="openpyxl",
        )

        self.df_sistemas = fc.ObtencionDatos().obtencion_Tablas(self.df_sistemas, 5, 6)

        # Mantain Barra, Zonal (RE244 2019) and Sistema (RE244 2019) and Nivel Tensión Zonal (según Barra)
        self.df_sistemas = self.df_sistemas[
            [
                "Barra",
                "Zonal (RE244 2019)",
                "Sistema (RE244 2019)",
                "Nivel Tensión Zonal (según Barra)",
            ]
        ]

        # Mayusculas
        self.df_sistemas["Zonal (RE244 2019)"] = self.df_sistemas[
            "Zonal (RE244 2019)"
        ].str.upper()
        self.df_sistemas["Nivel Tensión Zonal (según Barra)"] = self.df_sistemas[
            "Nivel Tensión Zonal (según Barra)"
        ].str.upper()

        # Si valor de nivel de tensión no está en la lista de zonal ni niveles de tensión permitidos, se reemplaza por "Nacional/Dedicado"
        self.df_sistemas["Zonal (RE244 2019)"] = self.df_sistemas["Zonal (RE244 2019)"].apply(
            lambda x: (
                x if x in self.sistemas_zonales_permitidos else "Nacional/Dedicado"
            )
        )
        self.df_sistemas["Nivel Tensión Zonal (según Barra)"] = self.df_sistemas[
            "Nivel Tensión Zonal (según Barra)"
        ].apply(
            lambda x: (
                x if x in self.niveles_de_tension_permitidos else "Nacional/Dedicado"
            )
        )

        return self.df_sistemas

    def cargar_datos_recaudacion(self):
        self.df_recaudacion = pd.read_csv(
            self.carpeta_recaudacion + "BDD Clientes Libres Históricos.csv",
            sep=";",
            encoding="UTF-8",
        )

        # Filtrar dataframe para obtener empresas informantes que sean recaduador y revissar caso que no hay recaduador pero sí energía
        self.df_recaudacion = self.df_recaudacion[
            ~(
                (self.df_recaudacion["Empresa_Planilla_Recauda_Cliente"] == 0)
                & (self.df_recaudacion["Recaudador No Informado"] == 0)
            )
        ]

        self.df_recaudacion = self.df_recaudacion[
            (self.df_recaudacion["Empresa_Planilla_Recauda_Cliente"] == 1)
        ]

        self.df_recaudacion = self.df_recaudacion[
            [
                "Barra",
                "Clave",
                "Mes Consumo",
                "Suministrador",
                "Recaudador",
                "mes_repartición",
                "Zonal",
                "Nivel Tensión Zonal",
            ]
        ]

        # Mayusculas
        self.df_recaudacion["Zonal"] = self.df_recaudacion["Zonal"].str.upper()
        self.df_recaudacion["Nivel Tensión Zonal"] = self.df_recaudacion[
            "Nivel Tensión Zonal"
        ].str.upper()

        # Si valor de nivel de tensión no está en la lista de zonal ni niveles de tensión permitidos, se reemplaza por "Nacional/Dedicado"
        self.df_recaudacion["Zonal"] = self.df_recaudacion["Zonal"].apply(
            lambda x: (
                x if x in self.sistemas_zonales_permitidos else "Nacional/Dedicado"
            )
        )
        self.df_recaudacion["Nivel Tensión Zonal"] = self.df_recaudacion[
            "Nivel Tensión Zonal"
        ].apply(
            lambda x: (
                x if x in self.niveles_de_tension_permitidos else "Nacional/Dedicado"
            )
        )

        return self.df_recaudacion

    def combinar_datos(self):
        df_combinado_sistemas = pd.merge(
            self.df_sistemas,
            self.df_recaudacion,
            on="Barra",
            how="left",
        ).reset_index(drop=True)

        df_combinado_sistemas["Tipo"] = df_combinado_sistemas.apply(
            lambda x: (
                "Sistema y Nivel de Tensión Incorrecto"
                if x["Zonal (RE244 2019)"] != x["Zonal"] and x["Nivel Tensión Zonal (según Barra)"] != x["Nivel Tensión Zonal"] 
                else (
                    "Sistema Incorrecto"
                    if x["Zonal (RE244 2019)"] != x["Zonal"]
                    else (
                        "Nivel de Tensión Incorrecto"
                        if x["Nivel Tensión Zonal (según Barra)"] != x["Nivel Tensión Zonal"]
                    else (
                        "Nivel de Tensión Incorrecto"
                        if x["Nivel Tensión Zonal (según Barra)"] != x["Nivel Tensión Zonal"]
                        else " Sistema y Nivel de Tensión Correcto"
                    )
                ) )
            ),
            axis=1,
        )

        # Drop Nan row when Clave column is nan
        df_combinado_sistemas = df_combinado_sistemas.dropna(subset=["Clave"]).reset_index(drop=True)


        """# Drop "Correcto" en columna Tipo
        df_combinado_sistemas = df_combinado_sistemas[df_combinado_sistemas["Tipo"] != "Correcto"]"""        
        df_combinado_sistemas.to_csv(self.carpeta_salida + "df_revision_sistemas.csv", sep=";", encoding="UTF-8", index=False)
        return df_combinado_sistemas

    def run(self):
        self.cargar_datos_sistemas()
        self.cargar_datos_recaudacion()
        self.combinar_datos()