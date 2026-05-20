"""Validation helpers for CLI input."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from .exceptions import ValidationError


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


def normalize_symbol(symbol: str) -> str:
    value = symbol.strip().upper()
    if not value:
        raise ValidationError("symbol is required.")
    if not value.isalnum():
        raise ValidationError("symbol must contain only letters and numbers, for example BTCUSDT.")
    if not value.endswith("USDT"):
        raise ValidationError("this bot is intended for USDT-M futures symbols, for example BTCUSDT.")
    return value


def normalize_side(side: str) -> str:
    value = side.strip().upper()
    if value not in VALID_SIDES:
        raise ValidationError("side must be BUY or SELL.")
    return value


def normalize_order_type(order_type: str) -> str:
    value = order_type.strip().upper()
    if value not in VALID_ORDER_TYPES:
        raise ValidationError("order type must be MARKET or LIMIT.")
    return value


def parse_positive_decimal(name: str, raw_value: str | None) -> Decimal:
    if raw_value is None or not str(raw_value).strip():
        raise ValidationError(f"{name} is required.")

    try:
        value = Decimal(str(raw_value).strip())
    except InvalidOperation as exc:
        raise ValidationError(f"{name} must be a valid decimal number.") from exc

    if value <= 0:
        raise ValidationError(f"{name} must be greater than 0.")
    return value


def validate_order_inputs(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None,
) -> dict[str, str]:
    normalized_type = normalize_order_type(order_type)
    normalized_price = None

    if normalized_type == "LIMIT":
        normalized_price = str(parse_positive_decimal("price", price))
    elif price is not None:
        raise ValidationError("price is only accepted for LIMIT orders.")

    return {
        "symbol": normalize_symbol(symbol),
        "side": normalize_side(side),
        "type": normalized_type,
        "quantity": str(parse_positive_decimal("quantity", quantity)),
        "price": normalized_price,
    }
