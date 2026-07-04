from binance.exceptions import BinanceAPIException, BinanceOrderException, BinanceRequestException

from bot.logging_config import setup_logger

logger = setup_logger("bot.orders")


class OrderPlacementError(Exception):
    pass


def build_order_summary(order_input: dict) -> str:
    lines = [
        "----- ORDER REQUEST SUMMARY -----",
        f"Symbol   : {order_input['symbol']}",
        f"Side     : {order_input['side']}",
        f"Type     : {order_input['order_type']}",
        f"Quantity : {order_input['quantity']}",
    ]
    if order_input["order_type"] in ("LIMIT", "STOP_LIMIT"):
        lines.append(f"Price    : {order_input['price']}")
    if order_input["order_type"] == "STOP_LIMIT":
        lines.append(f"Stop Price : {order_input['stop_price']}")
    lines.append("---------------------------------")
    return "\n".join(lines)


def _place_regular_order(client, symbol, side, order_type, quantity, price):
    params = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
    }
    if order_type == "LIMIT":
        params["price"] = price
        params["timeInForce"] = "GTC"

    logger.debug("Sending request to Binance Futures Demo API (order): %s", params)
    return client.futures_create_order(**params)


def _place_algo_stop_limit_order(client, symbol, side, quantity, price, stop_price):
    # Binance migrated conditional order types (STOP, STOP_MARKET, TAKE_PROFIT, etc.)
    # to a dedicated Algo Order endpoint: POST /fapi/v1/algoOrder. The classic
    # POST /fapi/v1/order endpoint now rejects these with error -4120.
    params = {
        "algoType": "CONDITIONAL",
        "symbol": symbol,
        "side": side,
        "type": "STOP",
        "quantity": quantity,
        "price": price,
        "triggerPrice": stop_price,
        "timeInForce": "GTC",
    }
    logger.debug("Sending request to Binance Futures Demo API (algoOrder): %s", params)
    return client._request_futures_api("post", "algoOrder", True, data=params)


def place_order(client, order_input: dict) -> dict:
    symbol = order_input["symbol"]
    side = order_input["side"]
    order_type = order_input["order_type"]
    quantity = order_input["quantity"]
    price = order_input["price"]
    stop_price = order_input["stop_price"]

    summary = build_order_summary(order_input)
    print(summary)
    logger.info("Placing order:\n%s", summary)

    try:
        if order_type == "STOP_LIMIT":
            response = _place_algo_stop_limit_order(client, symbol, side, quantity, price, stop_price)
        else:
            response = _place_regular_order(client, symbol, side, order_type, quantity, price)
        logger.info("Order response received: %s", response)
        return response
    except (BinanceAPIException, BinanceOrderException) as exc:
        logger.error("Binance API rejected the order: %s", exc)
        raise OrderPlacementError(f"Order was rejected by Binance: {exc}") from exc
    except BinanceRequestException as exc:
        logger.error("Network/request error while placing order: %s", exc)
        raise OrderPlacementError(f"Network error while placing order: {exc}") from exc
    except Exception as exc:
        logger.exception("Unexpected error while placing order.")
        raise OrderPlacementError(f"Unexpected error: {exc}") from exc


def print_order_result(response: dict) -> None:
    order_id = response.get("orderId", response.get("algoId", "N/A"))
    status = response.get("status", response.get("algoStatus", "N/A"))
    executed_qty = response.get("executedQty", "N/A")
    avg_price = response.get("avgPrice", "N/A")

    print("----- ORDER RESPONSE -----")
    print(f"Order ID      : {order_id}")
    print(f"Status        : {status}")
    print(f"Executed Qty  : {executed_qty}")
    print(f"Avg Price     : {avg_price}")
    print("--------------------------")

    if status in ("NEW", "FILLED", "PARTIALLY_FILLED"):
        print(f"SUCCESS: Order {order_id} placed successfully.")
    else:
        print(f"WARNING: Order {order_id} returned status '{status}'.")
