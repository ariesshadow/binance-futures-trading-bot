# Simplified Trading Bot (Binance Futures Demo/Testnet)

A small Python CLI application that places MARKET and LIMIT orders on
Binance Futures Demo Trading (USDT-M), with input validation, structured
code layers, and logging of every request/response/error.

## Project Structure

```
trading_bot/
  bot/
    __init__.py
    client.py           # Binance client setup (API layer)
    orders.py            # Order placement logic
    validators.py        # CLI input validation
    logging_config.py    # Logging setup
  cli.py                 # CLI entry point
  logs/
    trading_bot.log      # Generated automatically at runtime
  requirements.txt
  .env.example
  README.md
```

## Setup (Windows)

1. **Clone or download this repository**

2. **Create and activate a virtual environment**
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Set up your API credentials**
   - Copy `.env.example` to `.env`
   - Open `.env` and paste your Binance Demo Trading API Key and Secret Key:
     ```
     BINANCE_API_KEY=your_api_key_here
     BINANCE_API_SECRET=your_api_secret_here
     ```
   - Get these keys from https://demo.binance.com → Futures → Account → API Management
     (choose "System generated" and enable Futures trading)

## How to Run

### Place a MARKET order
```
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

### Place a LIMIT order
```
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 65000
```

### Place a STOP_LIMIT order (bonus feature)
```
python cli.py --symbol BTCUSDT --side SELL --type STOP_LIMIT --quantity 0.01 --price 59000 --stop-price 59500
```
This places a stop-limit order: once the market price hits the stop price
(`59500`), a LIMIT order is triggered at the given price (`59000`).

### Invalid input example (for testing validation)
```
python cli.py --symbol BTCUSDT --side HOLD --type MARKET --quantity 0.01
```
This will print a validation error and exit without calling the API.

## Output

For every order, the CLI prints:
1. An order request summary (symbol, side, type, quantity, price)
2. The order response (orderId, status, executedQty, avgPrice)
3. A success/failure message

All requests, responses, and errors are also written to `logs/trading_bot.log`.

## Assumptions

- This project uses the **Binance Futures Demo Trading** environment. The
  underlying `python-binance` client is initialized with `testnet=True`,
  which routes all Futures REST calls through
  `https://testnet.binancefuture.com/fapi`. Binance kept this host active
  for API traffic even after retiring the old standalone testnet website
  in favour of the unified Demo Trading UI at demo.binance.com.
- Only MARKET and LIMIT order types were implemented as per the core
  requirements. LIMIT orders use `GTC` (Good-Til-Cancelled) as the time in force.
- API keys are read from a local `.env` file and are never committed to
  version control (see `.gitignore`).
- Quantity and price precision/step-size rules for each symbol (e.g. lot
  size filters) are enforced by Binance itself; the CLI does not duplicate
  exchange-specific filter validation beyond basic type/positivity checks.

## Bonus

Implemented a third order type: **STOP_LIMIT**. Binance migrated conditional
order types (STOP, STOP_MARKET, TAKE_PROFIT, etc.) off the classic
`POST /fapi/v1/order` endpoint in late 2025 — they now require the newer
`POST /fapi/v1/algoOrder` endpoint. Since the installed `python-binance`
version predates this change, `bot/orders.py` calls the new endpoint
directly via the client's internal signed-request helper
(`client._request_futures_api`), using `algoType=CONDITIONAL`,
`type=STOP`, `price` (limit price once triggered), and `triggerPrice`
(the stop trigger).
