function formatMoney(value, signed = false){
    let sign = "";
    if(signed && value < 0)
        sign = "-";
    else if(signed && value > 0)
        sign = "+";

    let fixedAmount = Math.abs(value).toFixed(2);


    fixedAmount = fixedAmount.replace(/\B(?=(\d{3})+(?!\d))/g, ",");

    return `${sign}$${fixedAmount}`
}

function getTotalSpentByPlayer(player){
    let total = 0;
    player.stocks.forEach(stock => {
        total += stock.money_spent
    });
    return total;
}