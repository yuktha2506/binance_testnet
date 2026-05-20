"""Application-specific exceptions."""


class TradingBotError(Exception):
    """Base exception for user-facing trading bot failures."""


class ValidationError(TradingBotError):
    """Raised when CLI input is invalid."""


class BinanceAPIError(TradingBotError):
    """Raised when Binance returns an API error."""


class BinanceNetworkError(TradingBotError):
    """Raised when a request to Binance cannot be completed."""
