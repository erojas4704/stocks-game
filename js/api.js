
if(!localStorage.getItem('stockData')){
    localStorage.setItem('stockData', '{}');
}
/**Get stock details from our server API.
 * If we are rate limited, we will only receive old data.
 */
async function getStockDetails(symbol, forceRemote = false) {
    //TODO error handling
    //We'll cache a version of the stock in localstorage
    let stockCache = JSON.parse(localStorage.getItem('stockData'));
    
    if (!forceRemote && stockCache && stockCache[symbol]) {
        let data = stockCache[symbol];

        //Return cached data if it's less than 2 minutes old
        if ((Date.now() - data.updated) / 60000 < 5) {
            return stockCache[symbol];
        }
    }

    let resp = await axios.get('/api/stock', {
        params: {
            symbol
        }
    });
    
    //WORKAROUND. Because getStockDetail calls are asynchronous, another call may have altered stockData, so we need to pull it again.
    stockCache = JSON.parse(localStorage.getItem('stockData'));
    stockCache[symbol] = resp.data;
    stockCache[symbol].updated = Date.now();
    localStorage.setItem('stockData', JSON.stringify(stockCache));

    return resp.data;
}

/**Search for a stock by the symbol or company name.
 */
async function findStock(term) {
    let resp = await axios.get(`/api/stock/search?term=${term}`)
    return resp.data;
}

async function getPlayerStats(gameID) {
    let resp = await axios.get(`/api/games/${gameID}/player`)
    return resp.data;
}

async function getGameInfo(gameID) {
    let resp = await axios.get(`/api/games/${gameID}/info`)
    return resp.data;
}

async function getMessages(gameID) {
    let resp = await axios.get(`/api/games/${gameID}/messages`)
    return resp.data;
}

async function getGameHistory(gameID) {
    let resp = await axios.get(`/api/games/${gameID}/history`)
    return resp.data;
}