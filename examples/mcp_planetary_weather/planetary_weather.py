from typing import Literal

from eunomia_mcp.middleware import EunomiaMcpMiddleware
from fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP(
    name="Planetary Weather 🪐",
    instructions="Get weather information for planets in our solar system",
)


class WeatherRequest(BaseModel):
    time: Literal["day", "night"] = Field(
        default="day",
        description="The time of day to get the weather for",
    )


@mcp.tool()
def get_mars_weather(request: WeatherRequest) -> str:
    """Get the weather on Mars for a given time of day"""
    return f"The weather on Mars at {request.time} was sunny with dust storms in the afternoon"


@mcp.tool()
def get_jupiter_weather(request: WeatherRequest) -> str:
    """Get the weather on Jupiter for a given time of day"""
    return f"The weather on Jupiter at {request.time} was cloudy with massive storm systems"


@mcp.tool()
def get_saturn_weather(request: WeatherRequest) -> str:
    """Get the weather on Saturn for a given time of day"""
    return f"The weather on Saturn at {request.time} was windy with hexagonal storm patterns at the north pole"


@mcp.tool()
def get_venus_weather(request: WeatherRequest) -> str:
    """Get the weather on Venus for a given time of day"""
    return f"The weather on Venus at {request.time} was extremely hot (462°C) with sulfuric acid rain"


mcp.add_middleware(EunomiaMcpMiddleware())

if __name__ == "__main__":
    mcp.run()
