from datetime import datetime
from typing import Optional

import uvicorn
from eunomia_mcp import create_eunomia_middleware
from fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP(
    name="Planetary Weather 🪐",
    instructions="Get weather information for planets in our solar system",
)


class WeatherRequest(BaseModel):
    date: Optional[str] = Field(
        default=datetime.now().strftime("%Y-%m-%d"),
        description="The date to get the weather for in format YYYY-MM-DD",
    )


@mcp.tool()
def get_mars_weather(request: WeatherRequest) -> str:
    """Get the weather on Mars for a given date"""
    return f"The weather on Mars on {request.date} was sunny with dust storms in the afternoon"


@mcp.tool()
def get_jupiter_weather(request: WeatherRequest) -> str:
    """Get the weather on Jupiter for a given date"""
    return f"The weather on Jupiter on {request.date} was cloudy with massive storm systems"


@mcp.tool()
def get_saturn_weather(request: WeatherRequest) -> str:
    """Get the weather on Saturn for a given date"""
    return f"The weather on Saturn on {request.date} was windy with hexagonal storm patterns at the north pole"


@mcp.tool()
def get_venus_weather(request: WeatherRequest) -> str:
    """Get the weather on Venus for a given date"""
    return f"The weather on Venus on {request.date} was extremely hot (462°C) with sulfuric acid rain"


middleware = [create_eunomia_middleware()]
app = mcp.http_app(middleware=middleware)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
