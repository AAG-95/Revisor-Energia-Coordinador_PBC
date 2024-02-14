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
    def __init__(self, df_combinado_energia, df_combinado_sistemas, port=8052):
        self.port = port
        self.df_combinado_energia = df_combinado_energia
        self.df_combinado_sistemas = df_combinado_sistemas
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

        #? Diseño de Página Revisor de Energía

        # Revision por Tipo 
        df_combinado_por_tipo = (
            df_combinado_energia.groupby(["Tipo"])
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
        
        tabla_revision_tipo_energia = dash_table.DataTable(
            id="tabla_revision_tipo_energia",
            columns=[{"name": i, "id": i} for i in df_combinado_por_tipo.columns],
            data=df_combinado_por_tipo.to_dict("records"),
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

        for value in df_combinado_energia["Mes Consumo"].unique():
            self.df_dict[value] = df_combinado_energia[df_combinado_energia["Mes Consumo"] == value]

        # Convert 'Mes Consumo' to datetime if it's not already
        df_combinado_energia["Mes Consumo"] = pd.to_datetime(df_combinado_energia["Mes Consumo"])

        # Sort the DataFrame by 'Mes Consumo'
        df_combinado_energia = df_combinado_energia.sort_values("Mes Consumo")

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
        df_combinado_energia["Mes Consumo"] = pd.to_datetime(
            df_combinado_energia["Mes Consumo"], format="%d-%m-%Y"
        )

        # Change column format to Ene-2023
        df_combinado_energia["Mes Consumo"] = df_combinado_energia["Mes Consumo"].apply(
            lambda x: meses_esp[x.day] + "-" + str(x.year)
        )
        

        # Gráfico diferencias por Recaudador
        df_combinado_por_recaudador = (
            df_combinado_energia.groupby(["Recaudador"])
            .agg({"Diferencia Energía [kWh]": "sum"})
            .reset_index()
        )

        df_combinado_por_recaudador = df_combinado_por_recaudador.sort_values(
            "Diferencia Energía [kWh]", ascending=False
        )

        # Assuming df_combinado_por_tipo is your DataFrame and 'Tipo' and 'Diferencia Energía [kWh]' are your columns
        fig = px.bar(
            df_combinado_por_recaudador,
            y="Recaudador",
            x="Diferencia Energía [kWh]",
            orientation="h",
        )
        grafico = dcc.Graph(
            id="grafico_diferencias_recaudadores",
            figure=fig,
            className="grafico_recaudadores",
        )

        # Generate the dropdown options
        dropdown_mes_consumo = dcc.Dropdown(
            id="mes-consumo-dropdown",
            options=[
                {"label": i, "value": i} for i in df_combinado_energia["Mes Consumo"].unique()
            ]
            + [{"label": "Select All", "value": "ALL"}],
            value=["ALL"],
            multi=True,
            className="dropdown_mes_consumo",
            style={"width": "100%"},
        )

        # Generate the dropdown options
        dropdown_barra = dcc.Dropdown(
            id="barra-dropdown",
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
            id="recaudador-dropdown",
            options=[
                {"label": i, "value": i} for i in df_combinado_energia["Recaudador"].unique()
            ]
            + [{"label": "Select All", "value": "ALL"}],
            value=["ALL"],
            multi=True,
            className="dropdown_recaudador",
            style={"width": "100%"},
        )

        # Generate the dropdown options
        dropdown_clave = dcc.Dropdown(
            id="clave-dropdown",
            options=[{"label": i, "value": i} for i in df_combinado_energia["Clave"].unique()]
            + [{"label": "Select All", "value": "ALL"}],
            value=["ALL"],
            multi=True,
            className="dropdown_clave",
            style={"width": "100%"},
        )

        # Generate the dropdown options
        dropdown_tipo = dcc.Dropdown(
            id="tipo-dropdown",
            options=[{"label": i, "value": i} for i in df_combinado_energia["Tipo"].unique()]
            + [{"label": "Select All", "value": "ALL"}],
            value=["ALL"],
            multi=True,
            className="dropdown_tipo",
            style={"width": "100%"},
        )

        #? Diseño de Página Revisor de Sistemas



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
                       html.Label("Barra", className="label_barra"),
                        dropdown_barra,
                    ],
                   className="label_barra-y-dropdown",
                ), 

                html.Div(
                    [
                        html.Label("Recaudador", className="label_recaudador"),
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
    ]
),
        html.Div(
            [
                dcc.Loading(
                    id="loading2",
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
                                    id="loading",
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
                Output("barra-dropdown", "options"),
                Output("barra-dropdown", "value"),
            ],
            [Input("barra-dropdown", "value")],
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
        #

        
        @self.app.callback(
            [
                Output("recaudador-dropdown", "options"),
                Output("recaudador-dropdown", "value"),
            ],
            [Input("recaudador-dropdown", "value")],
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
                Output("clave-dropdown", "options"),
                Output("clave-dropdown", "value"),
            ],
            [Input("clave-dropdown", "value")],
        )
        def update_dropdown(selected_values):
            if selected_values:
                if "ALL" in selected_values:
                    return [
                        {"label": i, "value": i} for i in df_combinado_energia["Clave"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], ["ALL"]
                else:
                    return [
                        {"label": i, "value": i} for i in df_combinado_energia["Clave"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], [
                        value for value in selected_values if value != "ALL"
                    ]  # All options are displayed, selected values are selected
            else:
                return [
                    {"label": i, "value": i} for i in df_combinado_energia["Clave"].unique()
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
                        {"label": i, "value": i} for i in df_combinado_energia["Tipo"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], ["ALL"]
                else:
                    return [
                        {"label": i, "value": i} for i in df_combinado_energia["Tipo"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], [
                        value for value in selected_values if value != "ALL"
                    ]  # All options are displayed, selected values are selected
            else:
                return [
                    {"label": i, "value": i} for i in df_combinado_energia["Tipo"].unique()
                ] + [
                    {"label": "Select All", "value": "ALL"}
                ], selected_values  # Only "ALL" is displayed and selected





        @self.app.callback(
            Output("tabla_revision_energia", "data"),
            [
                Input("mes-consumo-dropdown", "value"),
                Input("barra-dropdown", "value"),
                Input("recaudador-dropdown", "value"),
                Input("clave-dropdown", "value"),
                Input("tipo-dropdown", "value"),
            ],
        )
        def update_table(
            selected_mes_consumo, selected_barra, selected_recaudador, selected_clave, selected_tipo
        ):
            if (
                selected_mes_consumo
                or selected_barra
                or selected_recaudador
                or selected_clave
                or selected_tipo
            ):
                if selected_mes_consumo == ["ALL"]:
                    selected_mes_consumo = df_combinado_energia["Mes Consumo"].unique().tolist()

                if selected_barra == ["ALL"]:
                      selected_barra = df_combinado_energia["Barra"].unique().tolist()
                
                if selected_recaudador == ["ALL"]:
                    selected_recaudador =  df_combinado_energia["Recaudador"].unique().tolist()
                    

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

                df_combinado_filtrado.loc[
                    :, "% Diferencia Energía"
                ] = df_combinado_filtrado["% Diferencia Energía"].apply(
                    lambda x: "{:.2%}".format(x)
                )

                return df_combinado_filtrado.to_dict("records")
            else:
                return df_combinado_energia.to_dict("records")

        @self.app.callback(
            Output("tabla_revision_tipo_energia", "data"),
            [
                Input("mes-consumo-dropdown", "value"),
                Input("recaudador-dropdown", "value"),
            ],
        )
        def update_table(selected_mes_consumo, selected_recaudador):
            if selected_mes_consumo and selected_recaudador:
                if selected_mes_consumo == ["ALL"]:
                    selected_mes_consumo = df_combinado_energia["Mes Consumo"].unique().tolist()

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
                return df_combinado_por_tipo.to_dict("records")

        @self.app.callback(
            Output("grafico_diferencias_recaudadores", "figure"),
            [Input("mes-consumo-dropdown", "value"), Input("tipo-dropdown", "value")],
        )
        def update_table(selected_mes_consumo, selected_tipo):
            if selected_mes_consumo:
                if selected_mes_consumo == ["ALL"]:
                    selected_mes_consumo = df_combinado_energia["Mes Consumo"].unique().tolist()

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
                    df_combinado_por_recaudador,
                    y="Recaudador",
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
