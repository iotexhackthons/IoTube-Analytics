# Import libraries
import pandas as pd
from google_auth_oauthlib import flow
from google.cloud import bigquery
from google.cloud import bigquery_storage
from google.oauth2 import service_account
from google.cloud import storage
import requests
import json
import csv



# Google Cloud Setup
SERVICE_ACCOUNT_FILE = 'key.json'
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
bqclient = bigquery.Client(project='iotube-analytics', credentials=credentials)
bqstorageclient = bigquery_storage.BigQueryReadClient(credentials=credentials)


# API Setup
COVALENT_KEY = "ckey_10446544a51944ffa7c6603a9e4"
chain = {
    "Polygon": 137,
    "Ethereum": 1,
    "BSC": 56
}
validator = {
    "Polygon": "0xFBe9A4138AFDF1fA639a8c2818a0C4513fc4CE4B",
    "Ethereum": "0xd8165188ccc135b3a3b2a5d2bc3af9d94753d955",
    "BSC": "0x116404F86e97846110EA08cd52fC2882d4AD3123"
}
cashier = {
    "Polygon": "0xf72CFb704d49aC7BB7FFa420AE5f084C671A29be",
    "Ethereum": "0xa0fd7430852361931b23a31f84374ba3314e1682",
    "BSC": "0x797f1465796fd89ea7135e76dbc7cdb136bba1ca"
}



# Network Level Base Statistics on a hourly level
def getHourData():
    '''
    Returns actions count by hour - yearly and last 24 hours
    '''
    
    query_string = """SELECT COUNT(*) as NoOfActions, 
    EXTRACT(HOUR FROM timestamp) as Hour
    FROM `public-data-finance.crypto_iotex.actions` 
    GROUP BY Hour
    ORDER BY Hour
    """
    yearHourData = (
        bqclient.query(query_string)
        .result()
        .to_dataframe(bqstorage_client=bqstorageclient)
    )

    upload_blob("iotube", yearHourData.to_csv(), "yearHourData")

    query_string = """
    SELECT COUNT(*) as NoOfActions, 
    EXTRACT(HOUR FROM timestamp) as Hour
    FROM `public-data-finance.crypto_iotex.actions` 
    WHERE DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
    GROUP BY Hour
    ORDER BY Hour
    """
    newHourData = (
        bqclient.query(query_string)
        .result()
        .to_dataframe(bqstorage_client=bqstorageclient)
    )

    upload_blob("iotube", newHourData.to_csv(), "newHourData")



# Inflow Bridge Data
def getBridgeDataIn(network):
    '''
    Gets inflow bridge data for a given network
    '''
    dfToIotex = pd.DataFrame(columns = ['Network', 'Date', 'Address', 'Transaction Fee', 'Token Name', 'Token Symbol', 'Value'])
    endpoint = "https://api.covalenthq.com/v1/{}/address/{}/transactions_v2/?page-size={}&key={}".format(chain[network], validator[network], 10000, COVALENT_KEY)
    response = requests.get(endpoint)
    JSON_DATA_RAW = response.json()
    JSON_DATA_RAW = JSON_DATA_RAW['data']

    for item in JSON_DATA_RAW['items']:
        temp = []
        temp.append(network)
        temp.append(item['block_signed_at'].split("T", 1)[0]) # Date
        temp.append(item['from_address']) # Address 
        temp.append(item['gas_price'] * item['gas_spent'] * pow(10, -18)) # Transaction Fee
        for event in item['log_events']:
            if(event['decoded']):
                if(event['decoded']['name'] == "Transfer"):
                    for param in event['decoded']['params']:
                        if(param["name"] == "to"):
                            address = param['value'] 
                        if(param["name"] == "value"):
                            value = param['value']
                    name = event['sender_name']
                    symbol = event['sender_contract_ticker_symbol']
                    decimals = -event['sender_contract_decimals']
                    value = int(value) * pow(10,decimals)
        temp.append(name) # Ticker Name
        temp.append(symbol) # Ticker Symbol
        temp.append(value) # Ticker Value
        dfToIotex.loc[len(dfToIotex)] = temp
                            
    dfToIotex['Date'] = pd.to_datetime(dfToIotex['Date'])
    return dfToIotex


