import json

from fyers_apiv3 import fyersModel


# def getOpenPositions(APP_ID, access_token):
#     # Initialize the FyersModel instance with your client_id, access_token, and enable async mode
#     fyers = fyersModel.FyersModel(client_id=APP_ID, token=access_token, is_async=False, log_path="")
#     response = fyers.positions()
#
#     # Parsing the JSON data
#     parsed_data = json.loads(json.dumps(response))
#
#     pos = 1
#     for net_position in parsed_data['netPositions']:
#         print('Position: ', pos)
#
#         if net_position['side'] == -1:
#             side = 'Sell'
#         else:
#             side = 'Buy'
#         print('Symbol: ', net_position['symbol']
#               , '|| Profit: ', round(net_position['pl'],3)
#               , '|| Qty: ', net_position['qty']
#               , '|| Price: ', net_position['sellAvg']
#               # , '|| Stop Loss: ', net_position['sellAvg']
#               , '|| LTP: ', net_position['ltp']
#               , '|| Side: ', side
#               , '|| productType: ', net_position['productType'])
#               # , '|| netAvg: ', net_position['netAvg'])
#
#         pos = pos + 1
#     return response['netPositions']
#
#     print('Position Open Count: ', parsed_data['overall']['count_open'], '|| Position Realized PL: ',
#           round(parsed_data['overall']['pl_unrealized'],3))

def getOpenPositions(app_id, access_token):
    fyers = fyersModel.FyersModel(client_id=app_id, token=access_token)
    response = fyers.positions()
    # print(response)
    if 'error' in response:
        print('Error fetching positions:', response['error'])
        return []
    return response['netPositions']

def closeOpenPositions(app_id, access_token, pos_id):
    fyers = fyersModel.FyersModel(client_id=app_id, token=access_token)
    response = fyers.exit_positions({'id': pos_id})
    return response