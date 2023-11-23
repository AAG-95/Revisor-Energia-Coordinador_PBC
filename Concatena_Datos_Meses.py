# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 11:12:18 2023
@author: alonso.flores
"""

# Importación de librerías necesarias
import os
import pandas as pd
import funciones as func

# Directorio donde se encuentran los archivos CSV
directorio = r'C:/Users/alonso.flores/Documents/Revisor2/'

# Lista de fechas en formato "YYMM" (por ejemplo, ["2106", "2107", ...])
Lista_meses=func.generar_listado_meses(2020,2023,6,7)

#Listado de nombres de BDD a Concatenar
Listado_BDD= ["Observaciones Clientes Libres", "Observaciones Clientes Regulados", "Revisor Clientes Libres", "Revisor Clientes Regulados", "Revisor_Clientes"]

# Uso de Fucnión que Concatena Dataframes 
func.combinar_y_guardar_csv(Listado_BDD,directorio,Lista_meses)

