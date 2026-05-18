# PixelPulse

A multi-mode ambient display for ESP32 + HUB75 RGB LED matrix, themed after the Mr. Robot aesthetic. Green terminal text on black, glitch transitions, hacker vibes.

## Hardware

- **MCU:** HiLetgo ESP32-DevKitC V4 (38-pin)
- **Display:** Waveshare 64x32 2.5mm pitch HUB75 RGB LED matrix panel
- **Adapter:** RGB Matrix Adapter Board (E) for ESP32-DevKitC V4
- **Power:** 5V 4A USB-C power supply

## Wiring

The RGB Matrix Adapter Board (E) connects the ESP32 to the HUB75 panel. Simply seat the ESP32 into the adapter board's pin headers and connect the HUB75 ribbon cable from the adapter to the panel's INPUT connector.

**Default pin mapping (Adapter Board E):**

| Signal | ESP32 Pin |
|--------|-----------|
| R1     | GPIO 25   |
| G1     | GPIO 26   |
| B1     | GPIO 27   |
| R2     | GPIO 14   |
| G2     | GPIO 12   |
| B2     | GPIO 13   |
| A      | GPIO 23   |
| B      | GPIO 19   |
| C      | GPIO 5    |
| D      | GPIO 17   |
| CLK    | GPIO 16   |
| LAT    | GPIO 4    |
| OE     | GPIO 15   |

**Power:** Connect the 5V 4A USB-C supply to the HUB75 panel's power connector. The ESP32 can be powered via its own USB port or through the adapter board's 5V rail.

## Modes

1. **WordClock** — Current time as natural language ("TWENTY PAST THREE") with typewriter effect, plus your name on a sub-line
2. **Weather** — Current conditions from OpenWeatherMap with ASCII weather icon
3. **Crypto** — Live price + 24h delta from CoinGecko, scrolling ticker style
4. **PixelArt** — Displays a 64x32 sprite from flash (default: fsociety mask)
5. **Flight** — Nearest airport departures from OpenSky Network, terminal readout style

Modes rotate every 15 seconds with a glitch transition effect.

## First Boot — Captive Portal

1. Power on the ESP32
2. The display shows "CONNECT TO PIXELPULSE WIFI SETUP"
3. On your phone/laptop, connect to the WiFi network **PIXELPULSE-SETUP**
4. A captive portal opens automatically (or navigate to 192.168.4.1)
5. Configure:
   - WiFi network + password (**must be a 2.4GHz network** — the ESP32 does not support 5GHz)
   - City name (for weather, e.g. "Salt Lake City")
   - Crypto symbol (e.g. "BTC", "ETH")
   - Airport ICAO code (e.g. "KSLC")
   - Your name (shown on word clock)
   - OpenWeatherMap API key
6. Save. The device reboots and connects to your WiFi.

Settings are stored in NVS (non-volatile storage) and persist across reboots.

## Web Dashboard

Once connected to your WiFi, PixelPulse runs a web dashboard at `http://<device-ip>/`. Open it in any browser on the same network to:

- View live weather, crypto, and flight data
- Change configuration (city, crypto symbol, airport, name, API key)
- Check device uptime and memory usage
- Access raw JSON at `/api/status` and logs at `/logs`

The device IP is printed to serial on boot, or you can find it in your router's attached devices list.

## API Keys

| Service | Key Required | Where to Get It |
|---------|-------------|-----------------|
| OpenWeatherMap | Yes (free tier) | https://openweathermap.org/api — sign up, get API key from dashboard |
| CoinGecko | No | Free public API, no key needed |
| OpenSky Network | No | Free public API, no key needed |

For a first-boot firmware fallback without committing the key, copy `.env.example` to `.env` and set:

```bash
OWM_API_KEY=your_openweathermap_api_key_here
```

PlatformIO injects this at build time as `PIXELPULSE_OWM_API_KEY`. If it is unset, the firmware still builds and the key can be entered later through the captive portal or web dashboard.

## macOS Setup

### 1. Install CP210x USB Driver

Download and install the Silicon Labs CP210x driver:
https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers

### 2. Install PlatformIO

```bash
brew install platformio
```

Or install the PlatformIO IDE extension in VS Code.

### 3. Install Python Dependencies

Python 3 is required for the simulator, serial reader, and tests.

```bash
pip3 install pygame pyserial pytest
```

### 4. Build and Flash

```bash
cd PixelPulse

# Build
pio run

# Flash to ESP32
pio run --target upload

# Monitor serial output
pio device monitor
```

### 4. Upload Custom Sprite via SPIFFS

Place your custom 64x32 sprite data in `src/data/fsociety.h` as a byte array (1 bit per pixel, row-major, MSB first, 256 bytes total).

To upload SPIFFS filesystem data:

```bash
pio run --target uploadfs
```

## Troubleshooting

**Display shows nothing after setup:** Make sure your WiFi is 2.4GHz. Most dual-band routers broadcast both 2.4GHz and 5GHz on the same name — check your router settings to confirm 2.4GHz is enabled. The ESP32 cannot connect to 5GHz networks.

**Can't find the PIXELPULSE-SETUP network:** The captive portal only appears when the device has no saved configuration. If it was previously configured, it will try to connect to the saved WiFi instead. Perform a configuration reset (see below).

**Weather shows no data:** Double-check your OpenWeatherMap API key. New keys can take a few hours to activate after signup.

**Flights show no data:** The OpenSky Network free API has strict rate limits. Flight data may take a few minutes to appear after boot.

## Configuration Reset

To reset all stored configuration and re-enter the captive portal, erase the ESP32's flash and reflash:

```bash
pio run --target erase
pio run --target upload
pio run --target uploadfs
```

## Project Structure

```
PixelPulse/
├── platformio.ini
├── README.md
├── src/
│   ├── main.cpp
│   ├── Config.h / .cpp          — NVS storage + WiFi captive portal
│   ├── ModeManager.h / .cpp     — Mode rotation + glitch transitions
│   ├── FontRenderer.h / .cpp    — 4x6 and 6x8 pixel font rendering
│   ├── ApiPoller.h / .cpp       — Non-blocking API polling manager
│   ├── data/
│   │   └── fsociety.h           — Default pixel art sprite
│   └── modes/
│       ├── WordClockMode.h / .cpp
│       ├── WeatherMode.h / .cpp
│       ├── CryptoMode.h / .cpp
│       ├── PixelArtMode.h / .cpp
│       └── FlightMode.h / .cpp
└── data/                         — SPIFFS filesystem (for future use)
```
