import pyotp
import time
from NorenRestApiPy.NorenApi import NorenApi
from threading import Timer
import logging
import pyotp  # Ensure you have this library installed

class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/', websocket='wss://api.shoonya.com/NorenWSTP/')        
        global api
        api = self

# Enable debugging to see request and responses
logging.basicConfig(level=logging.DEBUG)

# Start of the program
api = ShoonyaApiPy()

# Credentials
user    = 'FA338316'
pwd     = 'Zulekha88@89'
factor2 = pyotp.TOTP('UHTJ3357D77ZQ447W45464VCD76JX757').now()  # Replace 'YOUR_TOTP_SECRET' with your actual TOTP secret
vc      = 'FA338316_U'
app_key = 'fae6cadbd02755a67f7977eae25f4f20'
imei    = 'abc1234'

# Make the API call using the correct variable name for user ID
ret = api.login(userid=user, password=pwd, twoFA=factor2, vendor_code=vc, api_secret=app_key, imei=imei)

print(ret)
api.get_limits()
