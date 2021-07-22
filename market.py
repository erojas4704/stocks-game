"""Exposes methods for retrieving and handling stock market data."""
import requests
from threading import Timer
import os
from yahooquery import Ticker

API_KEY = os.environ.get("API_KEY")
EXCHANGES = os.environ.get("EXCHANGES").split(",")
tickers = {}

calls = 0

#TODO find a way to delay calls that are ignored.
#TODO make calls asynchronous, if possible.

MAX_CALLS_PER_MINUTE = 30


def search(term):
    """Search for a symbol using a term. This will use Finnhub to search for now so we will be rate limiting ourselves."""
    resp = requests.get(f'https://finnhub.io/api/v1/search?q={term}&token={API_KEY}')
    json = resp.json()

    #last ditch effort to catch other errors
    if json.get("error"):
        print("There's been an error")
        print(json["error"])
        return json

    return json

def basic_details(symbol):
    """Using a stock's symbol, return a dict containing information for a stock."""
    ticker = get_ticker(symbol)
    #print(results)
    #ticker = results[symbol]
    quote_type = ticker.quote_type
    info = quote_type[symbol]

    print(info)

    details = {
        "name": info['longName'],
    }
    
    return details


def quote(symbol):
    """Using a stock's symbol, return a dict containing pricing for the stock"""
    global calls
    ticker = get_ticker(symbol)

    #move to isquotevalid function
    if ticker.quotes == "No data found":
        return None

    quote = ticker.quotes.get(symbol)

    if quote == None :
        return None

    print(f"THI SIS THE QUOTE {quote}")

    if quote['fullExchangeName'].upper() not in EXCHANGES:
        print(f"{symbol} is not in a valid exchange")
        return None

    
    try:
        price_dict = {
            "c": quote["regularMarketPrice"],
            "pc": quote["regularMarketPreviousClose"],
            "h": quote["regularMarketDayHigh"],
            "l": quote["regularMarketDayLow"],
            "o": quote["regularMarketOpen"]
        }
    except KeyError as err:
        print(f"ERROR getting quote for [{symbol}]:: \n {err}")
        return None

    return price_dict

def get_ticker(symbol):
    """Return a Ticker object for a stock."""
    global tickers

    if symbol in tickers:
        return tickers[symbol]

    ticker = Ticker(symbol)
    tickers[symbol] = ticker
    return ticker

def reset_calls():
    """reset the call counter."""
    global calls
    calls = 0