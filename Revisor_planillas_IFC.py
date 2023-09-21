# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 11:12:18 2023

@author: alonso.flores
"""
import os
import pandas as pd
import re
from datetime import datetime
import numpy as np
import openpyxl
import warnings

# python version: 3.9.13 
# openpyxl version: 3.0.10
# pandas version: 1.4.4

# Disable warnings temporarily
warnings.filterwarnings("ignore")

# Crear la lista con los años
lista_años = [2020, 2021, 2022, 2023]

# Crear la lista con los pares de valores
pares_lista = []


#Función obtención Formulas 

#Función que permite obtener las tablas especificas, notar que la función fue modificada para que 
#las filas y las columnas seleccionadas sean acorde a excel y no al indice de pandas. Por ejemplo, la fila 2 de excel es la fila 2 en la entrada
# y la columna C corresponde a la columna 3 en la entrada

def obtencion_Tablas(data_total, primera_fila, primera_columna):
  primera_fila=primera_fila-2
  primera_columna=primera_columna-1
 #selected_columns = df.columns[6:15]
  selected_columns = data_total.columns[primera_columna:]
  # Crear una lista para almacenar las filas
  rows_to_add = []
  #all_null = False  # Declarar la variable all_null y asignarle un valor inicial
  Contador = 0

 # Iterar filas
  for i in range(primera_fila, len(data_total)):
     # Obtener los valores de las columnas seleccionadas para la fila actual
      values = data_total.loc[i, selected_columns].values
      Contador=Contador+1
      # Verificar si hay un valor nulo en todas las columnas
      if pd.isnull(values).all():
          all_null = True
          break
    
     # Agregar la fila a la lista
      rows_to_add.append(values)
     
  Largo_DF=(len(data_total)-primera_fila)      
  if Largo_DF == Contador:  # Verificar si se ha revisado la última fila
       all_null = True   

 # Verificar si se encontraron filas con valores no nulos
  if not all_null:
      print("No se encontraron filas con todos los valores nulos.")
  else:
    # Crear un DataFrame con las filas a agregar
      new_rows_df = pd.DataFrame(rows_to_add, columns=selected_columns)

    
 # Asignar la primera fila como encabezados de columna
  new_rows_df.columns = new_rows_df.iloc[0]

 # Reindexar el DataFrame para omitir la primera fila
  new_rows_df = new_rows_df.reindex(new_rows_df.index.drop(0)).reset_index(drop=True)
  return new_rows_df 


# Create a function to perform the main data processing
def process_data(dataframes,titulo):
    # Rest of your code (without importing the required libraries again)

    # Concatenate all the dataframes into a single dataframe
    combined_df = pd.concat(dataframes, ignore_index=True)

    carpeta_carga = r'C:/Users/alonso.flores/Documents/Revisor2/'
    archivo = carpeta_carga + titulo + str(par[1]) + '.csv'  # Add '.csv' to the filename

    combined_df.to_csv(archivo, encoding='utf-8', index=False, sep=";")
    del dataframes  # Remove dataframes from memory after saving to CSV
    del combined_df



# Agregar los pares de valores a la lista
for año in lista_años:
    if año == 2020:
        start = 6
    else:
        start = 1
    if año == 2023:
        end = 7
    else:
        end = 12
    for i in range(start, end+1):
        pares_lista.append((año, int(str(año % 100) + '{:02d}'.format(i))))

        

# Utilizar ambos valores de los pares
for par in pares_lista: 
 count = 0 
 carpeta =  r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\" + str(par[0]) + "\\" + str(par[1]) + "\\00 InfoRecibida\\IFC\\"
 entries = os.scandir(carpeta)
 
 # Lista para almacenar los nombres de los archivos encontrados
 file_list = [] 

 # Create an empty list to store the individual dataframes
 dataframes = [] #Datos Clientes Libres
 dataframes_regulados_E = []
 dataframes_regulados_R = []
 dataframes_libres_E = []
 dataframes_libres_R = []

 for val in entries:
     if val.is_file() and ("VE" in val.name) and ("FIFC" in val.name) and not val.name.startswith("~$"):
         count+=1
         file_list.append(val.name)      
 for file_name in file_list:
     print(file_name)
     excel_file_path = carpeta + file_name

     # Dataframe Hoja 'Detalle-Clientes L'
     df = pd.read_excel(excel_file_path, sheet_name='Detalle-Clientes L', engine='openpyxl')
     # Now you have the DataFrame 'df' with the data from the specified sheet
     df = obtencion_Tablas(df, 11, 2)
     Columnas_energía = df.columns[9:]
     df[Columnas_energía] = df[Columnas_energía].replace({0: np.nan}) 
     df[Columnas_energía] = df[Columnas_energía].replace({np.nan: None})
     df[Columnas_energía] = df[Columnas_energía].replace({None: np.nan})
     df = df.dropna(subset=Columnas_energía, how='all')
     df[Columnas_energía] = df[Columnas_energía].replace({np.nan: ""})  

    # Uncomment the following lines if you want to apply the replace operation
     for column in df.columns[9:]:
        df[column] = df[column].astype(str).str.replace('.', ',', regex=False)
     nombre_empresa  = re.findall(r'FIFC_(.*?)_RCUT', file_name) 
     df = df.assign(Recaudador=nombre_empresa[0])
    
     # Obtener los timestamps desde el índice
     timestamps = df.columns[9:]

     # Convertir a formato día-mes-año sin horas
     df.columns.values[9:] = [datetime.strftime(timestamp, '%d-%m-%Y') for timestamp in timestamps]
     Mes_Rep=df.columns[9]
     df = df.assign(Mes_Repartición=Mes_Rep)
     # Select columns from index 0 to 8 (inclusive) and the last column
     selected_columns = df.columns[:9].tolist() + [df.columns[-1]]
     df = pd.melt(df, id_vars=selected_columns, var_name='Mes Consumo', value_name='Energía [kWh]')
     # Filter out rows where the Value is not equal to 0 or not null (NaN)
     df = df[(~df['Energía [kWh]'].isnull()) & (df['Energía [kWh]'] != '')]
     # Add the dataframe to the list
     # Dataframe Hoja 'Formulario-Clientes L'
     df_FCL = pd.read_excel(excel_file_path, sheet_name='Formulario-Clientes L', engine='openpyxl')
   
     # Now you have the DataFrame 'df' with the data from the specified sheet
     df_FCL = obtencion_Tablas(df_FCL, 19, 3)
     df_FCL_E = df_FCL.iloc[:, :11]
     df_FCL_E = df_FCL_E[(~df_FCL_E['Observación'].isnull()) & (df_FCL_E['Observación'] != '')]
     df_FCL_E = df_FCL_E.assign(Mes_Repartición=Mes_Rep)
     df_FCL_E = df_FCL_E.assign(Recaudador=nombre_empresa[0])

     # Extract columns 15, 16, and 17 using iloc
     df_FCL_R = df_FCL.iloc[:, 14:18]
     df_FCL_R = df_FCL_R[(~df_FCL_R['Observación'].isnull()) & (df_FCL_R['Observación'] != '')]
     df_FCL_R = df_FCL_R.assign(Mes_Repartición=Mes_Rep)
     df_FCL_R = df_FCL_R.assign(Recaudador=nombre_empresa[0])

     df_FCR_E = None  # Initialize df_FCR_E to None
     df_FCR_R = None  # Initialize df_FCR_R to None
     try: 
      # Dataframe Hoja 'Formulario-Clientes R'
      df_FCR = pd.read_excel(excel_file_path, sheet_name='Formulario-Clientes R', engine='openpyxl')
      # Now you have the DataFrame 'df' with the data from the specified sheet
      df_FCR = obtencion_Tablas(df_FCR, 19, 3)
      df_FCR_E = df_FCR.iloc[:, :11]
      df_FCR_E = df_FCR_E[(~df_FCL_E['Observación'].isnull()) & (df_FCR_E['Observación'] != '')]
      df_FCR_E = df_FCR_E.assign(Mes_Repartición=Mes_Rep)
      df_FCR_E = df_FCR_E.assign(Recaudador=nombre_empresa[0])

      df_FCR_R = df_FCR.iloc[:, 14:22]
      df_FCR_R = df_FCR_R[(~df_FCR_R['Observación'].isnull()) & (df_FCR_R['Observación'] != '')]
      df_FCR_R = df_FCR_R.assign(Mes_Repartición=Mes_Rep)
      df_FCR_R = df_FCR_R.assign(Recaudador=nombre_empresa[0])
      
     except:
         pass
     
     dataframes.append(df)
     
     dataframes_libres_E.append(df_FCL_E)
     dataframes_libres_R.append(df_FCL_R)
     dataframes_regulados_E.append(df_FCR_E)
     dataframes_regulados_R.append(df_FCR_R)  
     # Extract the desired columns
     #selected_columns = df.loc[:, 'N°':'end_column']
     del df,df_FCL_E,df_FCL_R, df_FCR_E, df_FCR_R

 # Concatenate all the dataframes into a single dataframe
 process_data(dataframes, "Revisor_Clientes")
 process_data(dataframes_libres_E, "Observaciones Clientes Libres")
 process_data(dataframes_libres_R, "Revisor Clientes Libres")
 process_data(dataframes_regulados_E, "Observaciones Clientes Regulados")
 process_data(dataframes_regulados_R, "Revisor Clientes Regulados")
 del dataframes,dataframes_libres_E, dataframes_libres_R, dataframes_regulados_E,dataframes_regulados_R
 
# Concatenate all the dataframes into a single dataframe
