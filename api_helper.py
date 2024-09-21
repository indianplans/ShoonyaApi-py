from flask import Flask, request, jsonify, render_template, redirect, url_for
import pyotp
from NorenRestApiPy.NorenApi import NorenApi
import logging
import yaml
import os

app = Flask(__name__)

# Enable debugging to see request and responses
logging.basicConfig(level=logging.DEBUG)

# Load the configuration from the YAML file
config_file = 'cred.yml'
if os.path.exists(config_file):
    try:
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
    except yaml.YAMLError as e:
        logging.error(f"Error loading YAML file: {e}")
        raise
else:
    logging.error(f"Config file {config_file} not found!")
    raise FileNotFoundError(f"Config file {config_file} not found!")

# Check if all required keys are present in the config
required_keys = ['user', 'pwd', 'factor2', 'vc', 'apikey', 'imei']
for key in required_keys:
    if key not in config:
        logging.error(f"Missing required configuration key: {key}")
        raise KeyError(f"Missing required configuration key: {key}")

# Extract the values from the config
user = config['user']
pwd = config['pwd']
factor2 = pyotp.TOTP(config['factor2']).now()  # Generate OTP using the factor2 TOTP secret
vc = config['vc']
apikey = config['apikey']
imei = config['imei']

# Initialize the Shoonya API
class ShoonyaApiPy(NorenApi):
    def __init__(self):
        super().__init__(host='https://api.shoonya.com/NorenWClientTP/', websocket='wss://api.shoonya.com/NorenWSTP/')
        global api
        api = self

