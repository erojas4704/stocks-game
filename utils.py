from locale import setlocale, format, LC_ALL

#setlocale(LC_ALL, 'en_US')

def format_money(amount = 0, signed=False):
    sign = ""
    if signed and amount != 0:
        sign = "+" if amount > 0 else "-"

    return f'{sign}${format("%.2f", amount, grouping=True)}'

def get_money_class(amount):
    if amount == 0: return ""
    return "text-success" if amount > 0 else "text-danger"

def get_ordinal(place):
    print(str(place))
    last_digit = str(place)[-1]
    ordinals = {
        '0': "th",
        '1': "st",
        '2': "nd",
        '3': "rd",
        '4': "th",
        '5': "th",
        '6': "th",
        '7': "th",
        '8': "th",
        '9': "th",
    }

    return f"{place}{ordinals[last_digit]}"

def worth_sort(player):
    return player.final_value
