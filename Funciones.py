# Importación de las bibliotecas necesarias
import openpyxl
import pandas as pd
from datetime import datetime, timedelta
import tkinter as tk

# Versiones de las bibliotecas utilizadas
# python version: 3.9.13
# openpyxl version: 3.0.10
# pandas version: 1.4.4


class ObtencionDatos:
    # Función para obtener tablas desde una hoja de cálculo
    def obtencion_Tablas(data_total, primera_fila, primera_columna):
        primera_fila = primera_fila - 1
        primera_columna = primera_columna - 1

        # Seleccionar las columnas relevantes
        selected_columns = data_total.columns[primera_columna:]

        # Crear una lista para almacenar las filas
        rows_to_add = []
        all_null = False  # Inicializar la variable all_null como False
        Contador = 0

        # Iterar a través de las filas
        for i in range(primera_fila, len(data_total)):
            # Obtener los valores de las columnas seleccionadas para la fila actual
            values = data_total.loc[i, selected_columns].values
            Contador += 1

            # Verificar si todas las columnas son nulas
            if pd.isnull(values).all():
                all_null = True
                break

            # Agregar la fila a la lista
            rows_to_add.append(values)

        Largo_DF = len(data_total) - primera_fila

        # Verificar si se ha revisado la última fila
        if Largo_DF == Contador:
            all_null = True

        # Verificar si se encontraron filas con valores no nulos
        if not all_null:
            print("No se encontraron filas con todos los valores nulos.")
        else:
            # Crear un DataFrame con las filas recolectadas
            new_rows_df = pd.DataFrame(rows_to_add, columns=selected_columns)

        # Obtén la primera fila
        first_row = new_rows_df.iloc[0]

        # Inicializa un diccionario para realizar un seguimiento de las ocurrencias de valores
        value_counts = {}

        # Recorre cada elemento de la primera fila
        for i, value in enumerate(first_row):
            # Verifica si el valor ya ha aparecido antes
            if value in value_counts:
                # Incrementa el contador y modifica el valor actual
                value_counts[value] += 1
                first_row[i] = f"{value}_{value_counts[value]}"
            else:
                # Si es la primera aparición, registra el valor en el diccionario
                value_counts[value] = 1

        # Asignar la primera fila como encabezados de columna
        new_rows_df.columns = first_row

        # Reindexar el DataFrame para omitir la primera fila
        new_rows_df = new_rows_df.reindex(new_rows_df.index.drop(0)).reset_index(
            drop=True
        )

        return new_rows_df

    # Función para obtener tablas desde una hoja de cálculo
    def obtencion_tablas_clientes(
        data_total, primera_fila, primera_columna, ultima_columna
    ):
        """
        Extracts relevant rows and columns from a given DataFrame starting from the specified row and column.

        Args:
        - data_total: A pandas DataFrame containing the data to extract.
        - primera_fila: An integer representing the index of the first row to extract.
        - primera_columna: An integer representing the index of the first column to extract.

        Returns:
        - A pandas DataFrame containing the extracted rows and columns.
        """
        primera_fila = primera_fila - 1
        primera_columna = primera_columna - 1

        # Seleccionar las columnas relevantes
        selected_columns = data_total.columns[primera_columna:ultima_columna]

        # Crear una lista para almacenar las filas
        rows_to_add = []
        all_null = False  # Inicializar la variable all_null como False
        Contador = 0

        # Iterar a través de las filas
        for i in range(primera_fila, len(data_total)):
            # Obtener los valores de las columnas seleccionadas para la fila actual
            values = data_total.loc[i, selected_columns].values
            Contador += 1

            # Verificar si todas las columnas son nulas
            if pd.isnull(values).all() and pd.isnull(prev_values).all():
                all_null = True
                break

            # Agregar la fila a la lista
            rows_to_add.append(values)

            # Actualizar los valores de la iteración anterior
            prev_values = values

        Largo_DF = len(data_total) - primera_fila

        # Verificar si se ha revisado la última fila
        if Largo_DF == Contador:
            all_null = True

        # Verificar si se encontraron filas con valores no nulos
        if not all_null:
            print("No se encontraron filas con todos los valores nulos.")
        else:
            # Crear un DataFrame con las filas recolectadas
            new_rows_df = pd.DataFrame(rows_to_add, columns=selected_columns)

        # Obtén la primera fila
        first_row = new_rows_df.iloc[0]

        # Inicializa un diccionario para realizar un seguimiento de las ocurrencias de valores
        value_counts = {}

        # Recorre cada elemento de la primera fila
        for i, value in enumerate(first_row):
            # Verifica si el valor ya ha aparecido antes
            if value in value_counts:
                # Incrementa el contador y modifica el valor actual
                value_counts[value] += 1
                first_row[i] = f"{value}_{value_counts[value]}"
            else:
                # Si es la primera aparición, registra el valor en el diccionario
                value_counts[value] = 1

        # Asignar la primera fila como encabezados de columna
        new_rows_df.columns = first_row

        # Reindexar el DataFrame para omitir la primera fila
        new_rows_df = new_rows_df.reindex(new_rows_df.index.drop(0)).reset_index(
            drop=True
        )

        return new_rows_df

