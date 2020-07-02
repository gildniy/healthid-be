
def round_off_selling_price(val):

    price = float(val) + 0.001
    selling_price = round(price)

    return int(selling_price)
