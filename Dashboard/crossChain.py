# Import libraries
from json import load
from os import defpath
from .server import *
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Import styles
from .style import *

# ---COMPONENTS---

# Load and filter the dataset
def loadData():
    df = pd.read_csv('https://storage.googleapis.com/iotube/bridgeInflow')
    return df

def filter(value, inDf):
    mask = inDf.Network.isin(value)
    inDf = inDf[mask]

    return inDf

networks = ["Polygon", "BSC", "Ethereum"]

crossChain = html.Div(
    [
        dbc.Row(dbc.Col(html.Div(html.H3("Bridge Analytics", style=HEADING)))),
        dbc.Row([
            html.H5("Compare with:", style=TEXT),
            dcc.Checklist(
                id="bridge-select",
                options=[{"label": x, "value": x} 
                        for x in networks],
                value=networks[0:2],
                labelStyle={'display': 'inline-block', 'margin': '5px'}
            )
        ], style={'margin-left': '10px'}),
        dbc.Row(
            [
                dbc.Col(html.Div(children=[
                    dcc.Store(id='intermediate-value-in'),
                    dcc.Store(id='intermediate-value-out'),
                    dbc.Row([
                        dbc.Col(children=[
                            html.Div(id='in-load', n_clicks=0),
                        ]),
                    ]),
                    
                    dcc.Graph(id='price-graph', figure={'layout': go.Layout(paper_bgcolor='#262525', plot_bgcolor='#262525')}, style=COLUMNFULL),
                    # dcc.Graph(id='price-graph-out')
                ])),
            ]
        ),
        dbc.Row(children=[
                dbc.Col(dcc.Graph(id="uniqueUsers", style=GRAPHS, figure={'layout': go.Layout(paper_bgcolor='#262525', plot_bgcolor='#262525')}), style=COLUMN),
                dbc.Col(dcc.Graph(id="averageValue", style=GRAPHS, figure={'layout': go.Layout(paper_bgcolor='#262525', plot_bgcolor='#262525')}), style=COLUMN)
            ]
        ),
    ]
)

# Load data
@app.callback(
    Output('intermediate-value-in', 'data'),
    [dash.dependencies.Input('in-load', 'n_clicks')])
def update_output(n_clicks):
    if(n_clicks == 0):
        dfIn = loadData()
        n_clicks = n_clicks+1
        return dfIn.to_json(date_format='iso', orient='split')

# Inflow Volume
@app.callback(
    Output("price-graph", "figure"), 
    Input(component_id='bridge-select', component_property='value'),
    Input('intermediate-value-in', 'data'))
def update_line_chart(value, dfIn):
    dfInflow = pd.read_json(dfIn, orient='split')
    dfInflow = filter(value, dfInflow)

    fig = px.area(dfInflow, 
            x=dfInflow['Date'], 
            y=dfInflow['Volume'], 
            color=dfInflow['Network'],
            color_discrete_sequence=["goldenrod", "#8147E5", "red"],
       title="Bridge volume inflow to IoTeX (Log Scale)", log_y=True, template='plotly_dark').update_layout(
        {'plot_bgcolor': '#262525', 'paper_bgcolor': '#262525'})
    fig.update_xaxes(
    rangeslider_visible=True,
    rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(step="all")
            ])
        )
    )
    return fig

# Unique users inflow
@app.callback(
    Output("uniqueUsers", "figure"), 
    Input(component_id='bridge-select', component_property='value'),
    Input('intermediate-value-in', 'data'))
def update_line_chart(value, dfIn):
    dfPolygonIn = pd.read_json(dfIn, orient='split')
    dfPolygonInGrouped = filter(value, dfPolygonIn)

    fig = px.bar(dfPolygonInGrouped, 
            x=dfPolygonInGrouped['Date'], 
            y=dfPolygonInGrouped['Unique Addresses'], 
            color=dfPolygonInGrouped['Bridge'],
            color_discrete_sequence=["#8147E5", "red", "goldenrod"],
       title="Unique users count transferring to IoTeX", template='plotly_dark').update_layout(
        {'plot_bgcolor': '#262525', 'paper_bgcolor': '#262525'})
    fig.update_xaxes(
    rangeslider_visible=True,
    rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(step="all")
            ])
        )
    )
    return fig

# Average transfer volume inflow
@app.callback(
    Output("averageValue", "figure"), 
    Input(component_id='bridge-select', component_property='value'),
    Input('intermediate-value-in', 'data'))
def update_line_chart(value, dfIn):
    dfPolygonIn = pd.read_json(dfIn, orient='split')

    dfPolygonInGrouped = filter(value, dfPolygonIn)

    fig = px.bar(dfPolygonInGrouped, 
            x=dfPolygonInGrouped['Date'], 
            y=dfPolygonInGrouped['Average Transfer Volume'], 
            color=dfPolygonInGrouped['Bridge'], 
            color_discrete_sequence=["#8147E5", "red", "goldenrod"],
       title="Average transfer volume per user into IoTeX", template='plotly_dark').update_layout(
        {'plot_bgcolor': '#262525', 'paper_bgcolor': '#262525'})
    fig.update_xaxes(
    rangeslider_visible=True,
    rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(step="all")
            ])
        )
    )
    return fig