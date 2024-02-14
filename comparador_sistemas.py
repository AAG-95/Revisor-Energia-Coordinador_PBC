import pandas as pd
import funciones as fc
import numpy as np


#! comentario Rojo

#? comentario azul

#todo comentario naranjo 

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
        df_sistemas = pd.read_excel(
            self.carpeta_sistemas + "Revisores RCUT.xlsm",
            sheet_name="Sistemas Zonales vigentes Clien",
            header=None,
            engine="openpyxl",
        )

        df_sistemas = fc.ObtencionDatos().obtencion_Tablas(df_sistemas, 5, 6)

        # Mantain Barra, Zonal (RE244 2019) and Sistema (RE244 2019) and Nivel Tensión Zonal (según Barra)
        df_sistemas = df_sistemas[
            [
                "Barra",
                "Zonal (RE244 2019)",
                "Sistema (RE244 2019)",
                "Nivel Tensión Zonal (según Barra)",
            ]
        ]

        # Mayusculas
        df_sistemas["Zonal (RE244 2019)"] = df_sistemas[
            "Zonal (RE244 2019)"
        ].str.upper()
        df_sistemas["Nivel Tensión Zonal (según Barra)"] = df_sistemas[
            "Nivel Tensión Zonal (según Barra)"
        ].str.upper()

        # Si valor de nivel de tensión no está en la lista de zonal ni niveles de tensión permitidos, se reemplaza por "Nacional/Dedicado"
        df_sistemas["Zonal (RE244 2019)"] = df_sistemas["Zonal (RE244 2019)"].apply(
            lambda x: (
                x if x in self.sistemas_zonales_permitidos else "Nacional/Dedicado"
            )
        )
        df_sistemas["Nivel Tensión Zonal (según Barra)"] = df_sistemas[
            "Nivel Tensión Zonal (según Barra)"
        ].apply(
            lambda x: (
                x if x in self.niveles_de_tension_permitidos else "Nacional/Dedicado"
            )
        )

        return df_sistemas

    def cargar_datos_recaudacion(self):
        df_recaudacion = pd.read_csv(
            self.carpeta_recaudacion + "BDD Clientes Libres Históricos.csv",
            sep=";",
            encoding="UTF-8",
        )

        # Filtrar dataframe para obtener empresas informantes que sean recaduador y revissar caso que no hay recaduador pero sí energía
        df_recaudacion = df_recaudacion[
            ~(
                (df_recaudacion["Empresa_Planilla_Recauda_Cliente"] == 0)
                & (df_recaudacion["Recaudador No Informado"] == 0)
            )
        ]

        df_recaudacion = df_recaudacion[
            (df_recaudacion["Empresa_Planilla_Recauda_Cliente"] == 1)
        ]

        df_recaudacion = df_recaudacion[
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
        df_recaudacion["Zonal"] = df_recaudacion["Zonal"].str.upper()
        df_recaudacion["Nivel Tensión Zonal"] = df_recaudacion[
            "Nivel Tensión Zonal"
        ].str.upper()

        # Si valor de nivel de tensión no está en la lista de zonal ni niveles de tensión permitidos, se reemplaza por "Nacional/Dedicado"
        df_recaudacion["Zonal"] = df_recaudacion["Zonal"].apply(
            lambda x: (
                x if x in self.sistemas_zonales_permitidos else "Nacional/Dedicado"
            )
        )
        df_recaudacion["Nivel Tensión Zonal"] = df_recaudacion[
            "Nivel Tensión Zonal"
        ].apply(
            lambda x: (
                x if x in self.niveles_de_tension_permitidos else "Nacional/Dedicado"
            )
        )

        return df_recaudacion

    def combinar_datos(self, df_sistemas, df_recaudacion):
        df_combinado = pd.merge(
            df_sistemas,
            df_recaudacion,
            on="Barra",
            how="left",
        ).reset_index(drop=True)



        df_combinado["Tipo"] = df_combinado.apply(
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
                        else "Correcto"
                    )
                ) )
            ),
            axis=1,
        )
        
         # get unique values from column "Clave" list unique
        df_combinado_clave_unicos = df_combinado["Clave"].unique()
        df_combinado_clave_unicos_cuenta= len(df_combinado_clave_unicos)


        # Drop "Correcto" en columna Tipo
        df_combinado = df_combinado[df_combinado["Tipo"] != "Correcto"]

        # get unique values from column "Clave" list unique
        df_combinado_clave_unicos = df_combinado["Clave"].unique()
        df_combinado_clave_unicos_cuenta= len(df_combinado_clave_unicos)



        df_combinado[["Barra", "Clave", "Mes Consumo"]] = df_combinado[
            "Barra-Clave-Mes"
        ].str.split("-_-", expand=True)

        # rename Suministrador_final to Suministrador
        df_combinado = df_combinado.rename(
            columns={"Suministrador_final": "Suministrador"}
        )

        df_combinado = df_combinado[
            [
                "Barra",
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

        df_combinado["Recaudador"] = np.where(
            df_combinado["Recaudador"].isna() | (df_combinado["Recaudador"] == ""),
            df_combinado["Suministrador"],
            df_combinado["Recaudador"],
        )

        return df_combinado
