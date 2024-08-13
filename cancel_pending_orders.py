from fyers_api import accessToken
from fyers_api import fyersModel
from fyers_apiv3 import fyersModel


def initialize_fyers_app():
    client_id = 'YOUR_CLIENT_ID'
    secret_key = 'YOUR_SECRET_KEY'
    redirect_uri = 'YOUR_REDIRECT_URI'
    response_type = 'code'
    state = 'state'

    session = accessToken.SessionModel(client_id=client_id, secret_key=secret_key, redirect_uri=redirect_uri,
                                       response_type=response_type, state=state)
    response = session.generate_authcode()
    return response


def close_all_pending_orders(app_id, access_token):
    fyers = fyersModel.FyersModel(client_id=app_id, token=access_token)
    pending_orders = fyers.orderbook()  # Fetch all orders
    if 'error' in pending_orders:
        print('Error fetching order book:', pending_orders['error'])
        return

    for order in pending_orders['orderBook']:
        if order['status'] == 6:
            order_id = order['id']
            response = fyers.cancel_order({'id': order_id})
            if response['code'] == 200:
                print(f'Cancelled order {order_id}')
            else:
                print(f'Failed to cancel order {order_id}:', response['message'])


def close_Pending_Order(app_id, access_token, order_id):
    fyers = fyersModel.FyersModel(client_id=app_id, token=access_token)
    response = fyers.cancel_order({'id': order_id})

    return response
