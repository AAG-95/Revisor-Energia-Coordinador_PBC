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
        # region Inicialización de variables
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
        # endregion
        # Preprocess the data
        # region Diseño de Páginas
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
                "background-image": "url('/assets/paneles.png')",
                "background-size": "cover",
                "background-position": "center",
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
        # endregion

        # ? Diseño de Página Revisor de Energía
        # region Diseño Revisor de Energía
        # Preprocesamiento del dataframe
        # Convert 'Mes Consumo' to datetime if it's not already
        # region Procesamiento
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
        df_combinado_energia["Cantidad Registros"] = df_combinado_energia.groupby(
            "Tipo"
        )["Tipo"].transform("count")
        # endregion

        # region Tabla Resumen de Energía por Tipo
        # Original aggregation
        df_combinado_por_tipo_energia = (
            df_combinado_energia.groupby(["Tipo"])
            .agg(
                {
                    "Cantidad Registros": "first",
                    "Diferencia Energía [kWh]": "sum",
                    "Recaudación [$]": "sum",
                }
            )
            .reset_index()
        )

        # Aggregation by Tipo and Filtro_Registro_Clave
        df_combinado_filtro_clientes = (
            df_combinado_energia.groupby(["Tipo", "Filtro_Registro_Clave"])
            .size()  # This counts the number of occurrences
            .unstack(
                fill_value=0
            )  # Unstack to make Filtro_Registro_Clave values into columns, filling missing values with 0
        )

        # Join the two DataFrames
        df_combinado_por_tipo_energia = df_combinado_por_tipo_energia.join(
            df_combinado_filtro_clientes, on="Tipo"
        )

        df_combinado_por_tipo_energia["Porcentaje Registros [%]"] = (
            df_combinado_por_tipo_energia["Cantidad Registros"]
            / df_combinado_por_tipo_energia["Cantidad Registros"].sum()
            * 100
        )

        df_combinado_por_tipo_energia["Porcentaje Energía Dif [%]"] = (
            abs(df_combinado_por_tipo_energia["Diferencia Energía [kWh]"])
            / df_combinado_por_tipo_energia["Diferencia Energía [kWh]"].abs().sum()
            * 100
        )

        # Reordenar columnas
        df_combinado_por_tipo_energia = df_combinado_por_tipo_energia[
            [
                "Tipo",
                "Cantidad Registros",
                "Porcentaje Registros [%]",
                "Clientes Filtrados",
                "Clientes No Filtrados",
                "Diferencia Energía [kWh]",
                "Porcentaje Energía Dif [%]",
                "Recaudación [$]",
            ]
        ]

        df_combinado_energia.drop("Cantidad Registros", axis=1, inplace=True)

        # Revision De Clientes Filtrados de Energía

        #  thousands as dots
        columns_to_format = [
            "Diferencia Energía [kWh]",
            "Porcentaje Registros [%]",
            "Porcentaje Energía Dif [%]",
            "Recaudación [$]",
        ]

        for column in columns_to_format:
            df_combinado_por_tipo_energia[column] = df_combinado_por_tipo_energia[
                column
            ].apply(
                lambda x: "{:,.2f}".format(x)
                .replace(",", " ")
                .replace(".", ",")
                .replace(" ", ".")
            )
        # Tablas Revisor de Energía por tipo
        tabla_revision_tipo_energia = dash_table.DataTable(
            id="tabla_revision_tipo_energia",
            columns=[
                {"name": i, "id": i} for i in df_combinado_por_tipo_energia.columns
            ],
            data=df_combinado_por_tipo_energia.to_dict("records"),
        )
        # endregion

        # region Tabla Resumen de Energía
        # Tabla Revision detallada
        tabla_revision_energia = dash_table.DataTable(
            id="tabla_revision_energia",
            columns=[{"name": i, "id": i} for i in df_combinado_energia.columns],
            data=df_combinado_energia.to_dict("records"),
            hidden_columns=["mes_repartición"],
            export_format="csv",
            export_headers="display",
            css=[{"selector": ".export_button", "rule": "width: 100%;"}],
        )
        # endregion

        # ? Gráfico diferencias por Recaudador
        # region Gráfico diferencias por Recaudador
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
        # endregion

        # ? Gráfico diferencias por Recaudador y Mes Consumo
        # region Gráfico diferencias por Recaudador y Mes Consumo
        df_combinado_por_recaudador_mes = (
            df_combinado_energia.groupby(["Recaudador", "Mes Consumo"])
            .agg({"Diferencia Energía [kWh]": "sum"})
            .reset_index()
        )

        df_combinado_por_recaudador_mes = df_combinado_por_recaudador_mes.sort_values(
            ["Recaudador", "Mes Consumo"], ascending=[True, True]
        )

        fig_energia_mes = px.bar(
            df_combinado_por_recaudador_mes,
            y="Recaudador",
            x="Diferencia Energía [kWh]",
            color="Mes Consumo",
            orientation="h",
        )
        grafico_energia_mes = dcc.Graph(
            id="grafico_diferencias_recaudadores_mes_energia",
            figure=fig_energia_mes,
            className="grafico_recaudadores_mes",
        )
        # endregion

        # region Dropdowns
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
        # endregion
        # endregion
        # ? Diseño de Página Revisor de Sistemas
        # region Diseño Revisor de Sistemas
        # Preprocesamiento del dataframe
        # Convert 'Mes Consumo' to datetime if it's not already
        # region Procesamiento
        df_combinado_sistemas["Mes Consumo"] = pd.to_datetime(
            df_combinado_sistemas["Mes Consumo"]
        )

        # Sort the DataFrame by 'Mes Consumo'
        df_combinado_sistemas = df_combinado_sistemas.sort_values("Mes Consumo")

        # Ensure "Mes Consumo" is of datetime type
        df_combinado_sistemas["Mes Consumo"] = pd.to_datetime(
            df_combinado_sistemas["Mes Consumo"], format="%d-%m-%Y"
        )

        # Change column format to Ene-2023
        df_combinado_sistemas["Mes Consumo"] = df_combinado_sistemas[
            "Mes Consumo"
        ].apply(lambda x: self.meses_esp[x.day] + "-" + str(x.year))

        # Preprocesamiento del dataframe
        # Convert 'mes_repartición' to datetime if it's not already
        df_combinado_sistemas["mes_repartición"] = pd.to_datetime(
            df_combinado_sistemas["mes_repartición"]
        )

        """ # Sort the DataFrame by 'mes_repartición'
        df_combinado_sistemas = df_combinado_sistemas.sort_values("mes_repartición") """

        # Ensure "mes_repartición" is of datetime type
        df_combinado_sistemas["mes_repartición"] = pd.to_datetime(
            df_combinado_sistemas["mes_repartición"], format="%d-%m-%Y"
        )

        # Change column format to Ene-2023
        df_combinado_sistemas["mes_repartición"] = df_combinado_sistemas[
            "mes_repartición"
        ].apply(lambda x: self.meses_esp[x.day] + "-" + str(x.year))
        # endregion

        # Agrupar por tipo y obtener cantidad de errores
        # region Tabla Resumen de Sistemas
        df_combinado_por_tipo_sistemas = (
            df_combinado_sistemas.groupby("Tipo")
            .agg(
                Cantidad_Registros=("Tipo", "size"),
                Diferencia_Recaudacion_Sistema_y_NT_Sum=(
                    "Diferencia Recaudación Sistema y NT [$]",
                    "sum",
                ),
                Energia=("Energía [kWh]", "sum"),
            )
            .reset_index()
        )

        # Rename columns to replace underscores with spaces
        df_combinado_por_tipo_sistemas = df_combinado_por_tipo_sistemas.rename(
            columns={
                "Cantidad_Registros": "Cantidad Registros",
                "Diferencia_Recaudacion_Sistema_y_NT_Sum": "Diferencia Recaudacion Sistema y NT [$]",
                "Energia": "Energía [kWh]",
            }
        )

        df_combinado_por_tipo_sistemas["Porcentaje Registros [%]"] = (
            df_combinado_por_tipo_sistemas["Cantidad Registros"]
            / df_combinado_por_tipo_sistemas["Cantidad Registros"].sum()
            * 100
        )

        df_combinado_por_tipo_sistemas["Porcentaje Energía [%]"] = (
            abs(df_combinado_por_tipo_sistemas["Energía [kWh]"])
            / df_combinado_por_tipo_sistemas["Energía [kWh]"].abs().sum()
            * 100
        )

        columns_to_format = [
            "Porcentaje Energía [%]",
            "Porcentaje Registros [%]",
            "Energía [kWh]",
            "Diferencia Recaudacion Sistema y NT [$]",
        ]

        for column in columns_to_format:
            df_combinado_por_tipo_sistemas[column] = df_combinado_por_tipo_sistemas[
                column
            ].apply(
                lambda x: "{:,.2f}".format(x)
                .replace(",", " ")
                .replace(".", ",")
                .replace(" ", ".")
            )

        # Tablas Revisor de Energía
        tabla_revision_tipo_sistemas = dash_table.DataTable(
            id="tabla_revision_tipo_sistemas",
            columns=[
                {"name": i, "id": i} for i in df_combinado_por_tipo_sistemas.columns
            ],
            data=df_combinado_por_tipo_sistemas.to_dict("records"),
        )
        # endregion

        # Revision general
        # region Tabla Resumen de Sistemas
        tabla_revision_sistemas = dash_table.DataTable(
            id="tabla_revision_sistemas",
            columns=[{"name": i, "id": i} for i in df_combinado_sistemas.columns],
            data=df_combinado_sistemas.to_dict("records"),
            export_format="csv",
            export_headers="display",
            css=[{"selector": ".export_button", "rule": "width: 100%;"}],
        )
        # endregion

        # Gráfico diferencias por Recaudador
        # region Gráfico diferencias por Recaudador
        df_combinado_por_recaudador_sistemas = (
            df_combinado_sistemas.groupby(["Recaudador"])
            .size()
            .reset_index(name="Cantidad Registros")
        )

        df_combinado_por_recaudador_sistemas = (
            df_combinado_por_recaudador_sistemas.sort_values(
                "Cantidad Registros", ascending=False
            )
        )

        # Assuming df_combinado_por_tipo is your DataFrame and 'Tipo' and 'Diferencia Energía [kWh]' are your columns
        fig_sistemas = px.bar(
            df_combinado_por_recaudador_sistemas,
            y="Recaudador",
            x="Cantidad Registros",
            orientation="h",
        )
        grafico_sistemas = dcc.Graph(
            id="grafico_diferencias_recaudadores_sistemas",
            figure=fig_sistemas,
            className="grafico_recaudadores",
        )
        # endregion

        # region Dropdowns
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
        # endregion
        # endregion
        # ? Diseño de Página Revisor de Clientes Individualizados
        # region Diseño Revisor de Clientes Individualizados
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
        # endregion
        # ? Diseño de Página Revisor de Energia Clientes Regulados
        # region Diseño Revisor de Energía Clientes Regulados
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

        # Generate the dropdown_sistemas options
        dropdown_tipo_clientes_r = dcc.Dropdown(
            id="tipo-dropdown_clientes_r",
            options=[
                {"label": i, "value": i}
                for i in df_combinado_energia_clientes_r["Tipo"].unique()
            ]
            + [{"label": "Select All", "value": "ALL"}],
            value=["ALL"],
            multi=True,
            className="dropdown_tipo_sistemas",
            style={"width": "100%"},
        )
        # endregion
        #! Layout--------------------------------------------------------------------------------------
        # region Layout
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
                    className="button-link_energia_libres",
                ),
                dcc.Link(
                    "Revisor de Sistemas Zonales",
                    href="/page-2",
                    id="page-2-link",
                    className="button-link_sistemas",
                ),
                dcc.Link(
                    "Revisor de Clientes Individualizados",
                    href="/page-3",
                    id="page-3-link",
                    className="button-link_clientes_ind",
                ),
                dcc.Link(
                    "Revisor de Energía Clientes Regulados",
                    href="/page-4",
                    id="page-4-link",
                    className="button-link_energia_regulados",
                ),
            ],
            id="nav-links",
            style={
                "backgroundImage": "url('/assets/paneles.png')",  # Path to your PNG file
                "backgroundSize": "cover",  # Ensure the image covers the entire div
                "backgroundRepeat": "no-repeat",  # Prevent the image from repeating
                "height": "80px",  # Set the height of the div to the full viewport height
                "width": "100%",  # Ensure the div takes the full width of its container
            },
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
                    children=[
                        html.Div(
                            dcc.Loading(
                                id="loading_tipo_energia_1",
                                type="circle",
                                children=[tabla_revision_tipo_energia],
                                style={"flex": "1", "marginRight": "100px"},
                            ),
                            className="tabla2",
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justifyContent": "center",  # Center horizontally
                        "alignItems": "center",  # Center vertically
                        "transform": "translateX(-79px)",  # Shift everything slightly left
                        "marginBottom": "20px",
                    },
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

                html.Div(
                    [
                        grafico_energia_mes,
                    ],
                    className="figura_1",
                ),
              
            ],
            className="diseño_pagina_energia",
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
                                html.Div(
                                    [
                                        html.Label("Tipo", className="label_tipo"),
                                        dropdown_tipo_clientes_r,
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
                            id="loading_tipo_clientes_r",
                            type="circle",
                            children=[tabla_revision_energia_clientes_r],
                        )
                    ],
                    className="tabla_clientes_ind",
                ),
            ]
        )
        # endregion

        # ? Callbacks páginas
        # region Callbacks Páginas
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

        # endregion

        # ? Callbacks Revisor Energía
        # region Revisor Energía
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

        # region Tabla Revision Energía
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
                    "Porcentaje_No_Inf_y_Dif_por_Clave",
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
                    df_combinado_filtrado.loc[:, "% Diferencia Energía"].apply(
                        lambda x: "{:.2%}".format(x)
                    )
                )

                return df_combinado_filtrado.to_dict("records")
            else:
                return df_combinado_energia.to_dict("records")

        # endregion

        # region Tabla Revision Resumen Tipo Energía
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

                # Revision por Tipo

                df_combinado_filtrado["Cantidad Registros"] = (
                    df_combinado_filtrado.groupby("Tipo")["Tipo"].transform("count")
                )

                df_combinado_por_tipo_filtrado = (
                    df_combinado_filtrado.groupby(["Tipo"])
                    .agg(
                        {
                            "Diferencia Energía [kWh]": "sum",
                            "Recaudación [$]": "sum",
                            "Cantidad Registros": "first",
                        }
                    )
                    .reset_index()
                )

                # Filtro en Base a la columna "Filtro_Registro_Clave"
                df_combinado_por_tipo_y_filtro_cliente = (
                    df_combinado_filtrado.groupby(["Tipo", "Filtro_Registro_Clave"])
                    .size()
                    .unstack(fill_value=0)
                )

                df_combinado_por_tipo_filtrado = df_combinado_por_tipo_filtrado.join(
                    df_combinado_por_tipo_y_filtro_cliente, on="Tipo"
                )

                df_combinado_por_tipo_filtrado["Porcentaje Registros [%]"] = (
                    df_combinado_por_tipo_filtrado["Cantidad Registros"]
                    / df_combinado_por_tipo_filtrado["Cantidad Registros"].sum()
                    * 100
                )

                df_combinado_por_tipo_filtrado["Porcentaje Energía Dif [%]"] = (
                    abs(df_combinado_por_tipo_filtrado["Diferencia Energía [kWh]"])
                    / df_combinado_por_tipo_filtrado["Diferencia Energía [kWh]"]
                    .abs()
                    .sum()
                    * 100
                )

                # Ordenar Columnas
                df_combinado_por_tipo_filtrado = df_combinado_por_tipo_filtrado[
                    [
                        "Tipo",
                        "Cantidad Registros",
                        "Porcentaje Registros [%]",
                        "Clientes Filtrados",
                        "Clientes No Filtrados",
                        "Diferencia Energía [kWh]",
                        "Porcentaje Energía Dif [%]",
                        "Recaudación [$]",
                    ]
                ]

                #  thousands as dots
                columnas_nuevo_formato = [
                    "Porcentaje Registros [%]",
                    "Porcentaje Energía Dif [%]",
                    "Diferencia Energía [kWh]",
                    "Recaudación [$]",
                ]

                for column in columnas_nuevo_formato:
                    df_combinado_por_tipo_filtrado[
                        column
                    ] = df_combinado_por_tipo_filtrado[column].apply(
                        lambda x: "{:,.2f}".format(x)
                        .replace(",", " ")
                        .replace(".", ",")
                        .replace(" ", ".")
                    )

                return df_combinado_por_tipo_filtrado.to_dict("records")
            else:
                return df_combinado_por_tipo_energia.to_dict("records")

        # endregion

        # region Gráfico Diferencias por Recaudador
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

        # endregion
        # endregion

        # ? Callbacks Revisor Sistema
        # region Callbacks Revisor Sistemas
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

        # region Tabla Revision Sistemas
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

                columnas_a_modificar = [
                    "Energía [kWh]",
                    "Diferencia Recaudación Sistema y NT [$]",
                    "Recaudación Sistema y NT Según Barra [$]",
                    "Recaudación Sistema y NT Informado [$]",
                    "Cargo Acumulado Sistema y NT Informado",
                    "Cargo Acumulado Sistema y NT Según Barra",
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

                """ df_combinado_filtrado.loc[
                    :, "% Diferencia Energía"
                ] = df_combinado_filtrado["% Diferencia Energía"].apply(
                    lambda x: "{:.2%}".format(x)
                ) """

                return df_combinado_filtrado.to_dict("records")
            else:
                return df_combinado_sistemas.to_dict("records")

        # endregion

        # region Tabla Revision Resumen Tipo Sistemas
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
                    .agg(
                        Cantidad_Registros=("Tipo", "size"),
                        Diferencia_Recaudacion_Sistema_y_NT_Sum=(
                            "Diferencia Recaudación Sistema y NT [$]",
                            "sum",
                        ),
                        Energia=("Energía [kWh]", "sum"),
                    )
                    .reset_index()
                )
                # Rename columns to replace underscores with spaces
                df_combinado_por_tipo_filtrado = df_combinado_por_tipo_filtrado.rename(
                    columns={
                        "Cantidad_Registros": "Cantidad Registros",
                        "Diferencia_Recaudacion_Sistema_y_NT_Sum": "Diferencia Recaudacion Sistema y NT [$]",
                        "Energia": "Energía [kWh]",
                    }
                )

                df_combinado_por_tipo_filtrado["Porcentaje Registros [%]"] = (
                    df_combinado_por_tipo_filtrado["Cantidad Registros"]
                    / df_combinado_por_tipo_filtrado["Cantidad Registros"].sum()
                    * 100
                )

                df_combinado_por_tipo_filtrado["Porcentaje Energía [%]"] = (
                    df_combinado_por_tipo_filtrado["Energía [kWh]"]
                    / df_combinado_por_tipo_filtrado["Energía [kWh]"].sum()
                    * 100
                )

                columns_to_format = [
                    "Porcentaje Energía [%]",
                    "Porcentaje Registros [%]",
                    "Energía [kWh]",
                    "Diferencia Recaudacion Sistema y NT [$]",
                ]

                for column in columns_to_format:
                    df_combinado_por_tipo_filtrado[
                        column
                    ] = df_combinado_por_tipo_filtrado[column].apply(
                        lambda x: "{:,.2f}".format(x)
                        .replace(",", " ")
                        .replace(".", ",")
                        .replace(" ", ".")
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

        # endregion

        # region Gráfico Diferencias por Recaudador
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
                    .reset_index(name="Cantidad Registros")
                )

                df_combinado_por_recaudador_filtrado = (
                    df_combinado_por_recaudador_filtrado.sort_values(
                        "Cantidad Registros", ascending=False
                    )
                )

                fig_filtrada = px.bar(
                    df_combinado_por_recaudador_filtrado,
                    y="Recaudador",
                    x="Cantidad Registros",
                    orientation="h",
                )
                return fig_filtrada
            else:
                fig = px.bar(
                    df_combinado_por_recaudador_sistemas,
                    y="Recaudador",
                    x="Cantidad Registros",
                    orientation="h",
                )
                return fig

        # endregion
        # endregion

        # ? Callbacks Revisor Clientes Regualdos
        # region Callbacks Clientes Regulados
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
            [
                Output("tipo-dropdown_clientes_r", "options"),
                Output("tipo-dropdown_clientes_r", "value"),
            ],
            [Input("tipo-dropdown_clientes_r", "value")],
        )
        def update_dropdown(selected_values):
            if selected_values:
                if "ALL" in selected_values:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_energia_clientes_r["Tipo"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], ["ALL"]
                else:
                    return [
                        {"label": i, "value": i}
                        for i in df_combinado_energia_clientes_r["Tipo"].unique()
                    ] + [{"label": "Select All", "value": "ALL"}], [
                        value for value in selected_values if value != "ALL"
                    ]  # All options are displayed, selected values are selected
            else:
                return [
                    {"label": i, "value": i}
                    for i in df_combinado_energia_clientes_r["Tipo"].unique()
                ] + [
                    {"label": "Select All", "value": "ALL"}
                ], selected_values  # Only "ALL" is displayed and selected

        # region Tabla Revision Energía Clientes Regulados
        @self.app.callback(
            Output("tabla_revision_energia_clientes_r", "data"),
            [
                Input("mes-consumo-dropdown_clientes_r", "value"),
                Input("suministrador-dropdown_clientes_r", "value"),
                Input("tipo-dropdown_clientes_r", "value"),
            ],
        )
        def update_table(selected_mes_consumo, selected_recaudador, selected_tipo):
            if selected_mes_consumo or selected_recaudador or selected_tipo:
                if selected_mes_consumo == ["ALL"]:
                    selected_mes_consumo = (
                        df_combinado_energia_clientes_r["Mes"].unique().tolist()
                    )
                print("ss")
                if selected_recaudador == ["ALL"]:
                    selected_recaudador = (
                        df_combinado_energia_clientes_r["Suministrador"]
                        .unique()
                        .tolist()
                    )

                if selected_tipo == ["ALL"]:
                    selected_tipo = (
                        df_combinado_energia_clientes_r["Tipo"].unique().tolist()
                    )

                df_combinado_filtrado = df_combinado_energia_clientes_r[
                    df_combinado_energia_clientes_r["Mes"].isin(selected_mes_consumo)
                    & df_combinado_energia_clientes_r["Suministrador"].isin(
                        selected_recaudador
                    )
                    & df_combinado_energia_clientes_r["Tipo"].isin(selected_tipo)
                ]

                columnas_a_modificar = [
                    "Energía Balance [kWh]",
                    "Energía facturada [kWh]",
                    "Diferencia Energía [kWh]",
                ]  # replace with your column names

                for column in columnas_a_modificar:
                    df_combinado_filtrado.loc[:, column] = df_combinado_filtrado[
                        column
                    ].apply(
                        lambda x: "{:,.0f}".format(x)
                        .replace(",", " ")
                        .replace(".", ",")
                        .replace(" ", ".")
                    )

                return df_combinado_filtrado.to_dict("records")
            else:
                return df_combinado_energia_clientes_r.to_dict("records")

    # endregion
    # endregion

    # region Función Abrir Navegador
    def open_browser(self):
        # Abre el navegador web para visualizar la aplicación
        debug_mode = self.app.server.debug
        run_main = os.environ.get
        ("WERKZEUG_RUN_MAIN") == "true"
        if not debug_mode or run_main:
            webbrowser.get().open_new(f"http://localhost:{self.port}")

    # endregion

    # region Función Run
    def run(self):
        # Inicia la aplicación Dash y abre el navegador
        Timer(1, self.open_browser).start()
        self.app.run_server(debug=False, port=self.port)

    # endregion
