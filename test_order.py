import os
import yaml
import pyotp
from NorenRestApiPy.NorenApi import NorenApi

# Load the configuration from the YAML file
config_file = 'cred.yml'
if os.path.exists(config_file):
    try:
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
    except yaml.YAMLError as e:
        print(f"Error loading YAML file: {e}")
        raise
else:
    raise FileNotFoundError(f"Config file {config_file} not found!")

# Check if all required keys are present in the config
required_keys = ['user', 'pwd', 'factor2', 'vc', 'apikey', 'imei']
for key in required_keys:
    if key not in config:
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
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/', websocket='wss://api.shoonya.com/NorenWSTP/')
        global api
        api = self

# Initialize API and log in
api = ShoonyaApiPy()
ret = api.login(userid=user, password=pwd, twoFA=factor2, vendor_code=vc, api_secret=apikey, imei=imei)
print(f"Login response: {ret}")

def test_place_order():
    try:
        # Print parameters being sent to the API
        order_params = {
            'buy_or_sell': 'BUY',
            'product_type': 'C',
            'exchange': 'NSE',
            'tradingsymbol': 'IDEA-EQ',
            'quantity': 1,
            'discloseqty': 0,
            'price_type': 'MARKET',
            'price': None
        }
        print(f"Order Parameters: {order_params}")
        
        # Place the order
        response = api.place_order(
            buy_or_sell=order_params['buy_or_sell'],
            product_type=order_params['product_type'],
            exchange=order_params['exchange'],
            tradingsymbol=order_params['tradingsymbol'],
            quantity=order_params['quantity'],
            discloseqty=order_params['discloseqty'],
            price_type=order_params['price_type'],
            price=order_params['price']
        )
        
        if response:
            print("Test Order Response:", response)
        else:
            print("No response received from place_order.")
    except Exception as e:
        print("Test Order Error:", str(e))

test_place_order()
