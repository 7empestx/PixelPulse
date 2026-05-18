# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

PixelPulse is an ESP32 Arduino firmware for a 64x32 HUB75 RGB LED matrix panel. It displays rotating modes (word clock, analog clock, weather, crypto prices, pixel art, Game of Life, flight departures) with a Mr. Robot green-on-black terminal aesthetic. Configuration is done via a WiFi captive portal on first boot, stored in NVS.

## Build Commands

```bash
# Build for real hardware (ESP32-DevKitC V4)
pio run

# Build for QEMU emulation (defines QEMU_BUILD, skips DMA init)
pio run -e qemu

# Run native unit tests (no hardware needed)
pio test -e native

# Flash to ESP32 (USB)
pio run --target upload

# OTA upload over WiFi (after first USB flash)
pio run -e esp32dev-ota --target upload

# Upload SPIFFS data
pio run --target uploadfs

# Serial monitor
pio device monitor

# Erase NVS (factory reset) then reflash
pio run --target erase && pio run --target upload

# Run Python simulator (requires pygame)
python3 simulator.py

# Run Python tests
pytest tests/

# Regenerate enclosure STLs (requires CadQuery on Python 3.11)
# System Python 3.14 is too new for CadQuery's OCP bindings.
# pyenv local 3.11.9 is set in .python-version (gitignored).
# To activate: eval "$(pyenv init --path)" && eval "$(pyenv init -)"
python enclosure/pixelpulse_body.py
python enclosure/pixelpulse_diffuser.py
```

## Serial Utilities

- `serial_read.py` — non-interactive serial reader for capturing ESP32 output. Usage: `python3 serial_read.py [port] [baud] [duration_sec]` (defaults: `/dev/cu.usbserial-0001`, 115200, 15s)

## MCP Server

`mcp_server.py` is an MCP server that exposes the PixelPulse REST API as tools Codex can call directly. It connects to the device at `$PIXELPULSE_URL` (default: `http://pixelpulse.local`). Registered in `.mcp.json` and loads automatically in Codex.

Tools: `get_status`, `get_data`, `list_modes`, `set_mode`, `next_mode`, `previous_mode`, `set_paused`, `set_brightness`, `get_config`, `update_config`.

```bash
# Install dependencies
pip3 install "mcp[cli]" httpx

# Test with MCP inspector
mcp dev mcp_server.py
```

## Architecture

### Application entry point

`main.cpp` is a trivial 8-line wrapper that creates a `PixelPulseApp` and delegates to `begin()`/`update()`. **All application logic lives in `PixelPulseApp`** — display init, WiFi connection, mode instantiation, and the main loop.

### Three build targets in `platformio.ini`

- `esp32dev` — real hardware with HUB75 DMA display
- `qemu` — emulation build that sets `-DQEMU_BUILD`, skips DMA/WiFi/SPIFFS, logs to serial only
- `native` — host-machine unit tests using Unity test framework

### Core components (`src/`)

- `PixelPulseApp.h/.cpp` — top-level application class. Owns all subsystems (`_dma`, `_font`, `_modeManager`, `_apiPoller`) as private members. Handles display init, WiFi, boot screen, and mode registration.
- `Config.h` — `PixelPulseConfig` struct, `ConfigManager` class (NVS persistence via `Preferences`), global constants (colors, timing, panel dimensions, HUB75 pin mapping, API intervals), and NVS key macros (`KEY_*`).
- `ModeManager.h/.cpp` — abstract `Mode` base class with `init()/update()/isDone()` interface; manages mode rotation (15s each) and glitch transitions.
- `FontRenderer.h/.cpp` — custom 4x6 and 6x8 pixel bitmap fonts for the LED matrix. Uses `FontSize` enum.
- `ApiPoller.h/.cpp` — non-blocking HTTP polling for weather (OpenWeatherMap), crypto (CoinGecko), and flights (OpenSky Network) with per-API intervals.

### Modes (`src/modes/`)

Each extends `Mode` and receives dependencies via constructor (display pointer, font, api poller as needed):

- `WordClockMode` — time as natural language with typewriter effect. Takes `(dma, font, customerName)`.
- `AnalogClockMode` — analog clock face with hour/minute/second hands. Takes `(dma)`.
- `WeatherMode` — current conditions from OpenWeatherMap. Takes `(dma, font, poller)`.
- `CryptoMode` — live price + 24h delta from CoinGecko. Takes `(dma, font, poller)`.
- `FlightMode` — nearest airport departures from OpenSky. Takes `(dma, font, poller)`.
- `PixelArtMode` — displays a 64x32 sprite from flash. Takes `(dma)`.
- `GameOfLifeMode` — Conway's Game of Life simulation. Takes `(dma)`.

**Adding a new mode:** Create a class extending `Mode` in `src/modes/`, implement `init()/update()/isDone()`, instantiate in `PixelPulseApp::initModes()`, and register with `_modeManager.addMode()`.

### Shared utility library (`lib/pixelpulse-core/`)

Header-only utilities extracted for testability on native platform (no Arduino dependency):

- `FontMath.h` — pixel width calculations for 4x6/6x8 fonts, text centering
- `TimeWords.h` — time-to-English conversion, crypto symbol-to-CoinGecko-ID mapping, minute rounding
- `SpriteData.h` — bitpacked sprite pixel access and byte count calculations

### Tests

- `test/` — C++ Unity tests for `lib/pixelpulse-core/` utilities, run via `pio test -e native`
- `tests/` — Python pytest tests for the simulator (`tests/test_simulator.py`)

### Python Simulator

`simulator.py` renders the 64x32 panel in a pygame window with real API calls. Edit the `CONFIG` dict at the top of the file. The simulator is a standalone parallel implementation — it reimplements font rendering and mode logic in Python, it is not a wrapper around the C++ code.

### 3D Printable Enclosure (`enclosure/`)

CadQuery parametric models for body and diffuser, with generated STL files and preview renders. Build with `python3 enclosure/pixelpulse_body.py` etc.

## Key Constants (Config.h)

- Panel: 64x32, brightness 50
- Mode rotation: 15s per mode, 200ms glitch transition, 80ms typewriter char delay, 2s boot pause
- API polling: weather 10min, crypto 2min, flights 5min
- Colors: `COLOR_GREEN` (0x00FF41), `COLOR_RED`, `COLOR_WHITE`, `COLOR_BLACK`

## QEMU Mode

Code guarded by `#ifdef QEMU_BUILD` or runtime flag. In QEMU mode: no DMA display init, no WiFi/captive portal, uses hardcoded default config. All draw calls log to serial instead.

## Caveats

- **Hardcoded WiFi creds in `PixelPulseApp.cpp`** — WiFi SSID/password are hardcoded as fallback defaults in `begin()`. The default OWM API key is injected at build time from `OWM_API_KEY` via `scripts/load_secrets.py`, or entered later through the captive portal/dashboard.
- **Timezone hardcoded** — NTP is configured for `MST7MDT` (US Mountain). Changing timezone requires editing the NTP config string in `PixelPulseApp.cpp`.
- **All drawing goes through `_dma` pointer** — if `_dma` is nullptr (no panel / QEMU), modes should not be instantiated.
- **OTA hostname hardcoded** — ArduinoOTA uses the hostname `pixelpulse` (reachable as `pixelpulse.local` via mDNS). Changing it requires editing `initOTA()` in `PixelPulseApp.cpp` and the `upload_port` in `platformio.ini`.
