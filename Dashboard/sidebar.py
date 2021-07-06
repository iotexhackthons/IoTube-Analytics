# Import libraries
from .server import app
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Import styles
from .style import *

# ---COMPONENTS---
IOTUBE_LOGO = "https://tube.iotex.io/static/media/logo_iotube.81e6aa74.svg"

buttons = dbc.Row(
    [
        dbc.NavLink("Network Overview", href="/", active="exact", style=NAVLINK),
        dbc.NavLink("Bridge Analytics", href="/crossChain", active="exact", style=NAVLINK),
        dbc.NavLink("Bridge Token Transfer Analytics", href="/crossChainTokens", active="exact", style=NAVLINK),
    ],
    no_gutters=True,
    className="ml-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)

navbar = dbc.Navbar([
    html.A(
        # Use row and col to control vertical alignment of logo / brand
        dbc.Row(
            [
                dbc.Col(html.Img(src=IOTUBE_LOGO, height="30px")),
                dbc.Col(dbc.NavbarBrand("Analytics", className="ml-2")),
            ],
            align="center",
            no_gutters=True,
        ), 
        href="/",
    ),
    dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
    dbc.Collapse(
        buttons, id="navbar-collapse", navbar=True, is_open=False
    ),
], color="#3B3B3B", dark=True, style=NAVBAR_STYLE, sticky="top")

content = html.Div(id="page-content", style=CONTENT_STYLE)