# Initialize API and log in
api = ShoonyaApiPy()
ret = api.login(userid=user, password=pwd, twoFA=factor2, vendor_code=vc, api_secret=apikey, imei=imei)
logging.debug(f"Login response: {ret}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/orders', methods=['GET'])
def get_orders():
    try:
        orders = api.get_order_book()
        logging.debug(f"Orders response: {orders}")

        if isinstance(orders, list) and orders[0].get('stat') == 'Ok':
            return render_template('orders.html', orders=orders)
        else:
            error_message = orders[0].get('emsg', 'Unknown error occurred') if isinstance(orders, list) else orders.get('emsg', 'Unknown error occurred')
            return render_template('error.html', message=f"Error: {error_message}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return render_template('error.html', message=f"An error occurred: {e}")

@app.route('/holdings', methods=['GET'])
def get_holdings():
    try:
        holdings = api.get_holdings()
        logging.debug(f"Holdings response: {holdings}")

        if holdings and isinstance(holdings, list):
            if holdings[0].get('stat') == 'Ok':
                return render_template('holdings.html', holdings=holdings)
            else:
                return render_template('error.html', message=holdings[0].get('emsg', 'Error in response'))
        else:
            return render_template('holdings.html', holdings=[])
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return render_template('error.html', message=f"An error occurred: {e}")

@app.route('/trades', methods=['GET'])
def get_trades():
    try:
        trades = api.get_trade_book()
        logging.debug(f"Trades response: {trades}")

        if trades and isinstance(trades, list):
            if trades[0].get('stat') == 'Ok':
                return render_template('trades.html', trades=trades)
            else:
                return render_template('error.html', message=trades[0].get('emsg', 'Error in response'))
        else:
            return render_template('trades.html', trades=[])
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return render_template('error.html', message=f"An error occurred: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    logging.debug(f"Webhook received data: {data}")

    if data:
        try:
            symbol = data.get('symbol')
            quantity = data.get('quantity')
            transaction_type = data.get('transaction_type')
            price = data.get('price')

            if symbol and quantity and transaction_type:
                order_response = api.place_order(
                    buy_or_sell=transaction_type.upper(),
                    product_type='C',
                    exchange='NSE',
                    tradingsymbol=symbol,
                    quantity=quantity,
                    price=price
                )
                logging.debug(f"Order placement response: {order_response}")
                return jsonify({"status": "success", "message": "Order placed successfully!", "order_response": order_response})
            else:
                return jsonify({"status": "error", "message": "Invalid data received"})
        except Exception as e:
            logging.error(f"Error placing order: {e}")
            return jsonify({"status": "error", "message": str(e)})
    else:
        return render_template('error.html', message="No data received")

@app.route('/place_test_order', methods=['POST'])
def place_test_order():
    try:
        order_response = api.place_order(
            buy_or_sell='B',
            product_type='C',
            exchange='NSE',
            tradingsymbol='RELIANCE',
            quantity=1,
            price=2000
        )
        logging.debug(f"Test order placement response: {order_response}")
        return jsonify({"status": "success", "message": "Test order placed successfully!", "order_response": order_response})
    except Exception as e:
        logging.error(f"Error placing test order: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/positions', methods=['GET'])
def get_positions():
    try:
        positions = api.get_positions()
        logging.debug(f"Positions response: {positions}")

        if positions and isinstance(positions, list):
            mtm = sum(float(pos.get('urmtom', 0)) for pos in positions)
            pnl = sum(float(pos.get('rpnl', 0)) for pos in positions)
            day_m2m = mtm + pnl
            logging.debug(f'Daily MTM: {day_m2m}')
            return render_template('positions.html', positions=positions, day_m2m=day_m2m)
        else:
            return render_template('positions.html', positions=[], day_m2m=0)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return render_template('error.html', message=f"An error occurred: {e}")

@app.route('/buy_sell', methods=['GET'])
def buy_sell():
    return render_template('buy_sell.html')

@app.route('/place_order', methods=['POST'])
def place_order():
    try:
        # Extract form data
        buy_or_sell = request.form.get('buy_or_sell')
        product_type = request.form.get('product_type')
        exchange = request.form.get('exchange')
        tradingsymbol = request.form.get('tradingsymbol')
        quantity = request.form.get('quantity', 0)
        discloseqty = request.form.get('discloseqty', 0)
        price_type = request.form.get('price_type')
        price = request.form.get('price', '0.0')
        trigger_price = request.form.get('trigger_price', '0.0')
        retention = request.form.get('retention')
        amo = request.form.get('amo')
        remarks = request.form.get('remarks', None)

        # Convert to appropriate types with default values
        quantity = int(quantity) if quantity else 0
        discloseqty = int(discloseqty) if discloseqty else 0
        price = float(price) if price else 0.0
        trigger_price = float(trigger_price) if trigger_price else 0.0
        
        # Log the received parameters
        logging.debug(f"Received order parameters: buy_or_sell={buy_or_sell}, product_type={product_type}, exchange={exchange}, tradingsymbol={tradingsymbol}, quantity={quantity}, discloseqty={discloseqty}, price_type={price_type}, price={price}, trigger_price={trigger_price}, retention={retention}, amo={amo}, remarks={remarks}")
        
        # Validate parameters
        if not buy_or_sell or not product_type or not exchange or not tradingsymbol:
            logging.error("Required form fields are missing")
            return redirect(url_for('order_failure'))

        # Call the API to place the order
        ret = api.place_order(
            buy_or_sell=buy_or_sell.upper(),  # Ensure uppercase for buy/sell
            product_type=product_type,
            exchange=exchange,
            tradingsymbol=tradingsymbol,
            quantity=quantity,
            discloseqty=discloseqty,
            price_type=price_type,
            price=price,
            trigger_price=trigger_price,
            retention=retention,
            amo=amo,
            remarks=remarks
        )
        
        # Log and handle the response
        if ret is None:
            logging.error("API returned None")
            return redirect(url_for('order_failure'))
        
        logging.debug(f"Order placement response: {ret}")
        
        if ret.get('stat') == 'Ok':
            return redirect(url_for('order_success'))
        else:
            # Log the response for debugging
            logging.error(f"Order placement failed: {ret}")
            return redirect(url_for('order_failure'))
    except KeyError as e:
        logging.error(f"KeyError: Missing form data: {e}")
        return render_template('error.html', message=f"Missing form data: {e}")
    except ValueError as e:
        logging.error(f"ValueError: Incorrect data format: {e}")
        return render_template('error.html', message=f"Incorrect data format: {e}")
    except Exception as e:
        logging.error(f"Exception occurred: {e}")
        return render_template('error.html', message=f"An error occurred: {e}")



@app.route('/order_success')
def order_success():
    return "Order placed successfully!"

@app.route('/order_failure')
def order_failure():
    error_message = request.args.get('error', 'An error occurred')
    return f"Order placement failed: {error_message}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
