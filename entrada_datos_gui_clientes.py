import tkinter as tk


class VentanaIngresoDatos:
    def __init__(self):
        self.año_reparticion = None
        self.mes_reparticion = None
        self.fecha_generacion = None
        self.fecha_emision = None

        # Crear la ventana principal
        self.ventana = tk.Tk()
        self.ventana.title("Ingreso de Datos")

        # Etiqueta y entrada para "Año Repartición"
        self.etiqueta_año_reparticion = tk.Label(self.ventana, text="Año (ejemplo Formato: 2023):")
        self.etiqueta_año_reparticion.pack()
        self.entrada_año_reparticion = tk.Entry(self.ventana)
        self.entrada_año_reparticion.pack()

        # Etiqueta y entrada para "Mes Repartición"
        self.etiqueta_mes_reparticion = tk.Label(self.ventana, text="Mes (ejemplo Formato: Junio):")
        self.etiqueta_mes_reparticion.pack()
        self.entrada_mes_reparticion = tk.Entry(self.ventana)
        self.entrada_mes_reparticion.pack()

        # Etiqueta y entrada para "Fecha Generación"
        self.etiqueta_fecha_generacion = tk.Label(self.ventana, text="Fecha Generación (ejemplo Formato: 5/6/2023):")
        self.etiqueta_fecha_generacion.pack()
        self.entrada_fecha_generacion = tk.Entry(self.ventana)
        self.entrada_fecha_generacion.pack()

        # Etiqueta y entrada para "Fecha Emisión"
        self.etiqueta_fecha_emision = tk.Label(self.ventana, text="Fecha Emisión (ejemplo Formato: 5/6/2023):")
        self.etiqueta_fecha_emision.pack()
        self.entrada_fecha_emision = tk.Entry(self.ventana)
        self.entrada_fecha_emision.pack()

        # Botón para procesar la entrada
        self.boton_procesar = tk.Button(self.ventana, text="Procesar", command=self.visualizador)
        self.boton_procesar.pack()

    # Función para procesar la entrada
    def visualizador(self):
        self.año_reparticion = self.entrada_año_reparticion.get()
        self.mes_reparticion = self.entrada_mes_reparticion.get()
        self.fecha_generacion = self.entrada_fecha_generacion.get()
        self.fecha_emision = self.entrada_fecha_emision.get()

        # Aquí puedes realizar alguna acción con los valores ingresados, por ejemplo, imprimirlos
        print("Año Repartición:", self.año_reparticion)
        print("Mes Repartición:", self.mes_reparticion)
        print("Fecha Generación:", self.fecha_generacion)
        print("Fecha Emisión:", self.fecha_emision)
        

        self.ventana.quit()  # Cerrar la ventana

    def iniciar(self):
        # Iniciar la interfaz gráfica
        self.ventana.mainloop()
