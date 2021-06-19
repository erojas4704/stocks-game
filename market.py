"""Exposes methods for retrieving and handling stock market data."""
import requests
from threading import Timer
import os

API_KEY = os.environ.get("API_KEY")

calls = 0

#TODO find a way to delay calls that are ignored.
#TODO make calls asynchronous, if possible.


def search(term):
    """Search for a symbol using a term"""
    resp = requests.get(f'https://finnhub.io/api/v1/search?q={term}&token={API_KEY}')
    json = resp.json()

    #last ditch effort to catch other errors
    if json.get("error"):
        print("There's been an error")
        print(json["error"])
        return json

    return json


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
        print("There's been an error")
        return json

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

    print(f"[MARKET]: Currently we are at {calls} calls.")

    resp = requests.get(f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}')

    json = resp.json()
    #last ditch effort to catch other errors
    if json.get("error"):
        print("There's been an error")
        return json

    

    return resp.json()

def reset_calls():
    """reset the call counter."""
    global calls
    calls = 0