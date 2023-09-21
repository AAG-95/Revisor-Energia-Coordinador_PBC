import pandas as pd

 



carpeta =  r"C:\Users\alonso.flores\Documents\Datos_Recaudación\\"

 

df = pd.read_csv(carpeta+'resultado_final.csv', encoding='utf-8', sep=";")

print(df)

 

# Replace values in the 'SISTEMA' column

df['Zonal'] = df['Zonal'].str.replace(r'\bSISTEMA\b', 'Sistema', regex=True)

# Concatenar las columnas "B" y "C" para definir un valor único

df['SISTEMA'] = df['Zonal'] + '_' + df['Nivel Tensión Zonal']

 

# Agrupar por la columna "A" y obtener las listas de valores únicos en la columna "B_C"

valores_diferentes = df.groupby('Barra')['SISTEMA'].agg(lambda x: list(set(x))).reset_index()

valores_diferentes.rename(columns={'SISTEMA': 'Valores_diferentes_SISTEMA'}, inplace=True)

 

# Obtener la cantidad de valores diferentes en la columna "B_C" para cada valor único en la columna "A"

valores_diferentes['Cantidad_valores_SISTEMA'] = valores_diferentes['Valores_diferentes_SISTEMA'].apply(len)

 



# Obtener la lista de repeticiones de cada valor en la columna "B_C" para cada valor único en la columna "A"

valores_diferentes['Repeticiones_por_valor_SISTEMA'] = valores_diferentes['Barra'].apply(lambda x: [list(df[df['Barra'] == x]['SISTEMA']).count(i) for i in valores_diferentes[valores_diferentes['Barra'] == x]['Valores_diferentes_SISTEMA'].iloc[0]])

 



# Agregar una nueva columna que contenga el valor más repetido de la lista en "Repeticiones_por_valor_B_C"

valores_diferentes['Valor_mas_repetido'] = valores_diferentes['Repeticiones_por_valor_SISTEMA'].apply(lambda x: max(set(x), key=x.count))

 



# Guardar el resultado final como un archivo CSV en la misma carpeta del script

valores_diferentes.to_csv(carpeta+"valores_diferentes_barras.csv", sep=';', index=False,encoding='utf-8')

print(valores_diferentes)

 

print()