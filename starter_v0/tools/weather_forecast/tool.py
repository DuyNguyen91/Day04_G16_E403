import requests
import urllib.parse

def get_weather(location: str = "") -> dict:
    """Lấy thông tin thời tiết sử dụng wttr.in."""
    try:
        # Use format 3 for wttr.in which returns: location: condition, temperature
        loc_param = urllib.parse.quote(location) if location else ""
        url = f"https://wttr.in/{loc_param}?format=3"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        return {
            "error": None,
            "weather": response.text.strip()
        }
    except Exception as e:
        return {
            "error": f"Lỗi truy xuất thời tiết: {str(e)}",
            "weather": ""
        }
