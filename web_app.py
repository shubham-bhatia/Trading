import csv
import json
import logging
import os
from datetime import datetime

from flask import Flask, request, redirect, url_for, render_template, flash

import BO_Orders
import Orders
import cancel_pending_orders
import getPos
import order_processor
from cancel_pending_orders import close_all_pending_orders

logging.basicConfig(level=logging.INFO)
# APP_ID = accessTOTP.APP_ID
# access_token = accessTOTP.main()

# APP_ID = "abc"
# access_token = "abc"

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

UPLOAD_FOLDER = 'uploaded_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/run_scheduler')
def run_scheduler():
    try:
        # Run the order_processor.py script
        response = order_processor.process_orders()
        return render_template('fileProcessed.html', response=response)
    except Exception as e:
        return str(e)

@app.route('/process_order/<order_id>')
def process_order(order_id):
    try:
        # Run the order_processor.py script
        status = order_processor.process_single_order(order_id)
        delete_file = order_processor.delete_file(order_id)
        return render_template('fileProcessed.html', response=status)
    except Exception as e:
        return str(e)

def read_csv_file(file_path):
    data = []
    with open(file_path, 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip the header row
        for row in csv_reader:
            data.append({'symbol': row[0], 'qty': int(row[1]), 'limitPrice': float(row[2]), 'stopLoss': float(row[3]),
                         'side': int(row[4]), 'productType': row[5], 'type': row[6]})
    return data


def make_multiple_of_10(x):
    return round(x * 10) / 10  # Rounds down to nearest 10 and then multiples by 10


def getTradeToOpen(file_path, offlineOrder):
    csv_data = read_csv_file(file_path)
    for trade in csv_data:
        symbol = trade['symbol']
        if "#" not in symbol:
            qty = trade['qty']
            limitPrice = trade['limitPrice']
            # stopLoss = trade['stopLoss']
            side = trade['side']
            productType = trade['productType']
            type = trade['type']

            entryPrice = make_multiple_of_10(limitPrice + (limitPrice * 0.007))
            stopLoss = make_multiple_of_10(entryPrice + (entryPrice * 0.012))  # stopLoss
            calcPrice = (stopLoss - entryPrice) * 1.5
            takeProfit = make_multiple_of_10(entryPrice - calcPrice)  # Target
            tp = make_multiple_of_10(entryPrice - takeProfit)

            print(f"Processing trade for symbol: {symbol} and Product: {productType} and Stop Loss: {stopLoss}")
            resp1 = Orders.openNewOrder(symbol, qty, entryPrice, (stopLoss - entryPrice), side, productType, type,
                                        offlineOrder, tp)

            flash(resp1)


def getTradeToOpen2(desktop_path, symbol, qty, entryPrice, offlineOrder, mode, product_type, order_type, b_s, sl_input,
                    tp_input):
    entryPrice = make_multiple_of_10(entryPrice)

    if sl_input == 0:
        stopLoss = make_multiple_of_10(entryPrice + (entryPrice * 0.012))
    else:
        stopLoss = sl_input
    calcPrice = (stopLoss - entryPrice) * 1.5
    takeProfit = make_multiple_of_10(entryPrice - calcPrice)
    if tp_input == 0:
        tp = make_multiple_of_10(entryPrice - takeProfit)
    else:
        tp = make_multiple_of_10(entryPrice - tp_input)

    print(f'Entry Price: {entryPrice} Stop Loss: {stopLoss}')

    resp1 = Orders.openNewOrder(symbol, qty, entryPrice, (stopLoss - entryPrice), int(b_s), product_type, order_type,
                                offlineOrder, tp)

    flash(resp1)
    return resp1


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        flash('Please select the file')
        return redirect(url_for('index'))
    # if file:
    #     # Get the current directory where the script is running
    #     current_directory = os.getcwd()
    #     file_path = os.path.join(current_directory, file.filename)
    #     file.save(file_path)
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        getTradeToOpen(file_path, False)
        flash('File successfully uploaded and processed')
        return redirect(url_for('index'))


@app.route('/action', methods=['POST'])
def perform_action():
    selected_option = request.form.get('option')
    if selected_option:
        selected_value = int(selected_option)
        if selected_value == 1:
            current_directory = os.getcwd()
            desktop_path = os.path.join('uploaded_files', 'Trade.txt')
            file_path = os.path.join(current_directory, 'Trade.txt')
            # desktop_path = os.path.join('C:', os.sep, 'Users', 'SHUBHBHATIA', 'Desktop', 'Trade.txt')
            passcode = request.form.get('passcode')
            if passcode == '1':  # Replace 'your_passcode_here' with the actual passcode
                flash('Opening new trade...')
                getTradeToOpen(desktop_path, False)
            else:
                flash('Incorrect passcode.')  # getTradeToOpen(desktop_path)
        elif selected_value == 2:
            # flash('Showing open positions...')
            return redirect(url_for('show_positions'))
        elif selected_value == 3:
            flash('Canceling all orders...')
            close_all_pending_orders()  # Call the new function
        elif selected_value == 4:
            # flash('Showing order book...')
            return redirect(url_for('show_orderbook'))
        elif selected_value == 5:
            # flash('Showing pending BO orders...')
            return redirect(url_for('show_pending_bo_orders'))
    return redirect(url_for('index'))


@app.route('/positions')
def show_positions():
    positions = getPos.getOpenPositions()
    total_realized_profit = sum(position['realized_profit'] for position in positions)
    total_unrealized_profit = sum(position['unrealized_profit'] for position in positions)
    Total_pl = total_realized_profit + total_unrealized_profit
    return render_template('positions.html', positions=positions, total_realized_profit=total_realized_profit,
                           total_unrealized_profit=total_unrealized_profit, Total_pl=Total_pl)


@app.route('/show_saved_order')
def show_saved_order():
    # List all JSON files in the orders directory
    order_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.json')]
    orders = []

    # Load each order file and append it to the orders list
    for order_file in order_files:
        with open(os.path.join(UPLOAD_FOLDER, order_file), 'r') as file:
            order_data = json.load(file)
            orders.append(order_data)

    # Render the HTML template with the orders data
    return render_template('show_saved_order.html', orders=orders)


@app.route('/orderbook')
def show_orderbook():
    orderbook = Orders.getOrderbook()
    return render_template('orderbook.html', orderbook=orderbook)


@app.route('/pending_bo_orders')
def show_pending_bo_orders():
    pending_orders = BO_Orders.getPendingBOOrders()
    return render_template('pending_bo_orders.html', pending_orders=pending_orders)


@app.route('/cancel_order/<order_id>')
def cancel_order(order_id):
    flash('Order Cancelled: ', order_id)
    cancel_order = cancel_pending_orders.close_Pending_Order(order_id)
    return redirect(url_for('show_pending_bo_orders'))


@app.route('/delete_order/<order_id>')
def delete_order(order_id):
    flash('Order Deleted: ', order_id)
    filepath = os.path.join(UPLOAD_FOLDER, order_id)
    os.remove(filepath)
    logging.info(f"Order executed and file {order_id} deleted.")
    return redirect(url_for('show_saved_order'))


@app.route('/cancel__all_orders')
def cancel_all_orders():
    close_all_pending_orders()
    return redirect(url_for('show_pending_bo_orders'))


@app.route('/close_pos/<pos_id>')
def close_pos(pos_id):
    closePos = getPos.closeOpenPositions(pos_id)
    flash('Close Position: ', pos_id)
    return redirect(url_for('show_positions'))


@app.route('/new_order', methods=['POST'])
def new_order():
    return redirect(url_for('order_form'))


@app.route('/order_form', methods=['GET', 'POST'])
def order_form():
    desktop_path = os.path.join('C:', os.sep, 'Users', 'shubhbhatia', 'Desktop', 'Trade.txt')
    if request.method == 'POST':
        symbol = request.form['script']
        qty = request.form['qty']
        entry_price = request.form['entry_price']
        selected_option = request.form.get('option')
        mode = request.form.get('mode')
        product_type = request.form.get('product_type')
        order_type = request.form.get('order_type')
        b_s = request.form.get('b_s')
        sl = request.form.get('stop_loss')
        tp = request.form.get('take_profit')
        order_datetime_str = request.form.get('order_datetime')
        order_datetime = datetime.strptime(order_datetime_str, "%Y-%m-%dT%H:%M").time()

        # Get the current time
        current_time = datetime.now().time()

        if mode == 1:
            mode = True
        else:
            mode = False

        # Compare the current time with the target time
        if order_datetime <= current_time:
            response = getTradeToOpen2(desktop_path, symbol, qty, float(entry_price), mode, selected_option,
                                       product_type,
                                       order_type, b_s, float(sl), float(tp))
            return render_template('order_success.html', script=symbol, qty=qty, limit_price=entry_price,
                                   response=response)
        else:

            # Generate a unique filename for the JSON file (e.g., based on order_datetime)
            filename = f"order_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
            json_file_path = os.path.join(UPLOAD_FOLDER, filename)

            # Save the order details in a JSON file in the uploaded_files folder
            order_details = {
                "symbol": symbol,
                "qty": qty,
                "entry_price": entry_price,
                "order_datetime": order_datetime_str,
                "mode": mode,
                "selected_option": selected_option,
                "product_type": product_type,
                "order_type": order_type,
                "b_s": b_s,
                "sl": sl,
                "tp": tp,
                "filename": filename
            }

            # Save the order details to the JSON file
            with open(json_file_path, "w") as json_file:
                json.dump(order_details, json_file, indent=4)
                response = f"{filename} Saved"

            return render_template('order_saved.html', script=symbol, qty=qty, limit_price=entry_price,
                                   response=response)

    return render_template('order_form.html')


if __name__ == '__main__':
    app.run(debug=True)
