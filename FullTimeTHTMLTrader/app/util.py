import requests
import hashlib

ENDPOINT = "https://api.iextrading.com/1.0"
CALL = "/stock/{symbol}/price"
salt = "its a secret to everyone"

def hash_pass(password):
    # salted 128 character hash of a string
    hasher = hashlib.sha512()
    value = password.encode() + salt.encode()
    hasher.update(value)
    return hasher.hexdigest()

def get_price(symbol):
    response = requests.get(ENDPOINT + CALL.format(symbol=symbol))
    if response.status_code == 200:
        return response.json()
    else:
        raise requests.ConnectionError('http status: ' + format(response.status_code))