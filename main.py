import visualizador as vs
import comparador_recaudacion_y_energia as cre
import comparador_sistemas as csi


# Create an instance of ComparadorSistemas

comparador_sistemas = csi.ComparadorSistemas()

df_combinado_sistemas = comparador_sistemas.combinar_datos(
    comparador_sistemas.cargar_datos_sistemas(),
    comparador_sistemas.cargar_datos_recaudacion(),
)


""" 
# Create an instance of ComparadorRecaudacionEnergia
comparador = cre.ComparadorRecaudacionEnergia()

# Call the methods on the instance
df_combinado = comparador.combinar_datos(comparador.cargar_datos_energia(), comparador.cargar_datos_recaudacion())
# Run app

vs.DashBarChart(df_combinado).run()
 """
