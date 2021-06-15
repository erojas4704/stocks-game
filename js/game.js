$(() => {
    const data = $("#session-data");
    const gameID = data.data("gameid");
    let game;
    let pollTimer = 0;
    let timerActive = true;
    let stockData = {};

    const POLLRATE = 1;

    //TODO poll the server every X amount of seconds. We'll be moving to sockets soon instead of this.


    getGameInfo(gameID).then( resp => {
        game = resp;
        console.log(game);
        setInterval(gameTick, 1000);
    });

    function calculatePortfolioValue(player){
        //Calculate the value of of the player using local stockdata.
        let value = 0;
        let invalid = false;
        
        player.stocks.forEach( stock => {
            if(! stockData["symbol"]) {
                return;
            }

            let cost = stockData["symbol"].current;
            value += cost;
        });

        return value;
    }

    function gameTick(){
        let secondsRemaining = Math.floor((new Date(game.end) - Date.now())/1000);
        updateTimer(secondsRemaining);
    }

    function renderAllPlayers(players){
        players.forEach( player => {
            renderPlayer(player);
        });
    }

    function wipeFrame(frame){
        $('.g-name', frame).html("")
        $('.g-portfolio', frame).html("");
        $('.g-balance', frame).html("");
        $('.g-total', frame).html("");
        $('.g-return', frame).html("");
    }
    
    function createPlayerFrame(player){
        //Copy the first frame so we only have to edit it there.
        let frame = $(".player-frame")
            .first()
            .clone()
            .appendTo("#list-players");

        console.log(player.id);
        console.log(frame);

        frame.attr("data-playerid", player.id);
        frame.removeClass("active");
        
        wipeFrame(frame);

        return frame;
    }

    function renderPlayer(player){
        let frame = getPlayerFrame(player.id);
        console.log(`Renedering ${player.id}`);
        console.log("Frame", frame)

        if(frame.length < 1){
            //Frame does not exist
            console.log("Creating frame for player ", player.id);
            frame = createPlayerFrame(player);
        }
        let total = player.portfolio + player.balance;
        let returns = player.portfolio - getTotalSpentByPlayer(player);
        let className = "";

        let portfolioValue = calculatePortfolioValue(player) || player.portfolio;

        if(returns > 0 ){
            className = "text-success";
        }else if(returns < 0){
            className = "text-danger";
        }

        $('.g-name', frame).text(player.user.displayname)
        $('.g-portfolio', frame).text(`Portfolio: ${formatMoney(portfolioValue)} `);
        $('.g-balance', frame).text(`Balance: ${formatMoney(player.balance)} `);
        $('.g-total', frame).text(`Total: ${formatMoney(total)} `);
        $('.g-return', frame).html(`Return: <span class="${className} font-weight-bold">${formatMoney(returns, true)} </span>`);
    }

    function getPlayerFrame(id){
        return $(`.player-frame[data-playerid='${id}']`)
    }

    async function getAndRenderStateFromRemote(){
        let resp = await getGameInfo(gameID);
        console.log(resp);

        game = resp;

        await getAllOwnedStocks(game.players);
        renderAllPlayers(game.players);
        console.log(stockData);
        return resp;
    }

    async function getAllOwnedStocks(players){
        players.forEach( p => {
            p.stocks.forEach( async s => {
                stock = await getStockDetails(s.symbol);
                stockData[s.symbol] = stock;
            });
        })
    }

    function updateTimer(secondsRemaining){
        $("#timer").text("Game ends in " + secondsToEnglish(secondsRemaining));
        console.log(secondsRemaining);

        if(secondsRemaining < 0 ){
            $("#timer").text('');
        }

        if(timerActive) {
            pollTimer ++;
            if(pollTimer > POLLRATE){
                pollTimer = 0;
                timerActive = false;
                //Wait for it to load before doing anything else
                getAndRenderStateFromRemote().then( r => {
                    timerActive = true;
                });
            }
        }


    }

    function secondsToEnglish(seconds){
        let minutes = seconds / 60 | 0;
        let hours = minutes / 60 | 0;
        let days = hours / 24 | 0;

        return `${days > 0? `${days} days` : ''}  ${ hours > 0? `${hours % 24} hours` : ''}  ${ minutes > 0? `${minutes % 60} minutes` : ''}  ${seconds % 60} seconds`
    }
});