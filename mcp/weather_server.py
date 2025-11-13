

from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather-mcp")

_WEATHER_DATA = {
    "seattle": {
        "conditions": "showers",
        "temperature_c": 12,
        "humidity": 82,
    },
    "new york": {
        "conditions": "sunny",
        "temperature_c": 18,
        "humidity": 55,
    },
    "london": {
        "conditions": "overcast",
        "temperature_c": 14,
        "humidity": 70,
    },
}


@mcp.tool()
def list_supported_cities() -> list[str]:
    """Return the cities that have canned weather data."""

    return sorted(_WEATHER_DATA)


@mcp.tool()
def get_weather(city: str) -> str:
    """Return the current conditions for a city."""

    record = _WEATHER_DATA.get(city.lower())
    if not record:
        supported = ", ".join(list_supported_cities())
        return f"No data for {city}. Try one of: {supported}."

    temp_f = round(record["temperature_c"] * 9 / 5 + 32, 1)
    timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    intro = (
        f"As of {timestamp} UTC, {city.title()} reports "
        f"{record['conditions']} skies"
    )
    temps = f"{record['temperature_c']}°C/{temp_f}°F"
    return f"{intro}, {temps}, humidity {record['humidity']}%."


if __name__ == "__main__":
    mcp.run(transport="stdio")
