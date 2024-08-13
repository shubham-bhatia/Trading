import csv
# import accessTOTP
import json
import os
import tkinter as tk
from tkinter import messagebox

from fyers_apiv3 import fyersModel


def getOrderbook(app_id, access_token):
    fyers = fyersModel.FyersModel(client_id=app_id, token=access_token)
    response = fyers.orderbook()
    print(response)
    if 'error' in response:
        print('Error fetching order book:', response['error'])
        return []
    return response['orderBook']


def read_csv_file(file_path):
    data = []
    with open(file_path, 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file)
        # next(csv_reader)  # Skip the header row
        for row in csv_reader:
            data.append(row)
    return data


def getTradeToOpen():
    desktop_path = os.path.join('C:', os.sep, 'Users', 'shubhbhatia', 'Desktop', 'Trade.txt')
    csv_data = read_csv_file(desktop_path)
    print(csv_data)
    print(type(csv_data))

    for i in range(len(csv_data)):
        print(csv_data[i])
        print(type(csv_data[i]))


def openNewOrder(symbol, qty, limitPrice, stopLoss, side, productType, order_type, APP_ID, access_token, offlineOrder,
                 takeProfit):
    symbol = "NSE:" + symbol.upper() + "-EQ"

    stopPrice = 0
    if int(order_type) == 1 and productType == 'INTRADAY':
        stopLoss = 0
        takeProfit = 0
        stopPrice = 0
    elif productType == 'BO':
        stopPrice = 0

    data = {
        "symbol": symbol,
        "qty": int(qty),
        "type": int(order_type),
        "side": side,
        "productType": productType.upper(),
        "stopPrice": float(stopPrice),
        "limitPrice": float(limitPrice),
        "stopLoss": stopLoss,
        "takeProfit": takeProfit,
        "validity": "DAY",
        "disclosedQty": 0,
        "tag": "Python",
        "offlineOrder": offlineOrder
    }
    fyers = fyersModel.FyersModel(client_id=APP_ID, token=access_token, is_async=False, log_path="")
    response = fyers.place_order(data=data)
    # print(response)

    if response['message'] == "Successfully placed order":
        return "Order Status", "Order placed successfully!"
    else:
        return response


def checkSide(side):
    if side == -1:
        side = 'Sell'
    else:
        side = 'Buy'
    return side


def getParentOrderDetails(APP_ID, access_token, parentId):
    fyers = fyersModel.FyersModel(client_id=APP_ID, token=access_token, is_async=False, log_path="")
    response = fyers.orderbook()
    parsed_data = json.loads(json.dumps(response))

    for net_position in parsed_data['orderBook']:

        if net_position['id'] == parentId:
            side = checkSide(net_position['side'])

            if net_position['status'] == 6:
                status = "Pending"
            elif net_position['status'] == 2:
                status = "Completed"
            else:
                status = net_position['status']

            print('Status: ', status
                  , '|| Symbol: ', net_position['symbol']
                  , '|| Qty: ', net_position['qty']
                  , '|| Limit Price: ', net_position['limitPrice']
                  , '|| Stop Price: ', net_position['stopPrice']
                  , '|| Side: ', side
                  , '|| productType: ', net_position['productType']
                  , '|| orderDateTime: ', net_position['orderDateTime']
                  , '|| Type: ', (net_position['type'], "(1-LO 2-MO 3-SL/M 4-SL/L)")
                  )

# def getOrderbook(APP_ID, access_token):
#     fyers = fyersModel.FyersModel(client_id=APP_ID, token=access_token, is_async=False, log_path="")
#     response = fyers.orderbook()
#     parsed_data = json.loads(json.dumps(response))
#
#     # 1 = > Canceled
#     # 2 = > Traded / Filled
#     # 3 = > (Not used currently)
#     # 4 = > Transit
#     # 5 = > Rejected
#     # 6 = > Pending
#     # 7 = > Expired
#
#     _orderNo = 1
#     for net_position in parsed_data['orderBook']:
#         side = checkSide(net_position['side'])
#
#         if net_position['status'] == 6 or net_position['status'] == 2:
#             if net_position['status'] == 6:
#                 status = "Pending"
#             elif net_position['status'] == 2:
#                 status = "Completed"
#             else:
#                 status = net_position['status']
#
#             print(net_position)
#
#             print('Status: ', status
#                   , '|| Symbol: ', net_position['symbol']
#                   , '|| Qty: ', net_position['qty']
#                   , '|| Limit Price: ', net_position['limitPrice']
#                   , '|| Stop Price: ', net_position['stopPrice']
#                   , '|| Side: ', side
#                   , '|| productType: ', net_position['productType']
#                   , '|| orderDateTime: ', net_position['orderDateTime']
#                   , '|| Type: ', (net_position['type'], "(1-LO 2-MO 3-SL/M 4-SL/L)")
#                   )
#         _orderNo = _orderNo + 1
# if 'parentId' in net_position:
# parentId = net_position['parentId']
# print(net_position['parentId'])
# getParentOrderDetails(APP_ID, access_token, net_position['parentId'])
