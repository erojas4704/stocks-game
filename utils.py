from locale import setlocale, format, LC_ALL

setlocale(LC_ALL, 'en_US')

def format_money(amount):
    return f'${format("%.2f", amount, grouping=True)}'