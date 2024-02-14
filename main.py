import visualizador as vs
import comparador_recaudacion_y_energia as cre
import comparador_sistemas as csi
import pandas as pd

# Carpeta de entrada
carpeta_entrada = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Balance-Recaudación\\"

""" # Create an instance of ComparadorRecaudacionEnergia
comparador_energia = cre.ComparadorRecaudacionEnergia()

# Call the methods on the instance
df_combinado_energia = comparador_energia.combinar_datos(comparador_energia.cargar_datos_energia(), comparador_energia .cargar_datos_recaudacion()) """


df_combinado_energia = pd.read_csv(carpeta_entrada + "df_revision_energia.csv", sep=";", encoding="UTF-8")

# Create an instance of ComparadorSistemas
comparador_sistemas = csi.ComparadorSistemas()



df_combinado_sistemas = comparador_sistemas.combinar_datos(
    comparador_sistemas.cargar_datos_sistemas(),
    comparador_sistemas.cargar_datos_recaudacion(),
)




# Run app
vs.DashBarChart(df_combinado_energia, df_combinado_sistemas).run()

