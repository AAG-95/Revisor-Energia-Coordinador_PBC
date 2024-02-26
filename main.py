import visualizador as vs
import revisor_planillas_IFC as rpi
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


# Interfaz Meses
ventana_meses = gui.VentanaIngresoDatos()
ventana_meses.iniciar()
meses = ventana_meses.visualizador()
lista_meses = [x.strip() for x in meses.split(", ")]
ventana_meses.cerrar_ventana()

# Obtención de años y meses
datos_fechas = fc.ConversionDatos()
primer_año, ultimo_año, primer_mes, ultimo_mes = datos_fechas.años_y_meses(lista_meses)

# Create an instance of SeleccionProcesos
seleccion_procesos = gui.SeleccionProcesos()

# Start the GUI and get the user's input
codigos_a_correr = seleccion_procesos.iniciar()

if codigos_a_correr["revisor_recaudacion_mensual"]:
    rpi.PlanillaRevisor(primer_año, ultimo_año, primer_mes, ultimo_mes).run()
    # Run code block 1
    print("a")
    pass

if codigos_a_correr["revisor_recaudacion_historico"]:
    rech.ProcesadorRecaudacionesHistoricas(
        primer_año, ultimo_año, primer_mes, ultimo_mes
    ).run()
    # Run code block 1
    print("a")
    # Run code block 2
    print("b")
    pass

if codigos_a_correr["revisor_clientes_balance_mensual"]:
    clc.CreadorListaClientesBalance(lista_meses).run()
    # Run code block 1
    print("a")
    # Run code block 2
    print("b")
    pass

if codigos_a_correr["revisor_retiros_historico"]:
    reth.ProcesadorRetirosHistoricos(
        primer_año, ultimo_año, primer_mes, ultimo_mes
    ).run()
    # Run code block 1
    print("a")
    # Run code block 2
    print("b")
    pass

if codigos_a_correr["comparador_recaudacion_clientes_libres"]:
    cre.ComparadorRecaudacionEnergia().run()
    # Run code block 1
    print("a")
    # Run code block 2
    print("b")
    pass

if codigos_a_correr["comparador_recaudacion_clientes_regulados"]:
    crr.ComparadorRecaudacionEnergia().run()
    # Run code block 1
    print("a")
    # Run code block 2
    print("b")
    pass

if codigos_a_correr["comparador_sistemas"]:
    csi.ComparadorSistemas().run()
    # Run code block 1
    print("a")
    # Run code block 2
    print("b")
    pass

if codigos_a_correr["comparador_clientes_ind"]:
    cci.ComparadorClienteIndividualizado().run()
    # Run code block 1
    print("a")
    # Run code block 2
    print("b")
    pass


if codigos_a_correr["visualizador"]:
    # Carpeta de entrada
    carpeta_entrada = r"\\nas-cen1\D.Peajes\Cargo por Transmisión\02 Repartición\\Revisiones\\Revisión Balance-Recaudación\\"

    df_combinado_energia_libres = pd.read_csv(
        carpeta_entrada + "df_revision_energia_libres.csv", sep=";", encoding="UTF-8"
    )
    df_combinado_energia_regulados = pd.read_csv(
        carpeta_entrada + "df_revision_energia_regulados.csv", sep=";", encoding="UTF-8"
    )
    df_combinado_sistemas = pd.read_csv(
        carpeta_entrada + "df_revision_sistemas.csv", sep=";", encoding="UTF-8"
    )
    df_combinado_ind = pd.read_csv(
        carpeta_entrada + "df_clientes_ind.csv", sep=";", encoding="UTF-8"
    )

    # Run app
    vs.DashBarChart(
        df_combinado_energia_libres,
        df_combinado_sistemas,
        df_combinado_ind,
        df_combinado_energia_regulados,
    ).run()

   
    # Run code block 1
    print("a")
    # Run code block 2
    print("b")
    pass




