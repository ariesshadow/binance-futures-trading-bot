import argparse
import sys

from bot.client import BinanceClientError, get_client
from bot.logging_config import setup_logger
from bot.orders import OrderPlacementError, place_order, print_order_result
from bot.validators import ValidationError, validate_order_input

logger = setup_logger("bot.cli")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Simplified Trading Bot for Binance Futures Demo (Testnet)"
    )
    parser.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, choices=["BUY", "SELL", "buy", "sell"], help="Order side")
    parser.add_argument(
        "--type",
        dest="order_type",
        required=True,
        choices=["MARKET", "LIMIT", "STOP_LIMIT", "market", "limit", "stop_limit"],
        help="Order type",
    )
    parser.add_argument("--quantity", required=True, help="Order quantity")
    parser.add_argument("--price", required=False, default=None, help="Price (required for LIMIT and STOP_LIMIT orders)")
    parser.add_argument("--stop-price", dest="stop_price", required=False, default=None, help="Stop trigger price (required for STOP_LIMIT orders)")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        order_input = validate_order_input(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValidationError as exc:
        logger.error("Validation failed: %s", exc)
        print(f"ERROR: {exc}")
        sys.exit(1)

    try:
        client = get_client()
    except BinanceClientError as exc:
        logger.error("Client initialization failed: %s", exc)
        print(f"ERROR: {exc}")
        sys.exit(1)

    try:
        response = place_order(client, order_input)
    except OrderPlacementError as exc:
        print(f"FAILED: {exc}")
        sys.exit(1)

    print_order_result(response)


if __name__ == "__main__":
    main()
