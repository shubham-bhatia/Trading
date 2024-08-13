import csv
import os

import BO_Orders
import Orders
import accessTOTP
import getPos

APP_ID = accessTOTP.APP_ID
access_token = accessTOTP.main()


def read_csv_file(file_path):
    data = []
    with open(file_path, 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip the header row
        for row in csv_reader:
            data.append({
                'symbol': row[0],
                'qty': int(row[1]),
                'limitPrice': float(row[2]),
                'stopLoss': float(row[3]),
                'side': int(row[4]),
                'productType': row[5],
                'type': row[6]
            })
    return data


def getTradeToOpen(file_path):
    csv_data = read_csv_file(file_path)
    for trade in csv_data:
        symbol = trade['symbol']
        if "#" not in symbol:
            qty = trade['qty']
            limitPrice = trade['limitPrice']
            stopLoss = trade['stopLoss']
            side = trade['side']
            productType = trade['productType']
            type = trade['type']

            print(f"Processing trade for symbol: {symbol} and Product: {productType} and Stop Loss: {stopLoss}")
            Orders.openNewOrder(symbol, qty, limitPrice, stopLoss, side, productType, type, APP_ID, access_token, False)


def cancelAllPendingOrders(APP_ID, access_token):
    print('Hello')


if __name__ == '__main__':
    print('----------------------------------------------######################------------------------------------')
    desktop_path = os.path.join('C:', os.sep, 'Users', 'shubhbhatia', 'Desktop', 'Trade.txt')

    print("1-Show All Positions \n2-Show All Positions\n3-Cancel All Orders\n4-Show OrderBook\n5-Show Pending BO Orders")
    selectedValue = int(input("Select Any Option: "))

    if selectedValue == 1:
        print('----------------Opening New Trade--------------------')
        getTradeToOpen(desktop_path)
    elif selectedValue == 2:
        getPos.getOpenPositions(APP_ID, access_token)
    elif selectedValue == 3:
        cancelAllPendingOrders(APP_ID, access_token)
    elif selectedValue == 4:
        Orders.getOrderbook(APP_ID, access_token)
    elif selectedValue == 5:
        BO_Orders.getPendingBOOrders(APP_ID, access_token)
