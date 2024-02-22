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
import plotly.express as px


# Clase para visualizar los datos de la base de datos
class DashBarChart:
    def __init__(
        self,
        df_combinado_energia,
        df_combinado_sistemas,
        df_clientes_ind,
        df_combinado_energia_clientes_r,
        port=8052,
    ):
        self.port = port
        self.app = dash.Dash(__name__)
        self.df_combinado_energia = df_combinado_energia
        self.df_combinado_sistemas = df_combinado_sistemas
        self.df_clientes_ind = df_clientes_ind
        self.df_combinado_energia_clientes_r = df_combinado_energia_clientes_r
        self.df_dict = {}  # Lista de Fechas
        for value in df_combinado_energia["Mes Consumo"].unique():
            self.df_dict[value] = df_combinado_energia[
                df_combinado_energia["Mes Consumo"] == value
            ]
        # Spanish month abbreviations
        self.meses_esp = [
            "",
            "Ene",
            "Feb",
            "Mar",
            "Abr",
            "May",
            "Jun",
            "Jul",
            "Ago",
            "Sep",
            "Oct",
            "Nov",
            "Dic",
        ]

        # Preprocess the data

        inicio_energia = html.Div(
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

        inicio_sistemas = html.Div(
            [
                html.H1(
                    "Revisor de Sistemas Zonales",
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

        inicio_cliente_individualizados = html.Div(
            [
                html.H1(
                    "Revisor de Clientes Individualizados",
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

        inicio_energia_clientes_r = html.Div(
            [
                html.H1(
                    "Revisor de Energía Clientes Regulados",
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

        # ? Diseño de Página Revisor de Energía
        # Preprocesamiento del dataframe
        # Convert 'Mes Consumo' to datetime if it's not already
        df_combinado_energia["Mes Consumo"] = pd.to_datetime(
            df_combinado_energia["Mes Consumo"]
        )

        # Sort the DataFrame by 'Mes Consumo'
        df_combinado_energia = df_combinado_energia.sort_values("Mes Consumo")

        # Ensure "Mes Consumo" is of datetime type
        df_combinado_energia["Mes Consumo"] = pd.to_datetime(
            df_combinado_energia["Mes Consumo"], format="%d-%m-%Y"
        )
        # df_combinado_sistemas["Mes Consumo"] type

        # Change column format to Ene-2023
        df_combinado_energia["Mes Consumo"] = df_combinado_energia["Mes Consumo"].apply(
            lambda x: self.meses_esp[x.day] + "-" + str(x.year)
        )
        # Revision por Tipo
        df_combinado_por_tipo_energia = (
            df_combinado_energia.groupby(["Tipo"])
            .agg({"Diferencia Energía [kWh]": "sum"})
            .reset_index()
        )

        #  thousands as dots
        df_combinado_por_tipo_energia[
            "Diferencia Energía [kWh]"
        ] = df_combinado_por_tipo_energia["Diferencia Energía [kWh]"].apply(
            lambda x: "{:,}".format(x)
            .replace(",", " ")
            .replace(".", ",")
            .replace(" ", ".")
        )

        # Tablas Revisor de Energía
        tabla_revision_tipo_energia = dash_table.DataTable(
            id="tabla_revision_tipo_energia",
            columns=[
                {"name": i, "id": i} for i in df_combinado_por_tipo_energia.columns
            ],
            data=df_combinado_por_tipo_energia.to_dict("records"),
        )

        # Revision general
        tabla_revision_energia = dash_table.DataTable(
            id="tabla_revision_energia",
            columns=[{"name": i, "id": i} for i in df_combinado_energia.columns],
            data=df_combinado_energia.to_dict("records"),
            export_format="csv",
            export_headers="display",
            css=[{"selector": ".export_button", "rule": "width: 100%;"}],
        )

        # Gráfico diferencias por Recaudador
        df_combinado_por_recaudador_energia = (
            df_combinado_energia.groupby(["Recaudador"])
            .agg({"Diferencia Energía [kWh]": "sum"})
            .reset_index()
        )

        df_combinado_por_recaudador_energia = (
            df_combinado_por_recaudador_energia.sort_values(
                "Diferencia Energía [kWh]", ascending=False
            )
        )

        # Assuming df_combinado_por_tipo is your DataFrame and 'Tipo' and 'Diferencia Energía [kWh]' are your columns
        fig_energia = px.bar(
            df_combinado_por_recaudador_energia,
            y="Recaudador",
            x="Diferencia Energía [kWh]",
            orientation="h",
        )
        grafico_energia = dcc.Graph(
            id="grafico_diferencias_recaudadores_energia",
            figure=fig_energia,
            className="grafico_recaudadores",
        )

        # Generate the dropdown options
        dropdown_mes_consumo = dcc.Dropdown(
            id="mes-consumo-dropdown_energia",
            options=[
                {"label": i, "value": i}
                for i in df_combinado_energia["Mes Consumo"].unique()
            ]
            + [{"label": "Select All", "value": "ALL"}],
            value=["ALL"],
            multi=True,
            className="dropdown_mes_consumo",
            style={"width": "100%"},
        )

        # Generate the dropdown options
        dropdown_barra = dcc.Dropdown(
            id="barra-dropdown_energia",
            options=[
                {"label": i, "value": i} for i in df_combinado_energia["Barra"].unique()
            ]
            + [{"label": "Select All", "value": "ALL"}],
            value=["ALL"],
            multi=True,
            className="dropdown_barra",
            style={"width": "100%"},
        )

        # Generate the dropdown options
        dropdown_recaudador = dcc.Dropdown(
            id="recaudador-dropdown_energia",
            options=[
                {"label": i, "value": i}
                for i in df_combinado_energia["Recaudador"].unique()
            ]
            + [{"label": "Select All", "value": "ALL"}],
            value=["ALL"],
            multi=True,
            className="dropdown_recaudador",
            style={"width": "100%"},
        )

        # Generate the dropdown options
        dropdown_clave = dcc.Dropdown(
            id="clave-dropdown_energia",
            options=[
                {"label": i, "value": i} for i in df_combinado_energia["Clave"].unique()
            ]
            + [{"label": "Select All", "value": "ALL"}],
            value=["ALL"],
            multi=True,
            className="dropdown_clave",
            style={"width": "100%"},
        )

        # Generate the dropdown options
        dropdown_tipo = dcc.Dropdown(
            id="tipo-dropdown_energia",
            options=[
                {"label": i, "value": i} for i in df_combinado_energia["Tipo"].unique()
            ]
            + [{"label": "Select All", "value": "ALL"}],
            value=["ALL"],
            multi=True,
            className="dropdown_tipo",
            style={"width": "100%"},
        )

        # ? Diseño de Página Revisor de Sistemas
        # Preprocesamiento del dataframe
        # Convert 'Mes Consumo' to datetime if it's not already
        df_combinado_sistemas["Mes Consumo"] = pd.to_datetime(
            df_combinado_sistemas["Mes Consumo"]
        )

        # Sort the DataFrame by 'Mes Consumo'
        df_combinado_sistemas = df_combinado_sistemas.sort_values("Mes Consumo")

        # Ensure "Mes Consumo" is of datetime type
        df_combinado_sistemas["Mes Consumo"] = pd.to_datetime(
            df_combinado_sistemas["Mes Consumo"], format="%d-%m-%Y"
        )

        # df_combinado_sistemas["Mes Consumo"] type

        # Change column format to Ene-2023
        df_combinado_sistemas["Mes Consumo"] = df_combinado_sistemas[
            "Mes Consumo"
        ].apply(lambda x: self.meses_esp[x.day] + "-" + str(x.year))

        # Agrupar por tipo y obtener cantidad de errores
        df_combinado_por_tipo_sistemas = (
            df_combinado_sistemas.groupby("Tipo").size().reset_index(name="Count")
        )

        # Tablas Revisor de Energía
        tabla_revision_tipo_sistemas = dash_table.DataTable(
            id="tabla_revision_tipo_sistemas",
            columns=[
                {"name": i, "id": i} for i in df_combinado_por_tipo_sistemas.columns
            ],
            data=df_combinado_por_tipo_sistemas.to_dict("records"),
        )

        # Revision general
        tabla_revision_sistemas = dash_table.DataTable(
            id="tabla_revision_sistemas",
            columns=[{"name": i, "id": i} for i in df_combinado_sistemas.columns],
            data=df_combinado_sistemas.to_dict("records"),
            export_format="csv",
            export_headers="display",
            css=[{"selector": ".export_button", "rule": "width: 100%;"}],
        )

        # Gráfico diferencias por Recaudador
        df_combinado_por_recaudador_sistemas = (
            df_combinado_sistemas.groupby(["Recaudador"])
            .size()
            .reset_index(name="Count")
        )

        df_combinado_por_recaudador_sistemas = (
            df_combinado_por_recaudador_sistemas.sort_values("Count", ascending=False)
        )

        # Assuming df_combinado_por_tipo is your DataFrame and 'Tipo' and 'Diferencia Energía [kWh]' are your columns
        fig_sistemas = px.bar(
            df_combinado_por_recaudador_sistemas,
            y="Recaudador",
            x="Count",
            orientation="h",
        )
        grafico_sistemas = dcc.Graph(
            id="grafico_diferencias_recaudadores_sistemas",
            figure=fig_sistemas,
            className="grafico_recaudadores",
        )

        # Generate the dropdown options
        dropdown_mes_consumo_sistemas = dcc.Dropdown(
            id="mes-consumo-dropdown_sistemas",
            options=[
                {"label": i, "value": i}
                for i in df_combinado_sistemas["Mes Consumo"].unique()
            ]
            + [{"label": "Select All", "value": "ALL"}],
            value=["ALL"],
            multi=True,
            className="dropdown_mes_consumo_sistemas",
            style={"width": "100%"},
        )

        # Generate the dropdown_sistemas options
        dropdown_barra_sistemas = dcc.Dropdown(
            id="barra-dropdown_sistemas",
            options=[
                {"label": i, "value": i}
                for i in df_combinado_sistemas["Barra"].unique()
            ]
            + [{"label": "Select All", "value": "ALL"}],
            value=["ALL"],
            multi=True,
            className="dropdown_barra_sistemas",
            style={"width": "100%"},
        )

        # Generate the dropdown_sistemas options
        dropdown_recaudador_sistemas = dcc.Dropdown(
            id="recaudador-dropdown_sistemas",
            options=[
                {"label": i, "value": i}
                for i in df_combinado_sistemas["Recaudador"].unique()
            ]
            + [{"label": "Select All", "value": "ALL"}],
            value=["ALL"],
            multi=True,
            className="dropdown_recaudador_sistemas",
            style={"width": "100%"},
        )

        # Generate the dropdown_sistemas options
        dropdown_clave_sistemas = dcc.Dropdown(
            id="clave-dropdown_sistemas",
            options=[
                {"label": i, "value": i}
                for i in df_combinado_sistemas["Clave"].unique()
            ]
            + [{"label": "Select All", "value": "ALL"}],
            value=["ALL"],
            multi=True,
            className="dropdown_clave_sistemas",
            style={"width": "100%"},
        )

        # Generate the dropdown_sistemas options
        dropdown_tipo_sistemas = dcc.Dropdown(
            id="tipo-dropdown_sistemas",
            options=[
                {"label": i, "value": i} for i in df_combinado_sistemas["Tipo"].unique()
            ]
            + [{"label": "Select All", "value": "ALL"}],
            value=["ALL"],
            multi=True,
            className="dropdown_tipo_sistemas",
            style={"width": "100%"},
        )

        # ? Diseño de Página Revisor de Clientes Individualizados

        # Preprocesamiento del dataframe
        # Tablas Revisor de Energía
        tabla_revision_clientes_ind = dash_table.DataTable(
            id="tabla_revision_clientes_ind",
            columns=[{"name": i, "id": i} for i in self.df_clientes_ind.columns],
            data=self.df_clientes_ind.to_dict("records"),
            export_format="csv",
            export_headers="display",
            style_table={"overflowX": "auto", "overflowY": "auto"},
            style_data_conditional=[
                {
                    "if": {
                        "column_id": "Días para termino de contrato",
                        "filter_query": "{Días para termino de contrato} lt 100",
                    },
                    "backgroundColor": "white",
                    "color": "red",
                }
            ],
        )

        # ? Diseño de Página Revisor de Energia Clientes Regulados

        df_combinado_energia_clientes_r["Mes"] = pd.to_datetime(
            df_combinado_energia_clientes_r["Mes"]
        )

        # Sort the DataFrame by 'Mes'
        df_combinado_energia_clientes_r = df_combinado_energia_clientes_r.sort_values(
            "Mes"
        )

        # Ensure "Mes" is of datetime type
        df_combinado_energia_clientes_r["Mes"] = pd.to_datetime(
            df_combinado_energia_clientes_r["Mes"], format="%d-%m-%Y"
        )

        # Change column format to Ene-2023
        df_combinado_energia_clientes_r["Mes"] = df_combinado_energia_clientes_r[
            "Mes"
        ].apply(lambda x: self.meses_esp[x.day] + "-" + str(x.year))

        # Preprocesamiento del dataframe
        # Tablas Revisor de Energía
        tabla_revision_energia_clientes_r = dash_table.DataTable(
            id="tabla_revision_energia_clientes_r",
            columns=[
                {"name": i, "id": i}
                for i in self.df_combinado_energia_clientes_r.columns
            ],
            data=self.df_combinado_energia_clientes_r.to_dict("records"),
            export_format="csv",
            export_headers="display",
            style_table={"overflowX": "auto", "overflowY": "auto"},
        )

        # Generate the dropdown options
        dropdown_mes_consumo_clientes_r = dcc.Dropdown(
            id="mes-consumo-dropdown_clientes_r",
            options=[
                {"label": i, "value": i}
                for i in df_combinado_energia_clientes_r["Mes"].unique()
            ]
            + [{"label": "Select All", "value": "ALL"}],
            value=["ALL"],
            multi=True,
            className="dropdown_mes_consumo_sistemas",
            style={"width": "100%"},
        )

        # Generate the dropdown_sistemas options
        dropdown_suministrador_clientes_r = dcc.Dropdown(
            id="suministrador-dropdown_clientes_r",
            options=[
                {"label": i, "value": i}
                for i in df_combinado_energia_clientes_r["Suministrador"].unique()
            ]
            + [{"label": "Select All", "value": "ALL"}],
            value=["ALL"],
            multi=True,
            className="dropdown_recaudador_sistemas",
            style={"width": "100%"},
        )

        #! Layout--------------------------------------------------------------------------------------
        # Wait for a few seconds
        self.app.layout = html.Div(
            [
                dcc.Location(id="url", refresh=False, pathname="/page-1"),
                html.Div(
                    [
                        dcc.Link(
                            "Revisor de Energía",
                            href="/page-1",
                            id="page-1-link",
                            className="button-link",
                        ),
                        dcc.Link(
                            "Revisor de Sistemas Zonales",
                            href="/page-2",
                            id="page-2-link",
                            className="button-link",
                        ),
                        dcc.Link(
                            "Revisor de Clientes Individualizados",
                            href="/page-3",
                            id="page-3-link",
                            className="button-link",
                        ),
                        dcc.Link(
                            "Revisor de Energía Clientes Regulados",
                            href="/page-4",
                            id="page-4-link",
                            className="button-link",
                        ),
                    ],
                    id="nav-links",
                ),
                html.Div(id="page-content"),
            ]
        )

        energia_layout = html.Div(
            [
                dcc.Loading(
                    id="dropdown-loading_inicio",
                    type="circle",
                    className="your-class-name",  # replace with your actual class name
                    children=[
                        html.Div(
                            [
                                inicio_energia,
                                html.Div(
                                    [
                                        html.Label(
                                            "Mes Consumo", className="label_mes_consumo"
                                        ),
                                        dropdown_mes_consumo,
                                    ],
                                    className="label_mes-y-dropdown",
                                ),
                                html.Div(
                                    [
                                        html.Label("Barra", className="label_barra"),
                                        dropdown_barra,
                                    ],
                                    className="label_barra-y-dropdown",
                                ),
                                html.Div(
                                    [
                                        html.Label(
                                            "Recaudador", className="label_recaudador"
                                        ),
                                        dropdown_recaudador,
                                    ],
                                    className="label_recaudador-y-dropdown",
                                ),
                                html.Div(
                                    [
                                        html.Label("Clave", className="label_clave"),
                                        dropdown_clave,
                                    ],
                                    className="label_clave-y-dropdown",
                                ),
                                html.Div(
                                    [
                                        html.Label("Tipo", className="label_tipo"),
                                        dropdown_tipo,
                                    ],
                                    className="label_tipo-y-dropdown",
                                ),
                            ]
                        ),
                    ],
                ),
                html.Div(
                    [
                        dcc.Loading(
                            id="loading_tipo_energia",
                            type="circle",
                            children=[tabla_revision_tipo_energia],
                        )
                    ],
                    className="tabla2",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        dcc.Loading(
                                            id="loading_energia",
                                            type="circle",
                                            children=[tabla_revision_energia],
                                            className="loading-container",
                                        )
                                    ],
                                    className="tabla1",
                                ),
                            ],
                            className="tabla_diferencias",
                        ),
                        grafico_energia,
                    ],
                    className="tabla_y_figura_1",
                ),
            ]
        )

        # ? Sistemas
        sistemas_layout = html.Div(
            [
                dcc.Loading(
                    id="dropdown_sistemas-loading_inicio",
                    type="circle",
                    className="your-class-name",  # replace with your actual class name
                    children=[
                        html.Div(
                            [
                                inicio_sistemas,
                                html.Div(
                                    [
                                        html.Label(
                                            "Mes Consumo", className="label_mes_consumo"
                                        ),
                                        dropdown_mes_consumo_sistemas,
                                    ],
                                    className="label_mes-y-dropdown",
                                ),
                                html.Div(
                                    [
                                        html.Label("Barra", className="label_barra"),
                                        dropdown_barra_sistemas,
                                    ],
                                    className="label_barra-y-dropdown",
                                ),
                                html.Div(
                                    [
                                        html.Label(
                                            "Recaudador", className="label_recaudador"
                                        ),
                                        dropdown_recaudador_sistemas,
                                    ],
                                    className="label_recaudador-y-dropdown",
                                ),
                                html.Div(
                                    [
                                        html.Label("Clave", className="label_clave"),
                                        dropdown_clave_sistemas,
                                    ],
                                    className="label_clave-y-dropdown",
                                ),
                                html.Div(
                                    [
                                        html.Label("Tipo", className="label_tipo"),
                                        dropdown_tipo_sistemas,
                                    ],
                                    className="label_tipo-y-dropdown",
                                ),
                            ]
                        ),
                    ],
                ),
                html.Div(
                    [
                        dcc.Loading(
                            id="loading_tipo_sistemas",
                            type="circle",
                            children=[tabla_revision_tipo_sistemas],
                        )
                    ],
                    className="tabla2",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        dcc.Loading(
                                            id="loading_sistemas",
                                            type="circle",
                                            children=[tabla_revision_sistemas],
                                            className="loading-container",
                                        )
                                    ],
                                    className="tabla1",
                                ),
                            ],
                            className="tabla_diferencias",
                        ),
                        grafico_sistemas,
                    ],
                    className="tabla_y_figura_1",
                ),
            ]
        )

        # ? Clientes Individualizados
        clientes_ind_layout = html.Div(
            [
                dcc.Loading(
                    id="dropdown_sistemas-loading_inicio",
                    type="circle",
                    className="your-class-name",  # replace with your actual class name
                    children=[
                        html.Div([inicio_cliente_individualizados]),
                    ],
                ),
                html.Div(
                    [
                        dcc.Loading(
                            id="loading_tipo_sistemas",
                            type="circle",
                            children=[tabla_revision_clientes_ind],
                        )
                    ],
                    className="tabla_clientes_ind",
                ),
            ]
        )

        # ? Energia Clientes Regulados
        energia_clientes_r_layout = html.Div(
            [
                dcc.Loading(
                    id="dropdown_clientes_r-loading_inicio",
                    type="circle",
                    className="your-class-name",  # replace with your actual class name
                    children=[
                        html.Div(
                            [
                                inicio_energia_clientes_r,
                                html.Div(
                                    [
                                        html.Label(
                                            "Mes Consumo", className="label_mes_consumo"
                                        ),
                                        dropdown_mes_consumo_clientes_r,
                                    ],
                                    className="label_mes-y-dropdown",
                                ),
                                html.Div(
                                    [
                                        html.Label(
                                            "Suministrador", className="label_barra"
                                        ),
                                        dropdown_suministrador_clientes_r,
                                    ],
                                    className="label_barra-y-dropdown",
                                ),
                            ]
                        ),
                    ],
                ),
                html.Div(
                    [
                        dcc.Loading(
                            id="loading_tipo_clientes_r",
                            type="circle",
                            children=[tabla_revision_energia_clientes_r],
                        )
                    ],
                    className="tabla_clientes_ind",
                ),
            ]
        )

        # ? Callbacks páginas
        # Pagina de la app
        @self.app.callback(Output("page-content", "children"), Input("url", "pathname"))
        def display_page(pathname):
            if pathname == "/page-1":
                return energia_layout
            elif pathname == "/page-2":
                return sistemas_layout
            elif pathname == "/page-3":
                return clientes_ind_layout
            elif pathname == "/page-4":
                return energia_clientes_r_layout

            else:
                return html.Div([])  # Empty Div for no match

        # ? Callbacks Revisor Energía
        # Mes consumo dropdown
        @self.app.callback(
            [
                Output("mes-consumo-dropdown_energia", "options"),
                Output("mes-consumo-dropdown_energia", "value"),
            ],
            [Input("mes-consumo-dropdown_energia", "value")],
        )
        def update_dropdown(selected_values):
            if selected_values:
                if "ALL" in selected_values:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_energia["Mes Consumo"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], ["ALL"]
                else:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_energia["Mes Consumo"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], [
                        value for value in selected_values if value != "ALL"
                    ]  # All options are displayed, selected values are selected
            else:
                return [
                    {"label": i, "value": i}
                    for i in df_combinado_energia["Mes Consumo"].unique()
                ] + [
                    {"label": "Select All", "value": "ALL"}
                ], selected_values  # Only "ALL" is displayed and selected

        @self.app.callback(
            [
                Output("barra-dropdown_energia", "options"),
                Output("barra-dropdown_energia", "value"),
            ],
            [Input("barra-dropdown_energia", "value")],
        )
        def update_dropdown(selected_values):
            if selected_values:
                if "ALL" in selected_values:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_energia["Barra"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], ["ALL"]
                else:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_energia["Barra"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], [
                        value for value in selected_values if value != "ALL"
                    ]  # All options are displayed, selected values are selected
            else:
                return [
                    {"label": i, "value": i}
                    for i in df_combinado_energia["Barra"].unique()
                ] + [
                    {"label": "Select All", "value": "ALL"}
                ], selected_values  # Only "ALL" is displayed and selected"""

        @self.app.callback(
            [
                Output("recaudador-dropdown_energia", "options"),
                Output("recaudador-dropdown_energia", "value"),
            ],
            [Input("recaudador-dropdown_energia", "value")],
        )
        def update_dropdown(selected_values):
            if selected_values:
                if "ALL" in selected_values:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_energia["Recaudador"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], ["ALL"]
                else:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_energia["Recaudador"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], [
                        value for value in selected_values if value != "ALL"
                    ]  # All options are displayed, selected values are selected
            else:
                return [
                    {"label": i, "value": i}
                    for i in df_combinado_energia["Recaudador"].unique()
                ] + [
                    {"label": "Select All", "value": "ALL"}
                ], selected_values  # Only "ALL" is displayed and selected

        @self.app.callback(
            [
                Output("clave-dropdown_energia", "options"),
                Output("clave-dropdown_energia", "value"),
            ],
            [Input("clave-dropdown_energia", "value")],
        )
        def update_dropdown(selected_values):
            if selected_values:
                if "ALL" in selected_values:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_energia["Clave"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], ["ALL"]
                else:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_energia["Clave"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], [
                        value for value in selected_values if value != "ALL"
                    ]  # All options are displayed, selected values are selected
            else:
                return [
                    {"label": i, "value": i}
                    for i in df_combinado_energia["Clave"].unique()
                ] + [
                    {"label": "Select All", "value": "ALL"}
                ], selected_values  # Only "ALL" is displayed and selected

        @self.app.callback(
            [
                Output("tipo-dropdown_energia", "options"),
                Output("tipo-dropdown_energia", "value"),
            ],
            [Input("tipo-dropdown_energia", "value")],
        )
        def update_dropdown(selected_values):
            if selected_values:
                if "ALL" in selected_values:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_energia["Tipo"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], ["ALL"]
                else:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_energia["Tipo"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], [
                        value for value in selected_values if value != "ALL"
                    ]  # All options are displayed, selected values are selected
            else:
                return [
                    {"label": i, "value": i}
                    for i in df_combinado_energia["Tipo"].unique()
                ] + [
                    {"label": "Select All", "value": "ALL"}
                ], selected_values  # Only "ALL" is displayed and selected

        @self.app.callback(
            Output("tabla_revision_energia", "data"),
            [
                Input("mes-consumo-dropdown_energia", "value"),
                Input("barra-dropdown_energia", "value"),
                Input("recaudador-dropdown_energia", "value"),
                Input("clave-dropdown_energia", "value"),
                Input("tipo-dropdown_energia", "value"),
            ],
        )
        def update_table(
            selected_mes_consumo,
            selected_barra,
            selected_recaudador,
            selected_clave,
            selected_tipo,
        ):
            if (
                selected_mes_consumo
                or selected_barra
                or selected_recaudador
                or selected_clave
                or selected_tipo
            ):
                if selected_mes_consumo == ["ALL"]:
                    selected_mes_consumo = (
                        df_combinado_energia["Mes Consumo"].unique().tolist()
                    )

                if selected_barra == ["ALL"]:
                    selected_barra = df_combinado_energia["Barra"].unique().tolist()

                if selected_recaudador == ["ALL"]:
                    selected_recaudador = (
                        df_combinado_energia["Recaudador"].unique().tolist()
                    )

                if selected_clave == ["ALL"]:
                    selected_clave = df_combinado_energia["Clave"].unique().tolist()

                if selected_tipo == ["ALL"]:
                    selected_tipo = df_combinado_energia["Tipo"].unique().tolist()

                df_combinado_filtrado = df_combinado_energia[
                    df_combinado_energia["Mes Consumo"].isin(selected_mes_consumo)
                    & df_combinado_energia["Barra"].isin(selected_barra)
                    & df_combinado_energia["Recaudador"].isin(selected_recaudador)
                    & df_combinado_energia["Clave"].isin(selected_clave)
                    & df_combinado_energia["Tipo"].isin(selected_tipo)
                ]

                columnas_a_modificar = [
                    "Energía Balance [kWh]",
                    "Energía Declarada [kWh]",
                    "Diferencia Energía [kWh]",
                ]  # replace with your column names

                for column in columnas_a_modificar:
                    df_combinado_filtrado.loc[:, column] = df_combinado_filtrado[
                        column
                    ].apply(
                        lambda x: "{:,.2f}".format(x)
                        .replace(",", " ")
                        .replace(".", ",")
                        .replace(" ", ".")
                    )

                df_combinado_filtrado.loc[:, "% Diferencia Energía"] = (
                    df_combinado_filtrado["% Diferencia Energía"].apply(
                        lambda x: "{:.2%}".format(x)
                    )
                )

                return df_combinado_filtrado.to_dict("records")
            else:
                return df_combinado_energia.to_dict("records")

        @self.app.callback(
            Output("tabla_revision_tipo_energia", "data"),
            [
                Input("mes-consumo-dropdown_energia", "value"),
                Input("recaudador-dropdown_energia", "value"),
            ],
        )
        def update_table(selected_mes_consumo, selected_recaudador):
            if selected_mes_consumo and selected_recaudador:
                if selected_mes_consumo == ["ALL"]:
                    selected_mes_consumo = (
                        df_combinado_energia["Mes Consumo"].unique().tolist()
                    )

                if selected_recaudador == ["ALL"]:
                    selected_recaudador = (
                        df_combinado_energia["Recaudador"].unique().tolist()
                    )

                df_combinado_filtrado = df_combinado_energia[
                    df_combinado_energia["Mes Consumo"].isin(selected_mes_consumo)
                    & df_combinado_energia["Recaudador"].isin(selected_recaudador)
                ]

                df_combinado_por_tipo_filtrado = (
                    df_combinado_filtrado.groupby(["Tipo"])
                    .agg({"Diferencia Energía [kWh]": "sum"})
                    .reset_index()
                )

                df_combinado_por_tipo_filtrado[
                    "Diferencia Energía [kWh]"
                ] = df_combinado_por_tipo_filtrado["Diferencia Energía [kWh]"].apply(
                    lambda x: "{:,.0f}".format(x)
                    .replace(",", " ")
                    .replace(".", ",")
                    .replace(" ", ".")
                )

                return df_combinado_por_tipo_filtrado.to_dict("records")
            else:
                return df_combinado_por_tipo_energia.to_dict("records")

        @self.app.callback(
            Output("grafico_diferencias_recaudadores_energia", "figure"),
            [
                Input("mes-consumo-dropdown_energia", "value"),
                Input("tipo-dropdown_energia", "value"),
            ],
        )
        def update_table(selected_mes_consumo, selected_tipo):
            if selected_mes_consumo:
                if selected_mes_consumo == ["ALL"]:
                    selected_mes_consumo = (
                        df_combinado_energia["Mes Consumo"].unique().tolist()
                    )

                if selected_tipo == ["ALL"]:
                    selected_tipo = df_combinado_energia["Tipo"].unique().tolist()

                df_combinado_filtrado = df_combinado_energia[
                    df_combinado_energia["Mes Consumo"].isin(selected_mes_consumo)
                    & df_combinado_energia["Tipo"].isin(selected_tipo)
                ]

                df_combinado_por_recaudador_filtrado = (
                    df_combinado_filtrado.groupby(["Recaudador"])
                    .agg({"Diferencia Energía [kWh]": "sum"})
                    .reset_index()
                )

                df_combinado_por_recaudador_filtrado = (
                    df_combinado_por_recaudador_filtrado.sort_values(
                        "Diferencia Energía [kWh]", ascending=False
                    )
                )

                fig_filtrada = px.bar(
                    df_combinado_por_recaudador_filtrado,
                    y="Recaudador",
                    x="Diferencia Energía [kWh]",
                    orientation="h",
                )
                return fig_filtrada
            else:
                fig = px.bar(
                    df_combinado_por_recaudador_energia,
                    y="Recaudador",
                    x="Diferencia Energía [kWh]",
                    orientation="h",
                )
                return fig

        # ? Callbacks Revisor Sistema

        # Mes consumo dropdown
        @self.app.callback(
            [
                Output("mes-consumo-dropdown_sistemas", "options"),
                Output("mes-consumo-dropdown_sistemas", "value"),
            ],
            [Input("mes-consumo-dropdown_sistemas", "value")],
        )
        def update_dropdown(selected_values):
            if selected_values:
                if "ALL" in selected_values:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_sistemas["Mes Consumo"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], ["ALL"]
                else:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_sistemas["Mes Consumo"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], [
                        value for value in selected_values if value != "ALL"
                    ]  # All options are displayed, selected values are selected
            else:
                return [
                    {"label": i, "value": i}
                    for i in df_combinado_sistemas["Mes Consumo"].unique()
                ] + [
                    {"label": "Select All", "value": "ALL"}
                ], selected_values  # Only "ALL" is displayed and selected

        @self.app.callback(
            [
                Output("barra-dropdown_sistemas", "options"),
                Output("barra-dropdown_sistemas", "value"),
            ],
            [Input("barra-dropdown_sistemas", "value")],
        )
        def update_dropdown(selected_values):
            if selected_values:
                if "ALL" in selected_values:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_sistemas["Barra"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], ["ALL"]
                else:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_sistemas["Barra"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], [
                        value for value in selected_values if value != "ALL"
                    ]  # All options are displayed, selected values are selected
            else:
                return [
                    {"label": i, "value": i}
                    for i in df_combinado_sistemas["Barra"].unique()
                ] + [
                    {"label": "Select All", "value": "ALL"}
                ], selected_values  # Only "ALL" is displayed and selected"""

        #

        @self.app.callback(
            [
                Output("recaudador-dropdown_sistemas", "options"),
                Output("recaudador-dropdown_sistemas", "value"),
            ],
            [Input("recaudador-dropdown_sistemas", "value")],
        )
        def update_dropdown(selected_values):
            if selected_values:
                if "ALL" in selected_values:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_sistemas["Recaudador"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], ["ALL"]
                else:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_sistemas["Recaudador"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], [
                        value for value in selected_values if value != "ALL"
                    ]  # All options are displayed, selected values are selected
            else:
                return [
                    {"label": i, "value": i}
                    for i in df_combinado_sistemas["Recaudador"].unique()
                ] + [
                    {"label": "Select All", "value": "ALL"}
                ], selected_values  # Only "ALL" is displayed and selected

        @self.app.callback(
            [
                Output("clave-dropdown_sistemas", "options"),
                Output("clave-dropdown_sistemas", "value"),
            ],
            [Input("clave-dropdown_sistemas", "value")],
        )
        def update_dropdown(selected_values):
            if selected_values:
                if "ALL" in selected_values:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_sistemas["Clave"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], ["ALL"]
                else:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_sistemas["Clave"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], [
                        value for value in selected_values if value != "ALL"
                    ]  # All options are displayed, selected values are selected
            else:
                return [
                    {"label": i, "value": i}
                    for i in df_combinado_sistemas["Clave"].unique()
                ] + [
                    {"label": "Select All", "value": "ALL"}
                ], selected_values  # Only "ALL" is displayed and selected

        @self.app.callback(
            [
                Output("tipo-dropdown_sistemas", "options"),
                Output("tipo-dropdown_sistemas", "value"),
            ],
            [Input("tipo-dropdown_sistemas", "value")],
        )
        def update_dropdown(selected_values):
            if selected_values:
                if "ALL" in selected_values:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_sistemas["Tipo"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], ["ALL"]
                else:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_sistemas["Tipo"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], [
                        value for value in selected_values if value != "ALL"
                    ]  # All options are displayed, selected values are selected
            else:
                return [
                    {"label": i, "value": i}
                    for i in df_combinado_sistemas["Tipo"].unique()
                ] + [
                    {"label": "Select All", "value": "ALL"}
                ], selected_values  # Only "ALL" is displayed and selected

        @self.app.callback(
            Output("tabla_revision_sistemas", "data"),
            [
                Input("mes-consumo-dropdown_sistemas", "value"),
                Input("barra-dropdown_sistemas", "value"),
                Input("recaudador-dropdown_sistemas", "value"),
                Input("clave-dropdown_sistemas", "value"),
                Input("tipo-dropdown_sistemas", "value"),
            ],
        )
        def update_table(
            selected_mes_consumo,
            selected_barra,
            selected_recaudador,
            selected_clave,
            selected_tipo,
        ):
            if (
                selected_mes_consumo
                or selected_barra
                or selected_recaudador
                or selected_clave
                or selected_tipo
            ):
                if selected_mes_consumo == ["ALL"]:
                    selected_mes_consumo = (
                        df_combinado_sistemas["Mes Consumo"].unique().tolist()
                    )

                if selected_barra == ["ALL"]:
                    selected_barra = df_combinado_sistemas["Barra"].unique().tolist()

                if selected_recaudador == ["ALL"]:
                    selected_recaudador = (
                        df_combinado_sistemas["Recaudador"].unique().tolist()
                    )

                if selected_clave == ["ALL"]:
                    selected_clave = df_combinado_sistemas["Clave"].unique().tolist()

                if selected_tipo == ["ALL"]:
                    selected_tipo = df_combinado_sistemas["Tipo"].unique().tolist()

                df_combinado_filtrado = df_combinado_sistemas[
                    df_combinado_sistemas["Mes Consumo"].isin(selected_mes_consumo)
                    & df_combinado_sistemas["Barra"].isin(selected_barra)
                    & df_combinado_sistemas["Recaudador"].isin(selected_recaudador)
                    & df_combinado_sistemas["Clave"].isin(selected_clave)
                    & df_combinado_sistemas["Tipo"].isin(selected_tipo)
                ]

                """ columnas_a_modificar = [
                    "Energía Balance [kWh]",
                    "Energía Declarada [kWh]",
                    "Diferencia Energía [kWh]",
                ]  # replace with your column names

                for column in columnas_a_modificar:
                    df_combinado_filtrado.loc[:, column] = df_combinado_filtrado[
                        column
                    ].apply(
                        lambda x: "{:,.2f}".format(x)
                        .replace(",", " ")
                        .replace(".", ",")
                        .replace(" ", ".")
                    )

                df_combinado_filtrado.loc[
                    :, "% Diferencia Energía"
                ] = df_combinado_filtrado["% Diferencia Energía"].apply(
                    lambda x: "{:.2%}".format(x)
                ) """

                return df_combinado_filtrado.to_dict("records")
            else:
                return df_combinado_sistemas.to_dict("records")

        @self.app.callback(
            Output("tabla_revision_tipo_sistemas", "data"),
            [
                Input("mes-consumo-dropdown_sistemas", "value"),
                Input("recaudador-dropdown_sistemas", "value"),
            ],
        )
        def update_table(selected_mes_consumo, selected_recaudador):
            if selected_mes_consumo and selected_recaudador:
                if selected_mes_consumo == ["ALL"]:
                    selected_mes_consumo = (
                        df_combinado_sistemas["Mes Consumo"].unique().tolist()
                    )

                if selected_recaudador == ["ALL"]:
                    selected_recaudador = (
                        df_combinado_sistemas["Recaudador"].unique().tolist()
                    )

                df_combinado_filtrado = df_combinado_sistemas[
                    df_combinado_sistemas["Mes Consumo"].isin(selected_mes_consumo)
                    & df_combinado_sistemas["Recaudador"].isin(selected_recaudador)
                ]

                df_combinado_por_tipo_filtrado = (
                    df_combinado_filtrado.groupby("Tipo")
                    .size()
                    .reset_index(name="Count")
                )

                """ df_combinado_por_tipo_filtrado[
                        "Diferencia Energía [kWh]"
                    ] = df_combinado_por_tipo_filtrado["Diferencia Energía [kWh]"].apply(
                        lambda x: "{:,.0f}".format(x)
                        .replace(",", " ")
                        .replace(".", ",")
                        .replace(" ", ".")
                    ) """

                return df_combinado_por_tipo_filtrado.to_dict("records")
            else:
                return df_combinado_por_tipo_sistemas.to_dict("records")

        @self.app.callback(
            Output("grafico_diferencias_recaudadores_sistemas", "figure"),
            [
                Input("mes-consumo-dropdown_sistemas", "value"),
                Input("tipo-dropdown_sistemas", "value"),
            ],
        )
        def update_table(selected_mes_consumo, selected_tipo):
            if selected_mes_consumo:
                if selected_mes_consumo == ["ALL"]:
                    selected_mes_consumo = (
                        df_combinado_sistemas["Mes Consumo"].unique().tolist()
                    )

                if selected_tipo == ["ALL"]:
                    selected_tipo = df_combinado_sistemas["Tipo"].unique().tolist()

                df_combinado_filtrado = df_combinado_sistemas[
                    df_combinado_sistemas["Mes Consumo"].isin(selected_mes_consumo)
                    & df_combinado_sistemas["Tipo"].isin(selected_tipo)
                ]

                df_combinado_por_recaudador_filtrado = (
                    df_combinado_filtrado.groupby("Recaudador")
                    .size()
                    .reset_index(name="Count")
                )

                df_combinado_por_recaudador_filtrado = (
                    df_combinado_por_recaudador_filtrado.sort_values(
                        "Count", ascending=False
                    )
                )

                fig_filtrada = px.bar(
                    df_combinado_por_recaudador_filtrado,
                    y="Recaudador",
                    x="Count",
                    orientation="h",
                )
                return fig_filtrada
            else:
                fig = px.bar(
                    df_combinado_por_recaudador_sistemas,
                    y="Recaudador",
                    x="Count",
                    orientation="h",
                )
                return fig

        # ? Callbacks Revisor Clientes Regualdos
        @self.app.callback(
            [
                Output("mes-consumo-dropdown_clientes_r", "options"),
                Output("mes-consumo-dropdown_clientes_r", "value"),
            ],
            [Input("mes-consumo-dropdown_clientes_r", "value")],
        )
        def update_dropdown(selected_values):
            if selected_values:
                if "ALL" in selected_values:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_energia_clientes_r["Mes"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], ["ALL"]
                else:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_energia_clientes_r["Mes"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], [
                        value for value in selected_values if value != "ALL"
                    ]  # All options are displayed, selected values are selected
            else:
                return [
                    {"label": i, "value": i}
                    for i in df_combinado_energia_clientes_r["Mes"].unique()
                ] + [
                    {"label": "Select All", "value": "ALL"}
                ], selected_values  # Only "ALL" is displayed and selected

        @self.app.callback(
            [
                Output("suministrador-dropdown_clientes_r", "options"),
                Output("suministrador-dropdown_clientes_r", "value"),
            ],
            [Input("suministrador-dropdown_clientes_r", "value")],
        )
        def update_dropdown(selected_values):
            if selected_values:
                if "ALL" in selected_values:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_energia_clientes_r[
                            "Suministrador"
                        ].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], ["ALL"]
                else:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_energia_clientes_r[
                            "Suministrador"
                        ].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], [
                        value for value in selected_values if value != "ALL"
                    ]  # All options are displayed, selected values are selected
            else:
                return [
                    {"label": i, "value": i}
                    for i in df_combinado_energia_clientes_r["Suministrador"].unique()
                ] + [
                    {"label": "Select All", "value": "ALL"}
                ], selected_values  # Only "ALL" is displayed and selected

        @self.app.callback(
            Output("tabla_revision_energia_clientes_r", "data"),
            [
                Input("mes-consumo-dropdown_clientes_r", "value"),
                Input("suministrador-dropdown_clientes_r", "value"),
            ],
        )
        def update_table(selected_mes_consumo, selected_recaudador):
            if selected_mes_consumo or selected_recaudador:
                if selected_mes_consumo == ["ALL"]:
                    selected_mes_consumo = (
                        df_combinado_energia_clientes_r["Mes"].unique().tolist()
                    )

                if selected_recaudador == ["ALL"]:
                    selected_recaudador = (
                        df_combinado_energia_clientes_r["Suministrador"]
                        .unique()
                        .tolist()
                    )

                df_combinado_filtrado = df_combinado_energia_clientes_r[
                    df_combinado_energia_clientes_r["Mes"].isin(selected_mes_consumo)
                    & df_combinado_energia_clientes_r["Suministrador"].isin(
                        selected_recaudador
                    )
                ]

                """ columnas_a_modificar = [
                    "Energía Balance [kWh]",
                    "Energía Declarada [kWh]",
                    "Diferencia Energía [kWh]",
                ]  # replace with your column names

                for column in columnas_a_modificar:
                    df_combinado_filtrado.loc[:, column] = df_combinado_filtrado[
                        column
                    ].apply(
                        lambda x: "{:,.2f}".format(x)
                        .replace(",", " ")
                        .replace(".", ",")
                        .replace(" ", ".")
                    )

                df_combinado_filtrado.loc[
                    :, "% Diferencia Energía"
                ] = df_combinado_filtrado["% Diferencia Energía"].apply(
                    lambda x: "{:.2%}".format(x)
                ) """

                return df_combinado_filtrado.to_dict("records")
            else:
                return df_combinado_energia_clientes_r.to_dict("records")

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
