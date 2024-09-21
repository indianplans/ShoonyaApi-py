from flask import Flask, request, jsonify, render_template
import pyotp
from NorenRestApiPy.NorenApi import NorenApi
import logging

app = Flask(__name__)

# Enable debugging to see request and responses
logging.basicConfig(level=logging.DEBUG)

# Initialize the Shoonya API
class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/', websocket='wss://api.shoonya.com/NorenWSTP/')
        global api
        api = self

# Initialize API and credentials
api = ShoonyaApiPy()
user = 'FA338316'
pwd = 'Zulekha88@89'
factor2 = pyotp.TOTP('UHTJ3357D77ZQ447W45464VCD76JX757').now()
vc = 'FA338316_U'
app_key = 'fae6cadbd02755a67f7977eae25f4f20'
imei = 'abc1234'

# Login
ret = api.login(userid=user, password=pwd, twoFA=factor2, vendor_code=vc, api_secret=app_key, imei=imei)
print(ret)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/orders')
def orders():
    # Logic to fetch and display orders
    # Example placeholder content
    return '<h1>Order Picking Page</h1><p>Here you can pick and manage orders.</p>'

@app.route('/portfolio')
def portfolio():
    # Logic to fetch and display portfolio
    # Example placeholder content
    return '<h1>Portfolio Page</h1><p>Here you can view and manage your portfolio.</p>'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Received data:", data)
    
    if data:
        # Here you would process the data and place orders or other actions
        return jsonify({"status": "success", "message": "Order placed successfully!"})
    else:
        return render_template('error.html', message="No data received")

if __name__ == '__main__':
    app.run(port=5000)
