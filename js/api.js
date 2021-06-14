

/**Get stock details from our server API.
 * If we are rate limited, we will only receive old data.
 */
    async function getStockDetails(symbol){
    //TODO error handling
    let resp = await axios.get('/api/stock',{
        params:{
            symbol
        }
    });

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