from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("Hello Weather MCP", json_response=True)


@mcp.tool()
def say_hello(name: str) -> str:
    """Return a greeting for the given name."""
    return f"Hello, {name}"


@mcp.tool()
def get_weather(city: str) -> dict:
    """
    Return current weather for a city using Open-Meteo.
    No API key required.
    """

    # Step 1: Geocode city name
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    geo_response = requests.get(geo_url, params=geo_params, timeout=10)
    geo_response.raise_for_status()
    geo_data = geo_response.json()

    if "results" not in geo_data or not geo_data["results"]:
        return {
            "error": f"City not found: {city}"
        }

    location = geo_data["results"][0]
    latitude = location["latitude"]
    longitude = location["longitude"]

    # Step 2: Get current weather
    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
    }

    weather_response = requests.get(weather_url, params=weather_params, timeout=10)
    weather_response.raise_for_status()
    weather_data = weather_response.json()

    current = weather_data["current"]

    return {
        "city": location["name"],
        "country": location.get("country"),
        "temperature_c": current["temperature_2m"],
        "humidity_percent": current["relative_humidity_2m"],
        "wind_speed_kmh": current["wind_speed_10m"],
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
