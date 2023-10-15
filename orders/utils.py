import datetime

def generate_order_number(pk):
    # year month date hour minutes seconds pk
    current_datetime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    order_number = current_datetime + str(pk)
    return order_number