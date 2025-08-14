import visualizador as vs
import revisor_planillas_ifc as rpi
import recaudaciones_historicas as rech
import creador_listado_clientes_energia as clc
import retiros_historicos as reth   
import comparador_recaudacion_y_energia_clientes_libres as cre
import comparador_recaudacion_y_energia_clientes_regulados as crr
import comparador_cliente_individualizado as cci
import comparador_sistemas as csi
import interfaz as gui 
import funciones as fc
import pandas as pd

print("Iniciando programa...")

# Crear una instancia de SeleccionProcesos para obtener las opciones del usuario
seleccion_procesos = gui.SeleccionProcesos()

# Iniciar la GUI y obtener los códigos de procesos a correr
codigos_a_correr = seleccion_procesos.iniciar()

# Verificar si alguno de los procesos que requieren fechas está seleccionado
if (
    codigos_a_correr["revisor_recaudacion_mensual"]
    or codigos_a_correr["revisor_recaudacion_historico"]
    or codigos_a_correr["revisor_clientes_balance_mensual"]
    or codigos_a_correr["revisor_retiros_historico"]
):
    # Crear y mostrar la ventana para ingreso de meses
    ventana_meses = gui.VentanaIngresoDatos()
    ventana_meses.iniciar()
    # Obtener los meses ingresados por el usuario
    meses = ventana_meses.visualizador()
    lista_meses = [x.strip() for x in meses.split(", ")]
    # Cerrar la ventana de ingreso de datos
    ventana_meses.cerrar_ventana()

    # Convertir los meses ingresados en años y meses individuales
    datos_fechas = fc.ConversionDatos()
    primer_año, ultimo_año, primer_mes, ultimo_mes = datos_fechas.años_y_meses(lista_meses)

    # Ejecutar los procesos seleccionados por el usuario
    # Revisor de recaudación mensual
    if codigos_a_correr["revisor_recaudacion_mensual"]:
        print("Entrando a revisor_planillas_IFC.py...")
        rpi.PlanillaRevisor(primer_año, ultimo_año, primer_mes, ultimo_mes).run()
        print("Saliendo de revisor_planillas_IFC.py...")

    # Revisor de recaudación histórica
    if codigos_a_correr["revisor_recaudacion_historico"]:
        print("Entrando a recaudaciones_historicas.py...")
        rech.ProcesadorRecaudacionesHistoricas(primer_año, ultimo_año, primer_mes, ultimo_mes).run()
        print("Saliendo de recaudaciones_historicas.py...")

    # Revisor de balance mensual de clientes
    if codigos_a_correr["revisor_clientes_balance_mensual"]:
        print("Entrando a creador_listado_clientes_energia.py...")
        clc.CreadorListaClientesBalance(lista_meses).run()
        print("Saliendo de creador_listado_clientes_energia.py...")

    # Revisor de retiros históricos
    if codigos_a_correr["revisor_retiros_historico"]:
        print("Entrando a retiros_historicos.py...")
        reth.ProcesadorRetirosHistoricos(primer_año, ultimo_año, primer_mes, ultimo_mes).run()
        print("Saliendo de retiros_historicos.py...")

# Ejecutar otros procesos basados en la selección del usuario
# Comparador de recaudación de clientes libres
if codigos_a_correr["comparador_recaudacion_clientes_libres"]:
    print("Entrando a comparador_recaudacion_y_energia_clientes_libres.py...")
    cre.ComparadorRecaudacionEnergia().run()
    print("Saliendo de comparador_recaudacion_y_energia_clientes_libres.py...")

# Comparador de recaudación de clientes regulados
if codigos_a_correr["comparador_recaudacion_clientes_regulados"]:
    print("Entrando a comparador_recaudacion_y_energia_clientes_regulados.py...")
    crr.ComparadorRecaudacionEnergia().run()
    print("Saliendo de comparador_recaudacion_y_energia_clientes_regulados.py...")

# Comparador de sistemas
if codigos_a_correr["comparador_sistemas"]:
    print("Entrando a comparador_sistemas.py...")
    csi.ComparadorSistemas().run()
    print("Saliendo de comparador_sistemas.py...")

# Comparador de clientes individualizados
if codigos_a_correr["comparador_clientes_ind"]:
    print("Entrando a comparador_cliente_individualizdo.py...")
    cci.ComparadorClienteIndividualizado().run()
    print("Saliendo de comparador_cliente_individualizado.py...")

# Visualizador de datos11
if codigos_a_correr["visualizador"]:
    print("Entrando a visualizador.py...")

    # Definir la ruta de la carpeta de entrada
    carpeta_entrada = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Balance-Recaudación\\"

    # Leer los archivos CSV necesarios
    df_combinado_energia_libres = pd.read_csv(carpeta_entrada + "df_revision_energia_libres.csv", sep=";", encoding="UTF-8")
    df_combinado_energia_regulados = pd.read_csv(carpeta_entrada + "df_revision_energia_regulados.csv", sep=";", encoding="UTF-8")
    df_combinado_sistemas = pd.read_csv(carpeta_entrada + "df_revision_sistemas.csv", sep=";", encoding="UTF-8")
    df_combinado_ind = pd.read_csv(carpeta_entrada + "df_clientes_ind.csv", sep=";", encoding="UTF-8")

    # Ejecutar la aplicación de visualización
    vs.DashBarChart(df_combinado_energia_libres, df_combinado_sistemas, df_combinado_ind, df_combinado_energia_regulados).run()
    print("Saliendo de visualizador.py...")
