import visualizador as vs
import revisor_planillas_IFC as rpi
import recaudaciones_historicas as rh
import creador_listado_clientes_energia as clc
import retiros_historicos as rh
import comparador_recaudacion_y_energia_clientes_libres as cre
import comparador_recaudacion_y_energia_clientes_regulados as crr
import comparador_cliente_individualizado as cci
import comparador_sistemas as csi
import interfaz as gui
import funciones as fc
import pandas as pd



# Interfaz Meses
ventana_meses = gui.VentanaIngresoDatos()
ventana_meses.iniciar()
meses = ventana_meses.visualizador()
lista_meses = [x.strip() for x in meses.split(", ")]


# Carpeta de entrada
carpeta_entrada = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Balance-Recaudación\\"

""" # Create an instance of ComparadorRecaudacionEnergia
comparador_energia = cre.ComparadorRecaudacionEnergia()

# Call the methods on the instance 
df_combinado_energia = comparador_energia.combinar_datos(comparador_energia.cargar_datos_energia(), comparador_energia .cargar_datos_recaudacion())  """

df_combinado_energia = pd.read_csv(carpeta_entrada + "df_revision_energia.csv", sep=";", encoding="UTF-8")

""" # Create an instance of ComparadorSistemas
comparador_sistemas = csi.ComparadorSistemas()

df_combinado_sistemas = comparador_sistemas.combinar_datos(
    comparador_sistemas.cargar_datos_sistemas(),
    comparador_sistemas.cargar_datos_recaudacion(),
)  """

df_combinado_sistemas= pd.read_csv(carpeta_entrada + "df_revision_sistemas.csv", sep=";", encoding="UTF-8")

# Create an instance of ComparadorSistemas
comparador_clientes_ind = cci.ComparadorClienteIndividualizado()

df_clientes_ind = comparador_clientes_ind.cargar_datos_clientes_ind() 

# Create an instance of ComparadorRecaudacionEnergia
comparador_energia_regulados= crr.ComparadorRecaudacionEnergia()

df_combinado_energia_clientes_r = comparador_energia_regulados.combinar_datos(comparador_energia_regulados.cargar_datos_energia(), comparador_energia_regulados .cargar_datos_recaudacion()) 


# Run app
vs.DashBarChart(df_combinado_energia, df_combinado_sistemas,df_clientes_ind, df_combinado_energia_clientes_r).run()

