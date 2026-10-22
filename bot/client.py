from __future__ import annotations

import hashlib
import hmac
import logging
import time
from typing import Any
from urllib.parse import urlencode

import requests

from .exceptions import BinanceAPIError, BinanceNetworkError


LOGGER = logging.getLogger(__name__)
DEFAULT_BASE_URL = "https://testnet.binancefuture.com"


class BinanceFuturesClient:
    """Small signed REST client for Binance USDT-M Futures Testnet."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 10,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        if not api_secret:
            raise ValueError("api_secret is required")

        self.api_key = api_key
        self.api_secret = api_secret.encode("utf-8")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    def place_order(self, **params: Any) -> dict[str, Any]:
        """Place an order using POST /fapi/v1/order."""

        return self._signed_request("POST", "/fapi/v1/order", params)

    def _signed_request(self, method: str, path: str, params: dict[str, Any]) -> dict[str, Any]:
        request_params = {
            key: value
            for key, value in params.items()
            if value is not None
        }
        request_params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(request_params, doseq=True)
        signature = hmac.new(self.api_secret, query_string.encode("utf-8"), hashlib.sha256).hexdigest()
        signed_params = {**request_params, "signature": signature}

        safe_params = {key: value for key, value in request_params.items() if key != "signature"}
        LOGGER.info(
            "binance_request",
            extra={
                "extra": {
                    "event": "request",
                    "method": method,
                    "path": path,
                    "base_url": self.base_url,
                    "params": safe_params,
                }
            },
        )

        url = f"{self.base_url}{path}"
        try:
            response = self.session.request(method, url, params=signed_params, timeout=self.timeout)
        except requests.RequestException as exc:
            LOGGER.exception(
                "binance_network_error",
                extra={"extra": {"event": "network_error", "method": method, "path": path}},
            )
            raise BinanceNetworkError(f"Network failure while calling Binance: {exc}") from exc

        try:
            payload = response.json()
        except ValueError:
            payload = {"raw": response.text}

        LOGGER.info(
            "binance_response",
            extra={
                "extra": {
                    "event": "response",
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "body": payload,
                }
            },
        )

        if response.status_code >= 400:
            message = payload.get("msg") if isinstance(payload, dict) else response.text
            code = payload.get("code") if isinstance(payload, dict) else response.status_code
            LOGGER.error(
                "binance_api_error",
                extra={
                    "extra": {
                        "event": "api_error",
                        "status_code": response.status_code,
                        "code": code,
                        "message": message,
                    }
                },
            )
            raise BinanceAPIError(f"Binance API error {code}: {message}")

        if not isinstance(payload, dict):
            raise BinanceAPIError("Unexpected Binance response format.")
        return payload
