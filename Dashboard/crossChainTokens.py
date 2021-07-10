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
import plotly.graph_objects as go

# Import styles
from .style import *

# ---COMPONENTS---

# Load the dataset
def loadData():
    tokens = pd.read_csv('https://storage.googleapis.com/iotube/bridgeInflowToken')
    tokensAndPeriod = pd.read_csv('https://storage.googleapis.com/iotube/bridgeInflowTokenPeriod')
    return tokens, tokensAndPeriod

def loadDataOut():
    tokens = pd.read_csv('https://storage.googleapis.com/iotube/bridgeOutflowToken')
    tokensAndPeriod = pd.read_csv('https://storage.googleapis.com/iotube/bridgeOutflowTokenPeriod')
    return tokens, tokensAndPeriod

def filter(tokens, inDf):    
    mask = inDf["Token Symbol"].isin(tokens)
    inDf = inDf[mask]

    return inDf

networks = ["Polygon", "BSC", "Ethereum"]
tokens = ["CYC", "IOTX", "WETH", "BUSD", "WBNB", "UNI", "WMATIC", "PAXG", "WBTC", "AAVE", "DAI", "USDC", "QUICK"]
tokensTypes = ["Volume", "Frequency", 'Average Value', 'Median']

crossChainTokens = html.Div(
    [
        dbc.Row(dbc.Col(html.Div(html.H3("Bridge Token Analytics", style=HEADING)))),
        dbc.Row([
            html.H5("Tokens to consider:", style=TEXT),
            dbc.Col(dcc.Checklist(
                        id="token-select",
                        options=[{"label": x, "value": x} 
                                for x in tokens],
                        value=tokens[0:3],
                        labelStyle={'display': 'inline-block', 'margin': '5px'}
                )),
        ], style={'margin-left': '10px'}),
        dbc.Row(
            [
                dbc.Col(html.Div(children=[
                    dcc.Store(id='intermediate-value-in-2'),
                    dcc.Store(id='intermediate-value-in-3'),
                    dcc.Store(id='intermediate-value-in-4'),
                    dcc.Store(id='intermediate-value-in-5'),
                    html.Div(id='in-load'),
                    html.Div(id='out-load'),
                    
                    dcc.Graph(id='token-graph', figure={'layout': go.Layout(paper_bgcolor='#262525', plot_bgcolor='#262525')}, style=COLUMNFULL),
                    dcc.Graph(id='token-graph-out', figure={'layout': go.Layout(paper_bgcolor='#262525', plot_bgcolor='#262525')}, style=COLUMNFULL),
                    
                    dbc.Col(dcc.Dropdown(id='token-type-select',
                    options=[{'label': i, 'value': i}
                            for i in tokensTypes],
                    value='Volume')),

                    dcc.Graph(id='token-area', figure={'layout': go.Layout(paper_bgcolor='#262525', plot_bgcolor='#262525')}, style=COLUMNFULL),
                    dcc.Graph(id='token-area-out', figure={'layout': go.Layout(paper_bgcolor='#262525', plot_bgcolor='#262525')}, style=COLUMNFULL),
                    
                    html.H5("Select network and parameter for chain-specific statistics:", style=TEXTMARGIN),
                    dbc.Row([
                        dbc.Col(dcc.Dropdown(id='type-select',
                        options=[{'label': i, 'value': i}
                                for i in tokensTypes],
                        value='Volume')),
                        dbc.Col(dcc.Dropdown(id='network-select',
                            options=[{'label': i, 'value': i}
                                    for i in networks],
                            value='BSC')),
                    ], style={'margin-top': '10px', 'margin-bottom': '20px'}),
                    

                    dcc.Graph(id='token-area-network', figure={'layout': go.Layout(paper_bgcolor='#262525', plot_bgcolor='#262525')}, style=COLUMNFULL),
                    dcc.Graph(id='token-area-network-out', figure={'layout': go.Layout(paper_bgcolor='#262525', plot_bgcolor='#262525')}, style=COLUMNFULL),
                ])),
            ]
        ),
    ]
)

@app.callback(
    Output('intermediate-value-in-2', 'data'),
    [dash.dependencies.Input('in-load', 'n_clicks')])
def update_output(n_clicks):
    tokens, _ = loadData()
    return tokens.to_json(date_format='iso', orient='split')

@app.callback(
    Output('intermediate-value-in-3', 'data'),
    [dash.dependencies.Input('in-load', 'n_clicks')])
def update_output(n_clicks):
    _, period = loadData()
    return period.to_json(date_format='iso', orient='split')

@app.callback(
    Output('intermediate-value-in-4', 'data'),
    [dash.dependencies.Input('out-load', 'n_clicks')])
def update_output(n_clicks):
    tokens, _ = loadDataOut()
    return tokens.to_json(date_format='iso', orient='split')

