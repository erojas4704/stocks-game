if(!sessionStorage.getItem('stockData'))
    sessionStorage.setItem('stockData', {});


/**Get stock details from our server API.
 * If we are rate limited, we will only receive old data.
 */
    async function getStockDetails(symbol, forceRemote = false){
    //TODO error handling
    //We'll cache a version of the stock in localstorage
    if(sessionStorage.stockData[symbol]){
        let = data = sessionStorage.stockData[symbol];

        //Return cached data if it's less than 2 minutes old
        if( (Date.now - data.updated)/60000 < 2 )
            return sessionStorage.stockData[symbol];
    }

    let resp = await axios.get('/api/stock',{
        params:{
            symbol
        }
    });

    sessionStorage.stockData[symbol] = resp;
    sessionStorage.stockData[symbol].updated = Date.now();

    return resp.data;
}

/**Search for a stock by the symbol or company name.
 */
async function findStock(term){
    let resp = await axios.get(`/api/stock/search?term=${term}`)
    return resp.data;
}

async function getPlayerStats(gameID){
    let resp = await axios.get(`/api/games/${gameID}/player`)
    return resp.data;
}

async function getGameInfo(gameID){
    let resp = await axios.get(`/api/games/${gameID}/info`)
    return resp.data;
}

async function getMessages(gameID){
    let resp = await axios.get(`/api/games/${gameID}/messages`)
    return resp.data;
}