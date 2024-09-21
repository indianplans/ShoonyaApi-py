from api_helper import ShoonyaApiPy
import logging
import pyotp

# Enable debugging to see request and responses
logging.basicConfig(level=logging.DEBUG)

# Start of the program
api = ShoonyaApiPy()

# Credentials
user = 'FA338316'
pwd = 'Zulekha88@89'
factor2 = pyotp.TOTP('UHTJ3357D77ZQ447W45464VCD76JX757').now()
vc = 'FA338316_U'
apikey = 'fae6cadbd02755a67f7977eae25f4f20'
imei = 'abc1234'
print("Generated OTP:", factor2)

# Make the API call
ret = api.login(userid=user, password=pwd, twoFA=factor2, vendor_code=vc, api_secret=apikey, imei=imei)

print(ret)
