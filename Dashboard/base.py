# Import libraries
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from .server import app

# Import sub-layouts
from .sidebar import *
from .network import *
from .crossChain import *
from .crossChainTokens import *

# Import styles
from .style import *

# ---COMPONENTS---
app.layout = html.Div([
    dcc.Location(id="url"), 
    html.Div(navbar), 
    html.Div(content)
])

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return html.Div(network)
    elif pathname == "/crossChain":
        return html.Div(crossChain)
    elif pathname == "/crossChainTokens":
        return html.Div(crossChainTokens)

    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )