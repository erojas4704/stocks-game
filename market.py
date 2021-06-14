"""Exposes methods for retrieving and handling stock market data."""
import requests
from secrets import API_KEY
from threading import Timer

calls = 0


r = requests.get('https://finnhub.io/api/v1/search?q=apple&token=c30l912ad3i9gms5vfs0')

def basic_details(symbol):
    """Using a stock's symbol, return a dict containing information for a stock"""
    global calls

    #Keep us under the rate limit. Ignore calls that would exceed it.
    if calls >= 60:
        print("***ABOUT TO EXCEED RATE LIMIT***")
        return False
    elif calls == 0:
        Timer(1.0, reset_calls).start()
    
    calls += 1

    resp = requests.get(f'https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={API_KEY}')

    json = resp.json()
    #last ditch effort to catch other errors
    if json.get("error"):
        print("WE HAVE BEEN RATE LIMITED")
        return False

    return json

    
def quote(symbol):
    """Using a stock's symbol, return a dict containing pricing for the stock"""
    global calls

    #Keep us under the rate limit. Ignore calls that would exceed it.
    if calls >= 60:
        return False
    elif calls == 0:
        Timer(1.0, reset_calls).start()
    
    calls += 1

    print(f"RIGHT NOW WE ARE AT {calls} CALLS")

    resp = requests.get(f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}')

    json = resp.json()
    #last ditch effort to catch other errors
    if json.get("error"):
        print("WE HAVE BEEN RATE LIMITED")
        return False

    return resp.json()

def reset_calls():
    """reset the call counter."""
    global calls
    calls = 0