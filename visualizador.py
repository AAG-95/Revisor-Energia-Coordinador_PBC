# import individual libraries as in code index.py from folder code
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
import webbrowser
import os
from threading import Timer
import calendar


# Clase para visualizar los datos de la base de datos
class DashBarChart:
    def __init__(self, df_tarjeta_credito, df_cuenta_corriente, port=8052):
         

        self.port = port    
        self.app = dash.Dash(__name__)
        self.app.layout = html.Div([#print hola
            html.H1("Visualizador de Datos"),
            ])


    def open_browser(self):
        # Abre el navegador web para visualizar la aplicación
        debug_mode = self.app.server.debug
        run_main = os.environ.get
        ("WERKZEUG_RUN_MAIN") == "true"
        if not debug_mode or run_main:
            webbrowser.get().open_new(f"http://localhost:{self.port}")


    def run(self):
        # Inicia la aplicación Dash y abre el navegador
        Timer(1, self.open_browser).start()
        self.app.run_server(debug=False, port=self.port)
