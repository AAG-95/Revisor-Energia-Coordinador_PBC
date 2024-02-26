import tkinter as tk


class VentanaIngresoDatos:
    def __init__(self):
        self.mes_reparticion = None

        # Crear la ventana principal
        self.ventana = tk.Tk()
        self.ventana.title("Ingreso de Datos")

        # Etiqueta y entrada para "Año Repartición"
        self.etiqueta_mes_reparticion = tk.Label(
            self.ventana,
            text="Mes Procesado:\nEjemplo Formato 1 Mes: Ene2023\nEjemplo Formato 2 Meses o Más: Ene2023, Feb2023, Mar2023",
        )
        self.etiqueta_mes_reparticion.pack()
        self.entrada_mes_reparticion = tk.Entry(self.ventana)
        self.entrada_mes_reparticion.pack(fill=tk.BOTH, expand=True)

        # Botón para procesar la entrada
        self.boton_procesar = tk.Button(
            self.ventana, text="Procesar", command=self.visualizador
        )
        self.boton_procesar.pack()

    # Función para procesar la entrada
    def visualizador(self):
        self.mes_reparticion = self.entrada_mes_reparticion.get()

        self.ventana.quit()  # Cerrar la ventana
        return self.mes_reparticion

    def iniciar(self):
        # Iniciar la interfaz gráfica
        self.ventana.mainloop()

    def cerrar_ventana(self):
        self.ventana.destroy()    


class SeleccionProcesos:
    def __init__(self):
        # Crear la ventana principal
        self.ventana = tk.Tk()
        self.ventana.title("Ingreso de Datos")

        # Checkboxes for code blocks to run
        self.run_code1 = tk.BooleanVar()
        self.checkbox_code1 = tk.Checkbutton(self.ventana, text="Revisor Planillas Recaudación Mensuales", variable=self.run_code1)
        self.checkbox_code1.pack()

        self.run_code2 = tk.BooleanVar()
        self.checkbox_code2 = tk.Checkbutton(self.ventana, text="Creador Registro Recaudación Histórica", variable=self.run_code2)
        self.checkbox_code2.pack()

        self.run_code3 = tk.BooleanVar()
        self.checkbox_code3 = tk.Checkbutton(self.ventana, text="Revisor Clientes Listado de Clientes Balance de Energía", variable=self.run_code3)
        self.checkbox_code3.pack()

        self.run_code4 = tk.BooleanVar()
        self.checkbox_code4 = tk.Checkbutton(self.ventana, text="Creador Listado de Clientes Balance de Energía Histórica", variable=self.run_code4)
        self.checkbox_code4.pack()

        self.run_code5 = tk.BooleanVar()
        self.checkbox_code5 = tk.Checkbutton(self.ventana, text="Comparador Recaudación Recaudación ", variable=self.run_code5)
        self.checkbox_code5.pack()

        # Botón para procesar la entrada
        self.boton_procesar = tk.Button(
            self.ventana, text="Procesar", command=self.visualizador
        )
        self.boton_procesar.pack()

    # Función para procesar la entrada
    def visualizador(self):
        # Store the state of the checkboxes in instance variables
        self.code1 = self.run_code1.get()
        self.code2 = self.run_code2.get()
        self.code3 = self.run_code3.get()
        self.code4 = self.run_code4.get()
        self.code5 = self.run_code5.get()

        self.ventana.destroy()  # Destroy the ventana

    def iniciar(self):
        # Iniciar la interfaz gráfica
        self.ventana.mainloop()

        # Return the state of the checkboxes
        return {'revisor_recaudacion_mensual': self.code1, 'revisor_recaudacion_historico': self.code2, 'revisor_clientes_balance_mensual': self.code3, 'revisor_retiros_historico': self.code4, 'comparador_recaudacion_clientes_libres': self.code5}