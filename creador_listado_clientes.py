# Creador Listado Clientes 

import pandas as pd
import zipfile
import pandas as pd
import zipfile
import xlrd
import Funciones as fc
# Open data from a ZIP file Abril-2020-R03D-1.zip in \\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Balances\Balances de Energía\Archivos Fuente\2020

Mes = 'Ago20'
Mes = fc.convertir_fecha(Mes)

zip_path = r'\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\Balances\Balances de Energía\Archivos Fuente\2020\Ago20_R01D-2.zip'
with zipfile.ZipFile(zip_path) as myzip:
    with myzip.open('01 Resultados/02 Balance Físico/REVISION_NORTE_2008.xls') as myfile:
        df_balance_fisico = pd.read_excel(myfile, sheet_name='Balance por Barra', header= None)
        
        # Seleted table from sheet Balance por Barra
        df_balance_fisico = fc.obtencion_tablas_clientes(df_balance_fisico,6,2,17)
        
        # Change Nombre_2 to Barra
        df_balance_fisico.rename(columns={'Nombre_2':'Barra'}, inplace=True)

        # If values is found in column Barra, replace all nan values in bottom rows from same column with that value and stop when find another value
        df_balance_fisico['Barra'] = df_balance_fisico['Barra'].ffill()

        # Add month column
        #  


        
        
        print(df_balance_fisico)


