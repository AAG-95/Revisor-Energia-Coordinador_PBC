import tkinter as tk


class VentanaIngresoDatos:
    def __init__(self):
        self.año_reparticion = None

        # Crear la ventana principal
        self.ventana = tk.Tk()
        self.ventana.title("Ingreso de Datos")

        # Etiqueta y entrada para "Año Repartición"
        self.etiqueta_año_reparticion = tk.Label(self.ventana, text="Mes Procesado:\nEjemplo Formato 1 Mes: Ene2023\nEjemplo Formato 2 Meses o Más: Ene2023, Feb2023, Mar2023")
        self.etiqueta_año_reparticion.pack()
        self.entrada_año_reparticion = tk.Entry(self.ventana)
        self.entrada_año_reparticion.pack(fill=tk.BOTH, expand=True)

        # Botón para procesar la entrada
        self.boton_procesar = tk.Button(self.ventana, text="Procesar", command=self.visualizador)
        self.boton_procesar.pack()

    # Función para procesar la entrada
    def visualizador(self):
        self.año_reparticion = self.entrada_año_reparticion.get()

        # Aquí puedes realizar alguna acción con los valores ingresados, por ejemplo, imprimirlos
        print("Mes Repartición:", self.año_reparticion)
  
        self.ventana.quit()  # Cerrar la ventana
        return self.año_reparticion 

    def iniciar(self):
        # Iniciar la interfaz gráfica
        self.ventana.mainloop()
