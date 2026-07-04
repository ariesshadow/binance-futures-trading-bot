import os

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from dotenv import load_dotenv

from bot.logging_config import setup_logger

load_dotenv()

logger = setup_logger("bot.client")


class BinanceClientError(Exception):
    pass


def get_client() -> Client:
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        logger.error("API key/secret not found in environment variables.")
        raise BinanceClientError(
            "BINANCE_API_KEY and BINANCE_API_SECRET must be set in your .env file."
        )

    try:
        # testnet=True makes python-binance route all Futures REST calls
        # through Client.FUTURES_TESTNET_URL (https://testnet.binancefuture.com/fapi).
        # Binance kept this host live for API traffic even after retiring its
        # old standalone testnet website in favour of the unified Demo Trading UI.
        client = Client(api_key, api_secret, testnet=True)
        logger.info("Binance Futures Demo client initialized. Base URL: %s", client.FUTURES_TESTNET_URL)
        return client
    except (BinanceAPIException, BinanceRequestException) as exc:
        logger.error("Failed to initialize Binance client: %s", exc)
        raise BinanceClientError(f"Failed to initialize Binance client: {exc}") from exc