@app.callback(
    Output('intermediate-value-in-5', 'data'),
    [dash.dependencies.Input('out-load', 'n_clicks')])
def update_output(n_clicks):
    _, period = loadDataOut()
    return period.to_json(date_format='iso', orient='split')

# Frequency of token transfers by date
@app.callback(
    Output("token-graph", "figure"), 
    Input('intermediate-value-in-3', 'data'))
def update_line_chart(dfIn):
    df = pd.read_json(dfIn, orient='split')

    vendors = df['Token Symbol']
    regions = df.Network
    count = df['Frequency'].values
    dates = df['Date'].values

    df = pd.DataFrame(
        dict(vendors=vendors, regions=regions, dates=dates, count=count)
    )

    df["all"] = "all" # in order to have a single root node

    fig = px.treemap(df, path=['all', 'regions', 'dates', 'vendors'], 
                    values='count', title="Frequency of transactions to IoTeX via IoTube by token used by date (click to interact)",
                    template='plotly_dark').update_layout(
        {'plot_bgcolor': '#262525', 'paper_bgcolor': '#262525'})
    return fig

@app.callback(
    Output("token-graph-out", "figure"), 
    Input('intermediate-value-in-5', 'data'))
def update_line_chart(dfIn):
    df = pd.read_json(dfIn, orient='split')

    vendors = df['Token Symbol']
    regions = df.Network
    count = df['Frequency'].values
    dates = df['Date'].values

    df = pd.DataFrame(
        dict(vendors=vendors, regions=regions, dates=dates, count=count)
    )

    df["all"] = "all" # in order to have a single root node

    fig = px.treemap(df, path=['all', 'regions', 'dates', 'vendors'], 
                    values='count', title="Frequency of transactions from IoTeX to other chain via IoTube by token used by date (click to interact)",
                    template='plotly_dark').update_layout(
        {'plot_bgcolor': '#262525', 'paper_bgcolor': '#262525'})
    return fig

# Token stats
@app.callback(
    Output("token-area", "figure"), 
    Input(component_id='token-select', component_property='value'), 
    Input(component_id='token-type-select', component_property='value'),
    Input('intermediate-value-in-2', 'data'))
def update_line_chart(tokens, type, dfIn):
    dfIn = pd.read_json(dfIn, orient='split')

    grouped = filter(tokens, dfIn)

    fig = px.bar(grouped, 
            x=grouped['Date'], 
            y=grouped[type], 
            color=grouped['Token Symbol'], log_y=True,
    title="{} of transfers into IoTeX by Token (log scale)".format(type), template='plotly_dark').update_layout(
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

@app.callback(
    Output("token-area-out", "figure"), 
    Input(component_id='token-select', component_property='value'), 
    Input(component_id='token-type-select', component_property='value'),
    Input('intermediate-value-in-4', 'data'))
def update_line_chart(tokens, type, dfIn):
    dfIn = pd.read_json(dfIn, orient='split')

    grouped = filter(tokens, dfIn)

    fig = px.bar(grouped, 
            x=grouped['Date'], 
            y=grouped[type], 
            color=grouped['Token Symbol'], log_y=True,
    title="{} of transfers from IoTeX by Token (log scale)".format(type), template='plotly_dark').update_layout(
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

# Token stats network
@app.callback(
    Output("token-area-network", "figure"), 
    Input(component_id='token-select', component_property='value'), 
    Input(component_id='type-select', component_property='value'),
    Input(component_id='network-select', component_property='value'),
    Input('intermediate-value-in-3', 'data'))
def update_line_chart(tokens, type, network, dfIn):
    dfIn = pd.read_json(dfIn, orient='split')

    grouped = filter(tokens, dfIn)
    grouped = grouped[grouped["Network"] == network]
    fig = px.area(grouped, 
            x=grouped['Date'], 
            y=grouped[type], 
            color=grouped['Token Symbol'], log_y=True,
    title="{} of transfers from {} into IoTeX by Token (log scale)".format(type, network), template='plotly_dark').update_layout(
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

# Token stats network outflow
@app.callback(
    Output("token-area-network-out", "figure"), 
    Input(component_id='token-select', component_property='value'), 
    Input(component_id='type-select', component_property='value'),
    Input(component_id='network-select', component_property='value'),
    Input('intermediate-value-in-5', 'data'))
def update_line_chart(tokens, type, network, dfIn):
    dfIn = pd.read_json(dfIn, orient='split')

    grouped = filter(tokens, dfIn)
    grouped = grouped[grouped["Network"] == network]
    fig = px.area(grouped, 
            x=grouped['Date'], 
            y=grouped[type], 
            color=grouped['Token Symbol'], log_y=True,
    title="{} of transfers from IoTeX to {} by Token (log scale)".format(type, network), template='plotly_dark').update_layout(
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
