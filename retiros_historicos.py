import pandas as pd
import funciones as fc
import os
import warnings

warnings.filterwarnings("ignore", category=pd.errors.DtypeWarning)

# Rest of your code


class ProcesadorRetirosHistoricos:
    """
    Esta clase se encarga de cargar, procesar y organizar los datos de retiros históricos
    de energía de clientes libres y regulados. El objetivo principal es actualizar los registros
    históricos de retiros de energía de los clientes libres y regulados, y guardar los cambios
    en archivos CSV. Además, se actualiza el registro de cambios de los clientes libres y regulados.

    Atributos:
    - primer_año: año inicial para el procesamiento de datos históricos
    - último_año: año final para el procesamiento de datos históricos
    - primer_mes_primer_año: mes inicial del primer año para el procesamiento de datos históricos
    - último_mes_último_año: mes final del último año para el procesamiento de datos históricos
    - ruta_balances_clientes_libres: ruta donde se encuentran los balances mensuales de clientes libres
    - ruta_balances_historicos_clientes_L: ruta donde se encuentran los balances históricos de clientes libres
    - ruta_balances_historicos_clientes_R: ruta donde se encuentran los balances históricos de clientes regulados
    - ruta_registro_cambios_clientes_L: ruta del archivo de registro de cambios de clientes libres
    - ruta_registro_cambios_clientes_R: ruta del archivo de registro de cambios de clientes regulados
    - pares_lista: lista de pares de año y mes desde el primer año y mes hasta el último año y mes

    Métodos:
    - carga_informacion_historica: carga la información histórica de retiros de energía de clientes libres y regulados
    - procesamiento_mensual: procesa los balances mensuales de clientes libres y regulados
    - carga_datos_historicos: carga los datos históricos de retiros de energía de clientes libres y regulados

    """

    def __init__(
        self, primer_año, último_año, primer_mes_primer_año, último_mes_último_año
    ):
        # Ruta donde se encuentran los balances mensuales de clientes libres
        self.ruta_balances_clientes_libres = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Retiros Mensuales"

        # Ruta donde se encuentran los balances históricos de clientes libres
        self.ruta_balances_historicos_clientes_L = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Retiros Históricos Clientes"

        # Ruta donde se encuentran los balances históricos de clientes regulados
        self.ruta_balances_historicos_clientes_R = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Retiros Históricos Clientes"

        # Ruta del archivo de registro de cambios de clientes libres
        self.ruta_registro_cambios_clientes_L = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Registro de Cambios\Registro_de_Cambios_Clientes_Libres.csv"

        # Ruta del archivo de registro de cambios de clientes regulados
        self.ruta_registro_cambios_clientes_R = r"\\nas-cen1\D.Peajes\\Cargo por Transmisión\02 Repartición\Balances\Listados de Clientes\Registro de Cambios\Registro_de_Cambios_Clientes_Regulados.csv"

        # Año inicial para el procesamiento de datos históricos
        self.primer_año = primer_año

        # Mes inicial del primer año para el procesamiento de datos históricos
        self.primer_mes_primer_año = primer_mes_primer_año

        # Año final para el procesamiento de datos históricos
        self.último_año = último_año

        # Mes final del último año para el procesamiento de datos históricos
        self.último_mes_último_año = último_mes_último_año

        # Genera una lista de pares de año y mes desde el primer año y mes hasta el último año y mes
        self.pares_lista = fc.ConversionDatos().generar_pares(
            self.primer_año,
            self.último_año,
            self.primer_mes_primer_año,
            self.último_mes_último_año,
        )

    def carga_informacion_historica(self):
        """
        Carga la información histórica de retiros de energía de clientes libres y regulados.
        """
        #! Dataframes históricos Clientes Libres
        # Verificar si el archivo "Retiros_Históricos_Clientes_L.csv" existe en la ruta especificada
        if os.path.isfile(
            self.ruta_balances_historicos_clientes_L
            + "\Retiros_Históricos_Clientes_L.csv"
        ):

            # Leer el archivo CSV "Retiros_Históricos_Clientes_L.csv" con separador ";" y codificación "UTF-8"
            df_historico_clientes_L = pd.read_csv(
                self.ruta_balances_historicos_clientes_L
                + "\Retiros_Históricos_Clientes_L.csv",
                sep=";",
                encoding="UTF-8",
            )

            # Obtener los valores únicos de la columna "Mes"
            self.valores_mes = df_historico_clientes_L["Mes"].unique()
        else:
            # Imprimir mensaje de error si el archivo no existe
            print(
                f"No existe BDD de Retiros de Energía Histórica en: {self.ruta_balances_historicos_clientes_L}"
            )

            # Crear un DataFrame vacío y una lista vacía para valores_mes
            df_historico_clientes_L = pd.DataFrame()
            self.valores_mes = []

        #! Dataframes históricos Clientes Regulados
        # Verificar si el archivo "Retiros_Históricos_Clientes_R.csv" existe en la ruta especificada
        if os.path.isfile(
            self.ruta_balances_historicos_clientes_R
            + "\Retiros_Históricos_Clientes_R.csv"
        ):

            # Leer el archivo CSV "Retiros_Históricos_Clientes_R.csv" con separador ";" y codificación "UTF-8"
            df_historico_clientes_R = pd.read_csv(
                self.ruta_balances_historicos_clientes_R
                + "\Retiros_Históricos_Clientes_R.csv",
                sep=";",
                encoding="UTF-8",
            )

            # Obtener los valores únicos de la columna "Mes"
            self.valores_mes = df_historico_clientes_R["Mes"].unique()
        else:
            # Imprimir mensaje de error si el archivo no existe
            print(
                f"No existe BDD de Retiros de Energía Histórica en: {self.ruta_balances_historicos_clientes_R}"
            )

            # Crear un DataFrame vacío y una lista vacía para valores_mes
            df_historico_clientes_R = pd.DataFrame()
            self.valores_mes = []

    def procesamiento_mensual(self):
        """
        Procesa los balances mensuales de clientes libres y regulados para obtener los listados de clientes
        correspondientes a cada mes. Los datos procesados se almacenan en los atributos dataframe_clientes_L y
        dataframe_clientes_R.

        """
        #! Listado meses Clientes L
        # Convertir valores
        self.dataframe_clientes_L = []

        # Iterar sobre cada par en pares_lista
        for pair in self.pares_lista:
            i = pair[1]

            # Leer el archivo Excel correspondiente a cada par
            df_mes_clientes_L = pd.read_excel(
                self.ruta_balances_clientes_libres + f"\Retiros_{i}.xlsx",
                sheet_name="Listado_Clientes_L",
            )

            # Obtener las primeras 18 columnas
            df_mes_clientes_L = df_mes_clientes_L.iloc[:, :27]

            # Eliminar filas vacías
            df_mes_clientes_L = df_mes_clientes_L.dropna(how="all")

            # Agregar el DataFrame procesado a la lista dataframe_clientes_L
            self.dataframe_clientes_L.append(df_mes_clientes_L)

        #! Listado meses Clientes R
        # Convertir valores
        self.dataframe_clientes_R = []

        # Iterar sobre cada par en pares_lista
        for pair in self.pares_lista:
            i = pair[1]

            # Leer el archivo Excel correspondiente a cada par
            df_mes_clientes_R = pd.read_excel(
                self.ruta_balances_clientes_libres + f"\Retiros_{i}.xlsx",
                sheet_name="Listado_Clientes_R",
            )

            # Obtener las primeras 18 columnas
            df_mes_clientes_R = df_mes_clientes_R.iloc[:, :27]

            # Eliminar filas vacías
            df_mes_clientes_R = df_mes_clientes_R.dropna(how="all")

            # Agregar el DataFrame procesado a la lista dataframe_clientes_R
            self.dataframe_clientes_R.append(df_mes_clientes_R)

    # ? Update Registros Históricos Clientes Libres--------------------------------------------------------------

    def carga_datos_historicos(self):
        """
        Carga los datos históricos de retiros de energía de clientes libres y regulados, procesa los balances mensuales
        y actualiza los registros históricos de retiros de energía de los clientes libres y regulados. Además, guarda los
        cambios en archivos CSV y actualiza el registro de cambios de los clientes libres y regulados.
        """

        #! Dataframes históricos Clientes Libres
        # Verificar si el archivo "Retiros_Históricos_Clientes_L.csv" existe en la ruta especificada
        if os.path.isfile(
            self.ruta_balances_historicos_clientes_L
            + "\Retiros_Históricos_Clientes_L.csv"
        ):

            # Leer el archivo CSV "Retiros_Históricos_Clientes_L.csv" con separador ";" y codificación "UTF-8"
            df_historico_clientes_L = pd.read_csv(
                self.ruta_balances_historicos_clientes_L
                + "\Retiros_Históricos_Clientes_L.csv",
                sep=";",
                encoding="UTF-8",
            )

            # Obtener los valores únicos de la columna "Mes"
            self.valores_mes = df_historico_clientes_L["Mes"].unique()
        else:
            # Imprimir mensaje de error si el archivo no existe
            print(
                f"No existe BDD de Retiros de Energía Histórica en: {self.ruta_balances_historicos_clientes_L}"
            )

            # Crear un DataFrame vacío y una lista vacía para valores_mes
            df_historico_clientes_L = pd.DataFrame()
            self.valores_mes = []

        #! Dataframes históricos Clientes Regulados
        # Verificar si el archivo "Retiros_Históricos_Clientes_R.csv" existe en la ruta especificada
        if os.path.isfile(
            self.ruta_balances_historicos_clientes_R
            + "\Retiros_Históricos_Clientes_R.csv"
        ):

            # Leer el archivo CSV "Retiros_Históricos_Clientes_R.csv" con separador ";" y codificación "UTF-8"
            df_historico_clientes_R = pd.read_csv(
                self.ruta_balances_historicos_clientes_R
                + "\Retiros_Históricos_Clientes_R.csv",
                sep=";",
                encoding="UTF-8",
            )

            # Obtener los valores únicos de la columna "Mes"
            self.valores_mes = df_historico_clientes_R["Mes"].unique()
        else:
            # Imprimir mensaje de error si el archivo no existe
            print(
                f"No existe BDD de Retiros de Energía Histórica en: {self.ruta_balances_historicos_clientes_R}"
            )

            # Crear un DataFrame vacío y una lista vacía para valores_mes
            df_historico_clientes_R = pd.DataFrame()
            self.valores_mes = []

        #! Unión de Dataframes
        for df_clientes_L in self.dataframe_clientes_L:
            if os.path.isfile(
                self.ruta_balances_historicos_clientes_L
                + "\Retiros_Históricos_Clientes_L.csv"
            ):

                # Obtener el mes único en la columna Mes
                mes_fecha = pd.Timestamp(df_clientes_L["Mes"].unique()[0]).strftime(
                    "%m-%d-%Y"
                )

                df_historico_clientes_L = pd.read_csv(
                    self.ruta_balances_historicos_clientes_L
                    + "\Retiros_Históricos_Clientes_L.csv",
                    sep=";",
                    encoding="UTF-8",
                )

                # Convertir la columna Mes a formato datetime con formato "%m-%d-%Y"
                df_historico_clientes_L["Mes"] = pd.to_datetime(
                    df_historico_clientes_L["Mes"]
                ).dt.strftime("%m-%d-%Y")
                df_clientes_L["Mes"] = pd.to_datetime(df_clientes_L["Mes"])

                if mes_fecha not in df_historico_clientes_L["Mes"].unique().tolist():
                    print(
                        "Se actualiza el archivo Registro de Cambios Históricos Libre con registro mes: "
                        + str(mes_fecha)
                    )

                    df_retiros_historico_L_final = pd.concat(
                        [df_historico_clientes_L, df_clientes_L]
                    )

                    columnas_numericas = [
                        "medida1",
                        "flag1",
                        "medida2",
                        "flag2",
                        "medida2a",
                        "flag2a",
                        "medida3",
                        "flag3",
                        "error",
                        "calculo",
                    ]  # reemplazar con los nombres de tus columnas

                    # Reemplazar "." con "," en las columnas seleccionadas
                    for column in columnas_numericas:
                        df_retiros_historico_L_final[column] = (
                            df_retiros_historico_L_final[column]
                            .astype(str)
                            .str.replace(".", ",")
                        )

                    df_retiros_historico_L_final["Mes"] = pd.to_datetime(
                        df_retiros_historico_L_final["Mes"]
                    ).dt.strftime("%m-%d-%Y")

                    #! Salida de archivo retiros históricos Clientes Libres
                    # Reescribir df_retiros_historico_L_final en la ruta especificada
                    df_retiros_historico_L_final.to_csv(
                        self.ruta_balances_historicos_clientes_L
                        + "\Retiros_Históricos_Clientes_L.csv",
                        sep=";",
                        index=False,
                    )

                    # Actualizar y guardar Registro Cambios Clientes
                    df_registro_cambios_clientes_L = (
                        df_retiros_historico_L_final.reset_index(drop=True)
                    )

                    df_registro_cambios_clientes_L = df_registro_cambios_clientes_L[
                        ["nombre_medidor", "clave_medidor", "Suministrador_final", "Mes"]
                    ]

                    df_registro_cambios_clientes_L[
                        "Nombre_Cliente_Actual_Para_Clave"
                    ] = (
                        df_registro_cambios_clientes_L.sort_values("Mes")
                        .groupby("clave_medidor")["nombre_medidor"]
                        .transform("last")
                    )

                    df_registro_cambios_clientes_L["Mes_Actual_De_Nombre_Cliente"] = (
                        df_registro_cambios_clientes_L.sort_values("Mes")
                        .groupby("clave_medidor")["Mes"]
                        .transform("last")
                    )

                    # Reemplazar valores NaN en la columna Nombre con "-"
                    df_registro_cambios_clientes_L["nombre_medidor"] = (
                        df_registro_cambios_clientes_L["nombre_medidor"].fillna("-")
                    )

                    # Reemplazar espacios en blanco con un carácter especial
                    cols = ["nombre_medidor", "clave_medidor", "Suministrador_final"]
                    for col in cols:
                        df_registro_cambios_clientes_L[col] = (
                            df_registro_cambios_clientes_L[col].str.replace(" ", "##_#")
                        )

                    # Realizar operaciones necesarias
                    df_registro_cambios_clientes_L = (
                        df_registro_cambios_clientes_L.drop_duplicates(
                            subset=cols, keep="last"
                        )
                    )

                    # Reemplazar valores NaN en la columna Nombre con "-"
                    df_registro_cambios_clientes_L["nombre_medidor"] = (
                        df_registro_cambios_clientes_L["nombre_medidor"].fillna("-")
                    )

                    df_registro_cambios_clientes_L = (
                        df_registro_cambios_clientes_L.dropna(
                            subset=["nombre_medidor", "clave_medidor", "Suministrador_final"]
                        )
                    )

                    df_registro_cambios_clientes_L = (
                        df_registro_cambios_clientes_L.drop_duplicates(
                            subset=["nombre_medidor", "clave_medidor", "Suministrador_final"],
                            keep="last",
                        )
                    )

                    # Reemplazar el carácter especial de nuevo a espacios en blanco
                    for col in cols:
                        df_registro_cambios_clientes_L[col] = (
                            df_registro_cambios_clientes_L[col].str.replace("##_#", " ")
                        )

                    df_registro_cambios_clientes_L.rename(
                        columns={"nombre_medidor": "Cliente"}, inplace=True
                    )

                    df_registro_cambios_clientes_L.rename(
                        columns={"clave_medidor": "Clave"}, inplace=True
                    )

                    #! Salida de archivo registro cambios Clientes Libres
                    df_registro_cambios_clientes_L.to_csv(
                        self.ruta_registro_cambios_clientes_L,
                        sep=";",
                        index=False,
                        encoding="UTF-8",
                    )
                else:
                    print(
                        "Revisar Base De Datos de Clientes Libres Históricos, el Mes Actual"
                        + mes_fecha
                        + " ya fue actualizado anteriormente"
                    )
        # ? Update Registros Históricos Clientes Regulados--------------------------------------------------------------

        for df_clientes_R in self.dataframe_clientes_R:

            if os.path.isfile(
                self.ruta_balances_historicos_clientes_R
                + "\Retiros_Históricos_Clientes_R.csv"
            ):
                # Obtener el mes único en la columna Mes
                mes_fecha = pd.Timestamp(df_clientes_R["Mes"].unique()[0]).strftime(
                    "%m-%d-%Y"
                )
                df_historico_clientes_R = pd.read_csv(
                    self.ruta_balances_historicos_clientes_R
                    + "\Retiros_Históricos_Clientes_R.csv",
                    sep=";",
                    encoding="UTF-8",
                )

                # Convertir la columna Mes a formato datetime con formato "%m-%d-%Y"
                df_historico_clientes_R["Mes"] = pd.to_datetime(
                    df_historico_clientes_R["Mes"]
                ).dt.strftime("%m-%d-%Y")
                df_clientes_R["Mes"] = pd.to_datetime(df_clientes_R["Mes"])

                if mes_fecha not in df_historico_clientes_R["Mes"].unique().tolist():
                    print(
                        "Se actualiza el archivo Registro de Cambios Históricos Regulados con registro mes: "
                        + str(mes_fecha)
                    )

                    df_retiros_historico_R_final = pd.concat(
                        [df_historico_clientes_R, df_clientes_R]
                    )

                    columnas_numericas = [
                        "medida1",
                        "flag1",
                        "medida2",
                        "flag2",
                        "medida2a",
                        "flag2a",
                        "medida3",
                        "flag3",
                        "error",
                        "calculo",
                    ]  # reemplazar con los nombres de tus columnas

                    # Reemplazar "." con "," en las columnas seleccionadas
                    for column in columnas_numericas:
                        df_retiros_historico_R_final[column] = (
                            df_retiros_historico_R_final[column]
                            .astype(str)
                            .str.replace(".", ",")
                        )

                    df_retiros_historico_R_final["Mes"] = pd.to_datetime(
                        df_retiros_historico_R_final["Mes"]
                    )
                    df_retiros_historico_R_final["Mes"] = df_retiros_historico_R_final[
                        "Mes"
                    ].dt.strftime("%m-%d-%Y")

                    #! Salida de archivo retiros históricos Clientes Regulados
                    # Reescribir df_retiros_historico_R_final en la ruta especificada
                    df_retiros_historico_R_final.to_csv(
                        self.ruta_balances_historicos_clientes_R
                        + "\Retiros_Históricos_Clientes_R.csv",
                        sep=";",
                        index=False,
                    )

                    # Actualizar y guardar Registro Cambios Clientes
                    df_registro_cambios_clientes_R = (
                        df_retiros_historico_R_final.reset_index(drop=True)
                    )

                    df_registro_cambios_clientes_R = df_registro_cambios_clientes_R[
                        ["nombre_medidor", "clave_medidor", "Suministrador_final", "Mes"]
                    ]

                    df_registro_cambios_clientes_R[
                        "Nombre_Cliente_Actual_Para_Clave"
                    ] = (
                        df_registro_cambios_clientes_R.sort_values("Mes")
                        .groupby("clave_medidor")["nombre_medidor"]
                        .transform("last")
                    )

                    df_registro_cambios_clientes_R["Mes_Actual_De_Nombre_Cliente"] = (
                        df_registro_cambios_clientes_R.sort_values("Mes")
                        .groupby("clave_medidor")["Mes"]
                        .transform("last")
                    )

                    # Reemplazar valores NaN en la columna Nombre con "-"
                    df_registro_cambios_clientes_R["nombre_medidor"] = (
                        df_registro_cambios_clientes_R["nombre_medidor"].fillna("-")
                    )

                    # Reemplazar espacios en blanco con un carácter especial
                    cols = ["nombre_medidor", "clave_medidor", "Suministrador_final"]
                    for col in cols:
                        df_registro_cambios_clientes_R[col] = (
                            df_registro_cambios_clientes_R[col].str.replace(" ", "##_#")
                        )

                    # Realizar operaciones necesarias
                    df_registro_cambios_clientes_R = (
                        df_registro_cambios_clientes_R.drop_duplicates(
                            subset=cols, keep="last"
                        )
                    )

                    # Reemplazar valores NaN en la columna Nombre con "-"
                    df_registro_cambios_clientes_R["nombre_medidor"] = (
                        df_registro_cambios_clientes_R["nombre_medidor"].fillna("-")
                    )

                    df_registro_cambios_clientes_R = (
                        df_registro_cambios_clientes_R.dropna(
                            subset=["nombre_medidor", "clave_medidor", "Suministrador_final"]
                        )
                    )

                    df_registro_cambios_clientes_R = (
                        df_registro_cambios_clientes_R.drop_duplicates(
                            subset=["nombre_medidor", "clave_medidor", "Suministrador_final"],
                            keep="last",
                        )
                    )

                    # Reemplazar el carácter especial de nuevo a espacios en blanco
                    for col in cols:
                        df_registro_cambios_clientes_R[col] = (
                            df_registro_cambios_clientes_R[col].str.replace("##_#", " ")
                        )

                    df_registro_cambios_clientes_R.rename(
                        columns={"nombre_medidor": "Cliente"}, inplace=True
                    )
                    
                    df_registro_cambios_clientes_R.rename(
                        columns={"clave_medidor": "Clave"}, inplace=True
                    )

                    #! Salida de archivo registro cambios Clientes Regulados
                    df_registro_cambios_clientes_R.to_csv(
                        self.ruta_registro_cambios_clientes_R,
                        sep=";",
                        index=False,
                        encoding="UTF-8",
                    )
                else:
                    print(
                        "Revisar Base De Datos de Clientes Regulados Históricos, el Mes Actual"
                        + mes_fecha
                        + " ya fue actualizado anteriormente"
                    )

    def run(self):
        self.carga_informacion_historica()
        self.procesamiento_mensual()
        self.carga_datos_historicos()
        print("Process completed successfully")
