$( () => {

    const data = $("#session-data");
    const playerID = data.data("playerid");
    const gameID = data.data("gameid");
    const marketTable = $("#shares-market")
    const playerTable = $("#shares-owned")
    let playerStats;
    let selectedSymbol;
    let stockData = {};

    function getRow(symbol, table = marketTable){
        let result;
        $(".stock-row", table).each( (i, node) => {
            let row = $(node);
            
            if( $(".s-symbol", row).text().trim() == symbol ){
                result = row;
            }
        });

        return result;
    }

    function updateListing(symbol){
        let row = getRow(symbol);

        $(".loader", row).show();
        getStockDetails(symbol).then(
            data => {
                renderRow(symbol, data);
                $(".loader", row).hide();
            }
        );
    }

    function renderRow(symbol, data){
        row = getRow(symbol);
        if(!row) return;

        if(playerStats){
            $(".s-shares" , row).text( getShares(symbol) );
            $(".s-equity" , row).text( formatMoney( getEquity(symbol) ) );
            $(".s-return" , row).text( "0.00" );
        }

        if(data){
            $(".s-open" , row).text( formatMoney(data.open) );
            $(".s-close" , row).text( formatMoney(data.close) );
            $(".s-high" , row).text( formatMoney(data.high) );
            $(".s-low" , row).text( formatMoney(data.low) );
            $(".s-current" , row).text( formatMoney(data.current) );
        }

        console.log(stockData);
    }

    function getShares(symbol){
        let stock = getOwnedStock(symbol);
        return stock?.quantity || 0;
    }

    function getEquity(symbol){
        let stock = getOwnedStock(symbol);
        
        if(stock)
            return stockData[symbol].current * stock.quantity;
        else
            return 0;
    }

    function getOwnedStock(symbol){
        let stock;
        playerStats.stocks.some(s => {
            if(s.symbol == symbol){
                stock = s;
                return true;
            }
        });
        return stock;
    }

    function populatePurchaseForm(element){
        let node = $(element);
        let symbol = $(".s-symbol", node).text().trim();
        let name = $(".s-name", node).text().trim();

        selectedSymbol = symbol;

        renderSidePanel(selectedSymbol);

        $("#pp-symbol").text(symbol);

        getStockDetails(symbol).then( data => {
            $("#pp-name").text(name);
            $("#pp-current").text( formatMoney(data.current));
        });
    }

    async function tradeHandler(evt){
        let stock = await getStockDetails(selectedSymbol);
        let buying = $(evt.delegateTarget).data("purchase");
        let modalBody = generateBuyModal(stock, buying);

        openModal(`${buying? "Purchasing": "Selling"} ${selectedSymbol}`,
            modalBody , {
                label: buying? "Purchase" : "Sell", 
                class: "btn-primary",
                keepOpen: true
        }, ).then(purchaseConfirmationHandler);

        $("#purchase_dollar_amt").on("input", evt => {
            let amount = evt.delegateTarget.value;
            $("#purchase_stock_amt").val( calculateStockFromPrice(stock, amount))
        });
        
        $("#purchase_stock_amt").on("input", evt => {
            let amount = evt.delegateTarget.value;
            $("#purchase_dollar_amt").val( calculatePriceFromStock(stock, amount))
        });
    }

    function purchaseConfirmationHandler(userResponse){
        if(userResponse.action == "purchase" || userResponse.action == "sell"){
            let route = userResponse.action == "purchase"? "buy" : "sell";

            if(!(userResponse.form["price_amt"] && userResponse.form["stocks_amt"])){
                tradeHandler({delegateTarget: route == "buy"? $("#btn_buy")[0] : $("#btn_sell")[0]}) //Ugly Workaround
                setTimeout( () => {
                    $("#modal_error").text("Please properly fill out the fields.");
                 }, 400); //Ugly Workaround

                return;
            }

            lockModal();
            alterModal("Executing Trade...",`
                <div class="row justify-content-center">
                    <div class="loader spinner-border text-info spinner-border-lg"></div>
                </div>
            `);
            executeTrade(route, userResponse.form["price_amt"], userResponse.form["stocks_amt"], selectedSymbol)
            .then( data => {
                unlockModal();
                console.log(data);
                if(data.response)
                    openModal('Success!', data.response);
                else if(data.error)
                    openModal('Error', data.error);
            });
        }
    }

    function calculateStockFromPrice(stock, amount){
        return Math.floor(amount / stock.current);
    }

    function calculatePriceFromStock(stock, amount){
        return Math.floor((amount * stock.current) * 100) / 100;
    }

    async function executeTrade(type, amount, stock, symbol){
        try{
            resp = await axios.post(`/games/${gameID}/trade/${type}`, {
                stock,
                amount,
                symbol
            },{
                headers: {
                    'Content-Type': 'application/json;charset=UTF-8',
                    "Access-Control-Allow-Origin": "*",
                }
            });
        }catch(error){
            return {error};
        }

        if(!resp.data.error){
            renderPlayerStats(resp.data.player);
            renderPlayerOwnedStocks();
        }
        //console.log(resp.data);
        return resp.data;
    }
    
    function generateBuyModal(stock, buyMode){
        let html = `
            <div class="pb-3"> ${buyMode? "Purchasing" : "Selling" } at ${formatMoney(stock.current)} each</div>
            <form>
                <div class="form-group">
                    <label for="purchase_dollar_amt">Amount ($)</label>
                    <input min="0" type="number" class="form-control" name="price_amt" id="purchase_dollar_amt" placeholder="0" ${buyMode? '' : 'disabled'}>
                </div>
                
                <div class="form-group">
                    <label for="purchase_stock_amt">Stocks</label>
                    <input min="0" type="number" class="form-control" name="stocks_amt" id="purchase_stock_amt" placeholder="0">
                </div>

                <div id="modal_error" class="text-danger"></div>
            </form>
        `

        return html;
    }

    function renderPlayerStats(stats){
        playerStats = stats;
        $("#plr-balance").text(`Balance: ${formatMoney(stats.balance)}`);

    }

    function renderSidePanel(symbol){
        let stock = getOwnedStock(symbol);
        if(stock) $("#sp-shares").text(stock.quantity);
        else  $("#sp-shares").text("0");
    }

    function renderPlayerOwnedStocks(){
        playerStats.stocks.forEach(stock => {
            renderRow(stock.symbol);
            if(selectedSymbol == stock.symbol){
                renderSidePanel(selectedSymbol);
            }
        });

    }

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

        stockData[symbol] = resp.data;

        return resp.data;
    }

    async function getPlayerStats(gameID){
        let resp = await axios.get(`/api/games/${gameID}/player`)

        renderPlayerStats(resp.data);
        return resp.data;
    }
    
    //Hide all spinners
    $(".loader").hide();


    function updateAllListings(){
        $(".s-symbol").each( (i, node) => {
            let symbol = node.innerText;
            updateListing(symbol);
        });
    }

    function populatePlayerStocks(){
        playerStats.stocks.forEach(stock => {

            let row = getRow(stock, playerTable);
            
            if(!row){
                createRow(stock.symbol, playerTable);
            }else{
                let st = stockData[symbol];
                if(!stock){
                    getStockDetails(symbol).then( data => {
                        renderRow(stock.symbol, data);
                    });
                }

                renderRow(stock.symbol, st);
            }
        });
    }

    async function createRow(symbol, table){
        let stock = stockData[symbol];
        if(!stock)
            stock = await getStockDetails(symbol);

        let playerStock = getOwnedStock(symbol);

        console.log("Got stock ", stock);
        console.log(table);
        console.log($('tbody', table));

        $('tbody', table).append(`
            <tr class="stock-row">
                <th> <div class="loader spinner-border text-info spinner-border-sm d-none"></div> </th>
                <td> <span class="badge badge-success s-symbol"> ${symbol} </span></td>
                <td class="s-name">${stock.name}</td>
                <td class="s-shares">${formatMoney( playerStock.quantity)}</td>
                <td class="s-equity">${formatMoney( playerStock.quantity * stock.current )}</td>
                <td class="s-return"></td>
                <td class="s-current">${stock.current}</td>
            </tr>      
        `);
    }


    getPlayerStats(gameID).then( resp => {
        playerStats = resp;
        populatePlayerStocks();
        updateAllListings();
    });

    $("#btn-buy").click(tradeHandler);
    $("#btn-sell").click(tradeHandler);
    
    $(".stock-row").click( "tr",  e => {
        populatePurchaseForm(e.delegateTarget)
    });
});