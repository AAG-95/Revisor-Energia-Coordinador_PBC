import pandas as pd

ruta_balances = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\2021\Balances"

# List of years from 2021 to 2023
years = [str(i) for i in range(20, 22)]

# List of months from 01 to 12
months = [str(i).zfill(2) for i in range(1, 13)]

# Combine years and months
year_month = [y + m for y in years for m in months]

# Filter the list to include only the months from February 2021 to September 2023
year_month = [ym for ym in year_month if ym >= '2001' and ym <= '2102']

print(year_month)

dataframe= []

for i in year_month:
    df= pd.read_excel(ruta_balances + f"\Retiros_{i}_B01D.xlsx", sheet_name="Retiros")
    #Get first 18 columns
    df = df.iloc[:, :18]
    #Erase emprty rows
    df = df.dropna(how="all")
    dataframe.append(df)
    print(df)
dataframe = pd.concat(dataframe)
ruta_salida = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\2021\Balances"

dataframe.to_excel(ruta_salida + "\\" + "Retiros_histórico" +".xlsx", engine="openpyxl", index=False)


    


