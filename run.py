# -*- coding: utf-8 -*-
from flask import Flask, request, abort
from datetime import datetime, timezone
import requests, json, os

## CONSTANTS #####################################################################################
CYCLOS_ENDPOINT = os.getenv('CYCLOS_ENDPOINT')
CYCLOS_API_PATH = "/ca/api"
CYCLOS_AUTH_PATH = "/auth"

FX_ENPOINT = "https://v6.exchangerate-api.com"
FX_API_KEY = os.getenv('FX_API_KEY')
FX_API_PATH = f"/v6/{FX_API_KEY}/latest"

## VARIABLES #####################################################################################
fx_cache_data = {}

## APP CONTROLLERS ###############################################################################
app = Flask(__name__)

@app.route('/exchangerate/<currency>', methods=['GET', 'POST'])
def exchangerate(currency):
    auth_token = request.headers.get('Session-Token')
    if cyclosAuth(auth_token):
        return getFXrates(currency)
    abort(403)

@app.route('/exchangerate/public', methods=['GET', 'POST'])
def exchangeratepublic():
    return getFXrates('CAD')

## APP LOGIC #####################################################################################
def cyclosAuth(token):
    if token is None or token == "":
        return False
    request_url = CYCLOS_ENDPOINT + CYCLOS_API_PATH + CYCLOS_AUTH_PATH
    request_headers = {
        'channel': 'mobile',
        'Session-Token': token
    }
    response = requests.request("GET", request_url, headers=request_headers, data={})
    return response.status_code == 200

def getFXrates(currency):
    global fx_cache_data
    fx_cache = getFXcache(currency)
    if fx_cache is None:
        request_url = FX_ENPOINT + FX_API_PATH + f"/{currency}"
        response = requests.request("GET", request_url, headers={}, data={})
        fx_cache_data[currency] = response.json()
        return response.json()
    return fx_cache

def getFXcache(currency):
    if currency is None or currency == "":
        return None
    if currency in fx_cache_data:
        datetime_string_format = '%a, %d %b %Y %H:%M:%S %z'
        time_last_update_utc = datetime.strptime(fx_cache_data[currency]['time_last_update_utc'], datetime_string_format)
        time_next_update_utc = datetime.strptime(fx_cache_data[currency]['time_next_update_utc'], datetime_string_format)
        if datetime.now(timezone.utc) > time_last_update_utc and datetime.now(timezone.utc) < time_next_update_utc:
            return fx_cache_data[currency]
    return None

## APP START #####################################################################################
if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=8080)
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
