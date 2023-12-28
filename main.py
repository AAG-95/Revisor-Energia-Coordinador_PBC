import visualizador as vs
import comparador_recaudacion_y_energia as cre


# Create an instance of ComparadorRecaudacionEnergia
comparador = cre.ComparadorRecaudacionEnergia()

# Call the methods on the instance
df_combinado = comparador.combinar_datos(comparador.cargar_datos_energia(), comparador.cargar_datos_recaudacion())
# Run app
vs.DashBarChart(df_combinado).run()


