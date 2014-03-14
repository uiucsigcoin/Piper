import requests
import hmac
import hashlib
import time
import json

class CoinbaseAPI(object):
    base_url = "https://coinbase.com/api/v1"

    def __init__(self, key=None, secret=None):
        self.api_key = key
        self.api_secret = secret

    def _post(self, path, body=None):
        url = self.base_url + path
        nonce = int(time.time() * 1e6)
        message = str(nonce) + url + ('' if body is None else body)
        signature = hmac.new(self.api_secret, message, hashlib.sha256).hexdigest()
        headers = {'ACCESS_KEY': self.api_key,
                   'ACCESS_SIGNATURE': signature,
                   'ACCESS_NONCE': nonce,
                   'Content-type':'application/json',
                   'Accept': 'text/plain'
                   }
        r = requests.post(url, headers=headers, data=body)
        if r.status_code != 200:
            print "ERROR"
            return r.text
        else:
            return r.json()

    def _get(self, path):
        url = self.base_url + path
        nonce = int(time.time() * 1e6)
        message = str(nonce) + url 
        signature = hmac.new(self.api_secret, message, hashlib.sha256).hexdigest()
        headers = {'ACCESS_KEY': self.api_key,
                   'ACCESS_SIGNATURE': signature,
                   'ACCESS_NONCE': nonce,
                   'Content-type':'application/json',
                   'Accept': 'text/plain'
                   }
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            print "ERROR"
            return r.text
        else:
            return r.json()

    def send_coins(self, address, amount, currency="BTC", instant_buy=False, message="", tx_fee=0.0002):
        path = "/transactions/send_money"
        if amount <= 0:
            raise "Amount must be more than 0!"
        body =  {'transaction': {
                "instant_buy": instant_buy,
                "to": address,
                "notes": message,
                "user_fee": tx_fee
                }
                 }
        if currency == "BTC":
            body["transaction"]["amount"] = str(amount)
        else:
            body["transaction"]["amount_currency_iso"] = currency
            body["transaction"]["amount_string"] = str(amount)
        return self._post(path, json.dumps(body))

    def exchange_rates(self):
        path = "/currencies/exchange_rates"
        return self._get(path)

if __name__ == '__main__':
    from settings import *
    TEST_ADDR = "1PSVt9AxYCHpTDGTCaVf8KSB1CPEG6Cgyj"
    coinbase = CoinbaseAPI(key=COINBASE_KEY, secret=COINBASE_SECRET)
    rates = coinbase.exchange_rates()
    btc_to_usd = float(rates["btc_to_usd"])
    usd_to_btc = float(rates["usd_to_btc"])
    minimum_for_no_fee = 0.001
    print "Sending a few coins!"
    amount = 0.05
    if amount < minimum_for_no_fee * btc_to_usd:
        fee = COINBASE_MIN_TX_FEE
    else:
        fee = 0
    print "fee: {0}".format(fee)
    transaction = coinbase.send_coins(TEST_ADDR, 0.05,
                                      currency="USD",
                                      message="Testing for EOH",
                                      tx_fee=fee)
    print transaction