# Función para generar una lista de pares de años y meses
def generar_pares(primer_año, último_año, primer_mes_primer_año, último_mes_último_año):
    pares_lista = []

    for año in range(primer_año, último_año + 1):
        if año == primer_año:
            mes_inicio = primer_mes_primer_año
        else:
            mes_inicio = 1

        if año == último_año:
            mes_fin = último_mes_último_año
        else:
            mes_fin = 12

        for mes in range(mes_inicio, mes_fin + 1):
            año_mes = int(str(año % 100) + "{:02d}".format(mes))
            pares_lista.append((año, año_mes))

    return pares_lista


# Genera listado de datos
def generar_listado_meses(
    primer_año, último_año, primer_mes_primer_año, último_mes_último_año
):
    pares_lista = []

    for año in range(primer_año, último_año + 1):
        if año == primer_año:
            mes_inicio = primer_mes_primer_año
        else:
            mes_inicio = 1

        if año == último_año:
            mes_fin = último_mes_último_año
        else:
            mes_fin = 12

        for mes in range(mes_inicio, mes_fin + 1):
            # Formatear el año y el mes como "YYMM" y convertirlos a entero
            año_mes = int(str(año % 100) + "{:02d}".format(mes))
            pares_lista.append(año_mes)

    return pares_lista


