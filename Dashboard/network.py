# Import libraries
from json import load
from .server import *
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Import styles
from .style import *

# ---DATA---
networks = ["IoTeX", "Polygon", "Ethereum", "Zilliqa"]

# ---COMPONENTS---
network = html.Div(
    [
        dbc.Row([
            dcc.Store(id='intermediate-value-in-0'),
            dcc.Store(id='intermediate-value-in-00'),
            dcc.Store(id='intermediate-value-in-000'),
            dcc.Store(id='intermediate-value-in-0000'),
            html.Div(id='in-load'),
            dbc.Col(html.Div(html.H3("Network Analytics"))),
        ]),
        dbc.Row([
            dcc.Checklist(
                id="checklist",
                options=[{"label": x, "value": x} 
                        for x in networks],
                value=networks[0:1],
                labelStyle={'display': 'inline-block', 'margin': '5px'}
            )
        ], style={'margin-left': '20px'}),
        dbc.Row(children=[
                dbc.Col(dcc.Graph(id="allTxns", style=GRAPHS), style=COLUMN),
                dbc.Col(dcc.Graph(id="uniqueAddresses", style=GRAPHS), style=COLUMN)
            ]
        ),
        dbc.Row(children=[
                dbc.Col(dcc.Graph(id="hourData", style=GRAPHS), style=COLUMN),
                dbc.Col(dcc.Graph(id="hourDataRecent", style=GRAPHS), style=COLUMN)
            ]
        ),
        dbc.Row(children=[
                dbc.Col(dcc.Graph(id="cummulativeNetworkFee", style=GRAPHS), style=COLUMN),
            ]
        ),
        dbc.Row(children=[
                dbc.Col(dcc.Graph(id="cummulativeGasUsed", style=GRAPHS), style=COLUMN),
            ]
        ),
        dbc.Row(children=[
                dbc.Col(dcc.Graph(id="networkStats1", style=GRAPHS), style=COLUMN),
                dbc.Col(dcc.Graph(id="networkStats2", style=GRAPHS), style=COLUMN)
            ]
        ),
    ]
)

@app.callback(
    Output('intermediate-value-in-0', 'data'),
    [dash.dependencies.Input('in-load', 'n_clicks')])
def update_output(n_clicks):
    txnsByDate = pd.read_csv('https://storage.googleapis.com/iotube/txnStatsByDate')
    return txnsByDate.to_json(date_format='iso', orient='split')

@app.callback(
    Output('intermediate-value-in-00', 'data'),
    [dash.dependencies.Input('in-load', 'n_clicks')])
def update_output(n_clicks):
    networkStats = pd.read_csv('https://storage.googleapis.com/iotube/networkStatsNew')
    print(networkStats.shape)
    return networkStats.to_json(date_format='iso', orient='split')

@app.callback(
    Output('intermediate-value-in-000', 'data'),
    [dash.dependencies.Input('in-load', 'n_clicks')])
def update_output(n_clicks):
    df = pd.read_csv('https://storage.googleapis.com/iotube/yearHourData')
    print(df.shape)
    return df.to_json(date_format='iso', orient='split')

@app.callback(
    Output('intermediate-value-in-0000', 'data'),
    [dash.dependencies.Input('in-load', 'n_clicks')])
def update_output(n_clicks):
    df = pd.read_csv('https://storage.googleapis.com/iotube/newHourData')
    print(df.shape)
    return df.to_json(date_format='iso', orient='split')
    
@app.callback(
    Output("allTxns", "figure"), 
    Input(component_id='checklist', component_property='value'),
    Input('intermediate-value-in-0', 'data'))
def update_line_chart(value, data):
    txnsByDate = pd.read_json(data, orient='split')

    mask = txnsByDate.Network.isin(value)
    fig = px.line(txnsByDate[mask], 
        x="Date", y="Transactions", color="Network",
        title="Daily Transactions")
    return fig

@app.callback(
    Output("uniqueAddresses", "figure"), 
    Input(component_id='checklist', component_property='value'),
    Input('intermediate-value-in-0', 'data'))
def update_line_chart(value, data):
    txnsByDate = pd.read_json(data, orient='split')
    
    mask = txnsByDate.Network.isin(value)
    fig = px.line(txnsByDate[mask], 
        x="Date", y="Addresses", color="Network",
        title="Daily Active Addresses (Unique)")
    return fig

@app.callback(
    Output("hourData", "figure"), 
    Input(component_id='checklist', component_property='value'),
    Input('intermediate-value-in-000', 'data'))
def update_line_chart(value, data):
    hourData = pd.read_json(data, orient='split')

    fig = px.bar(hourData, 
        x="Hour", y="NoOfActions", title="Hourly Action Count - Calendar Year",
            labels={
                "Hour": "Hour (UTC)",
            },
        )
    return fig

@app.callback(
    Output("hourDataRecent", "figure"), 
    Input(component_id='checklist', component_property='value'),
    Input('intermediate-value-in-0000', 'data'))
def update_line_chart(value, data):
    hourData = pd.read_json(data, orient='split')

    fig = px.bar(hourData, 
        x="Hour", y="NoOfActions", title="Hourly Action Count - Last 24 Hours", 
            labels={
                "Hour": "Hour (UTC)",
            },
        )
    return fig

@app.callback(
    Output("cummulativeNetworkFee", "figure"), 
    Input(component_id='checklist', component_property='value'),
    Input('intermediate-value-in-00', 'data'))
def update_line_chart(value, data):
    networkStats = pd.read_json(data, orient='split')
    
    mask = networkStats.Network.isin(value)
    fig = px.line(networkStats[mask], 
        x="Date", y="CummulativeTotalTxnFee", color="Network",
        title="2021 Cummulative Network Transaction Fees (in USD) [log scale]", log_y=True)
    return fig

@app.callback(
    Output("cummulativeGasUsed", "figure"), 
    Input(component_id='checklist', component_property='value'),
    Input('intermediate-value-in-00', 'data'))
def update_line_chart(value, data):
    networkStats = pd.read_json(data, orient='split')
    
    mask = networkStats.Network.isin(value)
    fig = px.line(networkStats[mask], 
        x="Date", y="CummulativeTotalGasUsed", color="Network",
        title="2021 Cummulative Total Gas Used [log scale]", log_y=True)
    return fig

@app.callback(
    Output("networkStats1", "figure"), 
    Input(component_id='checklist', component_property='value'),
    Input('intermediate-value-in-00', 'data'))
def update_line_chart(value, data):
    networkStats = pd.read_json(data, orient='split')
    
    fig = px.line(networkStats[networkStats["Network"] == "IoTeX"], 
        x="Date", y="AvgTxnFeeUSD", color="Network",
        title="Average Network Transation Fee (in USD)")
    return fig

@app.callback(
    Output("networkStats2", "figure"), 
    Input(component_id='checklist', component_property='value'),
    Input('intermediate-value-in-00', 'data'))
def update_line_chart(value, data):
    networkStats = pd.read_json(data, orient='split')
    
    mask = networkStats.Network.isin(value)

    fig = px.line(networkStats[mask], 
        x="Date", y="TotalTxnFeeUSD", color="Network",
        title="Total Network Transaction Fees (in USD)")
    return fig