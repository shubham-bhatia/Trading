import csv
import json
import os

from fyers_apiv3 import fyersModel

def get_quotes(app_id, access_token, symbol):
    fyers = fyersModel.FyersModel(client_id=app_id, token=access_token)
    data = {
        "symbols": symbol
    }

    response = fyers.quotes(data=data)
    if 'error' in response:
        print('Error fetching scrip details:', response['error'])
        return []
    return response['d']
