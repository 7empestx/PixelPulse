#!/usr/bin/env python3
"""PixelPulse MCP Server — control the ESP32 LED matrix via Claude Code."""

import os
import json
import httpx
from mcp.server.fastmcp import FastMCP

PIXELPULSE_URL = os.environ.get("PIXELPULSE_URL", "http://pixelpulse.local")

mcp = FastMCP("pixelpulse")


async def api_request(method: str, path: str, body: dict | None = None) -> dict:
    """Make an HTTP request to the PixelPulse device."""
    url = f"{PIXELPULSE_URL}{path}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            if method == "GET":
                resp = await client.get(url)
            else:
                resp = await client.post(url, json=body or {})
            resp.raise_for_status()
            return resp.json()
    except httpx.ConnectError:
        return {"error": f"Device unreachable at {PIXELPULSE_URL}. Is PixelPulse powered on and connected to WiFi?"}
    except httpx.TimeoutException:
        return {"error": f"Device timed out at {PIXELPULSE_URL}. The ESP32 may be busy."}
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def get_status() -> str:
    """Get PixelPulse device status: current mode, brightness, uptime, WiFi signal, free heap."""
    result = await api_request("GET", "/api/status")
    return json.dumps(result)


@mcp.tool()
async def get_data() -> str:
    """Get live sensor data from PixelPulse: weather conditions, crypto price, flight departures."""
    result = await api_request("GET", "/api/data")
    return json.dumps(result)


@mcp.tool()
async def list_modes() -> str:
    """List all available display modes and which one is currently active."""
    result = await api_request("GET", "/api/modes")
    return json.dumps(result)


@mcp.tool()
async def set_mode(mode: str) -> str:
    """Switch the display to a specific mode by name (e.g. 'Weather', 'Crypto') or index (0-7)."""
    # If it's a number, use it directly
    try:
        index = int(mode)
        result = await api_request("POST", "/api/mode", {"index": index})
        return json.dumps(result)
    except ValueError:
        pass

    # Resolve name to index
    modes = await api_request("GET", "/api/modes")
    if "error" in modes:
        return json.dumps(modes)

    for i, name in enumerate(modes.get("modes", [])):
        if name.lower() == mode.lower():
            result = await api_request("POST", "/api/mode", {"index": i})
            return json.dumps(result)

    return json.dumps({"error": f"Unknown mode '{mode}'. Available: {modes.get('modes', [])}"})


@mcp.tool()
async def next_mode() -> str:
    """Advance to the next display mode."""
    result = await api_request("POST", "/api/mode/next")
    return json.dumps(result)


@mcp.tool()
async def previous_mode() -> str:
    """Go back to the previous display mode."""
    result = await api_request("POST", "/api/mode/prev")
    return json.dumps(result)


@mcp.tool()
async def set_paused(paused: bool) -> str:
    """Pause or resume automatic mode rotation. True = pause on current mode, False = resume cycling."""
    result = await api_request("POST", "/api/mode/pause", {"paused": paused})
    return json.dumps(result)


@mcp.tool()
async def set_brightness(brightness: int) -> str:
    """Set LED panel brightness. Range: 1 (dim) to 255 (max). Default is 50."""
    if brightness < 1 or brightness > 255:
        return json.dumps({"error": "Brightness must be between 1 and 255"})
    result = await api_request("POST", "/api/brightness", {"brightness": brightness})
    return json.dumps(result)


@mcp.tool()
async def get_config() -> str:
    """Get device configuration: city, crypto symbol, ICAO airport code, customer name."""
    result = await api_request("GET", "/api/config")
    return json.dumps(result)


@mcp.tool()
async def update_config(
    city: str | None = None,
    crypto: str | None = None,
    icao: str | None = None,
    customer_name: str | None = None,
) -> str:
    """Update device configuration. Only provided fields are changed. City affects weather, crypto sets the coin ticker (BTC/ETH/etc), ICAO sets the airport for flight data."""
    body = {}
    if city is not None:
        body["city"] = city
    if crypto is not None:
        body["crypto"] = crypto
    if icao is not None:
        body["icao"] = icao
    if customer_name is not None:
        body["customerName"] = customer_name

    if not body:
        return json.dumps({"error": "No fields provided to update"})

    result = await api_request("POST", "/api/config", body)
    return json.dumps(result)


if __name__ == "__main__":
    mcp.run(transport="stdio")
