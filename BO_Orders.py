import json
import accessTOTP
from fyers_apiv3 import fyersModel

def getPendingBOOrders():
    app_id = accessTOTP.APP_ID
    access_token = accessTOTP.main()
    fyers = fyersModel.FyersModel(client_id=app_id, token=access_token)
    response = fyers.orderbook()
    if 'error' in response:
        print('Error fetching orders:', response['error'])
        return []
    pending_orders = [order for order in response['orderBook'] if order['status'] == 6]
    return pending_orders

# def getPendingBOOrders(APP_ID, access_token):
#     fyers = fyersModel.FyersModel(client_id=APP_ID, token=access_token, is_async=False, log_path="")
#
#     try:
#         # Fetch order book details
#         response = fyers.orderbook()
#         parsed_data = json.loads(json.dumps(response))
#
#         # Iterate through order book to find pending BO orders
#         for order in parsed_data['orderBook']:
#             if order['productType'] == 'BO' and order['status'] == 6:
#                 # Status 6 indicates pending orders
#                 print('Order ID:', order['id'])
#                 print('Symbol:', order['symbol'])
#                 print('Qty:', order['qty'])
#                 print('Limit Price:', order['limitPrice'])
#                 print('Stop Price:', order['stopPrice'])
#                 print('Stop Loss:', order['stopLoss'])
#                 print('Take Profit:', order['takeProfit'])
#                 print('Order Type:', order['type'])  # Print the type of order (1-LO 2-MO 3-SL/M 4-SL/L)
#                 print('Order DateTime:', order['orderDateTime'])
#                 print('------------------------')
#
#     except Exception as e:
#         print("Error fetching order book:", e)

