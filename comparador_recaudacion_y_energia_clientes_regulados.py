import pandas as pd
import funciones as fc
import numpy as np


class ComparadorRecaudacionEnergia:
    """
    Esta clase se encarga de cargar, procesar y organizar los datos de recaudación y energía
    de clientes regulados a partir de archivos CSV. El objetivo principal es comparar la energía
    facturada con la energía balanceada de cada cliente, para luego clasificarlos en categorías
    según la diferencia entre ambas. Finalmente, el resultado se guarda en un archivo CSV.

    Atributos
    ----------
    carpeta_salida : Carpeta de salida donde se almacenarán los resultados de las revisiones
    carpeta_recaudacion : Carpeta donde se encuentran los archivos de recaudación para revisión histórica
    carpeta_energia : Carpeta donde se encuentran los archivos de energía con los listados de clientes y retiros históricos

    Metodos
    -------
    cargar_datos_energia: Carga los datos de energía de clientes regulados desde un archivo CSV
    cargar_datos_recaudacion: Carga los datos de recaudación de clientes regulados desde un archivo CSV
    combinar_datos: Combina los datos de energía y recaudación, y clasifica a los clientes en categorías
    """

    def __init__(self):
        # Define la carpeta de salida donde se almacenarán los resultados de las revisiones
        self.carpeta_salida = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Balance-Recaudación\\"

        # Define la carpeta donde se encuentran los archivos de recaudación para revisión histórica
        self.carpeta_recaudacion = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Recaudación\\Revisión Histórica\\"

        # Define la carpeta donde se encuentran los archivos de energía con los listados de clientes y retiros históricos
        self.carpeta_energia = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\\02 Repartición\Balances\\Listados de Clientes\\Retiros Históricos Clientes\\"

    def cargar_datos_energia(self):
        """
        Cargar los datos de energía de clientes regulados desde un archivo CSV

        """
        # Leer el archivo CSV "Retiros_Históricos_Clientes_R.csv" con separador ";" y codificación "UTF-8"
        self.df_energia = pd.read_csv(
            self.carpeta_energia + "Retiros_Históricos_Clientes_R.csv",
            sep=";",
            encoding="UTF-8",
        )

        # Crear columna "Suministrador-Mes" combinando "Suministrador_final" y "Mes"
        self.df_energia["Suministrador-Mes"] = (
            self.df_energia["Suministrador_final"].astype(str)
            + "-_-"
            + self.df_energia["Mes"].astype(str)
        )

        # Reemplazar comas por puntos en la columna "Medida 2" y convertir a tipo float
        self.df_energia["medida2"] = (
            self.df_energia["medida2"].str.replace(",", ".").astype(float)
        )

        # Multiplicar los valores de "Medida 2" por -1
        self.df_energia["medida2"] = self.df_energia["medida2"] * -1

        # Renombrar la columna "Medida 2" a "Energía Balance [kWh]"
        self.df_energia.rename(
            columns={"medida2": "Energía Balance [kWh]"}, inplace=True
        )

        # Seleccionar solo las columnas "Suministrador-Mes" y "Energía Balance [kWh]"
        self.df_energia = self.df_energia[
            ["Suministrador-Mes", "Energía Balance [kWh]"]
        ]

        # Agrupar por "Suministrador-Mes" y sumar los valores de "Energía Balance [kWh]"
        self.df_energia = (
            self.df_energia.groupby(["Suministrador-Mes"])
            .agg({"Energía Balance [kWh]": "sum"})
            .reset_index()
        )

        # Devolver el DataFrame resultante
        return self.df_energia

    def cargar_datos_recaudacion(self):
        """
        Cargar los datos de recaudación de clientes regulados desde un archivo CSV.
        """
        # Leer el archivo CSV "BDD Clientes Regulados Históricos.csv" con separador ";" y codificación "UTF-8"
        self.df_recaudacion = pd.read_csv(
            self.carpeta_recaudacion + "BDD Clientes Regulados Históricos.csv",
            sep=";",
            encoding="UTF-8",
        )

        # Mantener columnas Recaudador, Mes de consumo y Energía facturada [kWh]
        self.df_recaudacion = self.df_recaudacion[
            ["Recaudador", "Mes de consumo", "Energía facturada [kWh]"]
        ]

        # Convertir la columna Mes de consumo a formato de fecha d%m%Y
        self.df_recaudacion["Mes de consumo"] = pd.to_datetime(
            self.df_recaudacion["Mes de consumo"], format="%d-%m-%Y"
        ).dt.strftime("%d-%m-%Y")

        # Crear columna Suministrador-Mes combinando Recaudador y Mes de consumo
        self.df_recaudacion["Suministrador-Mes"] = (
            self.df_recaudacion["Recaudador"].astype(str)
            + "-_-"
            + self.df_recaudacion["Mes de consumo"].astype(str)
        )

        # Limpiar y convertir la columna Energía facturada [kWh] a tipo float
        self.df_recaudacion["Energía facturada [kWh]"] = (
            self.df_recaudacion["Energía facturada [kWh]"]
            .str.replace(",", ".")
            .replace("-", np.nan, regex=False)
            .replace("[^0-9.]", np.nan, regex=True)
            .replace("na", np.nan)
            .astype(float)
        )

        # Agrupar por Suministrador-Mes y sumar los valores de Energía facturada [kWh]
        self.df_recaudacion = (
            self.df_recaudacion.groupby(["Suministrador-Mes"])
            .agg({"Energía facturada [kWh]": "sum"})
            .reset_index()
        )

        # Filtrar filas donde Energía facturada [kWh] es mayor que 0
        self.df_recaudacion = self.df_recaudacion[
            self.df_recaudacion["Energía facturada [kWh]"] > 0
        ]

        # Devolver el DataFrame resultante
        return self.df_recaudacion

    def combinar_datos(self):
        """
        Combinar los datos de recaudación y energía, clasificar a los clientes regulados
        en categorías según la diferencia entre la energía facturada y la energía balanceada,
        y guardar el resultado en un archivo CSV.
        """
        # Combinar los DataFrames df_recaudacion y df_energia en df_combinado_regulados usando "Suministrador-Mes" como clave
        df_combinado_regulados = pd.merge(
            self.df_recaudacion,
            self.df_energia,
            on="Suministrador-Mes",
            how="left",
        ).reset_index(drop=True)

        # Separar "Suministrador" y "Mes" de la columna "Suministrador-Mes" y eliminar la columna original
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

        # Eliminar decimales de "Energía Balance [kWh]" y "Energía facturada [kWh]"
        df_combinado_regulados["Energía facturada [kWh]"] = (
            df_combinado_regulados["Energía facturada [kWh]"].fillna(0).astype(int)
        )

        df_combinado_regulados["Energía Balance [kWh]"] = (
            df_combinado_regulados["Energía Balance [kWh]"].fillna(0).astype(int)
        )

        # Calcular la diferencia entre "Energía Balance [kWh]" y "Energía facturada [kWh]"
        df_combinado_regulados["Diferencia Energía [kWh]"] = -(
            df_combinado_regulados["Energía Balance [kWh]"]
            - df_combinado_regulados["Energía facturada [kWh]"]
        )

        # Calcular la diferencia porcentual de energía
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

        # Clasificar los registros según la diferencia porcentual de energía
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
                            else "Other"  # Condición else adicional
                        )
                    )
                )
            ),
            axis=1,
        )

        # Guardar el DataFrame resultante en un archivo CSV
        df_combinado_regulados.to_csv(
            self.carpeta_salida + "df_revision_energia_regulados.csv",
            sep=";",
            encoding="UTF-8",
            index=False,
        )

    def run(self):
        self.cargar_datos_energia()
        self.cargar_datos_recaudacion()
        self.combinar_datos()
        """ self.df_recaudacion["Recaudador"] = self.df_recaudacion["Recaudador"].apply(lambda x: pd.Series(x).mode()[0] if pd.Series(x).mode().size else None) """