# Outflow Bridge Data
def getBridgeDataOut(network):
    '''
    Gets outflow bridge data for a given network
    '''
    dfFromIotex = pd.DataFrame(columns = ['Network', 'Date', 'Address', 'Transaction Fee', 'Token Name', 'Token Symbol', 'Value'])
    endpoint = "https://api.covalenthq.com/v1/{}/address/{}/transactions_v2/?page-size={}&key={}".format(chain[network], cashier[network], 10000, COVALENT_KEY)
    response = requests.get(endpoint)
    JSON_DATA_RAW = response.json()
    JSON_DATA_RAW = JSON_DATA_RAW['data']

    for item in JSON_DATA_RAW['items']:
        temp = []
        temp.append(network)
        temp.append(item['block_signed_at'].split("T", 1)[0]) # Date
        temp.append(item['from_address']) # Address 
        temp.append(item['gas_price'] * item['gas_spent'] * pow(10, -9)) # Transaction Fee
        for event in item['log_events']:
            if(event['decoded']):
                if(event['decoded']['name'] == "Transfer"):
                    for param in event['decoded']['params']:
                        if(param["name"] == "to"):
                            address = param['value'] 
                        if(param["name"] == "value"):
                            value = param['value']
                    name = event['sender_name']
                    symbol = event['sender_contract_ticker_symbol']
                    decimals = -event['sender_contract_decimals']
                    value = int(value) * pow(10,decimals)
        temp.append(name) # Ticker Name
        temp.append(symbol) # Ticker Symbol
        temp.append(value) # Ticker Value
        dfFromIotex.loc[len(dfFromIotex)] = temp
                            
    dfFromIotex['Date'] = pd.to_datetime(dfFromIotex['Date'])
    return dfFromIotex



# Network Level Basic Statistics
def txnsStatsByDate():
    '''
    Fetches network level stats of networks - IoTeX, Polygon, Ethereum and Zilliqa
    '''
    
    query_string = """SELECT COUNT(DISTINCT sender) AS Addresses, 
    COUNT(*) AS Transactions, 
    DATE(timestamp) as Date,
    "IoTeX" as Network
    FROM `public-data-finance.crypto_iotex.actions` 
    WHERE DATE(timestamp) >= '2021-03-01' 
    GROUP BY Date
    ORDER BY Date DESC
    """

    txnByDateIotex = (
        bqclient.query(query_string)
        .result()
        .to_dataframe(bqstorage_client=bqstorageclient)
    )
    
    query_string = """SELECT COUNT(DISTINCT from_address) AS Addresses, 
    COUNT(*) AS Transactions, 
    DATE(block_timestamp) as Date,
    "Polygon" as Network
    FROM `public-data-finance.crypto_polygon.transactions`
    WHERE block_timestamp >= '2021-03-01' 
    GROUP BY Date
    ORDER BY Date DESC
    """

    txnByDatePolygon = (
        bqclient.query(query_string)
        .result()
        .to_dataframe(bqstorage_client=bqstorageclient)
    )
    txnByDate = txnByDateIotex.append(txnByDatePolygon)

    query_string = """SELECT COUNT(DISTINCT sender) AS Addresses, 
    COUNT(*) AS Transactions, 
    DATE(block_timestamp) as Date,
    "Zilliqa" as Network
    FROM `public-data-finance.crypto_zilliqa.transactions`
    WHERE block_timestamp >= '2021-03-01' 
    GROUP BY Date
    ORDER BY Date DESC 
    """
    txnByDateZilliqa = (
        bqclient.query(query_string)
        .result()
        .to_dataframe(bqstorage_client=bqstorageclient)
    )
    txnByDate = txnByDate.append(txnByDateZilliqa)

    query_string = """SELECT COUNT(DISTINCT from_address) AS Addresses, 
    COUNT(*) AS Transactions, 
    DATE(block_timestamp) as Date,
    "Ethereum" as Network
    FROM `bigquery-public-data.crypto_ethereum.transactions`
    WHERE block_timestamp >= '2021-03-01' 
    GROUP BY Date
    ORDER BY Date DESC
    """
    txnByDateEth = (
        bqclient.query(query_string)
        .result()
        .to_dataframe(bqstorage_client=bqstorageclient)
    )
    txnByDate = txnByDate.append(txnByDateEth)

    upload_blob("iotube", txnByDate.to_csv(), "txnStats")



