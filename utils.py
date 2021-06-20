from locale import setlocale, format, LC_ALL
from math import floor

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
    last_digit = str(place)[-1]

    if place > 9:
        tenths = int( str(place)[-2])

        if tenths < 20 and tenths > 9:
            return f"{place}th"

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


def total_sort(player):
    return player.get_total_worth()


def worth_sort(player):
    return player.final_value


def seconds_to_english(seconds):
    """Returns seconds into a human read-able format"""
    minutes = floor(seconds / 60)
    hours = floor(minutes / 60)
    days = floor(hours / 24)

    str_days = f'{str( days )} days' if days > 0 else ''
    str_hours = f'{str( hours % 2 )} hours'  if hours > 0 else ''
    str_minutes = f'{str( minutes % 60 )} minutes' if minutes > 0 else 'less than a minute'

    return f'{str_days} {str_hours} {str_minutes}'
