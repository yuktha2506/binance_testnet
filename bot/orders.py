"""Order placement logic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .client import BinanceFuturesClient
from .validators import validate_order_inputs


@dataclass(frozen=True)
class OrderRequest:
    symbol: str
    side: str
    order_type: str
    quantity: str
    price: str | None = None

    @classmethod
    def from_cli(
        cls,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: str | None,
    ) -> "OrderRequest":
        values = validate_order_inputs(symbol, side, order_type, quantity, price)
        return cls(
            symbol=values["symbol"],
            side=values["side"],
            order_type=values["type"],
            quantity=values["quantity"],
            price=values["price"],
        )

    def to_binance_params(self) -> dict[str, Any]:
        params: dict[str, Any] = {
            "symbol": self.symbol,
            "side": self.side,
            "type": self.order_type,
            "quantity": self.quantity,
            "newOrderRespType": "RESULT",
        }
        if self.order_type == "LIMIT":
            params["price"] = self.price
            params["timeInForce"] = "GTC"
        return params

    def summary(self) -> dict[str, str | None]:
        return {
            "symbol": self.symbol,
            "side": self.side,
            "type": self.order_type,
            "quantity": self.quantity,
            "price": self.price,
        }


def place_order(client: BinanceFuturesClient, order: OrderRequest) -> dict[str, Any]:
    return client.place_order(**order.to_binance_params())
