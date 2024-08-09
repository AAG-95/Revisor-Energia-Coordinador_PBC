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

        self.carpeta_cargos = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\\01 Fijaciones\\00 Formatos de declaración CUT\\Cargos Actualizados\\"

        self.sistemas_zonales_permitidos = [
            "Sistema A",
            "Sistema B",
            "Sistema C",
            "Sistema D",
            "Sistema E",
            "Sistema F",
        ]

        self.niveles_de_tension_permitidos = [
            "Tx < 25",
            "66",
            "110",
            "220",
            "154",
            "44",
            "33",
        ]

    def cargar_datos_sistemas(self):
        self.df_sistemas = pd.read_excel(
            self.carpeta_sistemas + "Revisores RCUT.xlsm",
            sheet_name="Sistemas Zonales vigentes Clien",
            header=None,
            engine="openpyxl",
        )

        self.df_sistemas = fc.ObtencionDatos().obtencion_Tablas(self.df_sistemas, 5, 6)

        # Mantain Barra, Zonal Definitivo and Sistema (RE244 2019) and Nivel Tensión Definitivo
        self.df_sistemas = self.df_sistemas[
            [
                "Barra",
                "Zonal Definitivo",
                "Nivel Tensión Definitivo",
            ]
        ]

        # Mayusculas
        """ self.df_sistemas["Zonal Definitivo"] = self.df_sistemas[
            "Zonal Definitivo"
        ].str.upper()

        self.df_sistemas["Nivel Tensión Definitivo"] = self.df_sistemas[
            "Nivel Tensión Definitivo"
        ].str.upper() """

        # Replace in Zonal Definitivo word SISTEMA for Sistema
        self.df_sistemas["Zonal Definitivo"] = (
            self.df_sistemas["Zonal Definitivo"]
            .str.replace("SISTEMA", "Sistema")
            .str.replace("Nacional", "na")
            .str.replace("Dedicado", "na")
        )
        # Si valor de nivel de tensión no está en la lista de zonal ni niveles de tensión permitidos, se reemplaza por "na"
        self.df_sistemas["Zonal Definitivo"] = self.df_sistemas[
            "Zonal Definitivo"
        ].apply(lambda x: (x if x in self.sistemas_zonales_permitidos else "na"))
        self.df_sistemas["Nivel Tensión Definitivo"] = self.df_sistemas[
            "Nivel Tensión Definitivo"
        ].apply(lambda x: (x if x in self.niveles_de_tension_permitidos else "-"))

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
                "Cliente Individualizado",
                "Recaudador No Informado",
                "Zonal",
                "Nivel Tensión Zonal",
                "Energía [kWh]",
            ]
        ]

        # Mayusculas
        """ self.df_recaudacion["Zonal"] = self.df_recaudacion["Zonal"].str.upper()
        self.df_recaudacion["Nivel Tensión Zonal"] = self.df_recaudacion[
            "Nivel Tensión Zonal"
        ].str.upper() """

        # Si valor de nivel de tensión no está en la lista de zonal ni niveles de tensión permitidos, se reemplaza por "na"
        self.df_recaudacion["Zonal"] = self.df_recaudacion["Zonal"].apply(
            lambda x: (x if x in self.sistemas_zonales_permitidos else "na")
        )

        self.df_recaudacion["Nivel Tensión Zonal"] = self.df_recaudacion[
            "Nivel Tensión Zonal"
        ].apply(lambda x: (x if x in self.niveles_de_tension_permitidos else "-"))

        # ? Otros ajustes

        # Replace column "Cliente Individualizado" with 0 if "Cliente Individualizado" is not 0 or 1
        self.df_recaudacion["Cliente Individualizado"] = self.df_recaudacion[
            "Cliente Individualizado"
        ].apply(lambda x: 0 if x not in [0, 1] else x)

        return self.df_recaudacion

    def combinar_datos(self):
        self.df_combinado_sistemas = pd.merge(
            self.df_recaudacion,
            self.df_sistemas,
            on="Barra",
            how="left",
        ).reset_index(drop=True)

        self.df_combinado_sistemas["Tipo"] = self.df_combinado_sistemas.apply(
            lambda x: (
                "Sistema y Nivel de Tensión Incorrecto"
                if x["Zonal Definitivo"] != x["Zonal"]
                and x["Nivel Tensión Definitivo"] != x["Nivel Tensión Zonal"]
                else (
                    "Sistema Incorrecto"
                    if x["Zonal Definitivo"] != x["Zonal"]
                    else (
                        "Nivel de Tensión Incorrecto"
                        if x["Nivel Tensión Definitivo"] != x["Nivel Tensión Zonal"]
                        else (
                            "Nivel de Tensión Incorrecto"
                            if x["Nivel Tensión Definitivo"] != x["Nivel Tensión Zonal"]
                            else " Sistema y Nivel de Tensión Correcto"
                        )
                    )
                )
            ),
            axis=1,
        )

        # Drop Nan x when Clave column is nan
        self.df_combinado_sistemas = self.df_combinado_sistemas.dropna(
            subset=["Clave"]
        ).reset_index(drop=True)

        # Prepare data for cargos_sistemas_nt
        # replace - with na in Zonal
        self.df_combinado_sistemas["Zonal"] = self.df_combinado_sistemas[
            "Zonal"
        ].replace("-", "na")

        # If column Zonal has na then zonal is -[
        # If column Zonal has na then replace in Nivel Tensión Zonal with -
        self.df_combinado_sistemas["Nivel Tensión Definitivo"] = (
            self.df_combinado_sistemas.apply(
                lambda x: (
                    "-"
                    if x["Zonal Definitivo"] == "na"
                    else x["Nivel Tensión Definitivo"]
                ),
                axis=1,
            )
        )

        self.df_combinado_sistemas["Zonal Definitivo"] = (
            self.df_combinado_sistemas.apply(
                lambda x: (
                    "na"
                    if x["Nivel Tensión Definitivo"] == "-"
                    else x["Zonal Definitivo"]
                ),
                axis=1,
            )
        )
        """# Drop "Correcto" en columna Tipo
        df_combinado_sistemas = df_combinado_sistemas[df_combinado_sistemas["Tipo"] != "Correcto"]"""

    def cargos_sistemas_nt(self):

        # Fecha de Cargos Auxiliar
        self.df_combinado_sistemas["Mes Consumo Formato Datetime"] = pd.to_datetime(
            self.df_combinado_sistemas["Mes Consumo"], format="%d-%m-%Y"
        )

        #! Cargos Sistemas NT
        self.df_cargos_sistemas_nt = pd.read_excel(
            self.carpeta_cargos + "Cargos.xlsx", sheet_name="Cargos", engine="openpyxl"
        )  # Read the excel file

        self.df_cargos_sistemas_nt = self.df_cargos_sistemas_nt.dropna(
            subset=["Segmento", "Nivel Tensión [kV]"], how="all"
        )  # Drop xs where all columns (excluding the first column) are NaN

        self.df_combinado_sistemas[
            "Cliente Individualizado"
        ] = self.df_combinado_sistemas["Cliente Individualizado"].replace(
            np.nan, 0
        )  # Replace NaN with 0 in column Cliente Individualizado

        self.df_combinado_sistemas["Zonal"] = self.df_combinado_sistemas[
            "Zonal"
        ].replace(
            np.nan, "na"
        )  # Replace NaN with na in column Zonal

        # Replaces and type conversion
        self.df_cargos_sistemas_nt["Segmento"] = self.df_cargos_sistemas_nt[
            "Segmento"
        ].replace(np.nan, "na")

        self.df_combinado_sistemas["Nivel Tensión Zonal"] = self.df_combinado_sistemas[
            "Nivel Tensión Zonal"
        ].replace(np.nan, "-")
        self.df_cargos_sistemas_nt["Nivel Tensión [kV]"] = self.df_cargos_sistemas_nt[
            "Nivel Tensión [kV]"
        ].replace(np.nan, "-")

        self.df_combinado_sistemas["Nivel Tensión Zonal"] = self.df_combinado_sistemas[
            "Nivel Tensión Zonal"
        ].astype(str)
        self.df_cargos_sistemas_nt["Nivel Tensión [kV]"] = self.df_cargos_sistemas_nt[
            "Nivel Tensión [kV]"
        ].astype(str)

        # Column energia to float
        self.df_combinado_sistemas["Energía [kWh]"] = (
            self.df_combinado_sistemas["Energía [kWh]"]
            .str.replace(",", ".")
            .astype(float)
        )

        # ? Cargos Sistema y NT Reportado

        # Merge df_combinado_energia with df_cargos_sistemas_nt based in columns Zonal, Nivel Tensión Zonal and Mes Consumo Formato Datetime
        self.df_combinado_sistemas = self.df_combinado_sistemas.merge(
            self.df_cargos_sistemas_nt,
            left_on=["Zonal", "Nivel Tensión Zonal", "Mes Consumo Formato Datetime"],
            right_on=["Segmento", "Nivel Tensión [kV]", "Mes de Consumo"],
            how="left",
        )

        # New Column Recaudación[$] = Diferencia Energía [kWh] * Cargo Acumulado Individualizados  if Cliente Individualizado = 1 else Diferencia Energía [kWh] * Cargo Acumulado No Individualizados
        self.df_combinado_sistemas["Recaudación Sistema y NT Informado [$]"] = np.where(
            self.df_combinado_sistemas["Cliente Individualizado"] == 1,
            self.df_combinado_sistemas["Energía [kWh]"]
            * self.df_combinado_sistemas["Cargo Acumulado Individualizado"],
            self.df_combinado_sistemas["Energía [kWh]"]
            * self.df_combinado_sistemas["Cargo Acumulado No Individualizado"],
        ).round(4)

        # New Column Cargo Acumulado = Cargo Acumulado Individualizados if Cliente Individualizado = 1 else Cargo Acumulado No Individualizados
        self.df_combinado_sistemas["Cargo Acumulado Sistema y NT Informado"] = np.where(
            self.df_combinado_sistemas["Cliente Individualizado"] == 1,
            self.df_combinado_sistemas["Cargo Acumulado Individualizado"],
            self.df_combinado_sistemas["Cargo Acumulado No Individualizado"],
        )

        # Drop columns Cargo Acumulado Individualizados and Cargo Acumulado No Individualizados Segmento Nivel Tensión [kV] Mes de Consumo Formato Datetime and Mes de Consumo
        self.df_combinado_sistemas = self.df_combinado_sistemas.drop(
            columns=[
                "Cargo Acumulado Individualizado",
                "Cargo Acumulado No Individualizado",
                "Segmento",
                "Nivel Tensión [kV]",
                "Mes de Consumo",
            ]
        )

        # ? Cargos Sistema y NT Reportado

        # "Mes Consumo Formato Datetime",

        # Merge df_combinado_energia with df_cargos_sistemas_nt based in columns Zonal, Nivel Tensión Zonal and Mes Consumo Formato Datetime
        self.df_combinado_sistemas = self.df_combinado_sistemas.merge(
            self.df_cargos_sistemas_nt,
            left_on=[
                "Zonal Definitivo",
                "Nivel Tensión Definitivo",
                "Mes Consumo Formato Datetime",
            ],
            right_on=["Segmento", "Nivel Tensión [kV]", "Mes de Consumo"],
            how="left",
        )

        # New Column Recaudación[$] = Diferencia Energía [kWh] * Cargo Acumulado Individualizados  if Cliente Individualizado = 1 else Diferencia Energía [kWh] * Cargo Acumulado No Individualizados
        self.df_combinado_sistemas["Recaudación Sistema y NT Según Barra [$]"] = (
            np.where(
                self.df_combinado_sistemas["Cliente Individualizado"] == 1,
                self.df_combinado_sistemas["Energía [kWh]"]
                * self.df_combinado_sistemas["Cargo Acumulado Individualizado"],
                self.df_combinado_sistemas["Energía [kWh]"]
                * self.df_combinado_sistemas["Cargo Acumulado No Individualizado"],
            ).round(4)
        )

        # New Column Cargo Acumulado = Cargo Acumulado Individualizados if Cliente Individualizado = 1 else Cargo Acumulado No Individualizados
        self.df_combinado_sistemas["Cargo Acumulado Sistema y NT Según Barra"] = (
            np.where(
                self.df_combinado_sistemas["Cliente Individualizado"] == 1,
                self.df_combinado_sistemas["Cargo Acumulado Individualizado"],
                self.df_combinado_sistemas["Cargo Acumulado No Individualizado"],
            )
        )

        # Drop columns Cargo Acumulado Individualizados and Cargo Acumulado No Individualizados Segmento Nivel Tensión [kV] Mes de Consumo Formato Datetime and Mes de Consumo
        self.df_combinado_sistemas = self.df_combinado_sistemas.drop(
            columns=[
                "Cargo Acumulado Individualizado",
                "Cargo Acumulado No Individualizado",
                "Segmento",
                "Nivel Tensión [kV]",
                "Mes de Consumo",
                "Mes Consumo Formato Datetime",
            ]
        )

        self.df_combinado_sistemas["Diferencia Recaudación Sistema y NT [$]"] = (
            self.df_combinado_sistemas["Recaudación Sistema y NT Informado [$]"]
            - self.df_combinado_sistemas["Recaudación Sistema y NT Según Barra [$]"]
        )

        print("Cargando datos energía...")

    def cargar_datos_revision_sistemas(self):
        """# unite columns Barra - Mes ConsumO - Clave
        self.df_combinado_sistemas["Barra-Mes-Clave"] = (
            self.df_combinado_sistemas["Barra"]
            + "-"
            + self.df_combinado_sistemas["Mes Consumo"]
            + "-"
            + self.df_combinado_sistemas["Clave"]
        )"""

        self.df_sistema_filtro = pd.read_excel(
            self.carpeta_sistemas + "Revisores RCUT.xlsm",
            sheet_name="Casos excepcionales Sistemas",
            header=None,
            engine="openpyxl",
        )

        self.df_sistema_filtro = fc.ObtencionDatos().obtencion_tablas_clientes(
            self.df_sistema_filtro, 5, 2, 12
        )

        #! Clientes con diferencias de sistemas registrados
        # Eliminate rows where all columns (excluding the first column) are NaN
        self.df_sistema_filtro = self.df_sistema_filtro.dropna(
             how="all"
        )

        # mantaing columns Barra, Mes Inicial, Mes Final, Meses Particulares
        self.df_sistema_filtro = self.df_sistema_filtro[
            ["Barra", "Clave", "Mes Inicial", "Mes Final", "Meses Particulares"]
        ]

        # Change date format of columns Mes Inicial and Mes Final like columnas_rango_fecha = ["Mes Inicial", "Mes Final"] self.df_diferencias_clientes[columnas_rango_fecha] =     self.df_diferencias_clientes[columnas_rango_fecha.replace("-", np.nan).apply(lambda x: pd.to_datetime(x).dt.strftime("%d-%m-%Y")))

        columnas_rango_fecha = ["Mes Inicial", "Mes Final"]
        self.df_sistema_filtro[columnas_rango_fecha] = (
            self.df_sistema_filtro[columnas_rango_fecha]
            .replace("-", np.nan)
            .apply(lambda x: pd.to_datetime(x).dt.strftime("%d-%m-%Y"))
        )

        # Update 'Meses Particulares' column to change format only if value does not contain "," self.df_diferencias_clientes[ "Meses Particulares"] = self.df_diferencias_clientes["Meses Particulares"].apply(lambda x: (  pd.to_datetime(x, errors="coerce").strftime("%d-%m-%Y") if not pd.isna(x) and "," not in str(x) and pd.to_datetime(x, errors="coerce") is not pd.NaTelse x ))

        self.df_sistema_filtro[
            "Meses Particulares"
        ] = self.df_sistema_filtro["Meses Particulares"].apply(
            lambda x: (
                pd.to_datetime(x, errors="coerce").strftime("%d-%m-%Y")
                if not pd.isna(x)
                and "," not in str(x)
                and pd.to_datetime(x, errors="coerce") is not pd.NaT
                else x
            )
        )

        # Convert "Meses Particulares" to datetime and then format as "%d-%m-%Y"
        self.df_sistema_filtro["Meses Particulares"] = (
            self.df_sistema_filtro.apply(
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
        self.df_sistemas_filtro = self.df_sistema_filtro.assign(
            Mes_Consumo=self.df_sistema_filtro["Meses Particulares"].str.split(
                ", "
            )
        ).explode("Mes_Consumo")


        # Create column Barra-Clave-Mes
        self.df_sistemas_filtro["Barra-Clave-Mes"] = (
            self.df_sistemas_filtro["Barra"].astype(str)
            + "-_-"
            + self.df_sistemas_filtro["Clave"].astype(str)
            + "-_-"
            + self.df_sistemas_filtro["Mes_Consumo"].astype(str)
        )

        # Drop other columns
        self.df_sistemas_filtro = self.df_sistemas_filtro[
            [
                "Barra-Clave-Mes",
                
            ]
        ]
        print("")


    def guardar_datos(self):
        self.df_combinado_sistemas.to_csv(
            self.carpeta_salida + "df_revision_sistemas.csv",
            sep=";",
            encoding="UTF-8",
            index=False,
        )
        return self.df_combinado_sistemas

    def run(self):
        self.cargar_datos_sistemas()
        self.cargar_datos_recaudacion()
        self.combinar_datos()
        self.cargos_sistemas_nt()
        self.cargar_datos_revision_sistemas()
        self.guardar_datos()
