from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from config import DISCOUNT_PRECENT
from database.get_products import get_products_id

def get_prev_month(calc_date):
    current_month_start = calc_date.replace(day=1)
    if current_month_start == 1:
        prev_month_start = current_month_start.replace(year=current_month_start.year - 1, month=12)
    else:
        prev_month_start = current_month_start.replace(month=current_month_start.month - 1)
    return prev_month_start, current_month_start

def calc_final_price(price, has_orders_last_month):
    price = Decimal(price)
    if has_orders_last_month:
        return price
    mult = Decimal(100 - DISCOUNT_PRECENT) / Decimal(100)
    return (price * mult).quantize(Decimal("0.01"), rounding= ROUND_HALF_UP)

def apply_discount(products, calc_date=None):
    if calc_date is None:
        calc_date = date.today()
    per_start, per_end = get_prev_month(calc_date)
    order_id = get_products_id(per_start, per_end)
    for product in products:
        has_order = product["product_id"] in order_id
        product["final_price"] = calc_final_price(product["price"], has_order)
        product["has_discount"] = not has_order
    return products

def format_price(value):
    return f"{Decimal(value):,.2f} ₽".replace(","," ")