import pandas as pd
import funciones as func
import numpy as np


class ComparadorRecaudacionEnergia:
    def __init__(self):
        # Carpeta de salida
        self.carpeta_salida = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Balance-Recaudación\\"
        # Carpeta de recaudación
        self.carpeta_recaudacion = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Recaudación\\Revisión Histórica\\"
        # Carpeta de energía
        self.carpeta_energia = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\\02 Repartición\Balances\\Listados de Clientes\\Retiros Históricos Clientes\\"
        # Carpeta de revisión listado de cliente con diferencias de energía
        self.carpeta_rev_listado_clientes = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\\02 Repartición\\Revisiones\\Revisión Recaudación\\"

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
        self.df_energia.rename(
            columns={"Medida 2": "Energía Balance [kWh]"}, inplace=True
        )
        self.df_energia = self.df_energia[
            [
                "Barra-Clave-Mes",
                "Nombre",
                "Energía Balance [kWh]",
                "Suministrador_final",
            ]
        ]
        self.df_energia = (
            self.df_energia.groupby(["Barra-Clave-Mes"])
            .agg(
                {
                    "Energía Balance [kWh]": "sum",
                    "Suministrador_final": lambda x: list(x)[0],
                    "Nombre": lambda x: list(x)[0],
                }
            )
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

        self.df_recaudacion = self.df_recaudacion[
            (self.df_recaudacion["Empresa_Planilla_Recauda_Cliente"] == 1)
        ]

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

    def cargar_datos_revision_clientes(self):
        # read xlsm file
        self.df_revision_clientes = pd.read_excel(
            self.carpeta_rev_listado_clientes + "Revisores RCUT.xlsm",
            sheet_name="Casos excepcionales Clientes",
            engine="openpyxl",
            header=None,
        )

        self.df_diferencias_clientes = func.ObtencionDatos().obtencion_tablas_clientes(
            self.df_revision_clientes, 5, 2, 15
        )

        #! Clientes con diferencias de energía registrados
        # Eliminate rows where all columns (excluding the first column) are NaN
        self.df_diferencias_clientes = self.df_diferencias_clientes.dropna(
            subset=self.df_diferencias_clientes.columns[1:], how="all"
        )

        # Mantain column Barra, Clave, Mes Inicial, Mes Final, Meses Particulares
        self.df_diferencias_clientes = self.df_diferencias_clientes[
            [
                "Barra",
                "Clave",
                "Mes Inicial",
                "Mes Final",
                "Meses Particulares",
            ]
        ]

        # Change date format of column Mes Inicial and Mes Final

        # Replace "-" with np.nan just in "Mes Inicial" and "Mes Final" columns
        # Replace "-" with np.nan and convert to datetime format in fewer lines
        columnas_rango_fecha = ["Mes Inicial", "Mes Final"]
        self.df_diferencias_clientes[columnas_rango_fecha] = (
            self.df_diferencias_clientes[columnas_rango_fecha]
            .replace("-", np.nan)
            .apply(lambda x: pd.to_datetime(x).dt.strftime("%d-%m-%Y"))
        )

        # Update 'Meses Particulares' column to change format only if value does not contain ","
        self.df_diferencias_clientes[
            "Meses Particulares"
        ] = self.df_diferencias_clientes["Meses Particulares"].apply(
            lambda x: (
                pd.to_datetime(x, errors="coerce").strftime("%d-%m-%Y")
                if not pd.isna(x)
                and "," not in str(x)
                and pd.to_datetime(x, errors="coerce") is not pd.NaT
                else x
            )
        )

        # Convert "Meses Particulares" to datetime and then format as "%d-%m-%Y"
        self.df_diferencias_clientes["Meses Particulares"] = (
            self.df_diferencias_clientes.apply(
                lambda x: (
                    ", ".join(
                        pd.date_range(
                            start=pd.to_datetime(x["Mes Inicial"], format="%d-%m-%Y"),
                            end=pd.to_datetime(x["Mes Final"], format="%d-%m-%Y"),
                            freq="MS",
                        ).strftime("%d-%m-%Y")
                    )
                    if pd.notna(x["Mes Inicial"]) and pd.notna(x["Mes Final"])
                    else x["Meses Particulares"]
                ),
                axis=1,
            )
        )

        # Split "Meses Particulares" by ", " and then explode the column
        self.df_diferencias_clientes = self.df_diferencias_clientes.assign(
            Mes_Consumo=self.df_diferencias_clientes["Meses Particulares"].str.split(
                ", "
            )
        ).explode("Mes_Consumo")

        # Create column Barra-Clave-Mes
        self.df_diferencias_clientes["Barra-Clave-Mes"] = (
            self.df_diferencias_clientes["Barra"].astype(str)
            + "-_-"
            + self.df_diferencias_clientes["Clave"].astype(str)
            + "-_-"
            + self.df_diferencias_clientes["Mes_Consumo"].astype(str)
        )

        # Drop other columns
        self.df_diferencias_clientes = self.df_diferencias_clientes[
            [
                "Barra-Clave-Mes",
            ]
        ]

        #! Clientes homologados
        self.df_homologa_clientes = func.ObtencionDatos().obtencion_tablas_clientes(
            self.df_revision_clientes, 5, 17, 23
        )

        # Eliminate rows where all columns (excluding the first column) are NaN
        self.df_homologa_clientes = self.df_homologa_clientes.dropna(
            subset=self.df_homologa_clientes.columns[1:], how="all"
        )

        # Mantain column Barra, Clave, Mes Inicial, Mes Final, Meses Particulares

        self.df_homologa_clientes = self.df_homologa_clientes[
            [
                "Barra",
                "Clave Original",
                "Clave Homologada",
                "Mes Inicial",
                "Mes Final",
            ]
        ]

        # Change date format of column Mes Inicial and Mes Final

        # Replace "-" with np.nan just in "Mes Inicial" and "Mes Final" columns
        columnas_rango_fecha = ["Mes Inicial", "Mes Final"]
        self.df_homologa_clientes[columnas_rango_fecha] = (
            self.df_homologa_clientes[columnas_rango_fecha]
            .replace("-", np.nan)
            .apply(lambda x: pd.to_datetime(x).dt.strftime("%d-%m-%Y"))
        )

        # Convert "Meses Particulares" to datetime and then format as "%d-%m-%Y"
        self.df_homologa_clientes["Meses Particulares"] = (
            self.df_homologa_clientes.apply(
                lambda x: (
                    ", ".join(
                        pd.date_range(
                            start=pd.to_datetime(x["Mes Inicial"], format="%d-%m-%Y"),
                            end=pd.to_datetime(x["Mes Final"], format="%d-%m-%Y"),
                            freq="MS",
                        ).strftime("%d-%m-%Y")
                    )
                    if pd.notna(x["Mes Inicial"]) and pd.notna(x["Mes Final"])
                    else None
                ),
                axis=1,
            )
        )

        # Split "Meses Particulares" by ", " and then explode the column
        self.df_homologa_clientes = self.df_homologa_clientes.assign(
            Mes_Consumo=self.df_homologa_clientes["Meses Particulares"].str.split(", ")
        ).explode("Mes_Consumo")

        # Create column Barra-Clave-Mes
        self.df_homologa_clientes["Barra-Clave Orginal-Mes"] = (
            self.df_homologa_clientes["Barra"].astype(str)
            + "-_-"
            + self.df_homologa_clientes["Clave Original"].astype(str)
            + "-_-"
            + self.df_homologa_clientes["Mes_Consumo"].astype(str)
        )

        self.df_homologa_clientes["Barra-Clave Homologada-Mes"] = (
            self.df_homologa_clientes["Barra"].astype(str)
            + "-_-"
            + self.df_homologa_clientes["Clave Homologada"].astype(str)
            + "-_-"
            + self.df_homologa_clientes["Mes_Consumo"].astype(str)
        )

        # Drop other columns
        self.df_homologa_clientes = self.df_homologa_clientes[
            ["Barra-Clave Orginal-Mes", "Barra-Clave Homologada-Mes"]
        ]

        #! Clientes homologados con clientes y barras
        self.df_homologa_clientes_barras = (
            func.ObtencionDatos().obtencion_tablas_clientes(
                self.df_revision_clientes, 5, 25, 32
            )
        )

        # Eliminate rows where all columns (excluding the first column) are NaN
        self.df_homologa_clientes_barras = self.df_homologa_clientes_barras.dropna(
            subset=self.df_homologa_clientes_barras.columns[1:], how="all"
        )

        # Mantain column Barra, Clave, Mes Inicial, Mes Final, Meses Particulares
        self.df_homologa_clientes_barras = self.df_homologa_clientes_barras[
            [
                "Clave Original",
                "Clave Homologada",
                "Barra Original",
                "Barra Homologada",
                "Mes Inicial",
                "Mes Final",
            ]
        ]

        # Change date format of column Mes Inicial and Mes Final

        # Replace "-" with np.nan just in "Mes Inicial" and "Mes Final" columns
        columnas_rango_fecha = ["Mes Inicial", "Mes Final"]
        self.df_homologa_clientes_barras[columnas_rango_fecha] = (
            self.df_homologa_clientes_barras[columnas_rango_fecha]
            .replace("-", np.nan)
            .apply(lambda x: pd.to_datetime(x).dt.strftime("%d-%m-%Y"))
        )

        self.df_homologa_clientes_barras["Meses Particulares"] = (
            self.df_homologa_clientes_barras.apply(
                lambda x: (
                    ", ".join(
                        pd.date_range(
                            start=pd.to_datetime(x["Mes Inicial"], format="%d-%m-%Y"),
                            end=pd.to_datetime(x["Mes Final"], format="%d-%m-%Y"),
                            freq="MS",
                        ).strftime("%d-%m-%Y")
                    )
                    if pd.notna(x["Mes Inicial"]) and pd.notna(x["Mes Final"])
                    else None
                ),
                axis=1,
            )
        )

        # Split "Meses Particulares" by ", " and then explode the column
        self.df_homologa_clientes_barras = self.df_homologa_clientes_barras.assign(
            Mes_Consumo=self.df_homologa_clientes_barras[
                "Meses Particulares"
            ].str.split(", ")
        ).explode("Mes_Consumo")

        # Create column Barra Original -Clave Original-Mes

        self.df_homologa_clientes_barras["Barra Original-Clave Original-Mes"] = (
            self.df_homologa_clientes_barras["Barra Original"].astype(str)
            + "-_-"
            + self.df_homologa_clientes_barras["Clave Original"].astype(str)
            + "-_-"
            + self.df_homologa_clientes_barras["Mes_Consumo"].astype(str)
        )

        self.df_homologa_clientes_barras["Barra Homologada-Clave Homologada-Mes"] = (
            self.df_homologa_clientes_barras["Barra Homologada"].astype(str)
            + "-_-"
            + self.df_homologa_clientes_barras["Clave Homologada"].astype(str)
            + "-_-"
            + self.df_homologa_clientes_barras["Mes_Consumo"].astype(str)
        )

        # Drop other columns
        self.df_homologa_clientes_barras = self.df_homologa_clientes_barras[
            [
                "Barra Original-Clave Original-Mes",
                "Barra Homologada-Clave Homologada-Mes",
            ]
        ]

        #! Clientes Con Claves Cruzadas en otras Barras
        self.df_homologa_clientes_cruzados = (
            func.ObtencionDatos().obtencion_tablas_clientes(
                self.df_revision_clientes, 5, 34, 41
            )
        )

        # Eliminate rows where all columns (excluding the first column) are NaN
        self.df_homologa_clientes_cruzados = self.df_homologa_clientes_cruzados.dropna(
            subset=self.df_homologa_clientes_cruzados.columns[1:], how="all"
        )

        # Mantain column Barra, Clave, Mes Inicial, Mes Final, Meses Particulares
        self.df_homologa_clientes_cruzados = self.df_homologa_clientes_cruzados[
            [
                "Clave Original",
                "Clave Homologada",
                "Barra Original",
                "Barra Homologada",
                "Mes Inicial",
                "Mes Final",
            ]
        ]

        # Change date format of column Mes Inicial and Mes Final

        # Replace "-" with np.nan just in "Mes Inicial" and "Mes Final" columns
        columnas_rango_fecha = ["Mes Inicial", "Mes Final"]

        self.df_homologa_clientes_cruzados[columnas_rango_fecha] = (
            self.df_homologa_clientes_cruzados[columnas_rango_fecha]
            .replace("-", np.nan)
            .apply(lambda x: pd.to_datetime(x).dt.strftime("%d-%m-%Y"))
        )

        self.df_homologa_clientes_cruzados["Meses Particulares"] = (
            self.df_homologa_clientes_cruzados.apply(
                lambda x: (
                    ", ".join(
                        pd.date_range(
                            start=pd.to_datetime(x["Mes Inicial"], format="%d-%m-%Y"),
                            end=pd.to_datetime(x["Mes Final"], format="%d-%m-%Y"),
                            freq="MS",
                        ).strftime("%d-%m-%Y")
                    )
                    if pd.notna(x["Mes Inicial"]) and pd.notna(x["Mes Final"])
                    else None
                ),
                axis=1,
            )
        )

        # Split "Meses Particulares" by ", " and then explode the column
        self.df_homologa_clientes_cruzados = self.df_homologa_clientes_cruzados.assign(
            Mes_Consumo=self.df_homologa_clientes_cruzados[
                "Meses Particulares"
            ].str.split(", ")
        ).explode("Mes_Consumo")

        # Create column Barra Original -Clave Original-Mes
        self.df_homologa_clientes_cruzados["Barra Original-Clave Original-Mes"] = (
            self.df_homologa_clientes_cruzados["Barra Original"].astype(str)
            + "-_-"
            + self.df_homologa_clientes_cruzados["Clave Original"].astype(str)
            + "-_-"
            + self.df_homologa_clientes_cruzados["Mes_Consumo"].astype(str)
        )

        self.df_homologa_clientes_cruzados["Barra Homologada-Clave Homologada-Mes"] = (
            self.df_homologa_clientes_cruzados["Barra Homologada"].astype(str)
            + "-_-"
            + self.df_homologa_clientes_cruzados["Clave Homologada"].astype(str)
            + "-_-"
            + self.df_homologa_clientes_cruzados["Mes_Consumo"].astype(str)
        )

        # Drop other columns
        self.df_homologa_clientes_cruzados = self.df_homologa_clientes_cruzados[
            [
                "Barra Original-Clave Original-Mes",
                "Barra Homologada-Clave Homologada-Mes",
            ]
        ]

        return self.df_revision_clientes

    def filtro_clientes(self):
        # Add new column in df_recaudacion as Filtro Registro Cliente - If column Barra-Clave-Mes is in df_diferencias_clientes then a 1, if not a 0
        self.df_energia["Filtro_Registro_Cliente"] = self.df_energia[
            "Barra-Clave-Mes"
        ].apply(
            lambda x: (
                "Clientes Filtrados"
                if x in self.df_diferencias_clientes["Barra-Clave-Mes"].values
                else "Clientes No Filtrados"
            )
        )
        # Replace Barra-Clave-Mes of df_recaudación wirh Barra-Clave Homologada-Mes of df_homologa_clientes when Barra Clave Mes match with Barra-Clave Orginal-Mes
        self.df_recaudacion["Barra-Clave-Mes"] = self.df_recaudacion[
            "Barra-Clave-Mes"
        ].apply(
            lambda x: (
                self.df_homologa_clientes.loc[
                    self.df_homologa_clientes["Barra-Clave Orginal-Mes"] == x,
                    "Barra-Clave Homologada-Mes",
                ].values[0]
                if x in self.df_homologa_clientes["Barra-Clave Orginal-Mes"].values
                else x
            )
        )

        self.df_energia["Barra-Clave-Mes"] = self.df_energia["Barra-Clave-Mes"].apply(
            lambda x: (
                self.df_homologa_clientes.loc[
                    self.df_homologa_clientes["Barra-Clave Orginal-Mes"] == x,
                    "Barra-Clave Homologada-Mes",
                ].values[0]
                if x in self.df_homologa_clientes["Barra-Clave Orginal-Mes"].values
                else x
            )
        )

        # Replace Barra-Clave-Mes of df_recaudación wirh Barra Homologada - Clave Homologada - Mes of df_homologa_clientes_barras when Barra Clave Mes match with Barra Original -Clave Orginal-Mes
        self.df_recaudacion["Barra-Clave-Mes"] = self.df_recaudacion[
            "Barra-Clave-Mes"
        ].apply(
            lambda x: (
                self.df_homologa_clientes_barras.loc[
                    self.df_homologa_clientes_barras[
                        "Barra Original-Clave Original-Mes"
                    ]
                    == x,
                    "Barra Homologada-Clave Homologada-Mes",
                ].values[0]
                if x
                in self.df_homologa_clientes_barras[
                    "Barra Original-Clave Original-Mes"
                ].values
                else x
            )
        )

        self.df_energia["Barra-Clave-Mes"] = self.df_energia["Barra-Clave-Mes"].apply(
            lambda x: (
                self.df_homologa_clientes_barras.loc[
                    self.df_homologa_clientes_barras[
                        "Barra Original-Clave Original-Mes"
                    ]
                    == x,
                    "Barra Homologada-Clave Homologada-Mes",
                ].values[0]
                if x
                in self.df_homologa_clientes_barras[
                    "Barra Original-Clave Original-Mes"
                ].values
                else x
            )
        )

        #! Make a join based in Barra-Clave-Mes in df_recaudación and Barra Original-Claver Orignal-Mes of clientes Cruzados and then replace Barra-Clave-Mes  with Barra Homologada-Clave Homologada-Mes only if Barra-Clave-Mes is in Barra Original-Clave Original-Mes. Do these in two steps: Join and Replace

        # Join df_recaudación with df_homologa_clientes_cruzados
        self.df_recaudacion = pd.merge(
            self.df_recaudacion,
            self.df_homologa_clientes_cruzados,
            left_on="Barra-Clave-Mes",
            right_on="Barra Original-Clave Original-Mes",
            how="left",
        )

        # Replace
        self.df_recaudacion["Barra-Clave-Mes"] = self.df_recaudacion[
            "Barra Homologada-Clave Homologada-Mes"
        ].fillna(self.df_recaudacion["Barra-Clave-Mes"])

        #! Group by
        # gruo by barra clave mes and sum Energía [kWh]
        self.df_recaudacion = (
            self.df_recaudacion.groupby(["Barra-Clave-Mes"])
            .agg(
                {
                    "Energía [kWh]": "sum",
                    "Suministrador": lambda x: list(x)[0],
                    "Recaudador": lambda x: list(x)[-1],
                    "mes_repartición": lambda x: list(x),
                    "Recaudador No Informado": lambda x: x.iloc[0],
                }
            )
            .reset_index()
        )

        self.df_energia = (
            self.df_energia.groupby(["Barra-Clave-Mes"])
            .agg(
                {
                    "Energía Balance [kWh]": "sum",
                    "Suministrador_final": lambda x: list(x)[0],
                    "Nombre": lambda x: list(x)[0],
                    "Filtro_Registro_Cliente": "first",
                }
            )
            .reset_index()
        )

        return self.df_recaudacion

    def combinar_datos(self):
        self.df_combinado_energia = pd.merge(
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

        self.df_combinado_energia.rename(
            columns={"Energía [kWh]": "Energía Declarada [kWh]"}, inplace=True
        )
        self.df_combinado_energia["Energía Balance [kWh]"] = (
            self.df_combinado_energia["Energía Balance [kWh]"]
            .astype(str)
            .str.replace(",", ".")
            .astype(float)
        )
        self.df_combinado_energia["Energía Balance [kWh]"] = self.df_combinado_energia[
            "Energía Balance [kWh]"
        ].fillna(0)
        self.df_combinado_energia["Energía Declarada [kWh]"] = (
            self.df_combinado_energia["Energía Declarada [kWh]"].fillna(0)
        )
        self.df_combinado_energia["Diferencia Energía [kWh]"] = (
            self.df_combinado_energia["Energía Balance [kWh]"]
            - self.df_combinado_energia["Energía Declarada [kWh]"]
        )
        self.df_combinado_energia["% Diferencia Energía"] = (
            self.df_combinado_energia["Diferencia Energía [kWh]"]
            / self.df_combinado_energia["Energía Balance [kWh]"]
        )
        self.df_combinado_energia["Tipo"] = self.df_combinado_energia.apply(
            lambda x: (
                "Recaudador No Informado"
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
                                "Energía con Diferencias"
                                if abs(x["% Diferencia Energía"]) > 0.05
                                else "Energía sin Diferencias"
                            )
                        )
                    )
                )
            ),
            axis=1,
        )

        self.df_combinado_energia[["Barra", "Clave", "Mes Consumo"]] = (
            self.df_combinado_energia["Barra-Clave-Mes"].str.split("-_-", expand=True)
        )

        # rename Suministrador_final to Suministrador
        self.df_combinado_energia = self.df_combinado_energia.rename(
            columns={"Suministrador_final": "Suministrador"}
        )

        self.df_combinado_energia = self.df_combinado_energia[
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
                "Filtro_Registro_Cliente",
            ]
        ]

        self.df_combinado_energia["Recaudador"] = np.where(
            self.df_combinado_energia["Recaudador"].isna()
            | (self.df_combinado_energia["Recaudador"] == ""),
            self.df_combinado_energia["Suministrador"],
            self.df_combinado_energia["Recaudador"],
        )

        self.df_combinado_energia = self.df_combinado_energia.reset_index(drop=True)

    def contador_tipos_historicos_clientes(self):
        # If Tipo y Clave are the same, then count based in column Mes Consumo
        self.df_combinado_energia["Registro_Historico_por_Cliente_y_Tipo"] = (
            self.df_combinado_energia.groupby(["Clave", "Tipo"])[
                "Mes Consumo"
            ].transform("count")
        )

        self.df_combinado_energia["Registro_Historico_No_Inf_y_Dif"] = (
            self.df_combinado_energia.groupby(["Clave", "Tipo"])[
                "Mes Consumo"
            ].transform("count")
        )

        # "Registro_Historico_No_Inf_y_Dif group by where Tipo is Recaudador No Informado and Tipo is Energía con Diferencias

        # Create a mask for rows where "Tipo" is either "Con Diferencias" or "No informado"
        # Define the filter
        filtro_tipo = self.df_combinado_energia["Tipo"].isin(["Clave no informada en RCUT", "Clave no informada en RCUT"])

        # Group by "Clave" and "Tipo" and count "Mes Consumo" only for filtered rows
        counts = self.df_combinado_energia.loc[filtro_tipo].groupby(["Clave", "Tipo"])["Mes Consumo"].transform("count")

        # Initialize the new column with 0
        self.df_combinado_energia["Registro_Historico_No_Inf_y_Dif"] = 0

        # Assign the counts to the filtered rows
        self.df_combinado_energia.loc[filtro_tipo, "Registro_Historico_No_Inf_y_Dif"] = counts
        
        # Example list of date strings
        fechas = self.df_combinado_energia["Mes Consumo"].unique()

        # Convert to datetime
        fecha_max = pd.to_datetime(fechas)

        # Find the maximum date
        max_date = fecha_max.max()

        # Format the date as 'd m y'
        formatted_max_date = max_date.strftime('%m-%d-%Y')

        print(formatted_max_date)

        # If column Clave in any Mes has value 1 in column Filter Registro Cliente, then new column is 1
        self.df_combinado_energia["Registro_Historico_por_Cliente"] = self.df_combinado_energia.groupby(["Clave"])[
            "Filtro_Registro_Cliente"
        ].transform("max")  

        # If column Registro_Historico_por_Cliente has value 1 in and Registro_Historico_por Cliente is more than 2, then Filter Registro Cliente is also 1 in those column
        self.df_combinado_energia["Registro_Historico_por_Cliente"] = np.where(
            (self.df_combinado_energia["Registro_Historico_por_Cliente"] == 1) & (self.df_combinado_energia["Registro_Historico_por_Cliente_y_Tipo"] >= 2),
            1,
            self.df_combinado_energia["Registro_Historico_por_Cliente"],
        )
        return self.df_combinado_energia    

    def guardar_datos(self):

        self.df_combinado_energia.to_csv(
            self.carpeta_salida + "df_revision_energia_libres.csv",
            sep=";",
            encoding="UTF-8",
            index=False,
        )

        return self.df_combinado_energia

    def run(self):
        self.cargar_datos_energia()
        self.cargar_datos_recaudacion()
        self.cargar_datos_revision_clientes()
        self.filtro_clientes()
        self.combinar_datos()
        self.contador_tipos_historicos_clientes()
        self.guardar_datos()
