let getR;

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
    //TODO erase
    getR = getRow;


    function updateListing(symbol){
        let row = getRow(symbol);

        populateRowWithSpinners(row);
        
        getStockDetails(symbol).then(
            data => {
                stockData[symbol] = data;
                clearSpinners(row);
                renderRow(symbol, data);
                $(".loader", row).hide();
            }
        );
    }

    function populateRowWithSpinners(row){
        //TODO doesn't work $("td:not('td.s-symbol')", row).html(`<div class="loader spinner-border text-info spinner-border-sm"></div>`);

       $(".s-name", row).html(`<div class="loader spinner-border text-info spinner-border-sm"></div>`);
       $(".s-performance", row).html(`<div class="loader spinner-border text-info spinner-border-sm"></div>`);
       $(".s-shares", row).html(`<div class="loader spinner-border text-info spinner-border-sm"></div>`);
       $(".s-equity", row).html(`<div class="loader spinner-border text-info spinner-border-sm"></div>`);
       $(".s-return", row).html(`<div class="loader spinner-border text-info spinner-border-sm"></div>`);
    }

    function clearSpinners(row){
        $(".loader", row).remove();
    }

    function renderRow(symbol, data, table = marketTable){
        let row = getRow(symbol);
        if(!row) return;

        if(playerStats){

            let returns = 0;
            
            if(stockData[symbol] && getOwnedStock(symbol)){
                returns = calculateReturn(getOwnedStock(symbol), stockData[symbol]); 
            }

            let stockPerformance = data.current - data.open;

            $(".s-name" , row).text( data.name );
            $(".s-shares" , row).text( getShares(symbol) );
            $(".s-equity" , row).text( formatMoney( getEquity(symbol) ) );
            $(".s-return" , row).text( formatMoney( returns , true) || formatMoney(0) );
            $(".s-performance", row).html(formatMoney(stockPerformance, true, true));
            $(".s-performance", row).removeClass("text-danger text-success");
            $(".s-performance", row).addClass(getMoneyClass(stockPerformance));


            $(".s-return", row).removeClass("text-danger text-success");
            let classes = "";

            if(returns > 0){
                classes = "text-success"
            }else if( returns < 0){
                classes = "text-danger";
            }
            $(".s-return", row).addClass(classes);
            //${formatMoney( calculateReturn(playerStock, stock) ) || formatMoney(0)}
        }

        if(data){
            $(".s-open" , row).text( formatMoney(data.open) );
            $(".s-close" , row).text( formatMoney(data.close) );
            $(".s-high" , row).text( formatMoney(data.high) );
            $(".s-low" , row).text( formatMoney(data.low) );
            $(".s-current" , row).text( formatMoney(data.current) );
        }

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
        

        getStockDetails(symbol, true).then( data => {
            stockData[symbol] = data;
            
            let stockPerformance = data.current - data.open;
            $("#pp-performance").html(formatMoney(stockPerformance, true, true));
            $("#pp-performance").removeClass("text-danger text-success");
            $("#pp-performance").addClass(getMoneyClass(stockPerformance));

            $("#pp-name").text(name);
            $("#pp-current").text( formatMoney(data.current));
            $("#pp-price").text( formatMoney(data.current) );
            $("#pp-open").text( formatMoney(data.open) );
            $("#pp-close").text( formatMoney(data.close) );
            $("#pp-high").text( formatMoney(data.high) );
            $("#pp-low").text( formatMoney(data.low) );
        });
        
        $("#form_purchase").show();
    }

    async function tradeHandler(evt){
        let stock = await getStockDetails(selectedSymbol);
        stockData[selectedSymbol] = stock;

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
                playerData = data.player;
                populatePlayerStocks();
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
            <div class=""> ${buyMode? "Purchasing" : "Selling" } at ${formatMoney(stock.current)} each</div>
            <div>Available balance: ${formatMoney(playerStats.balance)}</div>
            <div>${buyMode? "" : `Shares available: ${getOwnedStock(stock.symbol).quantity}`} </div>
            <form class="pt-3">
                <div class="form-group">
                    <label for="purchase_dollar_amt">Amount ($)</label>
                    <input min="0" type="number" class="form-control" name="price_amt" id="purchase_dollar_amt" placeholder="0" ${buyMode? '' : 'disabled'}>
                </div>
                
                <div class="form-group">
                    <label for="purchase_stock_amt">Shares</label>
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

    async function renderPlayerOwnedStocks(){
        playerStats.stocks.forEach(async stock => {
            if(!stockData[stock]){
                stockData[stock] = await getStockDetails(stock.symbol);
            }
            renderRow(stock.symbol, stockData[stock.symbol]);
            if(selectedSymbol == stock.symbol){
                renderSidePanel(selectedSymbol);
            }
        });

    }

    /**Get stock details from our server API.
     * If we are rate limited, we will only receive old data.
     */
    /*
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
    */

    function updateAllListings(){
        $(".s-symbol").each( (i, node) => {
            let symbol = node.innerText;
            updateListing(symbol);
        });
    }

    function populatePlayerStocks(){
        playerStats.stocks.forEach(stock => {
            symbol = stock.symbol;
            let row = getRow(symbol, playerTable);
            
            if(!row){
                createRow(stock.symbol, playerTable);
            }else{
                let st = stockData[symbol];
                if(!stock){
                    getStockDetails(symbol).then( data => {
                        stockData[symbol] = data;
                        renderRow(stock.symbol, data);
                    });
                }else{
                    renderRow(stock.symbol, st);
                }
            }
        });
    }

    function calculateReturn(playerStock, stock){
        let value = 0;
        value = stock.current * playerStock.quantity - playerStock.money_spent;
        console.log(stock, playerStock);
        return value;
    }

    async function createRow(symbol, table){
        let stock = stockData[symbol];
        console.log(stock, symbol);

        if(!stock){
            stock = await getStockDetails(symbol);
            stockData[symbol] = stock;
        }

        let playerStock = getOwnedStock(symbol);

        let stockPerformance = stock.current - stock.open;

        //TODO copy an existing template instea of remaking it here
        $('tbody', table).append(`
            <tr class="stock-row">
                <td> <span class="badge badge-success s-symbol"> ${symbol} </span></td>
                <td class="s-name d-none d-lg-table-cell">${stock.name}</td>
                <td class="s-performance d-none d-lg-table-cell ${getMoneyClass(stockPerformance)}">${formatMoney(stockPerformance, true, true)}</td>
                <td class="s-shares">${playerStock?.quantity || 0}</td>
                <td class="s-equity d-none d-lg-table-cell">${formatMoney( (playerStock?.quantity || 0)* stock.current )}</td>
                <td class="s-return">${formatMoney( playerStock? calculateReturn(playerStock, stock) : 0 ) || formatMoney(0)}</td>
                <td class="s-current">${stock.current}</td>
            </tr>      
        `);
    }

    function filterOwnedStocks(owned){
        if(owned){
            $(".stock-row").each( (i, el) => {
                let quantity = $(el).find(".s-shares").text();
                if(Number(quantity) > 0){
                    $(el).show();
                } else{
                    $(el).hide();
                }
            });
        }
        else{
            $(".stock-row").show();
        }
    }
    
    function filter(term = "", ownedOnly=false){
        term = term.toLowerCase().trim();

        $(".stock-row").each( (i, el) => {
            let symbolNode = $(el).find(".s-symbol");
            let nameNode = $(el).find(".s-name");
            let shares = Number( $(el).find(".s-shares").text() );
            let termFound = symbolNode.text().toLowerCase().trim().includes(term) || nameNode.text().toLowerCase().trim().includes(term);

            if(term.length < 1) termFound = true;
            
            if( termFound && (ownedOnly ? shares > 0 : true)
            ){
                $(el).show();
            } else{
                $(el).hide();
            }
        });
    }

    $("#form-search").submit(async e => {
        e.preventDefault();
        let val = $("#input-search").val();
        //$("#input-search").val("");

        openModal();
        alterModal("Searching...",`
        <div class="row justify-content-center">
            <div class="loader spinner-border text-info spinner-border-lg"></div>
        </div>`)
        lockModal();

        let resp = await findStock(val)
        .catch( err => {
            openModal("Error", err);
        });
        
        unlockModal();
        closeModal();

        if(resp?.error){
            return;
        }
        
        //TODO only show results in table
        //TODO allow multiple results
        resp.stocks.forEach(stock => {
            stockData[stock.symbol] = stock;
            if(!getRow(stock.symbol)) createRow(stock.symbol)
        });
        console.log(resp);
    });
    
    $("#input-search").on("input", evt => {
        let term = evt.delegateTarget.value;
        let owned = $("#own-filter input:checked").val() == "true";

        filter(term, owned);
    });

    $("#input-search").on("blur", e => {
    });

    
    $("#btn-buy").click(tradeHandler);
    $("#btn-sell").click(tradeHandler);
    
    $("tbody").click( "tr",  e => {
        let delegate = $(e.target).parent("tr");
        populatePurchaseForm(delegate)
    });

    $("#own-filter input").change( e => {
        let checked = $("#own-filter input:checked");
        let onlyOwned = checked.val() == "true";

        filter($("#input-search").val(), onlyOwned);
    });

    $("#form_purchase").hide();
    
    getPlayerStats(gameID).then( resp => {
        playerStats = resp;
        renderPlayerOwnedStocks(resp)
        populatePlayerStocks();
        updateAllListings();
    });
});