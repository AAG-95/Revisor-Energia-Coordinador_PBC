import pandas as pd
import funciones as func
import numpy as np


class ComparadorRecaudacionEnergia:
    """
    Esta clase compara la energía del balance de energía con el proceso RCUT para identificar las diferencias
    entre energía y recaudación. Facilita la organización y revisión de los datos relacionados con recaudación,
    energía, y los sistemas zonales permitidos.

    Atributos:
    - carpeta_salida: Ruta de la carpeta donde se guardan los resultados de la comparación.
    - carpeta_recaudacion: Ruta de la carpeta donde se almacenan los datos históricos de recaudación.
    - carpeta_energia: Ruta de la carpeta donde se encuentran los listados de clientes con sus retiros históricos de energía.
    - carpeta_rev_listado_clientes: Ruta de la carpeta donde se revisan las diferencias de energía por cliente.
    - carpeta_sistemas: Ruta de la carpeta donde se realizan revisiones del proceso RCUT.
    - carpeta_cargos: Ruta de la carpeta donde se encuentran los formatos de declaración de cargos actualizados.
    - sistemas_zonales_permitidos: Lista de sistemas zonales permitidos para el análisis.
    - niveles_de_tension_permitidos: Lista de niveles de tensión permitidos para el análisis.

    Métodos:
    - cargar_datos_energia: Carga los datos de energía y los procesa para obtener una tabla balanceada por cliente.
    - cargar_datos_recaudacion: Carga los datos de recaudación y los procesa para obtener una tabla de empresas recaudadoras.
    - cargar_datos_revision_clientes: Carga los datos de revisión de clientes y procesa los datos para obtener tablas de diferencias de energía, clientes homologados, clientes homologados con clientes y barras, y clientes con claves cruzadas en otras barras.
    - filtro_clientes: Filtra los clientes en los DataFrames de recaudación y energía según las homologaciones y diferencias de clientes.
    - combinar_datos: Combina los datos de recaudación y energía en un solo DataFrame.
    - contador_tipos_historicos_claves: Cuenta los diferentes tipos históricos de claves en los datos combinados.
    - sistemas_nt_barras: Asigna el sistema y nivel de tensión según la barra para los clientes que faltan.
    - cargos_sistemas_nt: Carga los cargos de los sistemas y niveles de tensión.
    - guardar_datos: Guarda los datos procesados en un archivo.
    """
    
    def __init__(self):
        # Carpeta de salida
        self.carpeta_salida = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Balance-Recaudación\\"

        # Carpeta de recaudación
        self.carpeta_recaudacion = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Recaudación\\Revisión Histórica\\"

        # Carpeta de energía
        self.carpeta_energia = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\\02 Repartición\Balances\\Listados de Clientes\\Retiros Históricos Clientes\\"

        # Carpeta de revisión de listado de cliente con diferencias de energía
        self.carpeta_rev_listado_clientes = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\\02 Repartición\\Revisiones\\Revisión Recaudación\\"

        # Carpeta de revisiones del proceso RCUT
        self.carpeta_sistemas = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\\02 Repartición\\Revisiones\\Revisión Recaudación\\"

        # Carpeta de cargos actualizados
        self.carpeta_cargos = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\\01 Fijaciones\\00 Formatos de declaración CUT\\Cargos Actualizados\\"

        # Sistemas zonales permitidos
        self.sistemas_zonales_permitidos = [
            "Sistema A",
            "Sistema B",
            "Sistema C",
            "Sistema D",
            "Sistema E",
            "Sistema F"
        ]

        # Niveles de tensión permitidos
        self.niveles_de_tension_permitidos = ["Tx < 25", "33", "44", "66", "110", "154", "220"]

    def cargar_datos_energia(self):
        """
        Se encarga de cargar los datos de energía desde el archivo "Retiros_Históricos_Clientes_L.csv" y procesar
        los datos para obtener una tabla de energía balanceada por cliente.

        Los datos se almacenan en el DataFrame 'df_energia' y se utilizan para comparar y analizar los datos de
        energía y recaudación de los clientes.
        """
    # Cargar el archivo CSV de energía
        archivo_energia = self.carpeta_energia + "Retiros_Históricos_Clientes_L.csv"
        self.df_energia = pd.read_csv(archivo_energia, sep=";", encoding="UTF-8")

        # Crear columna "Barra-Clave-Mes"
        self.df_energia["Barra-Clave-Mes"] = (
            self.df_energia["Barra"].astype(str)
            + "-_-"
            + self.df_energia["Clave"].astype(str)
            + "-_-"
            + self.df_energia["Mes"].astype(str)
        )

        # Convertir "Medida 2" de string a float y cambiar el signo
        self.df_energia["Medida 2"] = (
            self.df_energia["Medida 2"].str.replace(",", ".").astype(float) * -1
        )

        # Renombrar la columna "Medida 2" a "Energía Balance [kWh]"
        self.df_energia.rename(columns={"Medida 2": "Energía Balance [kWh]"}, inplace=True)

        # Filtrar las columnas relevantes
        self.df_energia = self.df_energia[
            ["Barra-Clave-Mes", "Nombre", "Energía Balance [kWh]", "Suministrador_final"]
        ]

        # Agrupar por "Barra-Clave-Mes" y agregar los valores
        self.df_energia = (
            self.df_energia.groupby("Barra-Clave-Mes").agg(
                {
                    "Energía Balance [kWh]": "sum",
                    "Suministrador_final": lambda x: x.iloc[0],
                    "Nombre": lambda x: x.iloc[0],
                }
            ).reset_index()
        )

        return self.df_energia

    def cargar_datos_recaudacion(self):
        """
        Carga los datos de recaudación desde el archivo "BDD Clientes Libres Históricos.csv" y procesa los datos
        para obtener una tabla de recaudación de empresas recaudadoras.

        Los datos se almacenan en el DataFrame 'df_recaudacion' y se utilizan para comparar y analizar los datos
        de energía y recaudación de los clientes.

        """
        # Cargar el archivo CSV de recaudación
        archivo_recaudacion = self.carpeta_recaudacion + "BDD Clientes Libres Históricos.csv"
        self.df_recaudacion = pd.read_csv(archivo_recaudacion, sep=";", encoding="UTF-8")

        # Filtrar para obtener empresas recaudadoras, excluyendo aquellas sin recaudador pero con energía
        self.df_recaudacion = self.df_recaudacion[
            ~(
                (self.df_recaudacion["Empresa_Planilla_Recauda_Cliente"] == 0)
                & (self.df_recaudacion["Recaudador No Informado"] == 0)
            )
        ]

        # Filtrar empresas recaudadoras
        self.df_recaudacion = self.df_recaudacion[
            self.df_recaudacion["Empresa_Planilla_Recauda_Cliente"] == 1
        ]

        # Crear columna "Barra-Clave-Mes"
        self.df_recaudacion["Barra-Clave-Mes"] = (
            self.df_recaudacion["Barra"].astype(str)
            + "-_-"
            + self.df_recaudacion["Clave"].astype(str)
            + "-_-"
            + self.df_recaudacion["Mes Consumo"].astype(str)
        )

        # Limpiar y convertir la columna "Energía [kWh]" a float
        self.df_recaudacion["Energía [kWh]"] = (
            self.df_recaudacion["Energía [kWh]"]
            .str.replace(",", ".")
            .replace("-", np.nan, regex=False)
            .replace("[^0-9.]", np.nan, regex=True)
            .replace("na", np.nan)
            .astype(float)
        )

        # Agrupar por "Barra-Clave-Mes" y agregar los valores
        self.df_recaudacion = self.df_recaudacion.groupby("Barra-Clave-Mes").agg(
            {
                "Energía [kWh]": "sum",
                "Suministrador": lambda x: x.iloc[0],
                "Recaudador": lambda x: x.iloc[-1],
                "mes_repartición": lambda x: list(x),
                "Recaudador No Informado": lambda x: list(x),
                "Cliente Individualizado": lambda x: x.iloc[0],
                "Zonal": lambda x: x.iloc[0],
                "Nivel Tensión Zonal": lambda x: x.iloc[0],
            }
        ).reset_index()

        # Validar si "Zonal" está en sistemas zonales permitidos, si no, asignar "na"
        self.df_recaudacion["Zonal"] = self.df_recaudacion["Zonal"].apply(
            lambda x: x if x in self.sistemas_zonales_permitidos or pd.isna(x) else "na"
        )

        # Validar si "Nivel Tensión Zonal" está en niveles de tensión permitidos, si no, asignar "-"
        self.df_recaudacion["Nivel Tensión Zonal"] = self.df_recaudacion[
            "Nivel Tensión Zonal"
        ].apply(
            lambda x: x if x in self.niveles_de_tension_permitidos or pd.isna(x) else "-"
        )

        # Si "Zonal" es "na", asignar "-"
        self.df_recaudacion["Zonal"] = self.df_recaudacion["Zonal"].apply(
            lambda x: "-" if x == "na" else x
        )

        # Reemplazar "Cliente Individualizado" con 0 si no es 0 o 1
        self.df_recaudacion["Cliente Individualizado"] = self.df_recaudacion[
            "Cliente Individualizado"
        ].apply(lambda x: 0 if x not in [0, 1] else x)

        return self.df_recaudacion


    def cargar_datos_revision_clientes(self):
        """
        Carga los datos de revisión de clientes desde el archivo "Revisores RCUT.xlsm" y procesa los datos
        para obtener tablas de diferencias de energía, clientes homologados, clientes homologados con clientes y barras,
        y clientes con claves cruzadas en otras barras.

        Los datos se almacenan en los DataFrames:
        - df_diferencias_clientes: Tabla de diferencias de energía registradas por cliente.
        - df_homologa_clientes: Tabla de clientes homologados.
        - df_homologa_clientes_barras: Tabla de homologación de clientes por barras.
        - df_homologa_clientes_cruzados: Tabla de clientes con claves cruzadas en otras barras.

        Los DataFrames se utilizan para comparar y analizar los datos de energía y recaudación de los clientes.

        """
        # Carga el archivo "Revisores RCUT.xlsm" desde la carpeta especificada en 'carpeta_rev_listado_clientes'
        # Lee la hoja llamada "Casos excepcionales Clientes" sin encabezados (header=None)
        self.df_revision_clientes = pd.read_excel(
            self.carpeta_rev_listado_clientes + "Revisores RCUT.xlsm",
            sheet_name="Casos excepcionales Clientes",
            engine="openpyxl",
            header=None,
        )

        # Obtener tablas de diferencias de clientes
        # Utiliza la función 'obtencion_tablas_clientes' para procesar los datos del DataFrame 'df_revision_clientes'
        # Los parámetros 5, 2, 15 indican la configuración específica para obtener las tablas según primera fila, primera columna y última columna
        self.df_diferencias_clientes = func.ObtencionDatos().obtencion_tablas_clientes(
            self.df_revision_clientes, 5, 2, 15
        )
        #! Clientes con diferencias de energía registrados
       # Eliminar filas donde todas las columnas (excepto la primera) sean NaN
        self.df_diferencias_clientes = self.df_diferencias_clientes.dropna(
            subset=self.df_diferencias_clientes.columns[1:], how="all"
        )

        # Mantener solo las columnas específicas necesarias para el análisis
        self.df_diferencias_clientes = self.df_diferencias_clientes[
            [
                "Barra",
                "Clave",
                "Mes Inicial",
                "Mes Final",
                "Meses Particulares",
            ]
        ]

        # Cambiar el formato de fecha de las columnas "Mes Inicial" y "Mes Final"
        # Reemplaza los guiones "-" con NaN y aplica el formato de fecha "%d-%m-%Y"
        columnas_rango_fecha = ["Mes Inicial", "Mes Final"]
        self.df_diferencias_clientes[columnas_rango_fecha] = (
            self.df_diferencias_clientes[columnas_rango_fecha]
            .replace("-", np.nan)
            .apply(lambda x: pd.to_datetime(x).dt.strftime("%d-%m-%Y"))
        )

        # Actualizar la columna 'Meses Particulares' cambiando el formato solo si el valor no contiene ","
        # Se convierte a fecha en formato "%d-%m-%Y" si es posible
        self.df_diferencias_clientes["Meses Particulares"] = self.df_diferencias_clientes[
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
        # Si "Mes Inicial" y "Mes Final" no son NaN, genera un rango de fechas en formato "%d-%m-%Y"
        self.df_diferencias_clientes["Meses Particulares"] = self.df_diferencias_clientes.apply(
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

        # Dividir "Meses Particulares" por ", " y luego explotar la columna en filas individuales
        self.df_diferencias_clientes = self.df_diferencias_clientes.assign(
            Mes_Consumo=self.df_diferencias_clientes["Meses Particulares"].str.split(", ")
        ).explode("Mes_Consumo")

        # Crear una nueva columna "Barra-Clave-Mes" combinando "Barra", "Clave" y "Mes_Consumo"
        self.df_diferencias_clientes["Barra-Clave-Mes"] = (
            self.df_diferencias_clientes["Barra"].astype(str)
            + "-_-"
            + self.df_diferencias_clientes["Clave"].astype(str)
            + "-_-"
            + self.df_diferencias_clientes["Mes_Consumo"].astype(str)
        )

        # Mantener solo la columna "Barra-Clave-Mes"
        self.df_diferencias_clientes = self.df_diferencias_clientes[
            ["Barra-Clave-Mes"]
        ]

        #! Clientes homologados
        # Utiliza la función 'obtencion_tablas_clientes' para procesar los datos del DataFrame 'df_revision_clientes'
        # Los parámetros 5, 17, 23 indican la configuración específica para obtener las tablas de homologación
        self.df_homologa_clientes = func.ObtencionDatos().obtencion_tablas_clientes(
            self.df_revision_clientes, 5, 17, 23
        )

        # Eliminar filas donde todas las columnas (excepto la primera) sean NaN
        self.df_homologa_clientes = self.df_homologa_clientes.dropna(
            subset=self.df_homologa_clientes.columns[1:], how="all"
        )

        # Mantener solo las columnas específicas necesarias para el análisis
        self.df_homologa_clientes = self.df_homologa_clientes[
            [
                "Barra",
                "Clave Original",
                "Clave Homologada",
                "Mes Inicial",
                "Mes Final",
            ]
        ]

        # Cambiar el formato de fecha de las columnas "Mes Inicial" y "Mes Final"
        # Reemplaza los guiones "-" con NaN y aplica el formato de fecha "%d-%m-%Y"
        columnas_rango_fecha = ["Mes Inicial", "Mes Final"]
        self.df_homologa_clientes[columnas_rango_fecha] = (
            self.df_homologa_clientes[columnas_rango_fecha]
            .replace("-", np.nan)
            .apply(lambda x: pd.to_datetime(x).dt.strftime("%d-%m-%Y"))
        )

        # Convertir "Meses Particulares" a datetime y luego formatear como "%d-%m-%Y"
        # Si "Mes Inicial" y "Mes Final" no son NaN, genera un rango de fechas en formato "%d-%m-%Y"
        self.df_homologa_clientes["Meses Particulares"] = self.df_homologa_clientes.apply(
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

        # Dividir "Meses Particulares" por ", " y luego explotar la columna en filas individuales
        self.df_homologa_clientes = self.df_homologa_clientes.assign(
            Mes_Consumo=self.df_homologa_clientes["Meses Particulares"].str.split(", ")
        ).explode("Mes_Consumo")

        # Crear nuevas columnas "Barra-Clave Original-Mes" y "Barra-Clave Homologada-Mes"
        self.df_homologa_clientes["Barra-Clave Original-Mes"] = (
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

        # Mantener solo las columnas "Barra-Clave Original-Mes" y "Barra-Clave Homologada-Mes"
        self.df_homologa_clientes = self.df_homologa_clientes[
            ["Barra-Clave Original-Mes", "Barra-Clave Homologada-Mes"]
        ]


        #! Clientes homologados con clientes y barras
        # Obtener tablas de homologación de clientes por barras
        # Utiliza la función 'obtencion_tablas_clientes' para procesar los datos del DataFrame 'df_revision_clientes'
        # Los parámetros 5, 25, 32 indican la configuración específica para obtener las tablas de homologación por barras
        self.df_homologa_clientes_barras = func.ObtencionDatos().obtencion_tablas_clientes(
            self.df_revision_clientes, 5, 25, 32
        )

        # Eliminar filas donde todas las columnas (excepto la primera) sean NaN
        self.df_homologa_clientes_barras = self.df_homologa_clientes_barras.dropna(
            subset=self.df_homologa_clientes_barras.columns[1:], how="all"
        )

        # Mantener solo las columnas específicas necesarias para el análisis
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

        # Cambiar el formato de fecha de las columnas "Mes Inicial" y "Mes Final"
        # Reemplaza los guiones "-" con NaN y aplica el formato de fecha "%d-%m-%Y"
        columnas_rango_fecha = ["Mes Inicial", "Mes Final"]
        self.df_homologa_clientes_barras[columnas_rango_fecha] = (
            self.df_homologa_clientes_barras[columnas_rango_fecha]
            .replace("-", np.nan)
            .apply(lambda x: pd.to_datetime(x).dt.strftime("%d-%m-%Y"))
        )

        # Crear la columna "Meses Particulares" con un rango de fechas si "Mes Inicial" y "Mes Final" no son NaN
        self.df_homologa_clientes_barras["Meses Particulares"] = self.df_homologa_clientes_barras.apply(
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

        # Dividir "Meses Particulares" por ", " y luego explotar la columna en filas individuales
        self.df_homologa_clientes_barras = self.df_homologa_clientes_barras.assign(
            Mes_Consumo=self.df_homologa_clientes_barras["Meses Particulares"].str.split(", ")
        ).explode("Mes_Consumo")

        # Crear columnas "Barra Original-Clave Original-Mes" y "Barra Homologada-Clave Homologada-Mes"
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

        # Mantener solo las columnas "Barra Original-Clave Original-Mes" y "Barra Homologada-Clave Homologada-Mes"
        self.df_homologa_clientes_barras = self.df_homologa_clientes_barras[
            [
                "Barra Original-Clave Original-Mes",
                "Barra Homologada-Clave Homologada-Mes",
            ]
        ]


        #! Clientes Con Claves Cruzadas en otras Barras
        # Obtener datos y cargar en DataFrame
        self.df_homologa_clientes_cruzados = func.ObtencionDatos().obtencion_tablas_clientes(
            self.df_revision_clientes, 5, 34, 41
        )

        # Eliminar filas donde todas las columnas (excepto la primera) son NaN
        self.df_homologa_clientes_cruzados = self.df_homologa_clientes_cruzados.dropna(
            subset=self.df_homologa_clientes_cruzados.columns[1:], how="all"
        )

        # Mantener solo las columnas relevantes
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

        # Reemplazar "-" con np.nan en las columnas de fechas "Mes Inicial" y "Mes Final"
        columnas_rango_fecha = ["Mes Inicial", "Mes Final"]
        self.df_homologa_clientes_cruzados[columnas_rango_fecha] = (
            self.df_homologa_clientes_cruzados[columnas_rango_fecha]
            .replace("-", np.nan)
        )

        # Cambiar el formato de las fechas de "Mes Inicial" y "Mes Final" a "dd-mm-YYYY"
        self.df_homologa_clientes_cruzados[columnas_rango_fecha] = self.df_homologa_clientes_cruzados[columnas_rango_fecha].apply(
            lambda x: pd.to_datetime(x).dt.strftime("%d-%m-%Y")
        )

        # Crear la columna "Meses Particulares" con los meses en el rango de fechas
        self.df_homologa_clientes_cruzados["Meses Particulares"] = self.df_homologa_clientes_cruzados.apply(
            lambda x: (
                ", ".join(
                    pd.date_range(
                        start=pd.to_datetime(x["Mes Inicial"], format="%d-%m-%Y"),
                        end=pd.to_datetime(x["Mes Final"], format="%d-%m-%Y"),
                        freq="MS"
                    ).strftime("%d-%m-%Y")
                )
                if pd.notna(x["Mes Inicial"]) and pd.notna(x["Mes Final"])
                else None
            ),
            axis=1
        )

        # Dividir "Meses Particulares" por ", " y luego expandir la columna
        self.df_homologa_clientes_cruzados = self.df_homologa_clientes_cruzados.assign(
            Mes_Consumo=self.df_homologa_clientes_cruzados["Meses Particulares"].str.split(", ")
        ).explode("Mes_Consumo")

        # Crear columna combinada "Barra Original - Clave Original - Mes"
        self.df_homologa_clientes_cruzados["Barra Original-Clave Original-Mes"] = (
            self.df_homologa_clientes_cruzados["Barra Original"].astype(str)
            + "-_-"
            + self.df_homologa_clientes_cruzados["Clave Original"].astype(str)
            + "-_-"
            + self.df_homologa_clientes_cruzados["Mes_Consumo"].astype(str)
        )

        # Crear columna combinada "Barra Homologada - Clave Homologada - Mes"
        self.df_homologa_clientes_cruzados["Barra Homologada-Clave Homologada-Mes"] = (
            self.df_homologa_clientes_cruzados["Barra Homologada"].astype(str)
            + "-_-"
            + self.df_homologa_clientes_cruzados["Clave Homologada"].astype(str)
            + "-_-"
            + self.df_homologa_clientes_cruzados["Mes_Consumo"].astype(str)
        )

        # Mantener solo las columnas combinadas
        self.df_homologa_clientes_cruzados = self.df_homologa_clientes_cruzados[
            [
                "Barra Original-Clave Original-Mes",
                "Barra Homologada-Clave Homologada-Mes",
            ]
        ]

        return self.df_revision_clientes

    def filtro_clientes(self):
        """
        Filtra los clientes en los DataFrames de recaudación y energía según las homologaciones y diferencias de clientes.
        
        1. Filtro de Clientes en df_energia:
        - Se añade una nueva columna "Filtro_Registro_Clave" en df_energia.
        - Si el valor de "Barra-Clave-Mes" en df_energia está presente en df_diferencias_clientes, se asigna "Clientes Filtrados"; de lo contrario, "Clientes No Filtrados".

        2. Homologación de Claves en df_recaudacion:
        - Se reemplazan los valores de "Barra-Clave-Mes" en df_recaudacion usando los valores homologados de df_homologa_clientes.
        - Esto ocurre cuando "Barra-Clave-Mes" coincide con "Barra-Clave Original-Mes".

        3. Homologación de Claves en df_energia:
        - Similar a la homologación en df_recaudacion, se reemplazan los valores de "Barra-Clave-Mes" en df_energia.

        4. Homologación de Claves usando df_homologa_clientes_barras en df_recaudacion:
        - Se reemplazan los valores de "Barra-Clave-Mes" en df_recaudacion con "Barra Homologada-Clave Homologada-Mes".
        - Esto ocurre cuando "Barra-Clave-Mes" coincide con "Barra Original-Clave Original-Mes".

        5. Homologación de Claves usando df_homologa_clientes_barras en df_energia:
        - Se reemplazan los valores de "Barra-Clave-Mes" en df_energia de manera similar a df_recaudacion.

        6. Unión y Reemplazo con Clientes Cruzados:
        - Se realiza una unión (join) entre df_recaudacion y df_homologa_clientes_cruzados basada en "Barra-Clave-Mes".
        - Luego se reemplaza "Barra-Clave-Mes" con "Barra Homologada-Clave Homologada-Mes" si hay coincidencias.

        """
        # Se añade una nueva columna en df_energia llamada "Filtro_Registro_Clave".
        # Si el valor de "Barra-Clave-Mes" en df_energia está presente en df_diferencias_clientes, se asigna "Clientes Filtrados"; de lo contrario, "Clientes No Filtrados".
        self.df_energia["Filtro_Registro_Clave"] = self.df_energia[
            "Barra-Clave-Mes"
        ].apply(
            lambda x: (
                "Clientes Filtrados"
                if x in self.df_diferencias_clientes["Barra-Clave-Mes"].values
                else "Clientes No Filtrados"
            )
        )
        
        # 2. Homologación de Claves en df_recaudacion
        # Se reemplazan los valores de "Barra-Clave-Mes" en df_recaudacion usando los valores homologados de df_homologa_clientes.
        # Esto ocurre cuando "Barra-Clave-Mes" coincide con "Barra-Clave Original-Mes".
        self.df_recaudacion["Barra-Clave-Mes"] = self.df_recaudacion[
            "Barra-Clave-Mes"
        ].apply(
            lambda x: (
                self.df_homologa_clientes.loc[
                    self.df_homologa_clientes["Barra-Clave Original-Mes"] == x,
                    "Barra-Clave Homologada-Mes",
                ].values[0]
                if x in self.df_homologa_clientes["Barra-Clave Original-Mes"].values
                else x
            )
        )

        # 3. Homologación de Claves en df_energia
        # Similar a la homologación en df_recaudacion, se reemplazan los valores de "Barra-Clave-Mes" en df_energia.
        self.df_energia["Barra-Clave-Mes"] = self.df_energia["Barra-Clave-Mes"].apply(
            lambda x: (
                self.df_homologa_clientes.loc[
                    self.df_homologa_clientes["Barra-Clave Original-Mes"] == x,
                    "Barra-Clave Homologada-Mes",
                ].values[0]
                if x in self.df_homologa_clientes["Barra-Clave Original-Mes"].values
                else x
            )
        )

        # 4. Homologación de Claves usando df_homologa_clientes_barras en df_recaudacion
        # Se reemplazan los valores de "Barra-Clave-Mes" en df_recaudacion con "Barra Homologada-Clave Homologada-Mes".
        # Esto ocurre cuando "Barra-Clave-Mes" coincide con "Barra Original-Clave Original-Mes".
        self.df_recaudacion["Barra-Clave-Mes"] = self.df_recaudacion[
            "Barra-Clave-Mes"
        ].apply(
            lambda x: (
                self.df_homologa_clientes_barras.loc[
                    self.df_homologa_clientes_barras[
                        "Barra Original-Clave Original-Mes"
                    ] == x,
                    "Barra Homologada-Clave Homologada-Mes",
                ].values[0]
                if x in self.df_homologa_clientes_barras["Barra Original-Clave Original-Mes"].values
                else x
            )
        )

        # 5. Homologación de Claves usando df_homologa_clientes_barras en df_energia
        # Se reemplazan los valores de "Barra-Clave-Mes" en df_energia de manera similar a df_recaudacion.
        self.df_energia["Barra-Clave-Mes"] = self.df_energia["Barra-Clave-Mes"].apply(
            lambda x: (
                self.df_homologa_clientes_barras.loc[
                    self.df_homologa_clientes_barras[
                        "Barra Original-Clave Original-Mes"
                    ] == x,
                    "Barra Homologada-Clave Homologada-Mes",
                ].values[0]
                if x in self.df_homologa_clientes_barras["Barra Original-Clave Original-Mes"].values
                else x
            )
        )

        # 6. Unión y Reemplazo con Clientes Cruzados
        # Se realiza una unión (join) entre df_recaudacion y df_homologa_clientes_cruzados basada en "Barra-Clave-Mes".
        # Luego se reemplaza "Barra-Clave-Mes" con "Barra Homologada-Clave Homologada-Mes" si hay coincidencias.
        self.df_recaudacion = pd.merge(
            self.df_recaudacion,
            self.df_homologa_clientes_cruzados,
            left_on="Barra-Clave-Mes",
            right_on="Barra Original-Clave Original-Mes",
            how="left",
        )

        # Reemplazo
        self.df_recaudacion["Barra-Clave-Mes"] = self.df_recaudacion[
            "Barra Homologada-Clave Homologada-Mes"
        ].fillna(self.df_recaudacion["Barra-Clave-Mes"])

        # 7. Agrupación de Datos en df_recaudacion
        # Se agrupan los datos por "Barra-Clave-Mes" y se suman los valores de "Energía [kWh]".
        # Para otras columnas, se seleccionan valores únicos o el primer/último valor según corresponda.
        self.df_recaudacion = (
            self.df_recaudacion.groupby(["Barra-Clave-Mes"])
            .agg(
                {
                    "Energía [kWh]": "sum",
                    "Suministrador": lambda x: list(x)[0],
                    "Recaudador": lambda x: list(x)[-1],
                    "mes_repartición": lambda x: list(x),
                    "Recaudador No Informado": lambda x: x.iloc[0],
                    "Cliente Individualizado": lambda x: x.iloc[0],
                    "Zonal": lambda x: x.iloc[0],
                    "Nivel Tensión Zonal": lambda x: x.iloc[0],
                }
            )
            .reset_index()
        )

        # 8. Agrupación de Datos en df_energia
        # Similar a la agrupación en df_recaudacion, se agrupan los datos por "Barra-Clave-Mes".
        self.df_energia = (
            self.df_energia.groupby(["Barra-Clave-Mes"])
            .agg(
                {
                    "Energía Balance [kWh]": "sum",
                    "Suministrador_final": lambda x: list(x)[0],
                    "Nombre": lambda x: list(x)[0],
                    "Filtro_Registro_Clave": "first",
                }
            )
            .reset_index()
        )

        # 9. Retorno de Resultados
        # Se retorna el dataframe df_recaudacion actualizado.
        return self.df_recaudacion


    def combinar_datos(self):

        """
        Combinar los datos de energía y recaudación en un solo DataFrame.

        Se realiza una combinación de los DataFrames df_energia y df_recaudacion
        utilizando la columna "Barra-Clave-Mes" como clave de unión.

        Se realizan cálculos adicionales para obtener la diferencia de energía
        entre "Energía Balance [kWh]" y "Energía Declarada [kWh]", así como el
        porcentaje de diferencia de energía.

        Se clasifican los registros en base a ciertas condiciones y se separa la
        columna "Barra-Clave-Mes" en tres columnas: "Barra", "Clave" y "Mes Consumo".

        Finalmente, se renombran las columnas y se convierten los datos según sea necesario.

        Returns:
            None
        """
        # Combinar df_energia con df_recaudacion utilizando la columna "Barra-Clave-Mes" como clave
        self.df_combinado_energia = pd.merge(
            self.df_energia,
            self.df_recaudacion[
                [
                    "Barra-Clave-Mes",
                    "Recaudador",
                    "Energía [kWh]",
                    "mes_repartición",
                    "Recaudador No Informado",
                    "Cliente Individualizado",
                    "Zonal",
                    "Nivel Tensión Zonal",
                ]
            ],
            on="Barra-Clave-Mes",  # Realizar la unión en base a la columna "Barra-Clave-Mes"
            how="left"  # Usar un 'left join' para mantener todas las filas de df_energia
        ).reset_index(drop=True)  # Reiniciar el índice después de la combinación

        # Renombrar la columna "Energía [kWh]" a "Energía Declarada [kWh]" para clarificar su uso
        self.df_combinado_energia.rename(
            columns={"Energía [kWh]": "Energía Declarada [kWh]"}, inplace=True
        )
        
        # Convertir la columna "Energía Balance [kWh]" de string a float, reemplazando comas por puntos
        self.df_combinado_energia["Energía Balance [kWh]"] = (
            self.df_combinado_energia["Energía Balance [kWh]"]
            .astype(str)
            .str.replace(",", ".")
            .astype(float)
        )
        
        # Rellenar valores nulos en "Energía Balance [kWh]" con 0
        self.df_combinado_energia["Energía Balance [kWh]"] = self.df_combinado_energia[
            "Energía Balance [kWh]"
        ].fillna(0)
        
        # Rellenar valores nulos en "Energía Declarada [kWh]" con 0
        self.df_combinado_energia["Energía Declarada [kWh]"] = (
            self.df_combinado_energia["Energía Declarada [kWh]"].fillna(0)
        )
        
        # Calcular la diferencia entre "Energía Balance [kWh]" y "Energía Declarada [kWh]"
        self.df_combinado_energia["Diferencia Energía [kWh]"] = -(
            self.df_combinado_energia["Energía Balance [kWh]"]
            - self.df_combinado_energia["Energía Declarada [kWh]"]
        )
        
        # Calcular el porcentaje de diferencia de energía
        self.df_combinado_energia["% Diferencia Energía"] = (
            self.df_combinado_energia["Diferencia Energía [kWh]"]
            / self.df_combinado_energia["Energía Balance [kWh]"]
        )
        
        # Clasificar el tipo de registro basado en condiciones especificadas
        self.df_combinado_energia["Tipo"] = self.df_combinado_energia.apply(
            lambda x: (
                "Recaudador No Informado"
                if (np.array(x["Recaudador No Informado"]) == 1).any()
                or x["Recaudador No Informado"] == 1
                else (
                    "Clave Informado con Diferente Clave"
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
        
        # Separar la columna "Barra-Clave-Mes" en tres columnas: "Barra", "Clave" y "Mes Consumo"
        self.df_combinado_energia[["Barra", "Clave", "Mes Consumo"]] = (
            self.df_combinado_energia["Barra-Clave-Mes"].str.split("-_-", expand=True)
        )

        # Renombrar la columna "Suministrador_final" a "Suministrador" para consistencia
        self.df_combinado_energia = self.df_combinado_energia.rename(
            columns={"Suministrador_final": "Suministrador"}
        )
        
        # Reordenar las columnas del DataFrame para una presentación coherente
        self.df_combinado_energia = self.df_combinado_energia[
            [
                "Barra",
                "Nombre",
                "Clave",
                "Suministrador",
                "Recaudador",
                "Cliente Individualizado",
                "Zonal",
                "Nivel Tensión Zonal",
                "Mes Consumo",
                "mes_repartición",
                "Recaudador No Informado",
                "Energía Balance [kWh]",
                "Energía Declarada [kWh]",
                "Diferencia Energía [kWh]",
                "% Diferencia Energía",
                "Tipo",
                "Filtro_Registro_Clave",
            ]
        ]
        
        # Rellenar valores nulos o vacíos en "Recaudador" con el valor de "Suministrador"
        self.df_combinado_energia["Recaudador"] = np.where(
            self.df_combinado_energia["Recaudador"].isna()
            | (self.df_combinado_energia["Recaudador"] == ""),
            self.df_combinado_energia["Suministrador"],
            self.df_combinado_energia["Recaudador"],
        )
        
        # Reiniciar el índice del DataFrame después de las modificaciones
        self.df_combinado_energia = self.df_combinado_energia.reset_index(drop=True)

        # Devolver el DataFrame combinado y modificado
        return self.df_combinado_energia
    
    def contador_tipos_historicos_claves(self):
        """
        Calcula y clasifica los registros históricos de errores por 'Clave' y 'Mes Consumo' en el DataFrame combinado.

        Esta función agrega varias columnas al DataFrame 'df_combinado_energia' para:
        - Contar registros históricos filtrados por 'Clave'.
        - Calcular el número de meses por cada 'Clave'.
        - Contar registros históricos por combinación de 'Clave' y 'Tipo'.
        - Calcular el porcentaje de registros de energía no informada o con diferencias por 'Clave'.
        - Clasificar el nivel de error histórico basado en estos porcentajes.
        - Filtrar claves según criterios específicos para el análisis.

        Retorna:
            pd.DataFrame: DataFrame actualizado con las nuevas columnas y clasificaciones.
        """
        
        # Contar el número de registros históricos por 'Clave' y aplicar filtro para determinar si un cliente está registrado históricamente
        self.df_combinado_energia["Registro_Historico_de_Filtro_por_Clave"] = self.df_combinado_energia.groupby("Clave")[
            "Filtro_Registro_Clave"
        ].transform(
            lambda x: (
                "Cliente Registrado Históricamente"
                if "Clientes Filtrados" in x.values
                else "Cliente No Registrado Históricamente"
            )
        )

        # Contar el número de meses por cada 'Clave'
        self.df_combinado_energia["Registro_Historico_de_Mes_por_Clave"] = self.df_combinado_energia.groupby(["Clave"])["Mes Consumo"].transform(
            "count"
        )

        # Contar registros históricos por combinación de 'Clave' y 'Tipo'
        self.df_combinado_energia["Registro_Historico_por_Clave_y_Tipo"] = self.df_combinado_energia.groupby(["Clave", "Tipo"])[
            "Mes Consumo"
        ].transform("count")

        # Filtrar filas donde el "Tipo" sea "Clave no informada en RCUT" o "Energía con Diferencias"
        filtro_tipo = self.df_combinado_energia["Tipo"].isin(
            ["Clave no informada en RCUT", "Energía con Diferencias"]
        )

        # Inicializar la columna "Registro_Historico_No_Inf_y_Dif_por_Clave" con 0
        self.df_combinado_energia["Registro_Historico_No_Inf_y_Dif_por_Clave"] = 0

        # Para las filas que coinciden con el filtro, sumar las ocurrencias por cada "Clave" en ambas categorías de "Tipo"
        self.df_combinado_energia.loc[
            filtro_tipo, "Registro_Historico_No_Inf_y_Dif_por_Clave"
        ] = (
            self.df_combinado_energia[filtro_tipo]
            .groupby("Clave")["Mes Consumo"]
            .transform("count")
        )

        # Calcular el porcentaje de registros no informados y con diferencias por 'Clave'
        self.df_combinado_energia["Porcentaje_No_Inf_y_Dif_por_Clave"] = (
            self.df_combinado_energia["Registro_Historico_No_Inf_y_Dif_por_Clave"]
            / self.df_combinado_energia["Registro_Historico_de_Mes_por_Clave"]
        ) * 100

        # Definir condiciones para clasificar el nivel de error histórico
        conditions = [
            (self.df_combinado_energia["Porcentaje_No_Inf_y_Dif_por_Clave"] == 0),
            (self.df_combinado_energia["Porcentaje_No_Inf_y_Dif_por_Clave"] < 5),
            (self.df_combinado_energia["Porcentaje_No_Inf_y_Dif_por_Clave"] >= 5)
            & (self.df_combinado_energia["Porcentaje_No_Inf_y_Dif_por_Clave"] <= 20),
            (self.df_combinado_energia["Porcentaje_No_Inf_y_Dif_por_Clave"] > 20),
        ]

        # Opciones correspondientes a cada condición
        choices = [
            "Clave sin Errores de Recaudación",  # Para la primera condición: 0%
            "Clave con Errores de Recaudación Bajos",  # Para valores < 5%
            "Clave con Errores de Recaudación Medios",  # Para valores >= 5% y <= 20%
            "Clave con Errores de Recaudación Altos",  # Para valores > 20%
        ]

        # Aplicar condiciones y opciones para clasificar el nivel de error histórico
        self.df_combinado_energia["Nivel_de_Error_Historico_por_Clave"] = np.select(
            conditions,
            choices,
            default="Clientes No Filtrados",  # Es buena práctica tener un valor por defecto
        )

        # Convertir la columna de porcentaje a cadena de texto
        self.df_combinado_energia["Porcentaje_No_Inf_y_Dif_por_Clave"] = (
            self.df_combinado_energia["Porcentaje_No_Inf_y_Dif_por_Clave"].astype(str)
        )

        # Definir casos para análisis que no se consideran errores
        casos_por_analizar = ["Clave sin Error de Recaudación", "Clientes No Filtrados", "Clave con Errores de Recaudación Bajos"]

        # Filtrar registros de claves según condiciones específicas para el análisis
        self.df_combinado_energia["Filtro_Registro_Clave"] = np.where(
            (
                ~self.df_combinado_energia["Nivel_de_Error_Historico_por_Clave"].isin(
                    casos_por_analizar
                )
            )
            & (
                self.df_combinado_energia["Registro_Historico_de_Filtro_por_Clave"]
                == "Cliente Registrado Históricamente"
            ),
            "Clientes Filtrados",
            self.df_combinado_energia["Filtro_Registro_Clave"],
        )

        # Retornar el DataFrame actualizado
        return self.df_combinado_energia

    def sistemas_nt_barras(self):
        """
        Cargar y procesar los datos de sistemas zonales y niveles de tensión de barras en el DataFrame combinado.

        Esta función carga los datos de sistemas zonales y niveles de tensión de barras
        desde el archivo "Revisores RCUT.xlsm" y los combina con el DataFrame combinado
        utilizando la columna "Barra" como clave de unión.

        Se reemplazan valores y se llenan columnas con información relevante para el análisis.

        
        """
    # Cargar el archivo Excel "Revisores RCUT.xlsm" y leer la hoja "Sistemas Zonales vigentes Clien"
        self.df_sistemas_nt = pd.read_excel(
            self.carpeta_sistemas + "Revisores RCUT.xlsm",
            sheet_name="Sistemas Zonales vigentes Clien",
            engine="openpyxl",
            header=None,
        )

        # Obtener y procesar las tablas de clientes utilizando la función 'obtencion_tablas_clientes'
        self.df_sistemas_nt = func.ObtencionDatos().obtencion_tablas_clientes(
            self.df_sistemas_nt, 5, 6, 16
        )

        # Seleccionar únicamente las columnas relevantes: "Barra", "Zonal Definitivo" y "Nivel Tensión Definitivo"
        self.df_sistemas_nt = self.df_sistemas_nt[
            ["Barra", "Zonal Definitivo", "Nivel Tensión Definitivo"]
        ]

        # Reemplazar palabras en la columna "Zonal Definitivo"
        # Reemplaza "SISTEMA" con "Sistema", "Nacional" con "na" y "Dedicado" con "na"
        self.df_sistemas_nt["Zonal Definitivo"] = (
            self.df_sistemas_nt["Zonal Definitivo"]
            .str.replace("SISTEMA", "Sistema")
            .str.replace("Nacional", "na")
            .str.replace("Dedicado", "na")
        )

        # Preparación de datos combinados en 'df_combinado_energia'
        # Rellenar la columna "Zonal" en 'df_combinado_energia' con valores de 'df_sistemas_nt' basados en la columna "Barra"
        self.df_combinado_energia["Zonal"] = self.df_combinado_energia["Zonal"].fillna(
            self.df_combinado_energia["Barra"].map(
                self.df_sistemas_nt.set_index("Barra")["Zonal Definitivo"]
            )
        )

        # Rellenar la columna "Nivel Tensión Zonal" en 'df_combinado_energia' con valores de 'df_sistemas_nt' basados en la columna "Barra"
        self.df_combinado_energia["Nivel Tensión Zonal"] = self.df_combinado_energia[
            "Nivel Tensión Zonal"
        ].fillna(
            self.df_combinado_energia["Barra"].map(
                self.df_sistemas_nt.set_index("Barra")["Nivel Tensión Definitivo"]
            )
        )

        # Reemplazar valores '-' por 'na' en la columna "Zonal" de 'df_combinado_energia'
        self.df_combinado_energia["Zonal"] = self.df_combinado_energia["Zonal"].replace(
            "-", "na"
        )

        # Si la columna "Zonal" tiene "na", entonces reemplazar el valor en "Nivel Tensión Zonal" con "-"
        self.df_combinado_energia["Nivel Tensión Zonal"] = self.df_combinado_energia.apply(
            lambda row: "-" if row["Zonal"] == "na" else row["Nivel Tensión Zonal"],
            axis=1,
        )


    def cargos_sistemas_nt(self):
        """
        Cargar y procesar los datos de cargos de sistemas no transversales en el DataFrame combinado.

        Esta función carga los datos de cargos de sistemas no transversales
        desde el archivo "Cargos.xlsx" y los combina con el DataFrame combinado
        utilizando las columnas "Zonal", "Nivel Tensión Zonal" y "Mes Consumo" como claves de unión.

        Se realizan cálculos adicionales para obtener la recaudación y se eliminan columnas innecesarias.

        """
        # Convertir la columna "Mes Consumo" a formato datetime para facilitar la comparación y el filtrado
        self.df_combinado_energia["Mes Consumo Formato Datetime"] = pd.to_datetime(
            self.df_combinado_energia["Mes Consumo"], format="%d-%m-%Y"
        )

        # Cargar el archivo Excel "Cargos.xlsx" y leer la hoja "Cargos"
        self.df_cargos_sistemas_nt = pd.read_excel(
            self.carpeta_cargos + "Cargos.xlsx", sheet_name="Cargos", engine="openpyxl"
        )

        # Eliminar filas donde las columnas "Segmento" y "Nivel Tensión [kV]" tengan todos sus valores como NaN
        self.df_cargos_sistemas_nt = self.df_cargos_sistemas_nt.dropna(
            subset=["Segmento", "Nivel Tensión [kV]"], how="all"
        )

        # Reemplazar valores NaN con 0 en la columna "Cliente Individualizado"
        self.df_combinado_energia["Cliente Individualizado"] = (
            self.df_combinado_energia["Cliente Individualizado"].replace(np.nan, 0)
        )

        # Reemplazar valores NaN con 'na' en la columna "Zonal"
        self.df_combinado_energia["Zonal"] = self.df_combinado_energia["Zonal"].replace(
            np.nan, "na"
        )

        # Reemplazar valores NaN con 'na' en la columna "Segmento" de 'df_cargos_sistemas_nt'
        self.df_cargos_sistemas_nt["Segmento"] = self.df_cargos_sistemas_nt["Segmento"].replace(np.nan, "na")

        # Reemplazar valores NaN con '-' en las columnas "Nivel Tensión Zonal" y "Nivel Tensión [kV]"
        self.df_combinado_energia["Nivel Tensión Zonal"] = self.df_combinado_energia["Nivel Tensión Zonal"].replace(np.nan, "-")
        self.df_cargos_sistemas_nt["Nivel Tensión [kV]"] = self.df_cargos_sistemas_nt["Nivel Tensión [kV]"].replace(np.nan, "-")

        # Convertir las columnas "Nivel Tensión Zonal" y "Nivel Tensión [kV]" a tipo string
        self.df_combinado_energia["Nivel Tensión Zonal"] = self.df_combinado_energia["Nivel Tensión Zonal"].astype(str)
        self.df_cargos_sistemas_nt["Nivel Tensión [kV]"] = self.df_cargos_sistemas_nt["Nivel Tensión [kV]"].astype(str)

        # Realizar un merge entre 'df_combinado_energia' y 'df_cargos_sistemas_nt' basado en las columnas "Zonal", "Nivel Tensión Zonal" y "Mes Consumo Formato Datetime"
        self.df_combinado_energia = self.df_combinado_energia.merge(
            self.df_cargos_sistemas_nt,
            left_on=["Zonal", "Nivel Tensión Zonal", "Mes Consumo Formato Datetime"],
            right_on=["Segmento", "Nivel Tensión [kV]", "Mes de Consumo"],
            how="left",
        )

        # Crear una nueva columna "Cargo Acumulado" basada en la columna "Cliente Individualizado"
        # Si "Cliente Individualizado" es 1, usar "Cargo Acumulado Individualizado", de lo contrario, usar "Cargo Acumulado No Individualizado"
        self.df_combinado_energia["Cargo Acumulado"] = np.where(
            self.df_combinado_energia["Cliente Individualizado"] == 1,
            self.df_combinado_energia["Cargo Acumulado Individualizado"],
            self.df_combinado_energia["Cargo Acumulado No Individualizado"],
        )

        # Crear una nueva columna "Recaudación [$]" calculada como el producto de "Diferencia Energía [kWh]" y "Cargo Acumulado"
        # Si "Cliente Individualizado" es 1, usar "Cargo Acumulado Individualizado", de lo contrario, usar "Cargo Acumulado No Individualizado"
        self.df_combinado_energia["Recaudación [$]"] = np.where(
            self.df_combinado_energia["Cliente Individualizado"] == 1,
            self.df_combinado_energia["Diferencia Energía [kWh]"]
            * self.df_combinado_energia["Cargo Acumulado Individualizado"],
            self.df_combinado_energia["Diferencia Energía [kWh]"]
            * self.df_combinado_energia["Cargo Acumulado No Individualizado"],
        ).round(4)

        # Eliminar columnas innecesarias después del merge y los cálculos
        self.df_combinado_energia = self.df_combinado_energia.drop(
            columns=[
                "Cargo Acumulado Individualizado",
                "Cargo Acumulado No Individualizado",
                "Segmento",
                "Nivel Tensión [kV]",
                "Mes de Consumo",
                "Mes Consumo Formato Datetime",
            ]
        )

    def guardar_datos(self):

        self.df_combinado_energia.to_csv(
            self.carpeta_salida + "df_revision_energia_libres.csv",
            sep=";",
            encoding="UTF-8",
            index=False,
        )
        return self.df_combinado_energia

    def run(self):
        print("Cargando datos energía...")
        self.cargar_datos_energia()
        print("Cargando datos recaudación...")
        self.cargar_datos_recaudacion()
        print("Cargando datos revisión clientes...")
        self.cargar_datos_revision_clientes()
        print("Filtrando clientes...")
        self.filtro_clientes()
        print("Combinando datos...")
        self.combinar_datos()
        print("Contando tipos históricos de claves...")
        self.contador_tipos_historicos_claves()
        print("Sistema y nivel de tensión según Barra, para clientes faltantes...")
        self.sistemas_nt_barras()
        print("Cargando cargos de sistemas...")
        self.cargos_sistemas_nt()
        print("Guardando datos...")
        self.guardar_datos()