class ProcesamientosDeDatos:
    # Función para procesar datos y guardarlos en archivos CSV
    def process_data(carpeta_salida, dataframes, titulo, par):
        """
        Combines a list of dataframes into a single dataframe and saves it as a CSV file.

        Parameters:
        carpeta_salida (str): The output folder path.
        dataframes (list): A list of pandas dataframes to be combined.
        titulo (str): The title of the output CSV file.
        par (str or tuple): A string or tuple to be appended to the output CSV file name.

        Returns:
        None
        """

        # Concatenar todos los dataframes en un solo dataframe
        if len(dataframes) >= 2:
            combined_df = pd.concat(dataframes, ignore_index=True)
        else:
            combined_df = dataframes[0]

        carpeta_carga = carpeta_salida

        if isinstance(par, str):
            archivo = (
                carpeta_carga + titulo + par + ".csv"
            )  # Agregar '.csv' al nombre del archivo
        else:
            archivo = (
                carpeta_carga + titulo + str(par[1]) + ".csv"
            )  # Agregar '.csv' al nombre del archivo

        # Guardar el dataframe combinado en un archivo CSV
        combined_df.to_csv(archivo, encoding="utf-8", index=False, sep=";")

        # Eliminar dataframes de la memoria después de guardar en CSV
        del dataframes
        del combined_df

    def combinar_y_guardar_csv(lista_nombres_archivos, directorio, lista_meses):
        """
        Combina y guarda archivos CSV en una carpeta específica.

        Parameters:
            lista_nombres_archivos (list): Lista de nombres base de archivos (sin las fechas).
            directorio (str): Ruta completa de la carpeta donde se encuentran los archivos CSV.
            lista_meses (list): Lista de meses en formato "YYMM" (por ejemplo, ["2106", "2107"]).

        Returns:
            None
        """

        for nombre_archivo in lista_nombres_archivos:
            dataframes = []

            for fecha in lista_meses:
                nombre_completo_archivo = f"{nombre_archivo}{fecha}.csv"
                ruta_archivo = f"{directorio}{nombre_completo_archivo}"

                try:
                    # Leer el archivo CSV
                    df = pd.read_csv(ruta_archivo, encoding="utf-8", sep=";")
                    dataframes.append(df)
                except FileNotFoundError:
                    print(
                        f"No se encontró el archivo {nombre_completo_archivo} para la fecha {fecha}."
                    )

            if dataframes:
                # Combinar todos los DataFrames en uno solo
                resultado_final = pd.concat(dataframes, ignore_index=True)

                # Cambiar valores de SISTEMA a Sistema
                # Verificar si la columna 'Zonal' existe en el DataFrame
                if "Zonal" in resultado_final.columns:
                    resultado_final["Zonal"] = resultado_final["Zonal"].replace(
                        r"\bSISTEMA\b", "Sistema", regex=True
                    )

                # Nombre del archivo CSV de salida
                nombre_archivo_csv = f"{nombre_archivo}_resultado.csv"  # Cambia el nombre según tu preferencia
                ruta_archivo_csv = f"{directorio}{nombre_archivo_csv}"

                # Escribir el DataFrame en el archivo CSV de salida
                resultado_final.to_csv(ruta_archivo_csv, encoding="utf-8", index=False)
                print(resultado_final)
                print(f"DataFrame guardado en: {ruta_archivo_csv}")
            else:
                print(f"No se encontraron archivos CSV para {nombre_archivo}.")

    def guardar_en_excel(dataframes, output_file):
        # Create a Pandas Excel writer using XlsxWriter as the engine
        excel_writer = pd.ExcelWriter(output_file, engine="openpyxl")
        # Write each dataframe to a different worksheet with a generated sheet name
        for index, (name, df) in enumerate(dataframes):
            sheet_name = name
            df.to_excel(excel_writer, sheet_name=sheet_name, index=False)
        # Save the Excel file
        excel_writer.close()

    # Función comparador de valores (TRUE si son iguales, Falso si no)
    def comparador(valor1, valor2):
        return round(valor1, 3) == round(valor2, 3)

    # Función que muestra resultado correcto si entrada es True, Falso en caso contrario
    def mostrar_resultado(Nombre, result):
        if result:
            print(f"{Nombre} Correcto")
        else:
            print(f"Error en {Nombre}")


class ConversionDatos:
    # Define a function to convert month abbreviations to date, example input: "Ene20"
    def convertir_fecha(Mes):
        months = {
            "Ene": 1,
            "Feb": 2,
            "Mar": 3,
            "Abr": 4,
            "May": 5,
            "Jun": 6,
            "Jul": 7,
            "Ago": 8,
            "Sep": 9,
            "Oct": 10,
            "Nov": 11,
            "Dic": 12,
        }
        month = months[Mes[:3]]
        year = int(Mes[-4:])
        return datetime(year, month, 1)

    # Define a function to convert month abbreviations as for example "Ene20" converts to 2001
    def convertir_fecha_numeral(Mes):
        months = {
            "Ene": "01",
            "Feb": "02",
            "Mar": "03",
            "Abr": "04",
            "May": "05",
            "Jun": "06",
            "Jul": "07",
            "Ago": "08",
            "Sep": "09",
            "Oct": "10",
            "Nov": "11",
            "Dic": "12",
        }
        month = months[Mes[:3]]
        year = int(Mes[-2:])
        return str(year) + str(month)
