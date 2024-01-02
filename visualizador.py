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
    def __init__(self, df_combinado, port=8052):
        self.port = port
        self.df_combinado = df_combinado
        self.app = dash.Dash(__name__)
        # Preprocess the data
        self.df_dict = {}

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

        table = dash_table.DataTable(
            id="table",
            columns=[{"name": i, "id": i} for i in df_combinado.columns],
            data=df_combinado.to_dict("records"),
            export_format="csv",
            export_headers="display",
            css=[{"selector": ".export_button", "rule": "width: 100%;"}],
        )

        df_combinado_por_tipo = (
            df_combinado.groupby(["Tipo"])
            .agg({"Diferencia Energía [kWh]": "sum"})
            .reset_index()
        )

        #  thousands as dots
        df_combinado_por_tipo["Diferencia Energía [kWh]"] = df_combinado_por_tipo[
            "Diferencia Energía [kWh]"
        ].apply(
            lambda x: "{:,}".format(x)
            .replace(",", " ")
            .replace(".", ",")
            .replace(" ", ".")
        )

        table2 = dash_table.DataTable(
            id="table2",
            columns=[{"name": i, "id": i} for i in df_combinado_por_tipo.columns],
            data=df_combinado_por_tipo.to_dict("records"),
        )

        for value in df_combinado["Mes Consumo"].unique():
            self.df_dict[value] = df_combinado[df_combinado["Mes Consumo"] == value]

        # Convert 'Mes Consumo' to datetime if it's not already
        df_combinado["Mes Consumo"] = pd.to_datetime(df_combinado["Mes Consumo"])

        # Sort the DataFrame by 'Mes Consumo'
        df_combinado = df_combinado.sort_values("Mes Consumo")

        # Spanish month abbreviations
        meses_esp = [
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

        # Ensure "Mes Consumo" is of datetime type
        df_combinado["Mes Consumo"] = pd.to_datetime(
            df_combinado["Mes Consumo"], format="%d-%m-%Y"
        )

        # Change column format to Ene-2023
        df_combinado["Mes Consumo"] = df_combinado["Mes Consumo"].apply(
            lambda x: meses_esp[x.day] + "-" + str(x.year)
        )

        df_combinado_por_suministrador = (
            df_combinado.groupby(["Suministrador"])
            .agg({"Diferencia Energía [kWh]": "sum"})
            .reset_index()
        )

        df_combinado_por_suministrador = df_combinado_por_suministrador.sort_values(
            "Diferencia Energía [kWh]", ascending=False
        )

        # Assuming df_combinado_por_tipo is your DataFrame and 'Tipo' and 'Diferencia Energía [kWh]' are your columns
        fig = px.bar(
            df_combinado_por_suministrador,
            y="Suministrador",
            x="Diferencia Energía [kWh]",
            orientation="h",
        )
        grafico = dcc.Graph(
            id="grafico_diferencias_suministradores",
            figure=fig,
            className="grafico_suministradores",
        )

        # Generate the dropdown options
        dropdown_mes_consumo = dcc.Dropdown(
            id="mes-consumo-dropdown",
            options=[
                {"label": i, "value": i} for i in df_combinado["Mes Consumo"].unique()
            ]
            + [{"label": "Select All", "value": "ALL"}],
            value=["ALL"],
            multi=True,
            className="dropdown_mes_consumo",
            style={"width": "100%"},
        )

        # Generate the dropdown options
        dropdown_suministrador = dcc.Dropdown(
            id="suministrador-dropdown",
            options=[
                {"label": i, "value": i} for i in df_combinado["Suministrador"].unique()
            ]
            + [{"label": "Select All", "value": "ALL"}],
            value=["ALL"],
            multi=True,
            className="dropdown_suministrador",
            style={"width": "100%"},
        )

        # Generate the dropdown options
        dropdown_clave = dcc.Dropdown(
            id="clave-dropdown",
            options=[{"label": i, "value": i} for i in df_combinado["Clave"].unique()]
            + [{"label": "Select All", "value": "ALL"}],
            value=["ALL"],
            multi=True,
            className="dropdown_clave",
            style={"width": "100%"},
        )

        # Generate the dropdown options
        dropdown_tipo = dcc.Dropdown(
            id="tipo-dropdown",
            options=[{"label": i, "value": i} for i in df_combinado["Tipo"].unique()]
            + [{"label": "Select All", "value": "ALL"}],
            value=["ALL"],
            multi=True,
            className="dropdown_tipo",
            style={"width": "100%"},
        )

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
                    ],
                    id="nav-links",
                ),
                html.Div(id="page-content"),
            ]
        )

        page_1_layout = html.Div([ dcc.Loading(
    id="dropdown-loading_inicio",
    type="circle",
    className="your-class-name",  # replace with your actual class name
    children=[
        html.Div(
            [
                blue_square,
                html.Div(
                    [
                        html.Label("Mes Consumo", className="label_mes_consumo"),
                        dropdown_mes_consumo,
                    ],
                    className="label_mes-y-dropdown",
                ),
                html.Div(
                    [
                        html.Label("Suministrador", className="label_suministrador"),
                        dropdown_suministrador,
                    ],
                    className="label_suministrador-y-dropdown",
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
    ]
),
        html.Div(
            [
                dcc.Loading(
                    id="loading2",
                    type="circle",
                    children=[table2],
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
                                    id="loading",
                                    type="circle",
                                    children=[table],
                                    className="loading-container",
                                )
                            ],
                            className="tabla1",
                        ),
                    ],
                    className="tabla_diferencias",
                ),
                grafico,
            ],
            className="tabla_y_figura_1",
        ),])

        page_2_layout = html.Div(
            [
                html.H1("Page 2"),
            ]
        )

        # Pagina de la app
        @self.app.callback(Output("page-content", "children"), Input("url", "pathname"))
        def display_page(pathname):
            if pathname == "/page-1":
                return page_1_layout
            elif pathname == "/page-2":
                return page_2_layout
            else:
                return html.Div([])  # Empty Div for no match

        # Mes consumo dropdown

        @self.app.callback(
            [
                Output("mes-consumo-dropdown", "options"),
                Output("mes-consumo-dropdown", "value"),
            ],
            [Input("mes-consumo-dropdown", "value")],
        )
        def update_dropdown(selected_values):
            if selected_values:
                if "ALL" in selected_values:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado["Mes Consumo"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], ["ALL"]
                else:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado["Mes Consumo"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], [
                        value for value in selected_values if value != "ALL"
                    ]  # All options are displayed, selected values are selected
            else:
                return [
                    {"label": i, "value": i}
                    for i in df_combinado["Mes Consumo"].unique()
                ] + [
                    {"label": "Select All", "value": "ALL"}
                ], selected_values  # Only "ALL" is displayed and selected

        @self.app.callback(
            [
                Output("suministrador-dropdown", "options"),
                Output("suministrador-dropdown", "value"),
            ],
            [Input("suministrador-dropdown", "value")],
        )
        def update_dropdown(selected_values):
            if selected_values:
                if "ALL" in selected_values:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado["Suministrador"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], ["ALL"]
                else:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado["Suministrador"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], [
                        value for value in selected_values if value != "ALL"
                    ]  # All options are displayed, selected values are selected
            else:
                return [
                    {"label": i, "value": i}
                    for i in df_combinado["Suministrador"].unique()
                ] + [
                    {"label": "Select All", "value": "ALL"}
                ], selected_values  # Only "ALL" is displayed and selected

        @self.app.callback(
            [
                Output("clave-dropdown", "options"),
                Output("clave-dropdown", "value"),
            ],
            [Input("clave-dropdown", "value")],
        )
        def update_dropdown(selected_values):
            if selected_values:
                if "ALL" in selected_values:
                    return [
                        {"label": i, "value": i} for i in df_combinado["Clave"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], ["ALL"]
                else:
                    return [
                        {"label": i, "value": i} for i in df_combinado["Clave"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], [
                        value for value in selected_values if value != "ALL"
                    ]  # All options are displayed, selected values are selected
            else:
                return [
                    {"label": i, "value": i} for i in df_combinado["Clave"].unique()
                ] + [
                    {"label": "Select All", "value": "ALL"}
                ], selected_values  # Only "ALL" is displayed and selected

        @self.app.callback(
            [
                Output("tipo-dropdown", "options"),
                Output("tipo-dropdown", "value"),
            ],
            [Input("tipo-dropdown", "value")],
        )
        def update_dropdown(selected_values):
            if selected_values:
                if "ALL" in selected_values:
                    return [
                        {"label": i, "value": i} for i in df_combinado["Tipo"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], ["ALL"]
                else:
                    return [
                        {"label": i, "value": i} for i in df_combinado["Tipo"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], [
                        value for value in selected_values if value != "ALL"
                    ]  # All options are displayed, selected values are selected
            else:
                return [
                    {"label": i, "value": i} for i in df_combinado["Tipo"].unique()
                ] + [
                    {"label": "Select All", "value": "ALL"}
                ], selected_values  # Only "ALL" is displayed and selected

        @self.app.callback(
            Output("table", "data"),
            [
                Input("mes-consumo-dropdown", "value"),
                Input("suministrador-dropdown", "value"),
                Input("clave-dropdown", "value"),
                Input("tipo-dropdown", "value"),
            ],
        )
        def update_table(
            selected_mes_consumo, selected_suministrador, selected_clave, selected_tipo
        ):
            if (
                selected_mes_consumo
                or selected_suministrador
                or selected_clave
                or selected_tipo
            ):
                if selected_mes_consumo == ["ALL"]:
                    selected_mes_consumo = df_combinado["Mes Consumo"].unique().tolist()

                if selected_suministrador == ["ALL"]:
                    selected_suministrador = (
                        df_combinado["Suministrador"].unique().tolist()
                    )

                if selected_clave == ["ALL"]:
                    selected_clave = df_combinado["Clave"].unique().tolist()

                if selected_tipo == ["ALL"]:
                    selected_tipo = df_combinado["Tipo"].unique().tolist()

                print(selected_mes_consumo)
                print(df_combinado["Mes Consumo"].unique().tolist())
                df_combinado_filtrado = df_combinado[
                    df_combinado["Mes Consumo"].isin(selected_mes_consumo)
                    & df_combinado["Suministrador"].isin(selected_suministrador)
                    & df_combinado["Clave"].isin(selected_clave)
                    & df_combinado["Tipo"].isin(selected_tipo)
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

                df_combinado_filtrado.loc[
                    :, "% Diferencia Energía"
                ] = df_combinado_filtrado["% Diferencia Energía"].apply(
                    lambda x: "{:.2%}".format(x)
                )

                return df_combinado_filtrado.to_dict("records")
            else:
                return df_combinado.to_dict("records")

        @self.app.callback(
            Output("table2", "data"),
            [
                Input("mes-consumo-dropdown", "value"),
                Input("suministrador-dropdown", "value"),
            ],
        )
        def update_table(selected_mes_consumo, selected_suministrador):
            if selected_mes_consumo and selected_suministrador:
                if selected_mes_consumo == ["ALL"]:
                    print(df_combinado["Mes Consumo"])

                    selected_mes_consumo = df_combinado["Mes Consumo"].unique().tolist()

                if selected_suministrador == ["ALL"]:
                    selected_suministrador = (
                        df_combinado["Suministrador"].unique().tolist()
                    )

                df_combinado_filtrado = df_combinado[
                    df_combinado["Mes Consumo"].isin(selected_mes_consumo)
                    & df_combinado["Suministrador"].isin(selected_suministrador)
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
                return df_combinado_por_tipo.to_dict("records")

        @self.app.callback(
            Output("grafico_diferencias_suministradores", "figure"),
            [Input("mes-consumo-dropdown", "value"), Input("tipo-dropdown", "value")],
        )
        def update_table(selected_mes_consumo, selected_tipo):
            if selected_mes_consumo:
                if selected_mes_consumo == ["ALL"]:
                    selected_mes_consumo = df_combinado["Mes Consumo"].unique().tolist()

                if selected_tipo == ["ALL"]:
                    selected_tipo = df_combinado["Tipo"].unique().tolist()

                df_combinado_filtrado = df_combinado[
                    df_combinado["Mes Consumo"].isin(selected_mes_consumo)
                    & df_combinado["Tipo"].isin(selected_tipo)
                ]

                df_combinado_por_suministrador_filtrado = (
                    df_combinado_filtrado.groupby(["Suministrador"])
                    .agg({"Diferencia Energía [kWh]": "sum"})
                    .reset_index()
                )

                df_combinado_por_suministrador_filtrado = (
                    df_combinado_por_suministrador_filtrado.sort_values(
                        "Diferencia Energía [kWh]", ascending=False
                    )
                )

                fig_filtrada = px.bar(
                    df_combinado_por_suministrador_filtrado,
                    y="Suministrador",
                    x="Diferencia Energía [kWh]",
                    orientation="h",
                )
                return fig_filtrada
            else:
                fig = px.bar(
                    df_combinado_por_suministrador,
                    y="Suministrador",
                    x="Diferencia Energía [kWh]",
                    orientation="h",
                )
                return fig

    page_1_layout = html.Div(
        [
            html.H1("Page 1"),
        ]
    )

    page_2_layout = html.Div(
        [
            html.H1("Page 2"),
        ]
    )

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