# Network Level Gas Statistics
def getNetworkStats():
    '''
    Get network statistics for the networks on a daily basis
    '''
    
    # IoTeX
    query_string = """SELECT DATE(timestamp) as Date, 
    COUNT(`hash`) AS NoOfTxn, 
    SUM(gas_consumed) as TotalGasUsed,
    AVG(gas_price * POW(10, -18)) AS AvgGasPrice,
    SUM(gas_consumed) * AVG(gas_price * POW(10, -18)) AS TotalTxnFee,
    SUM(gas_consumed) * AVG(gas_price * POW(10, -18)) / COUNT(`hash`) AS AvgTxnFee,
    "IoTeX" AS Network
    FROM `public-data-finance.crypto_iotex.actions` 
    WHERE DATE(timestamp) > "2021-01-01" 
    GROUP BY Date
    ORDER BY Date ASC
    """

    txnByDateIotex = (
        bqclient.query(query_string)
        .result()
        .to_dataframe(bqstorage_client=bqstorageclient)
    )
    iotx = pd.read_csv('https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=IOTX&market=CNY&apikey=3NXQI7IVLOCKQTUO&datatype=csv')
    txnByDateIotex = pd.concat([txnByDateIotex, iotx], axis=1, join="inner")
    txnByDateIotex.sort_values(by=['Date'], inplace=True)
    txnByDateIotex['TotalTxnFeeUSD'] = txnByDateIotex['TotalTxnFee'] * txnByDateIotex['close (USD)']
    txnByDateIotex['CummulativeTotalTxnFee'] = txnByDateIotex['TotalTxnFeeUSD'].cumsum()
    txnByDateIotex['CummulativeTotalGasUsed'] = txnByDateIotex['TotalGasUsed'].cumsum()

    # Ethereum
    query_string = """SELECT DATE(block_timestamp) as Date, 
    COUNT(`hash`) AS NoOfTxn, 
    SUM(receipt_gas_used) as TotalGasUsed,
    AVG(gas_price * POW(10, -18)) AS AvgGasPrice,
    SUM(receipt_gas_used) * AVG(gas_price * POW(10, -18)) AS TotalTxnFee,
    SUM(receipt_gas_used) * AVG(gas_price * POW(10, -18)) / COUNT(`hash`) AS AvgTxnFee,
    "Ethereum" AS Network
    FROM bigquery-public-data.crypto_ethereum.transactions 
    WHERE DATE(block_timestamp) > "2021-01-01" 
    GROUP BY Date
    ORDER BY Date ASC
    """
    txnByDateEth = (
        bqclient.query(query_string)
        .result()
        .to_dataframe(bqstorage_client=bqstorageclient)
    )
    eth = pd.read_csv('https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=ETH&market=CNY&apikey=3NXQI7IVLOCKQTUO&datatype=csv')
    txnByDateEth = pd.concat([txnByDateEth, eth], axis=1, join="inner")
    txnByDateEth.sort_values(by=['Date'], inplace=True)
    txnByDateEth['TotalTxnFeeUSD'] = txnByDateEth['TotalTxnFee'] * txnByDateEth['close (USD)']
    txnByDateEth['CummulativeTotalTxnFee'] = txnByDateEth['TotalTxnFeeUSD'].cumsum()
    txnByDateEth['CummulativeTotalGasUsed'] = txnByDateEth['TotalGasUsed'].cumsum()

    txnByDate = txnByDateIotex.append(txnByDateEth)
    txnByDate['AvgTxnFeeUSD'] = txnByDate['AvgTxnFee'] * txnByDate['close (USD)']

    upload_blob("iotube", txnByDate.to_csv(), "networkStatsNew")



