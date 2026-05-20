"""Command line interface for the Binance Futures Testnet trading bot."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from typing import Any

from bot.client import BinanceFuturesClient, DEFAULT_BASE_URL
from bot.exceptions import BinanceAPIError, BinanceNetworkError, TradingBotError, ValidationError
from bot.logging_config import configure_logging
from bot.orders import OrderRequest, place_order


LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Place MARKET and LIMIT orders on Binance Futures Testnet (USDT-M)."
    )
    parser.add_argument("--symbol", required=True, help="USDT-M futures symbol, for example BTCUSDT.")
    parser.add_argument("--side", required=True, help="BUY or SELL.")
    parser.add_argument("--type", required=True, dest="order_type", help="MARKET or LIMIT.")
    parser.add_argument("--quantity", required=True, help="Order quantity, for example 0.001.")
    parser.add_argument("--price", help="Limit price. Required for LIMIT orders.")
    parser.add_argument("--api-key", default=os.getenv("BINANCE_FUTURES_TESTNET_API_KEY"))
    parser.add_argument("--api-secret", default=os.getenv("BINANCE_FUTURES_TESTNET_API_SECRET"))
    parser.add_argument("--base-url", default=os.getenv("BINANCE_FUTURES_TESTNET_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--log-file", default="logs/trading_bot.log")
    return parser


def compact_response(response: dict[str, Any]) -> dict[str, Any]:
    return {
        "orderId": response.get("orderId"),
        "status": response.get("status"),
        "executedQty": response.get("executedQty"),
        "avgPrice": response.get("avgPrice"),
        "clientOrderId": response.get("clientOrderId"),
        "symbol": response.get("symbol"),
        "side": response.get("side"),
        "type": response.get("type"),
    }


def print_json(title: str, payload: dict[str, Any]) -> None:
    print(f"\n{title}")
    print(json.dumps(payload, indent=2, default=str))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    log_path = configure_logging(args.log_file)

    try:
        order = OrderRequest.from_cli(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )

        if not args.api_key or not args.api_secret:
            raise ValidationError(
                "API credentials are required. Set BINANCE_FUTURES_TESTNET_API_KEY and "
                "BINANCE_FUTURES_TESTNET_API_SECRET, or pass --api-key and --api-secret."
            )

        print_json("Order request summary:", order.summary())
        client = BinanceFuturesClient(
            api_key=args.api_key,
            api_secret=args.api_secret,
            base_url=args.base_url,
        )
        response = place_order(client, order)
        print_json("Order response details:", compact_response(response))
        print(f"\nSUCCESS: {order.order_type} {order.side} order submitted. Logs: {log_path}")
        return 0

    except ValidationError as exc:
        LOGGER.error("validation_error", extra={"extra": {"event": "validation_error", "message": str(exc)}})
        print(f"\nFAILURE: {exc}", file=sys.stderr)
        print(f"Logs: {log_path}", file=sys.stderr)
        return 2
    except (BinanceAPIError, BinanceNetworkError) as exc:
        print(f"\nFAILURE: {exc}", file=sys.stderr)
        print(f"Logs: {log_path}", file=sys.stderr)
        return 1
    except TradingBotError as exc:
        LOGGER.exception("trading_bot_error", extra={"extra": {"event": "trading_bot_error"}})
        print(f"\nFAILURE: {exc}", file=sys.stderr)
        print(f"Logs: {log_path}", file=sys.stderr)
        return 1
    except Exception as exc:
        LOGGER.exception("unexpected_error", extra={"extra": {"event": "unexpected_error"}})
        print(f"\nFAILURE: Unexpected error: {exc}", file=sys.stderr)
        print(f"Logs: {log_path}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
