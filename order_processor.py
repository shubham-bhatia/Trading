import json
import logging
import os
import time
from datetime import datetime
import pytz
import web_app

# Setup logging
logging.basicConfig(level=logging.INFO)

# Directory where the JSON files are stored
uploaded_files_directory = 'uploaded_files'


def process_single_order(filename):
    order_status = "File unavailable"
    order_response = "Default"
    filepath = os.path.join(uploaded_files_directory, filename)
    with open(filepath, 'r') as json_file:
        order_data = json.load(json_file)

        order_time_str = order_data.get('order_datetime')
        order_time = datetime.strptime(order_time_str, '%Y-%m-%dT%H:%M').time()
        order_date = datetime.strptime(order_time_str, '%Y-%m-%dT%H:%M')

        # Get the current time
        # current_time = datetime.now().time()
        current_date = datetime.now()
        ist_timezone = pytz.timezone('Asia/Kolkata')
        ist_date = current_date.astimezone(ist_timezone)
        formatted_ist_date = ist_date.strftime('%Y-%m-%d %H:%M:%S')
        comparable_date = datetime.strptime(formatted_ist_date, '%Y-%m-%d %H:%M:%S')

        # local_now = datetime.now(ist_timezone)
        # current_date = datetime.strftime(ist_date, '%Y-%m-%dT%H:%M')

        # logging.info(f"Shubham-{formatted_ist_date}//{current_date}//{order_date}")
        # Check if the order time is less than or equal to the current time
        if order_date <= comparable_date:
            # Double-check if the file still exists before executing the order
            if os.path.exists(filepath):
                response = web_app.getTradeToOpen2(
                    filepath,
                    order_data["symbol"],
                    order_data["qty"],
                    float(order_data["entry_price"]),
                    order_data["mode"],
                    order_data["selected_option"],
                    order_data["product_type"],
                    order_data["order_type"],
                    order_data["b_s"],
                    float(order_data["sl"]),
                    float(order_data["tp"])
                )

                logging.info(f"Shubham: {response}")
                logging.info(f"response_s: {response[1]}")

                if response[1] == 'error': #response['s']
                    logging.info(f"Order failed: {response}")
                    order_status = "order_failed"
                    order_response = response

                elif response[1] == 'Order placed successfully!':
                    # Log the successful execution
                    logging.info(f"Order executed: {response}")
                    order_status = response
                    order_response = response[1]

        else:
            order_status = "Not the right time to execute the order"
            order_response = "Not the right time to execute the order"
    return order_status, order_response

def delete_file(filename):
    filepath = os.path.join(uploaded_files_directory, filename)
    os.remove(filepath)
    logging.info(f"File {filename} deleted.")

def process_orders():
    # Check if the directory exists
    if not os.path.exists(uploaded_files_directory):
        logging.error(f"Directory {uploaded_files_directory} does not exist.")
        return

    status = "No File Exists!"
    # List all files in the directory
    files = os.listdir(uploaded_files_directory)

    # Iterate over each file in the directory
    for filename in files:
        filepath = os.path.join(uploaded_files_directory, filename)

        # Ensure we only process JSON files
        if not filename.endswith('.json'):# and filename != 'Trade.txt':
            continue

        try:
            with open(filepath, 'r') as json_file:
                order_data = json.load(json_file)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON file {filename}: {e}")
            continue

        # Extract and parse the order time
        order_time_str = order_data.get('order_datetime')
        try:
            order_time = datetime.strptime(order_time_str, '%Y-%m-%dT%H:%M').time()
            order_date = datetime.strptime(order_time_str, '%Y-%m-%dT%H:%M')
        except ValueError as e:
            logging.error(f"Time format error in file {filename}: {e}")
            continue

        # Get the current time
        # current_time = datetime.now().time()
        current_date = datetime.now()
        ist_timezone = pytz.timezone('Asia/Kolkata')
        ist_date = current_date.astimezone(ist_timezone)
        formatted_ist_date = ist_date.strftime('%Y-%m-%d %H:%M:%S')
        comparable_date = datetime.strptime(formatted_ist_date, '%Y-%m-%d %H:%M:%S')

        # Check if the order time is less than or equal to the current time
        if order_date <= comparable_date:
            # Double-check if the file still exists before executing the order
            if os.path.exists(filepath):
                try:
                    response = web_app.getTradeToOpen2(
                        filepath,
                        order_data["symbol"],
                        order_data["qty"],
                        float(order_data["entry_price"]),
                        order_data["mode"],
                        order_data["selected_option"],
                        order_data["product_type"],
                        order_data["order_type"],
                        order_data["b_s"],
                        float(order_data["sl"]),
                        float(order_data["tp"])
                    )

                    if response['s'] == 'error':
                        logging.info(f"Order failed: {response}")
                        status = "order_failed"

                    else:
                        # Log the successful execution
                        logging.info(f"Order executed: {response}")
                        status = response

                except Exception as e:
                    logging.error(f"Failed to execute order: {e}")
                    status = "Failed to execute order"
            else:
                logging.warning(f"File {filename} does not exist anymore. Skipping execution.")
                status = f"File {filename} does not exist anymore. Skipping execution."
        else:
            logging.info(f"Holding order {filename} for next run.")
            status = f"Holding order {filename} for next run."
    return status