# Upload data
def upload_blob(bucket_name, source_file_name, destination_blob_name):
    '''
    Uploads data to Google Cloud Storage bucket
    '''
    storage_client = storage.Client.from_service_account_json(SERVICE_ACCOUNT_FILE)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    blob.upload_from_string(source_file_name, 'text/csv')
    blob.make_public()

    print("File uploaded to {}.".format(destination_blob_name))


# Bridge Helper Functions
def crossChainGrouping(inDf):
    '''
    Group bridge transactions by network
    '''
    flowDf = inDf.groupby(["Network", "Date"]).agg({'Value': ['count', 'sum', 'mean', 'median'],
                                                                'Transaction Fee': ['sum', 'mean', 'median']})
    flowDf['Value']['sum'] = flowDf['Value']['sum'].round()
    flowDf['Transaction Fee']['sum'] = flowDf['Transaction Fee']['sum']

    flowDf = flowDf.reset_index()
    flowDf.columns = flowDf.columns.droplevel(0)
    flowDf.columns = ['Network', 'Date', 'Frequency', 'Volume', 'Mean Volume', 'Median Volume', 'Transaction Fee', 'Mean Txn Fee', 'Median Txn Fee']
    
    return flowDf


def tokenGrouping(inDf):
    '''
    Bridge data grouping by token
    '''
    dfInGroupedToken = inDf.groupby(["Token Symbol", "Date"], as_index=False).agg({'Value': ['count', 'sum', 'mean', 'median']})
    dfInGroupedToken['Value']['sum'] = dfInGroupedToken['Value']['sum'].round()

    dfInGroupedToken = dfInGroupedToken.reset_index()
    dfInGroupedToken.columns = dfInGroupedToken.columns.droplevel(0)
    dfInGroupedToken.columns = ['', 'Token Symbol', 'Date', 'Frequency', 'Volume', 'Average Value', 'Median']

    dfInGroupedPeriod = inDf.groupby(["Network", "Token Symbol", "Date"], as_index=False).agg({'Value': ['count', 'sum', 'mean', 'median']})
    dfInGroupedPeriod['Value']['sum'] = dfInGroupedPeriod['Value']['sum'].round()

    dfInGroupedPeriod = dfInGroupedPeriod.reset_index()
    dfInGroupedPeriod.columns = dfInGroupedPeriod.columns.droplevel(0)
    dfInGroupedPeriod.columns = ['', 'Network', 'Token Symbol', 'Date', 'Frequency', 'Volume', 'Average Value', 'Median']
    
    return dfInGroupedToken, dfInGroupedPeriod


# Execute Scheduler Functions
if __name__ == "__main__":
    txnsStatsByDate()
    getNetworkStats()
    getHourData()

    # Fetch bridge data - inflow
    polygon = getBridgeDataIn("Polygon")
    ethereum = getBridgeDataIn("Ethereum")
    bsc = getBridgeDataIn("BSC")
    dfToIotex = polygon.append([ethereum, bsc])
    upload_blob("iotube", dfToIotex.to_csv(), "bridgeInflowRaw")
    upload_blob("iotube", crossChainGrouping(dfToIotex).to_csv(), "bridgeInflow")
    upload_blob("iotube", tokenGrouping(dfToIotex)[0].to_csv(), "bridgeInflowToken")
    upload_blob("iotube", tokenGrouping(dfToIotex)[1].to_csv(), "bridgeInflowTokenPeriod")

    # Fetch bridge data - outflow
    polygon = getBridgeDataOut("Polygon")
    ethereum = getBridgeDataOut("Ethereum")
    bsc = getBridgeDataOut("BSC")
    dfFromIotex = polygon.append([ethereum, bsc])
    upload_blob("iotube", dfFromIotex.to_csv(), "bridgeOutflowRaw")
    upload_blob("iotube", crossChainGrouping(dfFromIotex).to_csv(), "bridgeOutflow")
    upload_blob("iotube", tokenGrouping(dfFromIotex)[0].to_csv(), "bridgeOutflowToken")
    upload_blob("iotube", tokenGrouping(dfFromIotex)[1].to_csv(), "bridgeOutflowTokenPeriod")
