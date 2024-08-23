import pandas as pd
import numpy as np
import funciones as fc

class ComparadorClienteIndividualizado:
    """
    Esta clase se encarga de cargar, procesar y organizar los datos de clientes individuales
    a partir de un archivo Excel. El objetivo principal es calcular la diferencia en días entre
    la fecha actual y la fecha de término de contrato de cada cliente, para luego ordenar la 
    lista de clientes por aquellos cuyos contratos están más próximos a vencer. Finalmente, 
    el resultado se guarda en un archivo CSV.
    """
    
    def __init__(self):
        # Directorios de salida y sistemas
        self.carpeta_salida = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Balance-Recaudación\\"
        self.carpeta_sistemas = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Recaudación\\"

    def cargar_datos_clientes_ind(self):
        # Cargar datos de clientes individuales desde un archivo Excel
        df_clientes_ind = pd.read_excel(
            self.carpeta_sistemas + "Revisores RCUT.xlsm",
            sheet_name="Clientes Indiv. Vigentes",
            header=None,
            engine="openpyxl"
        )

        # Procesar la tabla usando la función obtencion_Tablas de fc
        df_clientes_ind = fc.ObtencionDatos().obtencion_Tablas(df_clientes_ind, 5, 4)

        # Filtrar las columnas relevantes
        df_clientes_ind = df_clientes_ind[
            [
                "Cliente (Balance de Energía)",
                "Clave (Balance de Energía)",
                "RUT Cliente",
                "Suministrador",
                "Empresa Cliente",
                "Suministrador",
                "Tipo Cliente",
                "Suscripción",
                "Inicio",
                "Termino"
            ]
        ]

        # Agregar la fecha actual a la tabla
        df_clientes_ind["Fecha Actual"] = pd.Timestamp.now()

        # Convertir columnas de fechas a tipo datetime
        df_clientes_ind["Fecha Actual"] = pd.to_datetime(df_clientes_ind["Fecha Actual"])
        df_clientes_ind["Termino"] = pd.to_datetime(df_clientes_ind["Termino"])

        # Calcular la diferencia de días entre "Termino" y "Fecha Actual"
        df_clientes_ind["Días para termino de contrato"] = (
            df_clientes_ind["Termino"] - df_clientes_ind["Fecha Actual"]
        ).dt.days

        # Ordenar por "Días para termino de contrato" en orden ascendente
        df_clientes_ind = df_clientes_ind.sort_values(
            by=["Días para termino de contrato"], ascending=True
        ).reset_index(drop=True)
        
        # Guardar el DataFrame resultante en un archivo CSV
        df_clientes_ind.to_csv(self.carpeta_salida + "df_clientes_ind.csv", sep=";", encoding="UTF-8", index=False)

    def run(self):
        # Ejecutar la carga y procesamiento de datos
        self.cargar_datos_clientes_ind()


            