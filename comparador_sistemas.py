import pandas as pd
import funciones as fc
import numpy as np


class ComparadorSistemas:
    """
    Esta clase se encarga de cargar, filtrar y combinar los datos de sistemas zonales y de recaudación
    para compararlos y encontrar posibles discrepancias entre ellos. Luego, guarda los resultados en un
    archivo CSV para su posterior análisis y revisión.

    Atributos:
    - carpeta_salida: Carpeta donde se guardan los resultados de la revisión de Balance-Recaudación
    - carpeta_recaudacion: Carpeta donde se encuentran los datos históricos de recaudación
    - carpeta_sistemas: Carpeta donde se encuentran los datos del sistema relacionados con la recaudación
    - sistemas_zonales_permitidos: Lista de sistemas zonales permitidos
    - niveles_de_tension_permitidos: Lista de niveles de tensión permitidos
    - df_sistemas: DataFrame con los datos de sistemas zonales
    - df_recaudacion: DataFrame con los datos históricos de recaudación
    - df_combinado_sistemas: DataFrame combinado con los datos de sistemas zonales y de recaudación

    Métodos:
    - cargar_datos_sistemas: Carga, filtra y normaliza los datos de sistemas zonales desde un archivo Excel
    - cargar_datos_recaudacion: Carga, filtra y normaliza los datos históricos de recaudación de clientes desde un archivo CSV
    - combinar_datos: Combina los datos de sistemas zonales y de recaudación en un solo DataFrame
    - cargar_datos_revision_sistemas: Carga los datos de sistemas zonales para la revisión de sistemas
    - filtro_sistemas: Filtra los datos de sistemas zonales para la revisión de sistemas
    - contador_tipos_historicos_sistemas: Cuenta los tipos de errores históricos de sistemas zonales
    - guardar_datos: Guarda los resultados de la comparación de sistemas en un archivo CSV


    """

    def __init__(self):
        # Carpeta donde se guardan los resultados de la revisión de Balance-Recaudación
        self.carpeta_salida = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Revisiones\Revisión Balance-Recaudación\\"

        # Carpeta donde se encuentran los datos históricos de recaudación
        self.carpeta_recaudacion = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Revisiones\Revisión Recaudación\Revisión Histórica\\"

        # Carpeta donde se encuentran los datos del sistema relacionados con la recaudación
        self.carpeta_sistemas = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Revisiones\Revisión Recaudación\\"

        # Carpeta donde se encuentran los cargos actualizados para las declaraciones CUT
        self.carpeta_cargos = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\01 Fijaciones\00 Formatos de declaración CUT\Cargos Actualizados\\"

        # Lista de sistemas zonales permitidos
        self.sistemas_zonales_permitidos = [
            "Sistema A",
            "Sistema B",
            "Sistema C",
            "Sistema D",
            "Sistema E",
            "Sistema F",
        ]

        # Lista de niveles de tensión permitidos
        self.niveles_de_tension_permitidos = [
            "Tx < 25",  # Tensión menor a 25 kV
            "66",  # Tensión de 66 kV
            "110",  # Tensión de 110 kV
            "220",  # Tensión de 220 kV
            "154",  # Tensión de 154 kV
            "44",  # Tensión de 44 kV
            "33",  # Tensión de 33 kV
        ]

    def cargar_datos_sistemas(self):
        """
        Esta función carga, filtra y normaliza los datos de sistemas zonales desde un archivo Excel.
        Se realizan diversas transformaciones, incluyendo reemplazos y normalizaciones de valores,
        para asegurarse de que los datos estén en un formato adecuado para su análisis.
        Finalmente, devuelve un DataFrame con las columnas relevantes.
        """
        # Cargar los datos desde un archivo Excel
        self.df_sistemas = pd.read_excel(
            self.carpeta_sistemas + "Revisores RCUT.xlsm",  # Ruta del archivo Excel
            sheet_name="Sistemas Zonales vigentes Clien",  # Hoja específica del Excel
            header=None,  # Sin encabezado en el archivo
            engine="openpyxl",  # Motor para leer el archivo Excel
        )

        # Obtener y procesar tablas específicas usando una función externa
        self.df_sistemas = fc.ObtencionDatos().obtencion_Tablas(self.df_sistemas, 5, 6)

        # Reemplazar en "Zonal Definitivo" ciertas palabras por otras
        self.df_sistemas["Zonal Definitivo"] = (
            self.df_sistemas["Zonal Definitivo"]
            .str.replace("SISTEMA", "Sistema")
            .str.replace("Nacional", "na")
            .str.replace("Dedicado", "na")
        )

        # Filtrar y normalizar el campo "Zonal Definitivo" según los sistemas zonales permitidos
        self.df_sistemas["Zonal Definitivo"] = self.df_sistemas[
            "Zonal Definitivo"
        ].apply(lambda x: (x if x in self.sistemas_zonales_permitidos else "na"))

        # Convertir columna "Nivel Tensión Definitivo" a tipo string
        self.df_sistemas["Nivel Tensión Definitivo"] = self.df_sistemas["Nivel Tensión Definitivo"].astype(str)

        # Filtrar y normalizar el campo "Nivel Tensión Definitivo" según los niveles de tensión permitidos
        self.df_sistemas["Nivel Tensión Definitivo"] = self.df_sistemas[
            "Nivel Tensión Definitivo"
        ].apply(lambda x: (x if x in self.niveles_de_tension_permitidos else "-"))

        # Seleccionar las columnas relevantes para el análisis
        self.df_sistemas = self.df_sistemas[
            [
                "Barra",  # Nombre de la barra de energía
                "Zonal Definitivo",  # Sistema zonal definitivo
                "Nivel Tensión Definitivo",  # Nivel de tensión definitivo del sistema zonal
            ]
        ]

        # Devolver el DataFrame procesado
        return self.df_sistemas

    def cargar_datos_recaudacion(self):
        """
        Esta función carga, filtra y normaliza los datos históricos de recaudación de clientes desde un archivo CSV.
        Se asegura de que solo se incluyan las filas relevantes para el análisis, elimina filas con datos faltantes
        o no informados, y ajusta ciertos campos a valores estandarizados. Finalmente, devuelve un DataFrame limpio
        y listo para su uso en posteriores análisis de recaudación.
        """
        # Cargar los datos históricos de recaudación desde un archivo CSV
        self.df_recaudacion = pd.read_csv(
            self.carpeta_recaudacion
            + "BDD Clientes Libres Históricos.csv",  # Ruta del archivo CSV
            sep=";",  # Separador de columnas
            encoding="UTF-8",  # Codificación del archivo
        )

        # Filtrar las filas donde no hay recaudador informado pero sí hay energía
        self.df_recaudacion = self.df_recaudacion[
            ~(
                (self.df_recaudacion["Empresa_Planilla_Recauda_Cliente"] == 0)
                & (self.df_recaudacion["Recaudador No Informado"] == 0)
            )
        ]

        # Filtrar las filas donde la empresa sí es recaudadora
        self.df_recaudacion = self.df_recaudacion[
            (self.df_recaudacion["Empresa_Planilla_Recauda_Cliente"] == 1)
        ]

        # Filtrar y normalizar el campo "Zonal" según los sistemas zonales permitidos
        self.df_recaudacion["Zonal"] = self.df_recaudacion["Zonal"].apply(
            lambda x: (x if x in self.sistemas_zonales_permitidos else "na")
        )

        # Filtrar y normalizar el campo "Nivel Tensión Zonal" según los niveles de tensión permitidos
        self.df_recaudacion["Nivel Tensión Zonal"] = self.df_recaudacion[
            "Nivel Tensión Zonal"
        ].apply(lambda x: (x if x in self.niveles_de_tension_permitidos else "-"))

        # Reemplazar el valor de "Cliente Individualizado" con 0 si no es 0 o 1
        self.df_recaudacion["Cliente Individualizado"] = self.df_recaudacion[
            "Cliente Individualizado"
        ].apply(lambda x: 0 if x not in [0, 1] else x)

        # Seleccionar las columnas relevantes para el análisis
        self.df_recaudacion = self.df_recaudacion[
            [
                "Barra",  # Nombre de la barra de energía
                "Clave",  # Clave de identificación
                "Mes Consumo",  # Mes de consumo de energía
                "Suministrador",  # Empresa suministradora
                "Recaudador",  # Empresa recaudadora
                "mes_repartición",  # Mes de repartición
                "Cliente Individualizado",  # Indicador de cliente individualizado
                "Recaudador No Informado",  # Indicador de recaudador no informado
                "Zonal",  # Sistema zonal
                "Nivel Tensión Zonal",  # Nivel de tensión del sistema zonal
                "Energía [kWh]",  # Energía consumida en kWh
            ]
        ]

        # Devolver el DataFrame procesado
        return self.df_recaudacion

    def combinar_datos(self):
        """
        Esta función combina los datos de sistemas zonales y de recaudación en un solo DataFrame.
        Se utiliza la columna "Barra" como clave para unir los dos DataFrames, y se garantiza que
        se mantengan todas las filas de recaudación. Luego, se crea una nueva columna "Tipo" que
        indica si hay discrepancias entre los sistemas zonales y la recaudación, y se eliminan las
        filas donde la columna "Clave" sea NaN. Finalmente, se preparan los datos para la función
        'cargos_sistemas_nt' realizando reemplazos y ajustes necesarios en las columnas "Zonal" y
        "Nivel Tensión Definitivo".
        """

        # Combinar los DataFrames 'df_recaudacion' y 'df_sistemas' usando la columna "Barra" como clave
        # El método 'left' garantiza que se mantengan todas las filas de 'df_recaudacion'
        self.df_combinado_sistemas = pd.merge(
            self.df_recaudacion,
            self.df_sistemas,
            on="Barra",
            how="left",
        ).reset_index(drop=True)

        # Crear una nueva columna "Tipo" basada en la comparación entre las columnas 'Zonal Definitivo' y 'Zonal'
        # y entre 'Nivel Tensión Definitivo' y 'Nivel Tensión Zonal'
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
                        else "Sistema y Nivel de Tensión Correcto"
                    )
                )
            ),
            axis=1,
        )

        # Eliminar filas donde la columna 'Clave' sea NaN y resetear el índice
        self.df_combinado_sistemas = self.df_combinado_sistemas.dropna(
            subset=["Clave"]
        ).reset_index(drop=True)

        # Preparar datos para la función 'cargos_sistemas_nt'
        # Reemplazar '-' por 'na' en la columna 'Zonal'
        self.df_combinado_sistemas["Zonal"] = self.df_combinado_sistemas[
            "Zonal"
        ].replace("-", "na")

        # Reemplazar en la columna 'Nivel Tensión Definitivo' por '-' si 'Zonal Definitivo' es 'na'
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

        # Reemplazar en la columna 'Zonal Definitivo' por 'na' si 'Nivel Tensión Definitivo' es '-'
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

    def cargos_sistemas_nt(self):
        """
        Esta función carga los datos de cargos del sistema
        y realiza los cálculos necesarios para obtener la recaudación
        del sistema y NT informado y según barra.
        """
        # Convertir la columna "Mes Consumo" a formato datetime
        self.df_combinado_sistemas["Mes Consumo Formato Datetime"] = pd.to_datetime(
            self.df_combinado_sistemas["Mes Consumo"], format="%d-%m-%Y"
        )

        #! Cargos Sistemas NT
        # Leer el archivo Excel con los cargos del sistema
        self.df_cargos_sistemas_nt = pd.read_excel(
            self.carpeta_cargos + "Cargos.xlsx", sheet_name="Cargos", engine="openpyxl"
        )

        # Eliminar filas donde tanto "Segmento" como "Nivel Tensión [kV]" son NaN
        self.df_cargos_sistemas_nt = self.df_cargos_sistemas_nt.dropna(
            subset=["Segmento", "Nivel Tensión [kV]"], how="all"
        )

        # Reemplazar NaN con 0 en la columna "Cliente Individualizado"
        self.df_combinado_sistemas["Cliente Individualizado"] = (
            self.df_combinado_sistemas["Cliente Individualizado"].replace(np.nan, 0)
        )

        # Reemplazar NaN con "na" en la columna "Zonal"
        self.df_combinado_sistemas["Zonal"] = self.df_combinado_sistemas[
            "Zonal"
        ].replace(np.nan, "na")

        # Reemplazos y conversión de tipos
        # Reemplazar NaN con "na" en la columna "Segmento"
        self.df_cargos_sistemas_nt["Segmento"] = self.df_cargos_sistemas_nt[
            "Segmento"
        ].replace(np.nan, "na")

        # Reemplazar NaN con "-" en las columnas "Nivel Tensión Zonal" y "Nivel Tensión [kV]"
        self.df_combinado_sistemas["Nivel Tensión Zonal"] = self.df_combinado_sistemas[
            "Nivel Tensión Zonal"
        ].replace(np.nan, "-")
        self.df_cargos_sistemas_nt["Nivel Tensión [kV]"] = self.df_cargos_sistemas_nt[
            "Nivel Tensión [kV]"
        ].replace(np.nan, "-")

        # Convertir a string las columnas "Nivel Tensión Zonal" y "Nivel Tensión [kV]"
        self.df_combinado_sistemas["Nivel Tensión Zonal"] = self.df_combinado_sistemas[
            "Nivel Tensión Zonal"
        ].astype(str)
        self.df_cargos_sistemas_nt["Nivel Tensión [kV]"] = self.df_cargos_sistemas_nt[
            "Nivel Tensión [kV]"
        ].astype(str)

        # Convertir la columna "Energía [kWh]" a tipo float
        # Reemplazar comas con puntos para asegurar la correcta conversión
        self.df_combinado_sistemas["Energía [kWh]"] = (
            self.df_combinado_sistemas["Energía [kWh]"]
            .str.replace(",", ".")
            .astype(float)
        )

        # ? Cargos Sistema y NT Reportado

        # Fusionar df_combinado_energia con df_cargos_sistemas_nt basado en las columnas Zonal, Nivel Tensión Zonal y Mes Consumo Formato Datetime
        self.df_combinado_sistemas = self.df_combinado_sistemas.merge(
            self.df_cargos_sistemas_nt,
            left_on=["Zonal", "Nivel Tensión Zonal", "Mes Consumo Formato Datetime"],
            right_on=["Segmento", "Nivel Tensión [kV]", "Mes de Consumo"],
            how="left",
        )

        # Nueva columna Recaudación Sistema y NT Informado [$] = Diferencia Energía [kWh] * Cargo Acumulado Individualizado si Cliente Individualizado = 1, de lo contrario Diferencia Energía [kWh] * Cargo Acumulado No Individualizado
        self.df_combinado_sistemas["Recaudación Sistema y NT Informado [$]"] = np.where(
            self.df_combinado_sistemas["Cliente Individualizado"] == 1,
            self.df_combinado_sistemas["Energía [kWh]"]
            * self.df_combinado_sistemas["Cargo Acumulado Individualizado"],
            self.df_combinado_sistemas["Energía [kWh]"]
            * self.df_combinado_sistemas["Cargo Acumulado No Individualizado"],
        ).round(4)

        # Nueva columna Cargo Acumulado Sistema y NT Informado = Cargo Acumulado Individualizado si Cliente Individualizado = 1, de lo contrario Cargo Acumulado No Individualizado
        self.df_combinado_sistemas["Cargo Acumulado Sistema y NT Informado"] = np.where(
            self.df_combinado_sistemas["Cliente Individualizado"] == 1,
            self.df_combinado_sistemas["Cargo Acumulado Individualizado"],
            self.df_combinado_sistemas["Cargo Acumulado No Individualizado"],
        )

        # Eliminar las columnas Cargo Acumulado Individualizado, Cargo Acumulado No Individualizado, Segmento, Nivel Tensión [kV], Mes de Consumo
        self.df_combinado_sistemas = self.df_combinado_sistemas.drop(
            columns=[
                "Cargo Acumulado Individualizado",
                "Cargo Acumulado No Individualizado",
                "Segmento",
                "Nivel Tensión [kV]",
                "Mes de Consumo",
            ]
        )

        # ? Cargos Sistema y NT según Barra
        # Fusionar df_combinado_energia con df_cargos_sistemas_nt basado en las columnas Zonal, Nivel Tensión Zonal y Mes Consumo Formato Datetime
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

        # Nueva columna Recaudación Sistema y NT Según Barra [$] = Diferencia Energía [kWh] * Cargo Acumulado Individualizado si Cliente Individualizado = 1, de lo contrario Diferencia Energía [kWh] * Cargo Acumulado No Individualizado
        self.df_combinado_sistemas["Recaudación Sistema y NT Según Barra [$]"] = (
            np.where(
                self.df_combinado_sistemas["Cliente Individualizado"] == 1,
                self.df_combinado_sistemas["Energía [kWh]"]
                * self.df_combinado_sistemas["Cargo Acumulado Individualizado"],
                self.df_combinado_sistemas["Energía [kWh]"]
                * self.df_combinado_sistemas["Cargo Acumulado No Individualizado"],
            ).round(4)
        )

        # Nueva columna Cargo Acumulado Sistema y NT Según Barra = Cargo Acumulado Individualizado si Cliente Individualizado = 1, de lo contrario Cargo Acumulado No Individualizado
        self.df_combinado_sistemas["Cargo Acumulado Sistema y NT Según Barra"] = (
            np.where(
                self.df_combinado_sistemas["Cliente Individualizado"] == 1,
                self.df_combinado_sistemas["Cargo Acumulado Individualizado"],
                self.df_combinado_sistemas["Cargo Acumulado No Individualizado"],
            )
        )

        # Eliminar las columnas Cargo Acumulado Individualizado, Cargo Acumulado No Individualizado, Segmento, Nivel Tensión [kV], Mes de Consumo y Mes Consumo Formato Datetime
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

        # Nueva columna Diferencia Recaudación Sistema y NT [$] = Recaudación Sistema y NT Informado [$] - Recaudación Sistema y NT Según Barra [$]
        self.df_combinado_sistemas["Diferencia Recaudación Sistema y NT [$]"] = (
            self.df_combinado_sistemas["Recaudación Sistema y NT Informado [$]"]
            - self.df_combinado_sistemas["Recaudación Sistema y NT Según Barra [$]"]
        )

    def cargar_datos_revision_sistemas(self):
        """
        Esta función carga los datos de sistemas zonales para la revisión de sistemas.
        Se eliminan las filas que no cumplen con los criterios de filtrado y se crean columnas
        adicionales para marcar los clientes filtrados y no filtrados. Finalmente, se eliminan
        las columnas innecesarias para el análisis.

        """

        # Leer el archivo Excel "Revisores RCUT.xlsm" de la hoja "Casos excepcionales Sistemas"
        self.df_sistema_filtro = pd.read_excel(
            self.carpeta_sistemas + "Revisores RCUT.xlsm",
            sheet_name="Casos excepcionales Sistemas",
            header=None,
            engine="openpyxl",
        )

        # Obtener tablas de clientes utilizando la función obtencion_tablas_clientes
        self.df_sistema_filtro = fc.ObtencionDatos().obtencion_tablas_clientes(
            self.df_sistema_filtro, 5, 2, 12
        )

        #! Clientes con diferencias de sistemas registrados
        # Eliminar filas donde todas las columnas (excluyendo la primera columna) son NaN
        self.df_sistema_filtro = self.df_sistema_filtro.dropna(how="all")

        # Mantener columnas Barra, Mes Inicial, Mes Final, Meses Particulares
        self.df_sistema_filtro = self.df_sistema_filtro[
            [
                "Barra",
                "Clave",
                "Mes Inicial",
                "Zonal",
                "Nivel Tensión [kV]",
                "Mes Final",
                "Meses Particulares",
            ]
        ]

        # Cambiar formato de fecha de las columnas Mes Inicial y Mes Final
        columnas_rango_fecha = ["Mes Inicial", "Mes Final"]
        self.df_sistema_filtro[columnas_rango_fecha] = (
            self.df_sistema_filtro[columnas_rango_fecha]
            .replace("-", np.nan)
            .apply(lambda x: pd.to_datetime(x).dt.strftime("%d-%m-%Y"))
        )

        # Actualizar columna 'Meses Particulares' para cambiar el formato solo si el valor no contiene ","
        self.df_sistema_filtro["Meses Particulares"] = self.df_sistema_filtro[
            "Meses Particulares"
        ].apply(
            lambda x: (
                pd.to_datetime(x, errors="coerce").strftime("%d-%m-%Y")
                if not pd.isna(x)
                and "," not in str(x)
                and pd.to_datetime(x, errors="coerce") is not pd.NaT
                else x
            )
        )

        # Convertir "Meses Particulares" a datetime y luego formatear como "%d-%m-%Y"
        self.df_sistema_filtro["Meses Particulares"] = self.df_sistema_filtro.apply(
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

        # Dividir "Meses Particulares" por ", " y luego explotar la columna
        self.df_sistemas_filtro = self.df_sistema_filtro.assign(
            Mes_Consumo=self.df_sistema_filtro["Meses Particulares"].str.split(", ")
        ).explode("Mes_Consumo")

        # Crear columna Barra-Clave-Mes-Zonal-Tension
        self.df_sistemas_filtro["Barra-Clave-Mes-Zonal-Tension"] = (
            self.df_sistemas_filtro["Barra"].astype(str)
            + "-_-"
            + self.df_sistemas_filtro["Clave"].astype(str)
            + "-_-"
            + self.df_sistemas_filtro["Mes_Consumo"].astype(str)
            + "-_-"
            + self.df_sistemas_filtro["Zonal"].astype(str)
            + "-_-"
            + self.df_sistemas_filtro["Nivel Tensión [kV]"].astype(str)
        )

        # Eliminar otras columnas
        self.df_sistemas_filtro = self.df_sistemas_filtro[
            ["Barra-Clave-Mes-Zonal-Tension"]
        ]

    def filtro_sistemas(self):
        """
        Esta función filtra los datos de sistemas zonales para la revisión de sistemas.
        Se eliminan las filas que no cumplen con los criterios de filtrado y se crean columnas
        adicionales para marcar los clientes filtrados y no filtrados. Finalmente, se eliminan
        las columnas innecesarias para el análisis.
        """

        # Crear columna Barra-Clave-Mes-Zonal-Tension en df_combinado_sistemas
        self.df_combinado_sistemas["Barra-Clave-Mes-Zonal-Tension"] = (
            self.df_combinado_sistemas["Barra"].astype(str)
            + "-_-"
            + self.df_combinado_sistemas["Clave"].astype(str)
            + "-_-"
            + self.df_combinado_sistemas["Mes Consumo"].astype(str)
            + "-_-"
            + self.df_combinado_sistemas["Zonal"].astype(str)
            + "-_-"
            + self.df_combinado_sistemas["Nivel Tensión Zonal"].astype(str)
        )

        # Crear columna Filtro_Registro_Clave para marcar clientes filtrados y no filtrados
        self.df_combinado_sistemas[
            "Filtro_Registro_Clave"
        ] = self.df_combinado_sistemas["Barra-Clave-Mes-Zonal-Tension"].apply(
            lambda x: (
                "Clientes Filtrados"
                if x in self.df_sistemas_filtro["Barra-Clave-Mes-Zonal-Tension"].values
                else "Clientes No Filtrados"
            )
        )

        # Eliminar columna Barra-Clave-Mes-Zonal-Tension de df_combinado_sistemas
        self.df_combinado_sistemas = self.df_combinado_sistemas.drop(
            columns=["Barra-Clave-Mes-Zonal-Tension"]
        )

    def contador_tipos_historicos_sistemas(self):
        """
        Esta función cuenta los tipos de errores históricos de sistemas zonales en los datos combinados.
        Se crean columnas adicionales que cuentan el número de meses por clave, el número de meses por clave y tipo,
        y el número de meses con errores de sistemas y nivel de tensión incorrectos. Luego, se calcula el porcentaje
        de registros históricos incorrectos y se clasifican en tres categorías: sin errores, con errores bajos,
        y con errores altos.
        """

        # Crear columna Registro_Historico_de_Mes_por_Clave que cuenta el número de meses por clave
        self.df_combinado_sistemas["Registro_Historico_de_Mes_por_Clave"] = (
            self.df_combinado_sistemas.groupby(["Clave"])["Mes Consumo"].transform(
                "count"
            )
        )

        # Crear columna Registro_Historico_por_Clave_y_Tipo que cuenta el número de meses por clave y tipo
        self.df_combinado_sistemas["Registro_Historico_por_Clave_y_Tipo"] = (
            self.df_combinado_sistemas.groupby(["Clave", "Tipo"])[
                "Mes Consumo"
            ].transform("count")
        )

        # Filtrar tipos incorrectos de sistemas y nivel de tensión
        filtro_tipo = self.df_combinado_sistemas["Tipo"].isin(
            [
                "Sistema y Nivel de Tensión Incorrecto",
                "Sistema Incorrecto",
                "Nivel de Tensión Incorrecto",
            ]
        )

        # Inicializar columna Registro_Historico_Sistemas_y_NT_Incorrectos con 0
        self.df_combinado_sistemas["Registro_Historico_Sistemas_y_NT_Incorrectos"] = 0

        # Actualizar columna Registro_Historico_Sistemas_y_NT_Incorrectos con el conteo de meses para los tipos incorrectos
        self.df_combinado_sistemas.loc[
            filtro_tipo, "Registro_Historico_Sistemas_y_NT_Incorrectos"
        ] = (
            self.df_combinado_sistemas[filtro_tipo]
            .groupby(["Clave"])["Mes Consumo"]
            .transform("count")
        )

        # Calcular el porcentaje de registros históricos incorrectos
        self.df_combinado_sistemas[
            "Porcentaje_Registro_Historico_Sistemas_y_NT_Incorrectos"
        ] = (
            self.df_combinado_sistemas["Registro_Historico_Sistemas_y_NT_Incorrectos"]
            / self.df_combinado_sistemas["Registro_Historico_de_Mes_por_Clave"]
            * 100
        ).round(
            2
        )

        # Definir condiciones para la clasificación de los registros históricos incorrectos

        # Definir condiciones para la clasificación de los registros históricos incorrectos
        # Definir condiciones para la clasificación de los registros históricos incorrectos
        condiciones_errores = [
            (
                self.df_combinado_sistemas[
                    "Porcentaje_Registro_Historico_Sistemas_y_NT_Incorrectos"
                ]
                == 0
            ),
            (
                self.df_combinado_sistemas[
                    "Porcentaje_Registro_Historico_Sistemas_y_NT_Incorrectos"
                ]
                < 5
            ),
            (
                self.df_combinado_sistemas[
                    "Porcentaje_Registro_Historico_Sistemas_y_NT_Incorrectos"
                ]
                >= 5
            )
            & (
                self.df_combinado_sistemas[
                    "Porcentaje_Registro_Historico_Sistemas_y_NT_Incorrectos"
                ]
                <= 20
            ),
            (
                self.df_combinado_sistemas[
                    "Porcentaje_Registro_Historico_Sistemas_y_NT_Incorrectos"
                ]
                > 20
            ),
        ]

        # Definir las opciones de clasificación basadas en las condiciones
        opciones_errores = [
            "Claves sin Errores de Sistemas y Nivel de Tensión",
            "Claves con Errores de Sistemas y Nivel de Tensión Bajos",
            "Claves con Errores de Sistemas y Nivel de Tensión Medios",
            "Claves con Errores de Sistemas y Nivel de Tensión Altos",
        ]

        # Crear columna Clasificación_Registro_Historico_Sistemas_y_NT_Incorrectos basada en las condiciones y opciones
        self.df_combinado_sistemas[
            "Clasificación_Registro_Historico_Sistemas_y_NT_Incorrectos"
        ] = np.select(condiciones_errores, opciones_errores, default="Error")

    def guardar_datos(self):
        self.df_combinado_sistemas.to_csv(
            self.carpeta_salida + "df_revision_sistemas.csv",
            sep=";",
            encoding="UTF-8",
            index=False,
        )
        return self.df_combinado_sistemas

    def run(self):
        print("Cargando datos sistemas...")
        self.cargar_datos_sistemas()
        print("Cargando datos recaudación...")
        self.cargar_datos_recaudacion()
        print("Combinando datos...")
        self.combinar_datos()
        print("Cargando datos reales sistemas y nivel de tensión...")
        self.cargos_sistemas_nt()
        print("Cargando datos revision sistemas...")
        self.cargar_datos_revision_sistemas()
        print("Filtrando datos...")
        self.filtro_sistemas()
        print("Contando tipos históricos sistemas...")
        self.contador_tipos_historicos_sistemas()
        print("Guardando datos...")
        self.guardar_datos()
