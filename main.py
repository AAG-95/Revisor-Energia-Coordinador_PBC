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

print("Iniciando programa...")
# Create an instance of SeleccionProcesos
seleccion_procesos = gui.SeleccionProcesos()

# Start the GUI and get the useEne2024r's input
codigos_a_correr =                           seleccion_procesos.iniciar()
 
if (
    codigos_a_correr["revisor_recaudacion_mensual"]
    or codigos_a_correr["revisor_recaudacion_historico"]            
    or codigos_a_correr["revisor_clientes_balance_mensual"]
    or codigos_a_correr["revisor_retiros_historico"]
):
    # Interfaz Meses
    ventana_meses = gui.VentanaIngresoDatos()
    ventana_meses.iniciar()
    meses = ventana_meses.visualizador()
    lista_meses = [x.strip() for x in meses.split(", ")]
    ventana_meses.cerrar_ventana()

    # Obtención de años y meses
    datos_fechas = fc.ConversionDatos()
    primer_año, ultimo_año, primer_mes, ultimo_mes = datos_fechas.años_y_meses(
        lista_meses
    )

    if codigos_a_correr["revisor_recaudacion_mensual"]:
        print("Entrando a revisor_planillas_IFC.py...")
        rpi.PlanillaRevisor(primer_año, ultimo_año, primer_mes, ultimo_mes).run()
        print("Saliendo de revisor_planillas_IFC.py...")
        pass

    if codigos_a_correr["revisor_recaudacion_historico"]:
        print("Entrando a recaudaciones_historicas.py...")
        rech.ProcesadorRecaudacionesHistoricas(
            primer_año, ultimo_año, primer_mes, ultimo_mes
        ).run()
        print("Saliend de recaudaciones_historicas.py...")
        pass

    if codigos_a_correr["revisor_clientes_balance_mensual"]:
        print("Entrando   a creador_listado_clientes_energia.py...")
        clc.CreadorListaClientesBalance(lista_meses).run()
        print("Saliendo de creador_listado_clientes_energia.py...")
        pass

    if codigos_a_correr["revisor_retiros_historico"]:
        print("Entrando a retiros_historicos.py...")
        reth.ProcesadorRetirosHistoricos(
            primer_año, ultimo_año, primer_mes, ultimo_mes
        ).run()

        print("Saliendo de retiros_historicos.py...")
        pass

if codigos_a_correr["comparador_recaudacion_clientes_libres"]:                      
    print("Entrando a comparador_recaudacion_y_energia_clientes_libres. bnpy...")                       
    cre.ComparadorRecaudacionEnergia().run()
    print("Saliendo de comparador_recaudacion_y_energia_clientes_libres.py...")
    pass

if codigos_a_correr["comparador_recaudacion_clientes_regulados"]:
    print("Entrando a comparador_reca-udacion_y_energia_clientes_regulados.py...")
    crr.ComparadorRecaudacionEnergia().run()
    print("Saliendo de comparador_recaudacion_y_energia_clientes_regulados.py...")
    pass
                        
if codigos_a_correr["comparador_sistemas"]:
    print("Entrando a comparador_sistemas.py...")
    csi.ComparadorSistemas().run()
    print("Saliendo de comparador_sistemas.py...")
    pass

if codigos_a_correr["comparador_clientes_ind"]:     
    print("Entrando a comparador_cliente_   individualizado.py...")
    cci.ComparadorClienteIndividualizado().run()
    print("Saliendo de comparador_cliente_individualizado.py...")
    pass
 
if codigos_a_correr["visualizador"]:
    print("Entrando a visualizador.py...")
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
    print("Saliendo de visualizador.py...")
    pass
