function formatMoney(value, signed = false, triangle=false){
    let sign = "";
    let prefix = "";

    if(signed && value < 0)
        sign = "-";
    else if(signed && value > 0)
        sign = "+";
    
    if(triangle && value > 0){
        prefix = "&#9650; ";
    }else if(triangle && value < 0){
        prefix = "&#9660; ";
    }

    let fixedAmount = Math.abs(value).toFixed(2);


    fixedAmount = fixedAmount.replace(/\B(?=(\d{3})+(?!\d))/g, ",");

    return `${prefix}${sign}$${fixedAmount}`
}

function getTotalSpentByPlayer(player){
    let total = 0;
    player.stocks.forEach(stock => {
        total += stock.money_spent
    });
    return total;
}

function formatMessageString(message){
    let reg = /%s(.*?)%/ig;
    
    return message.replaceAll(reg, `<div class="stock-symbol badge badge-success">$1</div>`)
}

function getMoneyClass(amount){
    if (amount == 0) return "";
    if(amount > 0) return "text-success";
    return "text-danger";
}

function getOrdinal(val){
    val = String(val);
    let lastChar = val.slice(-1);
    let tenths = Number(val.slice(-2));

    if(tenths > 9 && tenths < 20){
        return `${val}th`
    }

    return `${val}${{
        '0': 'th',
        '1': 'st',
        '2': 'nd',
        '3': 'rd',
        '4': 'th',
        '5': 'th',
        '6': 'th',
        '7': 'th',
        '8': 'th',
        '9': 'th'
    }[lastChar]}`;
}