import json
import logging
import os
import time
from datetime import datetime

import web_app

# Setup logging
logging.basicConfig(level=logging.INFO)

# Directory where the JSON files are stored
uploaded_files_directory = 'uploaded_files'


def process_single_order(filename):
    order_status = "No File Exists!"
    filepath = os.path.join(uploaded_files_directory, filename)
    with open(filepath, 'r') as json_file:
        order_data = json.load(json_file)

        order_time_str = order_data.get('order_datetime')
        order_time = datetime.strptime(order_time_str, '%Y-%m-%dT%H:%M').time()

        # Get the current time
        current_time = datetime.now().time()

        # Check if the order time is less than or equal to the current time
        if order_time <= current_time:
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

                # Log the successful execution
                logging.info(f"Order executed: {response}")
                order_status = "Order executed"

                # os.remove(filepath)
                # logging.info(f"Order executed and file {filename} deleted.")
    return order_status

def delete_file(filename):
    filepath = os.path.join(uploaded_files_directory, filename)
    os.remove(filepath)
    logging.info(f"Order executed and file {filename} deleted.")

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
        if not filename.endswith('.json') and filename != 'Trade.txt':
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
        except ValueError as e:
            logging.error(f"Time format error in file {filename}: {e}")
            continue

        # Get the current time
        current_time = datetime.now().time()

        # Check if the order time is less than or equal to the current time
        if order_time <= current_time:
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

                    # Log the successful execution
                    logging.info(f"Order executed: {response}")
                    status = "Order executed"

                    # After executing, delete the file
                    os.remove(filepath)
                    logging.info(f"Order executed and file {filename} deleted.")
                except Exception as e:
                    logging.error(f"Failed to execute order: {e}")
                    status = f"Failed to execute order: {e}"
            else:
                logging.warning(f"File {filename} does not exist anymore. Skipping execution.")
                status = f"File {filename} does not exist anymore. Skipping execution."
        else:
            logging.info(f"Holding order {filename} for next run.")
            status = f"Holding order {filename} for next run."
    return status
