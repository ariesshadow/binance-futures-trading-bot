import re

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_LIMIT"}
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{5,15}$")


class ValidationError(Exception):
    pass


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not SYMBOL_PATTERN.match(symbol):
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Expected format like BTCUSDT."
        )
    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(f"Invalid side '{side}'. Must be BUY or SELL.")
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be MARKET, LIMIT, or STOP_LIMIT."
        )
    return order_type


def validate_quantity(quantity) -> float:
    try:
        quantity = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(f"Quantity must be a number, got '{quantity}'.")
    if quantity <= 0:
        raise ValidationError("Quantity must be greater than 0.")
    return quantity


def validate_price(price, order_type: str):
    if order_type in ("LIMIT", "STOP_LIMIT"):
        if price is None:
            raise ValidationError(f"Price is required for {order_type} orders.")
        try:
            price = float(price)
        except (TypeError, ValueError):
            raise ValidationError(f"Price must be a number, got '{price}'.")
        if price <= 0:
            raise ValidationError("Price must be greater than 0.")
        return price
    return None


def validate_stop_price(stop_price, order_type: str):
    if order_type == "STOP_LIMIT":
        if stop_price is None:
            raise ValidationError("Stop price is required for STOP_LIMIT orders.")
        try:
            stop_price = float(stop_price)
        except (TypeError, ValueError):
            raise ValidationError(f"Stop price must be a number, got '{stop_price}'.")
        if stop_price <= 0:
            raise ValidationError("Stop price must be greater than 0.")
        return stop_price
    return None


def validate_order_input(symbol, side, order_type, quantity, price, stop_price=None):
    symbol = validate_symbol(symbol)
    side = validate_side(side)
    order_type = validate_order_type(order_type)
    quantity = validate_quantity(quantity)
    price = validate_price(price, order_type)
    stop_price = validate_stop_price(stop_price, order_type)
    return {
        "symbol": symbol,
        "side": side,
        "order_type": order_type,
        "quantity": quantity,
        "price": price,
        "stop_price": stop_price,
    }
