from flask import Flask
import pandas as pd
from dash import Dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from pandas.core.frame import DataFrame
import os

# Create the Dash app
app = Dash(external_stylesheets=[dbc.themes.FLATLY])
server = app.server
app.title = 'iOTube Analytics'