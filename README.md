# Binance Futures Testnet Trading Bot

Small Python CLI app for placing `MARKET` and `LIMIT` orders on Binance Futures Testnet (USDT-M).

## Features

- Signed REST calls to `https://testnet.binancefuture.com`
- Supports `BUY` and `SELL`
- Supports `MARKET` and `LIMIT`
- Validates symbol, side, order type, quantity, and limit price
- Prints a request summary and compact response details
- Logs structured JSON request, response, and error records to a log file
- Keeps API/client code separate from CLI and order validation logic

## Setup

1. Create and activate a Python 3 virtual environment.

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies.

   ```powershell
   pip install -r requirements.txt
   ```

3. Create Binance Futures Testnet API credentials from your Binance Futures Testnet account.

4. Set credentials in your shell.

   ```powershell
   $env:BINANCE_FUTURES_TESTNET_API_KEY = "your_testnet_key"
   $env:BINANCE_FUTURES_TESTNET_API_SECRET = "your_testnet_secret"
   ```

## Run Examples

Market buy:

```powershell
python .\cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

Limit sell:

```powershell
python .\cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 70000
```

Use a custom log path:

```powershell
python .\cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --log-file .\logs\market_run.log
```

Pass credentials directly instead of environment variables:

```powershell
python .\cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --api-key "key" --api-secret "secret"
```

## Output

The app prints:

- order request summary
- order response details: `orderId`, `status`, `executedQty`, `avgPrice`, and related fields
- clear success or failure message
- log file location

## Logs

Runtime logs are JSON-lines records written to `logs/trading_bot.log` by default.

Sample deliverable logs are included:

- `logs/sample_market_order.log`
- `logs/sample_limit_order.log`

These sample files show the expected structure for successful testnet `MARKET` and `LIMIT` calls. Real runs will create or append to the configured runtime log file.

## Assumptions

- This project targets Binance USD-M Futures Testnet only.
- Symbols are expected to be USDT-M futures symbols such as `BTCUSDT`.
- Limit orders use `timeInForce=GTC`.
- `newOrderRespType=RESULT` is requested so the response includes useful execution details when Binance returns them.
- API secrets are never logged. Request signatures are also omitted from logs.
