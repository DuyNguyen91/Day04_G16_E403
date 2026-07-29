import requests

def get_crypto_price(symbol: str = "BTCUSDT") -> dict:
    """Lấy giá crypto sử dụng Binance API."""
    try:
        symbol = symbol.upper()
        if not symbol.endswith("USDT"):
             if symbol == "BTC":
                 symbol = "BTCUSDT"
             else:
                 symbol += "USDT" # Default to USDT pair if not specified
             
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 400:
             return {"error": f"Không tìm thấy mã giao dịch: {symbol}. Hãy thử lại bằng mã khác (ví dụ BTC, ETH).", "data": None}
             
        response.raise_for_status()
        data = response.json()
        
        return {
            "error": None,
            "data": {
                "symbol": data.get("symbol"),
                "current_price": data.get("lastPrice"),
                "price_change_percent": data.get("priceChangePercent") + "%",
                "volume": data.get("volume")
            }
        }
    except Exception as e:
        return {
            "error": f"Lỗi truy xuất giá crypto: {str(e)}",
            "data": None
        }
