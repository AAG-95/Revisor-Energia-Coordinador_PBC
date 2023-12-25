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
from dash import dash_table
import time


# Clase para visualizar los datos de la base de datos
class DashBarChart:
    def __init__(self, df_combinado, port=8052):
        self.port = port
        self.df_combinado = df_combinado
        self.app = dash.Dash(__name__)
        # Preprocess the data
        self.df_dict = {}

        table = dash_table.DataTable(
            id="table",
            columns=[{"name": i, "id": i} for i in df_combinado.columns],
            data=df_combinado.to_dict("records"),
        )

        table2 = dash_table.DataTable(
            id="table2",
            columns=[{"name": i, "id": i} for i in df_combinado.columns],
            data=df_combinado.to_dict("records"),
        )

        for value in df_combinado["Mes Consumo"].unique():
            self.df_dict[value] = df_combinado[df_combinado["Mes Consumo"] == value]

        blue_square = html.Div(
            [
                html.H1(
                    "Revisor de Energía",
                    style={"text-align": "center", "color": "black"},
                ),
                html.Img(
                    src="assets\coordinador_logo.png",
                    style={"height": "80px", "margin-left": "auto"},
                ),
            ],
            style={
                "background-color": "lightblue",
                "width": "100%",
                "height": "80px",
                "display": "flex",
                "align-items": "center",
                "justify-content": "start",
                "padding": "0 10px",
            },
        )

        # Convert 'Mes Consumo' to datetime if it's not already
        df_combinado["Mes Consumo"] = pd.to_datetime(df_combinado["Mes Consumo"])

        # Sort the DataFrame by 'Mes Consumo'
        df_combinado = df_combinado.sort_values("Mes Consumo")

        # Generate the dropdown options
        dropdown = dcc.Dropdown(
            id="mes-consumo-dropdown",
            options=[
                {"label": i.strftime("%Y-%m-%d"), "value": i.strftime("%Y-%m-%d")}
                for i in df_combinado["Mes Consumo"].unique()
            ]
            + [{"label": "Select All", "value": "ALL"}],
            value=df_combinado["Mes Consumo"].unique().tolist(),
            multi=True,
            className='my-dropdown'
        )

        # Wait for a few seconds

        self.app.layout = html.Div(
            [  # print hola
                blue_square,
                html.H1("Visualizador de Datos"),
                html.Div(
                    [
                        html.Div(
                            [
                               
                                html.Div(
                                    [
                                        html.Label("My Label", className="my-label"),
                                        dropdown,
                                    ],
                                    className="label-and-dropdown",
                                ),
                                dcc.Loading(
                                    id="loading",
                                    type="circle",
                                    children=[table],
                                ),
                            ],
                            className="tabla_diferencias",
                        ),
                        html.Div(
                            [
                                dcc.Loading(
                                    id="loading2",
                                    type="circle",
                                    children=[table2],
                                )
                            ],
                            className="tabla_diferencias2",
                        ),
                    ],
                    className="tabla_y_figura_1",
                ),
            ]
        )

        @self.app.callback(
            Output("mes-consumo-dropdown", "value"),
            [Input("mes-consumo-dropdown", "value")],
        )
        def update_dropdown(selected_values):
            if selected_values:
                if "ALL" in selected_values:
                    print(selected_values)
                    return df_combinado["Mes Consumo"].unique().tolist()
                else:
                    print(selected_values)
                    return [value for value in selected_values if value != "ALL"]
            else:
                return df_combinado.to_dict("records")

        @self.app.callback(
            Output("table", "data"), [Input("mes-consumo-dropdown", "value")]
        )
        def update_table(selected_values):
            if selected_values:
                filtered_df = df_combinado[
                    df_combinado["Mes Consumo"].isin(selected_values)
                ]
                return filtered_df.to_dict("records")
            else:
                return df_combinado.to_dict("records")

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
