#!/usr/bin/env python3
"""
PixelPulse Simulator — renders the 64x32 HUB75 panel in a pygame window
with real API calls over WiFi. Mr. Robot aesthetic.
"""

import pygame
import sys
import time
import json
import threading
import math
import random
import os
import socket
import struct
import select
from urllib.request import urlopen, Request
from urllib.error import URLError
from datetime import datetime

# ── Display Config ──
PANEL_W = 64
PANEL_H = 32
PIXEL_SCALE = 14  # Each LED pixel = 14x14 screen pixels
PIXEL_GAP = 1
SCREEN_W = PANEL_W * PIXEL_SCALE
SCREEN_H = PANEL_H * PIXEL_SCALE
FPS = 30

# ── Mr. Robot Palette ──
BLACK  = (0, 0, 0)
GREEN  = (0, 255, 65)     # #00FF41
RED    = (255, 0, 0)       # #FF0000
WHITE  = (255, 255, 255)   # #FFFFFF
DIM_GREEN = (0, 80, 20)
CYAN    = (0, 255, 255)
AMBER   = (255, 191, 0)
MAGENTA = (255, 0, 255)
ORANGE  = (255, 140, 0)
YELLOW  = (255, 255, 0)
PURPLE  = (180, 0, 255)
TEAL    = (0, 200, 180)
PINK    = (255, 105, 180)

# ── Config (edit these) ──
CONFIG = {
    "city": "Salt Lake City",
    "crypto": "BTC",
    "icao": "KSLC",
    "customer_name": "GRANT",
    "owm_api_key": os.environ.get("OWM_API_KEY", ""),
    "offline": False,  # Set True for no-network mode
}

# ── 4x6 Font Data ──
FONT_4x6 = {
    ' ': [0x00,0x00,0x00,0x00,0x00,0x00],
    '!': [0x40,0x40,0x40,0x00,0x40,0x00],
    '"': [0xA0,0xA0,0x00,0x00,0x00,0x00],
    '#': [0xA0,0xF0,0xA0,0xF0,0xA0,0x00],
    '$': [0x60,0xC0,0x60,0xA0,0xC0,0x00],
    '%': [0xA0,0x20,0x40,0x80,0xA0,0x00],
    '&': [0x40,0xA0,0x60,0xA0,0xD0,0x00],
    "'": [0x40,0x40,0x00,0x00,0x00,0x00],
    '(': [0x20,0x40,0x40,0x40,0x20,0x00],
    ')': [0x80,0x40,0x40,0x40,0x80,0x00],
    '*': [0xA0,0x40,0xE0,0x40,0xA0,0x00],
    '+': [0x00,0x40,0xE0,0x40,0x00,0x00],
    ',': [0x00,0x00,0x00,0x40,0x80,0x00],
    '-': [0x00,0x00,0xE0,0x00,0x00,0x00],
    '.': [0x00,0x00,0x00,0x00,0x40,0x00],
    '/': [0x20,0x20,0x40,0x80,0x80,0x00],
    '0': [0x60,0xA0,0xA0,0xA0,0xC0,0x00],
    '1': [0x40,0xC0,0x40,0x40,0xE0,0x00],
    '2': [0xC0,0x20,0x40,0x80,0xE0,0x00],
    '3': [0xC0,0x20,0x40,0x20,0xC0,0x00],
    '4': [0xA0,0xA0,0xE0,0x20,0x20,0x00],
    '5': [0xE0,0x80,0xC0,0x20,0xC0,0x00],
    '6': [0x60,0x80,0xE0,0xA0,0xE0,0x00],
    '7': [0xE0,0x20,0x40,0x40,0x40,0x00],
    '8': [0xE0,0xA0,0xE0,0xA0,0xE0,0x00],
    '9': [0xE0,0xA0,0xE0,0x20,0xC0,0x00],
    ':': [0x00,0x40,0x00,0x40,0x00,0x00],
    ';': [0x00,0x40,0x00,0x40,0x80,0x00],
    '<': [0x20,0x40,0x80,0x40,0x20,0x00],
    '=': [0x00,0xE0,0x00,0xE0,0x00,0x00],
    '>': [0x80,0x40,0x20,0x40,0x80,0x00],
    '?': [0xC0,0x20,0x40,0x00,0x40,0x00],
    '@': [0x60,0xA0,0xE0,0x80,0x60,0x00],
    'A': [0x40,0xA0,0xE0,0xA0,0xA0,0x00],
    'B': [0xC0,0xA0,0xC0,0xA0,0xC0,0x00],
    'C': [0x60,0x80,0x80,0x80,0x60,0x00],
    'D': [0xC0,0xA0,0xA0,0xA0,0xC0,0x00],
    'E': [0xE0,0x80,0xC0,0x80,0xE0,0x00],
    'F': [0xE0,0x80,0xC0,0x80,0x80,0x00],
    'G': [0x60,0x80,0xA0,0xA0,0x60,0x00],
    'H': [0xA0,0xA0,0xE0,0xA0,0xA0,0x00],
    'I': [0xE0,0x40,0x40,0x40,0xE0,0x00],
    'J': [0x20,0x20,0x20,0xA0,0x40,0x00],
    'K': [0xA0,0xA0,0xC0,0xA0,0xA0,0x00],
    'L': [0x80,0x80,0x80,0x80,0xE0,0x00],
    'M': [0xA0,0xE0,0xE0,0xA0,0xA0,0x00],
    'N': [0xA0,0xE0,0xE0,0xA0,0xA0,0x00],
    'O': [0x40,0xA0,0xA0,0xA0,0x40,0x00],
    'P': [0xC0,0xA0,0xC0,0x80,0x80,0x00],
    'Q': [0x40,0xA0,0xA0,0xA0,0x60,0x00],
    'R': [0xC0,0xA0,0xC0,0xA0,0xA0,0x00],
    'S': [0x60,0x80,0x40,0x20,0xC0,0x00],
    'T': [0xE0,0x40,0x40,0x40,0x40,0x00],
    'U': [0xA0,0xA0,0xA0,0xA0,0xE0,0x00],
    'V': [0xA0,0xA0,0xA0,0xA0,0x40,0x00],
    'W': [0xA0,0xA0,0xE0,0xE0,0xA0,0x00],
    'X': [0xA0,0xA0,0x40,0xA0,0xA0,0x00],
    'Y': [0xA0,0xA0,0x40,0x40,0x40,0x00],
    'Z': [0xE0,0x20,0x40,0x80,0xE0,0x00],
    '[': [0x60,0x40,0x40,0x40,0x60,0x00],
    ']': [0xC0,0x40,0x40,0x40,0xC0,0x00],
    '_': [0x00,0x00,0x00,0x00,0xE0,0x00],
}

# ── 6x8 Font Data ──
FONT_6x8 = {
    ' ': [0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],
    '!': [0x20,0x20,0x20,0x20,0x20,0x00,0x20,0x00],
    '"': [0x50,0x50,0x00,0x00,0x00,0x00,0x00,0x00],
    '#': [0x50,0xF8,0x50,0x50,0xF8,0x50,0x00,0x00],
    '$': [0x20,0x78,0xA0,0x70,0x28,0xF0,0x20,0x00],
    '%': [0xC8,0xD0,0x10,0x20,0x40,0x58,0x98,0x00],
    "'": [0x20,0x20,0x00,0x00,0x00,0x00,0x00,0x00],
    '(': [0x10,0x20,0x40,0x40,0x40,0x20,0x10,0x00],
    ')': [0x40,0x20,0x10,0x10,0x10,0x20,0x40,0x00],
    '+': [0x00,0x20,0x20,0xF8,0x20,0x20,0x00,0x00],
    ',': [0x00,0x00,0x00,0x00,0x00,0x20,0x20,0x40],
    '-': [0x00,0x00,0x00,0xF8,0x00,0x00,0x00,0x00],
    '.': [0x00,0x00,0x00,0x00,0x00,0x00,0x20,0x00],
    '/': [0x08,0x10,0x10,0x20,0x40,0x40,0x80,0x00],
    '0': [0x70,0x88,0x98,0xA8,0xC8,0x88,0x70,0x00],
    '1': [0x20,0x60,0x20,0x20,0x20,0x20,0x70,0x00],
    '2': [0x70,0x88,0x08,0x10,0x20,0x40,0xF8,0x00],
    '3': [0x70,0x88,0x08,0x30,0x08,0x88,0x70,0x00],
    '4': [0x10,0x30,0x50,0x90,0xF8,0x10,0x10,0x00],
    '5': [0xF8,0x80,0xF0,0x08,0x08,0x88,0x70,0x00],
    '6': [0x30,0x40,0x80,0xF0,0x88,0x88,0x70,0x00],
    '7': [0xF8,0x08,0x10,0x20,0x40,0x40,0x40,0x00],
    '8': [0x70,0x88,0x88,0x70,0x88,0x88,0x70,0x00],
    '9': [0x70,0x88,0x88,0x78,0x08,0x10,0x60,0x00],
    ':': [0x00,0x00,0x20,0x00,0x00,0x20,0x00,0x00],
    'A': [0x20,0x50,0x88,0x88,0xF8,0x88,0x88,0x00],
    'B': [0xF0,0x88,0x88,0xF0,0x88,0x88,0xF0,0x00],
    'C': [0x70,0x88,0x80,0x80,0x80,0x88,0x70,0x00],
    'D': [0xF0,0x88,0x88,0x88,0x88,0x88,0xF0,0x00],
    'E': [0xF8,0x80,0x80,0xF0,0x80,0x80,0xF8,0x00],
    'F': [0xF8,0x80,0x80,0xF0,0x80,0x80,0x80,0x00],
    'G': [0x70,0x88,0x80,0xB8,0x88,0x88,0x70,0x00],
    'H': [0x88,0x88,0x88,0xF8,0x88,0x88,0x88,0x00],
    'I': [0x70,0x20,0x20,0x20,0x20,0x20,0x70,0x00],
    'J': [0x38,0x10,0x10,0x10,0x10,0x90,0x60,0x00],
    'K': [0x88,0x90,0xA0,0xC0,0xA0,0x90,0x88,0x00],
    'L': [0x80,0x80,0x80,0x80,0x80,0x80,0xF8,0x00],
    'M': [0x88,0xD8,0xA8,0xA8,0x88,0x88,0x88,0x00],
    'N': [0x88,0xC8,0xA8,0x98,0x88,0x88,0x88,0x00],
    'O': [0x70,0x88,0x88,0x88,0x88,0x88,0x70,0x00],
    'P': [0xF0,0x88,0x88,0xF0,0x80,0x80,0x80,0x00],
    'Q': [0x70,0x88,0x88,0x88,0xA8,0x90,0x68,0x00],
    'R': [0xF0,0x88,0x88,0xF0,0xA0,0x90,0x88,0x00],
    'S': [0x70,0x88,0x80,0x70,0x08,0x88,0x70,0x00],
    'T': [0xF8,0x20,0x20,0x20,0x20,0x20,0x20,0x00],
    'U': [0x88,0x88,0x88,0x88,0x88,0x88,0x70,0x00],
    'V': [0x88,0x88,0x88,0x88,0x50,0x50,0x20,0x00],
    'W': [0x88,0x88,0x88,0xA8,0xA8,0xD8,0x88,0x00],
    'X': [0x88,0x88,0x50,0x20,0x50,0x88,0x88,0x00],
    'Y': [0x88,0x88,0x50,0x20,0x20,0x20,0x20,0x00],
    'Z': [0xF8,0x08,0x10,0x20,0x40,0x80,0xF8,0x00],
    '>': [0x80,0x40,0x20,0x10,0x20,0x40,0x80,0x00],
    '<': [0x08,0x10,0x20,0x40,0x20,0x10,0x08,0x00],
}

# ── fsociety sprite (same as C header) ──
FSOCIETY_SPRITE = bytes([
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x7F,0xFE,0x00,0x00,0x00,
    0x00,0x00,0x01,0xFF,0xFF,0x80,0x00,0x00,
    0x00,0x00,0x07,0xFF,0xFF,0xE0,0x00,0x00,
    0x00,0x00,0x0F,0xFF,0xFF,0xF0,0x00,0x00,
    0x00,0x00,0x1F,0xFF,0xFF,0xF8,0x00,0x00,
    0x00,0x00,0x3F,0xFF,0xFF,0xFC,0x00,0x00,
    0x00,0x00,0x3F,0xFF,0xFF,0xFC,0x00,0x00,
    0x00,0x00,0x3F,0x07,0xE0,0xFC,0x00,0x00,
    0x00,0x00,0x3E,0x03,0xC0,0x7C,0x00,0x00,
    0x00,0x00,0x3E,0x03,0xC0,0x7C,0x00,0x00,
    0x00,0x00,0x3F,0x07,0xE0,0xFC,0x00,0x00,
    0x00,0x00,0x3F,0xFF,0xFF,0xFC,0x00,0x00,
    0x00,0x00,0x3F,0xFB,0xDF,0xFC,0x00,0x00,
    0x00,0x00,0x3F,0xF9,0x9F,0xFC,0x00,0x00,
    0x00,0x00,0x3F,0xE0,0x07,0xFC,0x00,0x00,
    0x00,0x00,0x3F,0xC0,0x03,0xFC,0x00,0x00,
    0x00,0x00,0x1F,0xE0,0x07,0xF8,0x00,0x00,
    0x00,0x00,0x1F,0xF0,0x0F,0xF8,0x00,0x00,
    0x00,0x00,0x0F,0xFF,0xFF,0xF0,0x00,0x00,
    0x00,0x00,0x0F,0xFF,0xFF,0xF0,0x00,0x00,
    0x00,0x00,0x07,0xFF,0xFF,0xE0,0x00,0x00,
    0x00,0x00,0x03,0xFF,0xFF,0xC0,0x00,0x00,
    0x00,0x00,0x01,0xFF,0xFF,0x80,0x00,0x00,
    0x00,0x00,0x00,0x7F,0xFE,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
])


class PixelBuffer:
    """64x32 pixel framebuffer with pygame rendering."""

    def __init__(self, surface):
        self.surface = surface
        self.pixels = [[(0,0,0)] * PANEL_W for _ in range(PANEL_H)]

    def clear(self):
        self.pixels = [[(0,0,0)] * PANEL_W for _ in range(PANEL_H)]

    def set_pixel(self, x, y, color):
        if 0 <= x < PANEL_W and 0 <= y < PANEL_H:
            self.pixels[y][x] = color

    def render(self):
        self.surface.fill((5, 5, 5))  # Very dark background (PCB color)
        for y in range(PANEL_H):
            for x in range(PANEL_W):
                r, g, b = self.pixels[y][x]
                if r > 0 or g > 0 or b > 0:
                    color = (r, g, b)
                else:
                    color = (3, 3, 3)  # Dim "off" LEDs
                px = x * PIXEL_SCALE
                py = y * PIXEL_SCALE
                sz = PIXEL_SCALE - PIXEL_GAP
                # Draw circular LED pixel
                cx = px + PIXEL_SCALE // 2
                cy = py + PIXEL_SCALE // 2
                radius = sz // 2
                pygame.draw.circle(self.surface, color, (cx, cy), radius)
                # Add glow for bright pixels
                if r + g + b > 100:
                    glow = (min(r//3, 255), min(g//3, 255), min(b//3, 255))
                    pygame.draw.circle(self.surface, glow, (cx, cy), radius + 2, 1)


class FontRenderer:
    """Renders text onto the pixel buffer using the bitmap fonts."""

    def __init__(self, buf):
        self.buf = buf

    def draw_char(self, x, y, ch, color, font_data, char_w, char_h):
        ch = ch.upper()
        glyph = font_data.get(ch, font_data.get(' '))
        for row in range(min(char_h, len(glyph))):
            line = glyph[row]
            for col in range(char_w):
                if line & (0x80 >> col):
                    self.buf.set_pixel(x + col, y + row, color)
        return char_w + 1

    def draw_string(self, x, y, text, color, large=False):
        font_data = FONT_6x8 if large else FONT_4x6
        char_w = 6 if large else 4
        char_h = 8 if large else 6
        cx = x
        for ch in text:
            cx += self.draw_char(cx, y, ch, color, font_data, char_w, char_h)

    def string_width(self, text, large=False):
        char_w = 6 if large else 4
        if len(text) == 0:
            return 0
        return len(text) * (char_w + 1) - 1

    def draw_centered(self, y, text, color, large=False):
        w = self.string_width(text, large)
        x = max(0, (PANEL_W - w) // 2)
        self.draw_string(x, y, text, color, large)

    def draw_cursor(self, x, y, color, large=False):
        char_h = 8 if large else 6
        if int(time.time() * 2) % 2 == 0:
            for row in range(char_h):
                self.buf.set_pixel(x, y + row, color)
                self.buf.set_pixel(x + 1, y + row, color)


# ── API Poller (background threads) ──
class ApiPoller:
    def __init__(self, config):
        self.config = config
        self.weather = None
        self.crypto = None
        self.flights = None
        self._lock = threading.Lock()
        self._running = True

    def start(self):
        if self.config.get("offline"):
            print("[API] Offline mode — skipping all API calls")
            return
        threading.Thread(target=self._poll_weather, daemon=True).start()
        threading.Thread(target=self._poll_crypto, daemon=True).start()
        threading.Thread(target=self._poll_flights, daemon=True).start()

    def _fetch_json(self, url):
        try:
            req = Request(url, headers={"User-Agent": "PixelPulse/1.0"})
            with urlopen(req, timeout=8) as resp:
                return json.loads(resp.read())
        except Exception as e:
            print(f"[API] Error: {e}")
            return None

    def _poll_weather(self):
        while self._running:
            key = self.config.get("owm_api_key", "")
            city = self.config.get("city", "")
            if key and city:
                data = self._fetch_json(
                    f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=imperial"
                )
                if data and "main" in data:
                    with self._lock:
                        self.weather = {
                            "temp_f": data["main"]["temp"],
                            "condition": data["weather"][0]["main"],
                        }
                    print(f"[API] Weather: {self.weather}")
            else:
                # Mock weather for demo without API key
                with self._lock:
                    self.weather = {"temp_f": 72, "condition": "Clear"}
            time.sleep(600)

    def _poll_crypto(self):
        while self._running:
            sym = self.config.get("crypto", "BTC").lower()
            coin_map = {
                "btc": "bitcoin", "eth": "ethereum", "sol": "solana",
                "ada": "cardano", "doge": "dogecoin", "xrp": "ripple",
                "dot": "polkadot", "ltc": "litecoin",
            }
            coin_id = coin_map.get(sym, sym)
            data = self._fetch_json(
                f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
            )
            if data and coin_id in data:
                with self._lock:
                    self.crypto = {
                        "symbol": self.config.get("crypto", "BTC").upper(),
                        "price": data[coin_id]["usd"],
                        "change": data[coin_id].get("usd_24h_change", 0),
                    }
                print(f"[API] Crypto: {self.crypto}")
            else:
                # Mock crypto data when API fails
                with self._lock:
                    if self.crypto is None:
                        self.crypto = {"symbol": "BTC", "price": 97542.0, "change": 2.34}
                        print("[API] Crypto: using mock data")
            time.sleep(120)

    def _poll_flights(self):
        while self._running:
            icao = self.config.get("icao", "")
            if icao:
                now = int(time.time())
                begin = now - 3600
                data = self._fetch_json(
                    f"https://opensky-network.org/api/flights/departure?airport={icao}&begin={begin}&end={now}"
                )
                if data and isinstance(data, list):
                    flights = []
                    for f in data[:5]:
                        cs = (f.get("callsign") or "").strip()
                        if cs:
                            flights.append(cs)
                    if flights:
                        with self._lock:
                            self.flights = flights
                        print(f"[API] Flights: {self.flights}")
                    else:
                        # API returned empty list — use mock
                        with self._lock:
                            self.flights = ["DAL1234", "UAL567", "SWA890"]
                        print("[API] Flights: empty response, using mock data")
                else:
                    # API failed — use mock
                    with self._lock:
                        self.flights = ["DAL1234", "UAL567", "SWA890"]
                    print("[API] Flights: API failed, using mock data")
            time.sleep(300)

    def get_weather(self):
        with self._lock:
            return self.weather

    def get_crypto(self):
        with self._lock:
            return self.crypto

    def get_flights(self):
        with self._lock:
            return self.flights


# ── Modes ──

class BootMode:
    def __init__(self, buf, font):
        self.buf = buf
        self.font = font
        self.start = None
        self.done = False

    def init(self):
        self.start = time.time()
        self.done = False

    def update(self):
        self.buf.clear()
        self.font.draw_centered(12, "HELLO FRIEND", GREEN, large=True)
        if time.time() - self.start > 2.0:
            self.done = True

    def is_done(self):
        return self.done


class GlitchTransition:
    """Scanline wipe with trailing noise — sweeps top to bottom."""

    DURATION = 0.5  # seconds total

    def __init__(self, buf):
        self.buf = buf
        self.start = None
        self.done = False
        self.phase = 0  # 0=scanline wipe, 1=fade out

    def init(self):
        self.start = time.time()
        self.done = False
        self.phase = 0

    def update(self):
        elapsed = time.time() - self.start
        if elapsed > self.DURATION:
            self.done = True
            self.buf.clear()
            return

        progress = elapsed / self.DURATION  # 0.0 → 1.0

        if progress < 0.6:
            # Phase 1: Scanline wipe — green line sweeps down, noise trails behind
            scan_y = int((progress / 0.6) * PANEL_H)
            # Draw the bright scanline
            for x in range(PANEL_W):
                self.buf.set_pixel(x, min(scan_y, PANEL_H - 1), GREEN)
                if scan_y + 1 < PANEL_H:
                    self.buf.set_pixel(x, min(scan_y + 1, PANEL_H - 1),
                                       (0, 120, 30))
            # Noise behind the scanline (above it)
            for _ in range(40):
                nx = random.randint(0, PANEL_W - 1)
                ny = random.randint(0, max(0, scan_y - 1))
                r = random.random()
                if r < 0.3:
                    g_val = random.randint(20, 100)
                    self.buf.set_pixel(nx, ny, (0, g_val, 0))
                elif r < 0.5:
                    self.buf.set_pixel(nx, ny, (0, 0, 0))
                # else leave existing pixel
        else:
            # Phase 2: Dissolve — random pixels fade to black
            fade_progress = (progress - 0.6) / 0.4  # 0→1 within this phase
            clear_count = int(fade_progress * PANEL_W * PANEL_H * 0.3)
            for _ in range(min(clear_count, 300)):
                nx = random.randint(0, PANEL_W - 1)
                ny = random.randint(0, PANEL_H - 1)
                self.buf.set_pixel(nx, ny, BLACK)
            # Occasional green flicker
            if random.random() < 0.3:
                for _ in range(5):
                    fx = random.randint(0, PANEL_W - 1)
                    fy = random.randint(0, PANEL_H - 1)
                    self.buf.set_pixel(fx, fy, (0, random.randint(30, 80), 0))

    def is_done(self):
        return self.done


class InfoMode:
    """Displays customer name and current date, terminal style."""

    def __init__(self, buf, font, name):
        self.buf = buf
        self.font = font
        self.name = name.upper()
        self.chars_revealed = 0
        self.last_char = 0
        self.lines = []
        self.current_line = 0
        self.done_time = 0
        self.all_done = False

    def init(self):
        now = datetime.now()
        self.lines = [
            f"> {self.name}",
            f"> {now.strftime('%b %d %Y').upper()}",
        ]
        self.current_line = 0
        self.chars_revealed = 0
        self.last_char = time.time()
        self.all_done = False
        self.done_time = 0

    def update(self):
        now = time.time()

        if not self.all_done:
            if now - self.last_char >= 0.06:
                self.chars_revealed += 1
                self.last_char = now
                if self.current_line < len(self.lines) and \
                   self.chars_revealed >= len(self.lines[self.current_line]):
                    self.current_line += 1
                    self.chars_revealed = 0
                    if self.current_line >= len(self.lines):
                        self.all_done = True
                        self.done_time = now

        self.buf.clear()
        y = 2
        for i in range(min(self.current_line + 1, len(self.lines))):
            if i < self.current_line:
                text = self.lines[i]
            elif i == self.current_line and not self.all_done:
                text = self.lines[i][:self.chars_revealed]
            else:
                text = self.lines[i] if i < len(self.lines) else ""

            color = CYAN if i == 1 else GREEN
            self.font.draw_string(1, y, text, color)

            # Cursor on current line
            if i == self.current_line and not self.all_done:
                cx = 1 + self.font.string_width(text)
                self.font.draw_cursor(cx, y, GREEN)

            y += 7

    def is_done(self):
        return self.all_done and (time.time() - self.done_time > 2)


class WordClockMode:
    def __init__(self, buf, font, name):
        self.buf = buf
        self.font = font
        self.name = name.upper()
        self.chars_revealed = 0
        self.sub_chars = 0
        self.last_char = 0
        self.time_text = ""
        self.sub_text = ""
        self.text_done = False
        self.sub_done = False
        self.done_time = 0

    def init(self):
        self.time_text = self._time_to_words()
        self.last_time_text = self.time_text
        self.sub_text = f"> {self.name}"
        self.chars_revealed = 0
        self.sub_chars = 0
        self.last_char = time.time()
        self.text_done = False
        self.sub_done = False
        self.done_time = 0

    def _wrap_text(self, text, max_width):
        """Split text into lines that fit within max_width pixels."""
        words = text.split()
        lines = []
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            if self.font.string_width(test) <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def update(self):
        now = time.time()

        # Build all display lines: wrapped time lines + sub line
        time_lines = self._wrap_text(self.time_text, PANEL_W - 4)
        all_lines = time_lines + [self.sub_text]
        total_chars = sum(len(l) for l in all_lines)

        if not self.text_done:
            if now - self.last_char >= 0.08:
                self.chars_revealed += 1
                self.last_char = now
                time_total = sum(len(l) for l in time_lines)
                if self.chars_revealed >= time_total:
                    self.text_done = True
                    self.chars_revealed = time_total
        elif not self.sub_done:
            if now - self.last_char >= 0.08:
                self.sub_chars += 1
                self.last_char = now
                if self.sub_chars >= len(self.sub_text):
                    self.sub_done = True
                    self.done_time = now

        self.buf.clear()

        # Calculate vertical centering
        line_h = 7
        total_h = len(all_lines) * line_h
        start_y = max(1, (PANEL_H - total_h) // 2)

        # Draw time lines with typewriter reveal
        chars_left = self.chars_revealed
        y = start_y
        for i, line in enumerate(time_lines):
            if chars_left <= 0:
                # Draw cursor on this line
                self.font.draw_cursor(max(0, (PANEL_W - self.font.string_width(line)) // 2), y, GREEN)
                break
            show = min(chars_left, len(line))
            revealed = line[:show]
            self.font.draw_centered(y, revealed, GREEN)
            if show < len(line):
                # Cursor at end of partial line
                w = self.font.string_width(revealed)
                cx = max(0, (PANEL_W - self.font.string_width(line)) // 2) + w
                self.font.draw_cursor(cx, y, GREEN)
            chars_left -= len(line)
            y += line_h

        # Draw sub line
        sub_y = start_y + len(time_lines) * line_h
        if self.text_done:
            sub_rev = self.sub_text[:self.sub_chars]
            self.font.draw_centered(sub_y, sub_rev, AMBER)
            if not self.sub_done:
                sw = self.font.string_width(sub_rev)
                full_sw = self.font.string_width(self.sub_text)
                scx = max(0, (PANEL_W - full_sw) // 2) + sw
                self.font.draw_cursor(scx, sub_y, AMBER)

    def is_done(self):
        return self.sub_done and (time.time() - self.done_time > 3)

    # Every time string, indexed by [hour % 12][minute // 5]
    TIME_TABLE = {
        (0,  0): "TWELVE O'CLOCK",   (0,  5): "FIVE PAST TWELVE",    (0, 10): "TEN PAST TWELVE",
        (0, 15): "QUARTER PAST TWELVE", (0, 20): "TWENTY PAST TWELVE", (0, 25): "TWENTY FIVE PAST TWELVE",
        (0, 30): "HALF PAST TWELVE", (0, 35): "TWENTY FIVE TO ONE",  (0, 40): "TWENTY TO ONE",
        (0, 45): "QUARTER TO ONE",   (0, 50): "TEN TO ONE",          (0, 55): "FIVE TO ONE",

        (1,  0): "ONE O'CLOCK",      (1,  5): "FIVE PAST ONE",       (1, 10): "TEN PAST ONE",
        (1, 15): "QUARTER PAST ONE", (1, 20): "TWENTY PAST ONE",     (1, 25): "TWENTY FIVE PAST ONE",
        (1, 30): "HALF PAST ONE",    (1, 35): "TWENTY FIVE TO TWO",  (1, 40): "TWENTY TO TWO",
        (1, 45): "QUARTER TO TWO",   (1, 50): "TEN TO TWO",          (1, 55): "FIVE TO TWO",

        (2,  0): "TWO O'CLOCK",      (2,  5): "FIVE PAST TWO",       (2, 10): "TEN PAST TWO",
        (2, 15): "QUARTER PAST TWO", (2, 20): "TWENTY PAST TWO",     (2, 25): "TWENTY FIVE PAST TWO",
        (2, 30): "HALF PAST TWO",    (2, 35): "TWENTY FIVE TO THREE",(2, 40): "TWENTY TO THREE",
        (2, 45): "QUARTER TO THREE", (2, 50): "TEN TO THREE",        (2, 55): "FIVE TO THREE",

        (3,  0): "THREE O'CLOCK",    (3,  5): "FIVE PAST THREE",     (3, 10): "TEN PAST THREE",
        (3, 15): "QUARTER PAST THREE",(3, 20): "TWENTY PAST THREE",  (3, 25): "TWENTY FIVE PAST THREE",
        (3, 30): "HALF PAST THREE",  (3, 35): "TWENTY FIVE TO FOUR", (3, 40): "TWENTY TO FOUR",
        (3, 45): "QUARTER TO FOUR",  (3, 50): "TEN TO FOUR",         (3, 55): "FIVE TO FOUR",

        (4,  0): "FOUR O'CLOCK",     (4,  5): "FIVE PAST FOUR",      (4, 10): "TEN PAST FOUR",
        (4, 15): "QUARTER PAST FOUR",(4, 20): "TWENTY PAST FOUR",    (4, 25): "TWENTY FIVE PAST FOUR",
        (4, 30): "HALF PAST FOUR",   (4, 35): "TWENTY FIVE TO FIVE", (4, 40): "TWENTY TO FIVE",
        (4, 45): "QUARTER TO FIVE",  (4, 50): "TEN TO FIVE",         (4, 55): "FIVE TO FIVE",

        (5,  0): "FIVE O'CLOCK",     (5,  5): "FIVE PAST FIVE",      (5, 10): "TEN PAST FIVE",
        (5, 15): "QUARTER PAST FIVE",(5, 20): "TWENTY PAST FIVE",    (5, 25): "TWENTY FIVE PAST FIVE",
        (5, 30): "HALF PAST FIVE",   (5, 35): "TWENTY FIVE TO SIX",  (5, 40): "TWENTY TO SIX",
        (5, 45): "QUARTER TO SIX",   (5, 50): "TEN TO SIX",          (5, 55): "FIVE TO SIX",

        (6,  0): "SIX O'CLOCK",      (6,  5): "FIVE PAST SIX",       (6, 10): "TEN PAST SIX",
        (6, 15): "QUARTER PAST SIX", (6, 20): "TWENTY PAST SIX",     (6, 25): "TWENTY FIVE PAST SIX",
        (6, 30): "HALF PAST SIX",    (6, 35): "TWENTY FIVE TO SEVEN",(6, 40): "TWENTY TO SEVEN",
        (6, 45): "QUARTER TO SEVEN", (6, 50): "TEN TO SEVEN",        (6, 55): "FIVE TO SEVEN",

        (7,  0): "SEVEN O'CLOCK",    (7,  5): "FIVE PAST SEVEN",     (7, 10): "TEN PAST SEVEN",
        (7, 15): "QUARTER PAST SEVEN",(7, 20): "TWENTY PAST SEVEN",  (7, 25): "TWENTY FIVE PAST SEVEN",
        (7, 30): "HALF PAST SEVEN",  (7, 35): "TWENTY FIVE TO EIGHT",(7, 40): "TWENTY TO EIGHT",
        (7, 45): "QUARTER TO EIGHT", (7, 50): "TEN TO EIGHT",        (7, 55): "FIVE TO EIGHT",

        (8,  0): "EIGHT O'CLOCK",    (8,  5): "FIVE PAST EIGHT",     (8, 10): "TEN PAST EIGHT",
        (8, 15): "QUARTER PAST EIGHT",(8, 20): "TWENTY PAST EIGHT",  (8, 25): "TWENTY FIVE PAST EIGHT",
        (8, 30): "HALF PAST EIGHT",  (8, 35): "TWENTY FIVE TO NINE", (8, 40): "TWENTY TO NINE",
        (8, 45): "QUARTER TO NINE",  (8, 50): "TEN TO NINE",         (8, 55): "FIVE TO NINE",

        (9,  0): "NINE O'CLOCK",     (9,  5): "FIVE PAST NINE",      (9, 10): "TEN PAST NINE",
        (9, 15): "QUARTER PAST NINE",(9, 20): "TWENTY PAST NINE",    (9, 25): "TWENTY FIVE PAST NINE",
        (9, 30): "HALF PAST NINE",   (9, 35): "TWENTY FIVE TO TEN",  (9, 40): "TWENTY TO TEN",
        (9, 45): "QUARTER TO TEN",   (9, 50): "TEN TO TEN",          (9, 55): "FIVE TO TEN",

        (10, 0): "TEN O'CLOCK",      (10, 5): "FIVE PAST TEN",       (10,10): "TEN PAST TEN",
        (10,15): "QUARTER PAST TEN", (10,20): "TWENTY PAST TEN",     (10,25): "TWENTY FIVE PAST TEN",
        (10,30): "HALF PAST TEN",    (10,35): "TWENTY FIVE TO ELEVEN",(10,40): "TWENTY TO ELEVEN",
        (10,45): "QUARTER TO ELEVEN",(10,50): "TEN TO ELEVEN",       (10,55): "FIVE TO ELEVEN",

        (11, 0): "ELEVEN O'CLOCK",   (11, 5): "FIVE PAST ELEVEN",    (11,10): "TEN PAST ELEVEN",
        (11,15): "QUARTER PAST ELEVEN",(11,20): "TWENTY PAST ELEVEN",(11,25): "TWENTY FIVE PAST ELEVEN",
        (11,30): "HALF PAST ELEVEN", (11,35): "TWENTY FIVE TO TWELVE",(11,40): "TWENTY TO TWELVE",
        (11,45): "QUARTER TO TWELVE",(11,50): "TEN TO TWELVE",       (11,55): "FIVE TO TWELVE",
    }

    def _time_to_words(self):
        now = datetime.now()
        h = now.hour % 12
        m = ((now.minute + 2) // 5) * 5  # round to nearest 5
        if m == 60:
            m = 0
            h = (h + 1) % 12
        return self.TIME_TABLE.get((h, m), "TIME ERROR")


class WeatherMode:
    def __init__(self, buf, font, poller):
        self.buf = buf
        self.font = font
        self.poller = poller

    def init(self):
        pass

    def _draw_sun(self, x, y):
        for dx, dy in [(5,0),(1,4),(9,4),(5,8)]:
            self.buf.set_pixel(x+dx, y+dy, GREEN)
        for i in range(3, 8):
            self.buf.set_pixel(x+i, y+2, GREEN)
            self.buf.set_pixel(x+i, y+6, GREEN)
        for i in range(2, 7):
            self.buf.set_pixel(x+2, y+i, GREEN)
            self.buf.set_pixel(x+8, y+i, GREEN)

    def _draw_cloud(self, x, y):
        for i in range(3, 9): self.buf.set_pixel(x+i, y+2, WHITE)
        for i in range(2, 10): self.buf.set_pixel(x+i, y+3, WHITE)
        for i in range(1, 11):
            self.buf.set_pixel(x+i, y+4, WHITE)
            self.buf.set_pixel(x+i, y+5, WHITE)
        for i in range(2, 10): self.buf.set_pixel(x+i, y+6, WHITE)

    def _draw_rain(self, x, y):
        for i in range(3, 9): self.buf.set_pixel(x+i, y+1, WHITE)
        for i in range(2, 10):
            self.buf.set_pixel(x+i, y+2, WHITE)
            self.buf.set_pixel(x+i, y+3, WHITE)
        blue = (0, 128, 255)
        for dx, dy in [(3,5),(5,6),(7,5),(4,7),(6,7)]:
            self.buf.set_pixel(x+dx, y+dy, blue)

    def _draw_snow(self, x, y):
        for dx, dy in [(3,2),(7,3),(5,4),(2,5),(8,6),(4,7),(6,2)]:
            self.buf.set_pixel(x+dx, y+dy, WHITE)

    def update(self):
        self.buf.clear()
        w = self.poller.get_weather()
        if not w:
            self.font.draw_centered(8, "WEATHER", GREEN, large=True)
            self.font.draw_centered(20, "NO SIGNAL", RED)
            self.font.draw_cursor(52, 20, RED)
            return

        cond = w["condition"].lower()
        if "clear" in cond or "sun" in cond:
            self._draw_sun(2, 4)
        elif "rain" in cond or "drizzle" in cond:
            self._draw_rain(2, 4)
        elif "snow" in cond:
            self._draw_snow(2, 4)
        elif "cloud" in cond:
            self._draw_cloud(2, 4)
        else:
            # fog/mist
            for i in range(2, 11): self.buf.set_pixel(i+2, 6, GREEN)
            for i in range(1, 10): self.buf.set_pixel(i+2, 8, GREEN)
            for i in range(3, 12): self.buf.set_pixel(i+2, 10, GREEN)

        self.font.draw_string(30, 4, f"{int(w['temp_f'])}F", CYAN, large=True)
        self.font.draw_centered(20, w["condition"].upper(), GREEN)

    def is_done(self):
        return False


class CryptoMode:
    def __init__(self, buf, font, poller):
        self.buf = buf
        self.font = font
        self.poller = poller
        self.scroll_x = PANEL_W
        self.last_scroll = 0

    def init(self):
        self.scroll_x = PANEL_W
        self.last_scroll = time.time()

    def update(self):
        self.buf.clear()
        c = self.poller.get_crypto()
        if not c:
            self.font.draw_centered(8, "CRYPTO", GREEN, large=True)
            self.font.draw_centered(20, "NO SIGNAL", RED)
            self.font.draw_cursor(52, 20, RED)
            return

        self.font.draw_centered(2, c["symbol"], AMBER, large=True)

        price = c["price"]
        if price >= 1000:
            price_str = f"${price:,.0f}"
        elif price >= 1:
            price_str = f"${price:.2f}"
        else:
            price_str = f"${price:.4f}"
        self.font.draw_centered(12, price_str, GREEN)

        # Separator line
        for x in range(PANEL_W):
            self.buf.set_pixel(x, 20, CYAN)

        # Scrolling delta
        change = c["change"]
        delta_str = f"+{change:.2f}%" if change >= 0 else f"{change:.2f}%"
        delta_color = GREEN if change >= 0 else RED

        now = time.time()
        if now - self.last_scroll > 0.05:
            self.scroll_x -= 1
            self.last_scroll = now
            text_w = self.font.string_width(delta_str)
            if self.scroll_x < -text_w:
                self.scroll_x = PANEL_W

        self.font.draw_string(self.scroll_x, 22, delta_str, delta_color)

    def is_done(self):
        return False


class FsocietyLifeMode:
    """Shows fsociety mask for 3 seconds, then seeds Game of Life with it.
    The face dissolves into living chaos."""

    def __init__(self, buf):
        self.buf = buf
        self.grid = []
        self.last_step = 0
        self.generation = 0
        self.phase = 0  # 0=show face, 1=game of life
        self.phase_start = 0

    def init(self):
        self.phase = 0
        self.phase_start = time.time()
        self.generation = 0
        # Load face into grid
        self.grid = [[False] * PANEL_W for _ in range(PANEL_H)]
        for y in range(PANEL_H):
            for x in range(PANEL_W):
                byte_idx = (y * PANEL_W + x) // 8
                bit_idx = 7 - ((y * PANEL_W + x) % 8)
                if FSOCIETY_SPRITE[byte_idx] & (1 << bit_idx):
                    self.grid[y][x] = True

    def _neighbors(self, x, y):
        count = 0
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx = (x + dx) % PANEL_W
                ny = (y + dy) % PANEL_H
                if self.grid[ny][nx]:
                    count += 1
        return count

    def update(self):
        now = time.time()

        if self.phase == 0:
            # Show the face for 3 seconds
            if now - self.phase_start >= 3.0:
                self.phase = 1
                self.last_step = now
        elif self.phase == 1:
            # Game of Life running on the face
            if now - self.last_step >= 0.12:
                new_grid = [[False] * PANEL_W for _ in range(PANEL_H)]
                for y in range(PANEL_H):
                    for x in range(PANEL_W):
                        n = self._neighbors(x, y)
                        if self.grid[y][x]:
                            new_grid[y][x] = n in (2, 3)
                        else:
                            new_grid[y][x] = n == 3
                self.grid = new_grid
                self.last_step = now
                self.generation += 1

        # Render
        self.buf.clear()
        for y in range(PANEL_H):
            for x in range(PANEL_W):
                if self.grid[y][x]:
                    # Dim CYAN cells for variety in Game of Life phase
                    if self.phase == 1 and (x + y) % 7 == 0:
                        self.buf.set_pixel(x, y, (0, 180, 180))
                    else:
                        self.buf.set_pixel(x, y, GREEN)

    def is_done(self):
        return False


class PixelArtMode:
    """10 pixel rabbits hopping around the screen."""

    # 7x7 rabbit sprite frames — ears up and mid-hop
    RABBIT_STAND = [
        "..X.X..",
        "..X.X..",
        ".XXXXX.",
        ".XX.XX.",
        ".XXXXX.",
        "..XXX..",
        ".X...X.",
    ]
    RABBIT_HOP = [
        "..X.X..",
        "..X.X..",
        ".XXXXX.",
        ".XX.XX.",
        ".XXXXX.",
        "...X...",
        "..X.X..",
    ]

    def __init__(self, buf):
        self.buf = buf
        self.rabbits = []

    def init(self):
        self.rabbits = []
        for _ in range(10):
            self.rabbits.append({
                "x": random.uniform(2, PANEL_W - 9),
                "y": random.uniform(2, PANEL_H - 9),
                "vx": random.choice([-1, 1]) * random.uniform(0.3, 1.0),
                "vy": 0,
                "on_ground": True,
                "hop_timer": random.uniform(0, 2),
                "frame": 0,
                "color": random.choice([GREEN, (0, 220, 50), (0, 180, 40), WHITE, CYAN, PINK, AMBER]),
            })

    def update(self):
        self.buf.clear()
        now = time.time()

        for r in self.rabbits:
            # Hop logic
            r["hop_timer"] -= 1.0 / FPS
            if r["hop_timer"] <= 0 and r["on_ground"]:
                r["vy"] = -random.uniform(1.5, 3.0)
                r["on_ground"] = False
                r["hop_timer"] = random.uniform(0.5, 2.0)
                r["frame"] = 1
                # Sometimes change direction
                if random.random() < 0.3:
                    r["vx"] = -r["vx"]

            # Gravity
            if not r["on_ground"]:
                r["vy"] += 0.15  # gravity
                if r["vy"] > 0:
                    r["frame"] = 0

            # Move
            r["x"] += r["vx"] * 0.5
            r["y"] += r["vy"] * 0.5

            # Ground collision
            ground = PANEL_H - 8
            if r["y"] >= ground:
                r["y"] = ground
                r["vy"] = 0
                r["on_ground"] = True
                r["frame"] = 0

            # Wall bounce
            if r["x"] <= 0:
                r["x"] = 0
                r["vx"] = abs(r["vx"])
            if r["x"] >= PANEL_W - 7:
                r["x"] = PANEL_W - 7
                r["vx"] = -abs(r["vx"])

            # Draw sprite
            sprite = self.RABBIT_HOP if r["frame"] == 1 else self.RABBIT_STAND
            bx, by = int(r["x"]), int(r["y"])
            # Flip sprite based on direction
            flip = r["vx"] < 0
            for sy, row in enumerate(sprite):
                chars = list(reversed(row)) if flip else list(row)
                for sx, ch in enumerate(chars):
                    if ch == 'X':
                        self.buf.set_pixel(bx + sx, by + sy, r["color"])

    def is_done(self):
        return False


class RaveMode:
    """Psychedelic rainbow plasma with color cycling."""

    WORDS = ["RAVE", "PULSE", "PIXEL", "GLOW"]

    def __init__(self, buf, font):
        self.buf = buf
        self.font = font
        self.start_time = 0
        self.last_word_time = 0
        self.current_word = ""
        self.word_y = 12
        self.word_color = (255, 0, 255)

    @staticmethod
    def hsv_to_rgb(h, s, v):
        """h: 0-360, s: 0-1, v: 0-1 -> (r, g, b) 0-255"""
        h = h % 360
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        if h < 60:
            r, g, b = c, x, 0
        elif h < 120:
            r, g, b = x, c, 0
        elif h < 180:
            r, g, b = 0, c, x
        elif h < 240:
            r, g, b = 0, x, c
        elif h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))

    def init(self):
        self.start_time = time.time()
        self.last_word_time = time.time()
        self.current_word = random.choice(self.WORDS)
        self.word_y = random.randint(4, PANEL_H - 10)
        self.word_color = self.hsv_to_rgb(random.uniform(0, 360), 1.0, 1.0)

    def update(self):
        self.buf.clear()
        now = time.time()
        t = now - self.start_time
        base_hue = (t * 120) % 360  # 120 degrees/second rotation

        # ── Layer 1: Rainbow plasma ──
        for y in range(PANEL_H):
            for x in range(PANEL_W):
                val = (math.sin(x * 0.15 + t * 2.0)
                       + math.sin(y * 0.2 + t * 1.5)
                       + math.sin((x + y) * 0.1 + t * 2.5))
                hue = (base_hue + val * 60) % 360
                color = self.hsv_to_rgb(hue, 1.0, 0.5)
                self.buf.set_pixel(x, y, color)

        # ── Layer 2: Concentric rings pulsing outward ──
        cx, cy = PANEL_W // 2, PANEL_H // 2
        for ring in range(1, 20):
            radius = ((ring * 3 + t * 15) % 40)
            ring_hue = (base_hue + ring * 40) % 360
            ring_color = self.hsv_to_rgb(ring_hue, 1.0, 0.8)
            for angle_deg in range(0, 360, 5):
                rad = math.radians(angle_deg)
                px = int(cx + radius * math.cos(rad))
                py = int(cy + radius * math.sin(rad) * 0.5)  # squish Y for aspect ratio
                if 0 <= px < PANEL_W and 0 <= py < PANEL_H:
                    self.buf.set_pixel(px, py, ring_color)

        # ── Layer 3: Random sparkle ──
        for _ in range(25):
            sx = random.randint(0, PANEL_W - 1)
            sy = random.randint(0, PANEL_H - 1)
            self.buf.set_pixel(sx, sy, WHITE)

        # ── Layer 4: Text flash ──
        if now - self.last_word_time >= 0.8:
            self.last_word_time = now
            self.current_word = random.choice(self.WORDS)
            self.word_y = random.randint(4, PANEL_H - 10)
            self.word_color = self.hsv_to_rgb(random.uniform(0, 360), 1.0, 1.0)

        # Flash the word with a brief visible window
        if now - self.last_word_time < 0.4:
            self.font.draw_centered(self.word_y, self.current_word, self.word_color, large=True)

    def is_done(self):
        return False


class AnalogClockMode:
    """Ticking analog clock rendered in green phosphor style."""

    def __init__(self, buf):
        self.buf = buf
        # True center of a 64x32 grid (use floats for precision)
        self.cx = 31.5
        self.cy = 15.5
        self.radius = 14

    def init(self):
        pass

    def update(self):
        self.buf.clear()
        now = datetime.now()
        h, m, s = now.hour % 12, now.minute, now.second

        # Draw clock face — circle outline
        for angle in range(360):
            rad = math.radians(angle)
            x = round(self.cx + self.radius * math.cos(rad))
            y = round(self.cy + self.radius * math.sin(rad))
            self.buf.set_pixel(x, y, (0, 60, 15))

        # Hour tick marks
        for tick in range(12):
            angle = math.radians(tick * 30 - 90)
            for r in range(self.radius - 2, self.radius + 1):
                x = round(self.cx + r * math.cos(angle))
                y = round(self.cy + r * math.sin(angle))
                self.buf.set_pixel(x, y, GREEN)

        # Hour hand
        h_angle = math.radians((h + m / 60.0) * 30 - 90)
        self._draw_hand(h_angle, 7, CYAN)

        # Minute hand
        m_angle = math.radians((m + s / 60.0) * 6 - 90)
        self._draw_hand(m_angle, 10, GREEN)

        # Second hand — ticking, red
        s_angle = math.radians(s * 6 - 90)
        self._draw_hand(s_angle, 12, RED)

        # Center dot — 2x2 centered on true center
        cx, cy = int(self.cx), int(self.cy)
        self.buf.set_pixel(cx, cy, WHITE)
        self.buf.set_pixel(cx + 1, cy, WHITE)
        self.buf.set_pixel(cx, cy + 1, WHITE)
        self.buf.set_pixel(cx + 1, cy + 1, WHITE)

    def _draw_hand(self, angle, length, color):
        """Line from center outward."""
        for i in range(length + 1):
            t = i / length
            x = round(self.cx + t * length * math.cos(angle))
            y = round(self.cy + t * length * math.sin(angle))
            self.buf.set_pixel(x, y, color)

    def is_done(self):
        return False


class MatrixMode:
    """Digital rain — dense falling green characters, Mr. Robot style.
    Starts sparse, builds to a torrent over the mode duration."""

    def __init__(self, buf, font):
        self.buf = buf
        self.font = font
        self.columns = []
        self.start_time = 0
        self.next_spawn = 0

    def _make_column(self, x=None):
        return {
            "x": x if x is not None else random.randint(0, (PANEL_W // 5)) * 5,
            "y": random.uniform(-PANEL_H * 1.5, -1),
            "speed": random.uniform(0.04, 0.18),
            "length": random.randint(6, PANEL_H),
            "chars": [chr(random.randint(33, 126)) for _ in range(PANEL_H)],
            "last_step": time.time(),
            "mutate_rate": random.uniform(0.05, 0.3),
        }

    def init(self):
        self.start_time = time.time()
        self.next_spawn = time.time()
        self.columns = []
        # Seed with a few columns
        for x_col in range(0, PANEL_W, 5):
            if random.random() < 0.4:
                self.columns.append(self._make_column(x_col))

    def update(self):
        self.buf.clear()
        now = time.time()
        elapsed = now - self.start_time

        # Ramp density: spawn more columns over time
        # At 0s: ~13 columns, at 10s: every slot filled, overlapping
        spawn_interval = max(0.05, 0.6 - elapsed * 0.06)
        if now >= self.next_spawn:
            self.next_spawn = now + spawn_interval
            # Pick a random x slot, allow duplicates for density
            x = random.randint(0, (PANEL_W // 5)) * 5
            self.columns.append(self._make_column(x))
            # After 5s, start spawning offset columns too (between slots)
            if elapsed > 5 and random.random() < 0.5:
                x2 = random.randint(0, (PANEL_W // 5)) * 5 + random.choice([2, 3])
                self.columns.append(self._make_column(x2))

        alive = []
        for col in self.columns:
            if now - col["last_step"] >= col["speed"]:
                col["y"] += 1
                col["last_step"] = now
                # Mutate characters in the trail for shimmer
                if random.random() < col["mutate_rate"]:
                    idx = random.randint(0, len(col["chars"]) - 1)
                    col["chars"][idx] = chr(random.randint(33, 126))

            head_y = int(col["y"])

            # Draw the trail
            for i in range(col["length"]):
                cy = head_y - i
                if 0 <= cy < PANEL_H:
                    char_idx = (head_y - i) % len(col["chars"])
                    ch = col["chars"][char_idx]
                    if i == 0:
                        color = WHITE
                    elif i == 1:
                        color = (180, 255, 190)
                    elif i == 2:
                        color = (0, 255, 65)
                    elif i < 5:
                        # Occasional CYAN or PURPLE for variety
                        r_val = random.random()
                        if r_val < 0.08:
                            color = CYAN
                        elif r_val < 0.12:
                            color = PURPLE
                        else:
                            color = (0, 200, 50)
                    elif i < 8:
                        color = (0, 140, 35)
                    elif i < 12:
                        color = (0, 80, 20)
                    else:
                        fade = max(10, 60 - (i - 12) * 5)
                        color = (0, fade, fade // 4)
                    self.font.draw_char(col["x"], cy, ch, color,
                                        FONT_4x6, 4, 6)

            # Keep alive if still on screen
            if head_y - col["length"] < PANEL_H:
                alive.append(col)

        self.columns = alive

        # Cap to prevent runaway memory (shouldn't happen but safety)
        if len(self.columns) > 80:
            self.columns = self.columns[-80:]

    def is_done(self):
        return False


class NetworkSniffer:
    """Background listener for LAN broadcast/multicast traffic."""

    def __init__(self):
        self._lock = threading.Lock()
        self._packets = []       # Recent packet log [(timestamp, proto, info), ...]
        self._counts = {}        # Protocol → count
        self._running = True
        self._sockets = []

    def start(self):
        listeners = [
            self._listen_mdns,       # mDNS/Bonjour
            self._listen_ssdp,       # SSDP/UPnP
            self._listen_netbios,    # NetBIOS
            self._listen_broadcast,  # DHCP/LLMNR
            self._listen_arp,        # ARP table polling
            self._listen_igmp,       # IGMP multicast
            self._listen_ntp,        # NTP
            self._listen_smb,        # SMB datagrams
            self._poll_connections,  # HTTPS/HTTP/DNS/SSH/ICMP via netstat
        ]
        for fn in listeners:
            threading.Thread(target=fn, daemon=True).start()
        print(f"[NET] Started {len(listeners)} network listeners")

    def _log_packet(self, proto, info):
        with self._lock:
            self._counts[proto] = self._counts.get(proto, 0) + 1
            self._packets.append((time.time(), proto, info))
            # Keep last 50
            if len(self._packets) > 50:
                self._packets = self._packets[-50:]

    def get_recent(self, n=8):
        with self._lock:
            return list(self._packets[-n:])

    def get_counts(self):
        with self._lock:
            return dict(self._counts)

    def _make_multicast_socket(self, group, port):
        """Create a UDP socket joined to a multicast group."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            sock.bind(('', port))
            # Join multicast group
            mreq = struct.pack("4sl", socket.inet_aton(group), socket.INADDR_ANY)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            sock.settimeout(2.0)
            return sock
        except Exception as e:
            print(f"[NET] Failed to bind {group}:{port}: {e}")
            return None

    def _make_broadcast_socket(self, port):
        """Create a UDP socket for broadcast traffic."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.bind(('', port))
            sock.settimeout(2.0)
            return sock
        except Exception as e:
            print(f"[NET] Failed to bind broadcast:{port}: {e}")
            return None

    def _listen_mdns(self):
        """mDNS / Bonjour — 224.0.0.251:5353"""
        sock = self._make_multicast_socket("224.0.0.251", 5353)
        if not sock:
            return
        while self._running:
            try:
                data, addr = sock.recvfrom(4096)
                # Parse mDNS query/response name (simplified)
                name = self._parse_dns_name(data, 12) if len(data) > 12 else "?"
                self._log_packet("MDNS", f"{addr[0]} {name[:20]}")
            except socket.timeout:
                pass
            except Exception:
                pass

    def _listen_ssdp(self):
        """SSDP/UPnP — 239.255.255.250:1900"""
        sock = self._make_multicast_socket("239.255.255.250", 1900)
        if not sock:
            return
        while self._running:
            try:
                data, addr = sock.recvfrom(4096)
                text = data.decode('utf-8', errors='ignore')
                if 'M-SEARCH' in text:
                    self._log_packet("SSDP", f"{addr[0]} SEARCH")
                elif 'NOTIFY' in text:
                    self._log_packet("SSDP", f"{addr[0]} NOTIFY")
                else:
                    self._log_packet("SSDP", f"{addr[0]}")
            except socket.timeout:
                pass
            except Exception:
                pass

    def _listen_netbios(self):
        """NetBIOS Name Service — broadcast port 137"""
        sock = self._make_broadcast_socket(137)
        if not sock:
            return
        while self._running:
            try:
                data, addr = sock.recvfrom(4096)
                self._log_packet("NBNS", f"{addr[0]}")
            except socket.timeout:
                pass
            except Exception:
                pass

    def _listen_broadcast(self):
        """DHCP and general broadcast — port 68 (DHCP client)"""
        sock = self._make_broadcast_socket(68)
        if not sock:
            # Try LLMNR instead — 224.0.0.252:5355
            sock = self._make_multicast_socket("224.0.0.252", 5355)
            if not sock:
                return
            while self._running:
                try:
                    data, addr = sock.recvfrom(4096)
                    self._log_packet("LLMNR", f"{addr[0]}")
                except socket.timeout:
                    pass
                except Exception:
                    pass
            return

        while self._running:
            try:
                data, addr = sock.recvfrom(4096)
                self._log_packet("DHCP", f"{addr[0]}")
            except socket.timeout:
                pass
            except Exception:
                pass

    def _listen_arp(self):
        """ARP — poll ARP table for device changes."""
        import subprocess
        last_table = set()
        while self._running:
            try:
                result = subprocess.run(['arp', '-a'], capture_output=True, text=True, timeout=5)
                lines = result.stdout.strip().split('\n')
                current = set()
                for line in lines:
                    if '(' in line and ')' in line:
                        ip = line.split('(')[1].split(')')[0]
                        current.add(ip)
                        if ip not in last_table and last_table:
                            self._log_packet("ARP", f"{ip} NEW")
                for ip in last_table - current:
                    self._log_packet("ARP", f"{ip} GONE")
                if not last_table and current:
                    for ip in list(current)[:5]:
                        self._log_packet("ARP", f"{ip}")
                last_table = current
            except Exception:
                pass
            time.sleep(8)

    def _listen_igmp(self):
        """IGMP — 224.0.0.22 / all-hosts 224.0.0.1"""
        sock = self._make_multicast_socket("224.0.0.1", 0)
        if not sock:
            return
        while self._running:
            try:
                data, addr = sock.recvfrom(4096)
                self._log_packet("IGMP", f"{addr[0]}")
            except socket.timeout:
                pass
            except Exception:
                pass

    def _listen_ntp(self):
        """NTP — watch for NTP traffic on port 123."""
        sock = self._make_broadcast_socket(123)
        if not sock:
            return
        while self._running:
            try:
                data, addr = sock.recvfrom(512)
                self._log_packet("NTP", f"{addr[0]}")
            except socket.timeout:
                pass
            except Exception:
                pass

    def _listen_smb(self):
        """SMB/NetBIOS Session — port 138 (datagram service)."""
        sock = self._make_broadcast_socket(138)
        if not sock:
            return
        while self._running:
            try:
                data, addr = sock.recvfrom(4096)
                self._log_packet("SMB", f"{addr[0]}")
            except socket.timeout:
                pass
            except Exception:
                pass

    def _poll_connections(self):
        """Poll active TCP connections for HTTPS, HTTP, DNS, ICMP, SMB activity."""
        import subprocess
        last_conns = set()
        while self._running:
            try:
                result = subprocess.run(
                    ['netstat', '-n', '-p', 'tcp'],
                    capture_output=True, text=True, timeout=5
                )
                current = set()
                for line in result.stdout.split('\n'):
                    parts = line.split()
                    if len(parts) >= 5 and 'ESTABLISHED' in line:
                        remote = parts[4]
                        current.add(remote)
                        if remote not in last_conns:
                            port = remote.split('.')[-1] if '.' in remote else '?'
                            ip = '.'.join(remote.split('.')[:-1]) if '.' in remote else remote
                            if port == '443':
                                self._log_packet("HTTPS", f"{ip}")
                            elif port == '80':
                                self._log_packet("HTTP", f"{ip}")
                            elif port == '53':
                                self._log_packet("DNS", f"{ip}")
                            elif port == '445':
                                self._log_packet("SMB", f"{ip}")
                            elif port == '22':
                                self._log_packet("SSH", f"{ip}")
                last_conns = current
            except Exception:
                pass
            # Also check ICMP via ping count
            try:
                result = subprocess.run(
                    ['netstat', '-s', '-p', 'icmp'],
                    capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.split('\n'):
                    if 'received' in line.lower() and 'echo' in line.lower():
                        self._log_packet("ICMP", "PING")
                        break
            except Exception:
                pass
            time.sleep(5)

    def _parse_dns_name(self, data, offset):
        """Extract first DNS name from packet."""
        labels = []
        try:
            while offset < len(data):
                length = data[offset]
                if length == 0:
                    break
                if length >= 0xC0:  # pointer
                    break
                offset += 1
                labels.append(data[offset:offset+length].decode('utf-8', errors='ignore'))
                offset += length
        except Exception:
            pass
        return '.'.join(labels) if labels else '?'


class NetworkMode:
    """Radar sweep display with live LAN packet blips."""

    def __init__(self, buf, font, sniffer):
        self.buf = buf
        self.font = font
        self.sniffer = sniffer
        self.sweep_angle = 0.0
        self.blips = []  # [(x, y, birth_time), ...]
        self.trail = [0] * 72  # 5 degrees each, brightness 0-255
        self.scroll_x = PANEL_W
        self.last_scroll = 0
        self.last_packet_count = 0
        self.ticker_entries = []

    # Radar geometry
    CX = 31
    CY = 10
    RADIUS = 10
    SWEEP_SPEED = math.radians(3)  # ~3 degrees per frame

    def init(self):
        self.sweep_angle = 0.0
        self.blips = []
        self.trail = [0] * 72
        self.scroll_x = PANEL_W
        self.last_scroll = time.time()
        self.last_packet_count = 0
        self.ticker_entries = []

    def update(self):
        self.buf.clear()
        now = time.time()

        # ── Advance sweep ──
        self.sweep_angle += self.SWEEP_SPEED
        if self.sweep_angle >= 2 * math.pi:
            self.sweep_angle -= 2 * math.pi

        # ── Update trail brightness ──
        bucket = int(self.sweep_angle / (2 * math.pi) * 72) % 72
        for i in range(72):
            if i == bucket:
                self.trail[i] = 255
            else:
                self.trail[i] = max(0, self.trail[i] - 6)

        # ── Check for new packets → spawn blips ──
        recent = self.sniffer.get_recent(8)
        current_count = len(recent)
        if current_count > self.last_packet_count:
            new_packets = current_count - self.last_packet_count
            for _ in range(min(new_packets, 3)):
                angle = random.uniform(0, 2 * math.pi)
                dist = random.uniform(3, self.RADIUS - 1)
                bx = self.CX + int(dist * math.cos(angle))
                by = self.CY + int(dist * math.sin(angle))
                if 0 <= bx < PANEL_W and 0 <= by < 22:
                    self.blips.append((bx, by, now))
            # Update ticker
            for _, proto, info in recent[-(current_count - self.last_packet_count):]:
                ip = info.split()[0] if info else "?"
                self.ticker_entries.append(f"{proto} {ip}")
                if len(self.ticker_entries) > 10:
                    self.ticker_entries = self.ticker_entries[-10:]
        self.last_packet_count = current_count

        # ── Fade old blips ──
        self.blips = [(bx, by, bt) for bx, by, bt in self.blips if now - bt < 2.0]

        # ── Draw radar circle outline (rows 0-21) ──
        for angle_deg in range(360):
            rad = math.radians(angle_deg)
            x = self.CX + int(self.RADIUS * math.cos(rad))
            y = self.CY + int(self.RADIUS * math.sin(rad))
            if 0 <= x < PANEL_W and 0 <= y < 22:
                self.buf.set_pixel(x, y, (0, 60, 15))

        # ── Draw phosphor trail ──
        for i in range(72):
            if self.trail[i] < 10:
                continue
            angle = i / 72.0 * 2 * math.pi
            g = self.trail[i]
            color = (0, g, g // 8 if g > 180 else 0)
            for d in range(2, self.RADIUS + 1, 2):
                x = self.CX + int(d * math.cos(angle))
                y = self.CY + int(d * math.sin(angle))
                if 0 <= x < PANEL_W and 0 <= y < 22:
                    self.buf.set_pixel(x, y, color)

        # ── Draw sweep line (bright green) ──
        for d in range(1, self.RADIUS + 1):
            x = self.CX + int(d * math.cos(self.sweep_angle))
            y = self.CY + int(d * math.sin(self.sweep_angle))
            if 0 <= x < PANEL_W and 0 <= y < 22:
                self.buf.set_pixel(x, y, GREEN)

        # ── Draw blips (CYAN, fading) ──
        for bx, by, bt in self.blips:
            age = now - bt
            brightness = max(0, 1.0 - age / 2.0)
            color = (0, int(255 * brightness), int(255 * brightness))
            self.buf.set_pixel(bx, by, color)
            # Larger blip when fresh
            if brightness > 0.7:
                if bx + 1 < PANEL_W:
                    self.buf.set_pixel(bx + 1, by, color)
                if by + 1 < 22:
                    self.buf.set_pixel(bx, by + 1, color)

        # Center dot
        self.buf.set_pixel(self.CX, self.CY, WHITE)

        # ── Separator line (row 22) ──
        for x in range(PANEL_W):
            self.buf.set_pixel(x, 22, (0, 60, 15))

        # ── Scrolling ticker (rows 23-28) ──
        if self.ticker_entries:
            ticker_text = "  >  ".join(self.ticker_entries[-5:])
        else:
            ticker_text = "LISTENING..."
        if now - self.last_scroll >= 0.05:
            self.last_scroll = now
            self.scroll_x -= 1
            tw = self.font.string_width(ticker_text)
            if self.scroll_x < -tw:
                self.scroll_x = PANEL_W
        self.font.draw_string(self.scroll_x, 23, ticker_text, AMBER)

        # ── Separator line (row 29) ──
        for x in range(PANEL_W):
            self.buf.set_pixel(x, 29, (0, 60, 15))

        # ── "RADAR" label (rows 30-31) ──
        self.font.draw_centered(30, "RADAR", WHITE)

    def is_done(self):
        return False


class WiFiRadarMode:
    """Animated radar sweep showing nearby WiFi networks as colored blips.
    Uses fake randomized data in the simulator (real WiFi.scanNetworks on ESP32)."""

    CYAN   = (0, 255, 255)
    AMBER  = (255, 170, 0)
    DIM_CYAN = (0, 80, 80)
    DIM_GREEN_RING = (0, 26, 8)

    CX = 15
    CY = 12
    RADIUS = 11
    SWEEP_SPEED = 0.07    # radians per frame
    TRAIL_SLICES = 72     # 5 degrees each
    SCAN_INTERVAL = 10.0  # seconds

    def __init__(self, buf, font):
        self.buf = buf
        self.font = font
        self.sweep_angle = 0.0
        self.trail = [0] * self.TRAIL_SLICES
        self.networks = []
        self.last_scan = 0
        self.scroll_x = PANEL_W
        self.last_scroll = 0
        self.display_idx = 0

    def _generate_fake_networks(self):
        """Generate randomized WiFi networks for the simulator."""
        names = [
            "TellMyWifiLoveHer", "xfinitywifi", "FBI_VAN_7", "PrettyFlyForAWiFi",
            "TP-LINK_5G", "ASUS_HOME", "linksys", "THE_MATRIX",
            "virus.exe", "NotYourWifi", "SkyNet", "DUNDER_MIFFLIN",
            "Wu-Tang_LAN", "BillWitheScienceFi", "404_NotFound",
        ]
        count = random.randint(8, 15)
        nets = []
        for i in range(count):
            name = names[i % len(names)]
            # Generate a fake BSSID for stable angle hashing
            bssid = ":".join(f"{random.randint(0,255):02X}" for _ in range(6))
            rssi = random.randint(-92, -28)
            # Hash BSSID to angle
            h = 5381
            for c in bssid:
                h = ((h << 5) + h) + ord(c)
            angle = (h % 3600) * 2 * math.pi / 3600.0
            # RSSI to distance
            dist = (-rssi - 30) / 60.0
            dist = max(0.15, min(1.0, dist))
            nets.append({
                "ssid": name,
                "rssi": rssi,
                "angle": angle,
                "distance": dist,
                "glow": 55,
                "last_swept": 0,
                "bssid": bssid,
            })
        # Sort strongest first
        nets.sort(key=lambda n: n["rssi"], reverse=True)
        return nets

    def init(self):
        self.sweep_angle = 0.0
        self.trail = [0] * self.TRAIL_SLICES
        self.scroll_x = PANEL_W
        self.display_idx = 0
        self.last_scan = time.time()
        self.networks = self._generate_fake_networks()

    def _rssi_color(self, rssi):
        if rssi > -50:  return self.CYAN
        if rssi > -70:  return GREEN
        if rssi > -85:  return self.AMBER
        return RED

    def _rssi_glow_color(self, rssi, glow):
        """Scale base color by glow factor (0-255)."""
        f = glow / 255.0
        if rssi > -50:
            return (0, int(255 * f), int(255 * f))
        elif rssi > -70:
            return (0, int(255 * f), int(65 * f))
        elif rssi > -85:
            return (int(255 * f), int(170 * f), 0)
        else:
            return (int(255 * f), int(32 * f), 0)

    def update(self):
        now = time.time()
        self.buf.clear()

        # ── Re-scan (re-randomize signal strengths slightly) ──
        if now - self.last_scan >= self.SCAN_INTERVAL:
            self.last_scan = now
            for net in self.networks:
                net["rssi"] = max(-95, min(-25, net["rssi"] + random.randint(-5, 5)))
                net["distance"] = max(0.15, min(1.0, (-net["rssi"] - 30) / 60.0))

        # ── Advance sweep ──
        self.sweep_angle += self.SWEEP_SPEED
        if self.sweep_angle >= 2 * math.pi:
            self.sweep_angle -= 2 * math.pi

        # ── Update trail ──
        bucket = int(self.sweep_angle / (2 * math.pi) * self.TRAIL_SLICES) % self.TRAIL_SLICES
        for i in range(self.TRAIL_SLICES):
            if i == bucket:
                self.trail[i] = 255
            else:
                self.trail[i] = max(0, self.trail[i] - 8)

        # ── Update blip glow ──
        for net in self.networks:
            diff = abs(self.sweep_angle - net["angle"])
            if diff > math.pi:
                diff = 2 * math.pi - diff
            if diff < 0.15:
                net["glow"] = 255
                net["last_swept"] = now
            else:
                elapsed = now - net["last_swept"]
                if elapsed < 1.0:
                    net["glow"] = max(55, int(255 - elapsed * 200))
                else:
                    net["glow"] = 55

        # ── Draw range rings ──
        for ring in range(1, 4):
            r = (self.RADIUS * ring) // 3
            for a in range(0, 360, 3):
                rad = a * math.pi / 180.0
                x = self.CX + int(r * math.cos(rad))
                y = self.CY + int(r * math.sin(rad))
                if 0 <= x < PANEL_W and 0 <= y < 25:
                    self.buf.set_pixel(x, y, self.DIM_GREEN_RING)

        # Cross-hairs
        for i in range(-self.RADIUS, self.RADIUS + 1, 2):
            px, py = self.CX + i, self.CY + i
            if 0 <= px < PANEL_W and 0 <= self.CY < 25:
                self.buf.set_pixel(px, self.CY, self.DIM_GREEN_RING)
            if 0 <= self.CX < PANEL_W and 0 <= py < 25:
                self.buf.set_pixel(self.CX, py, self.DIM_GREEN_RING)

        # ── Draw phosphor trail ──
        for i in range(self.TRAIL_SLICES):
            if self.trail[i] < 10:
                continue
            angle = i / self.TRAIL_SLICES * 2 * math.pi
            g = self.trail[i]
            b = g // 8 if g > 180 else 0
            color = (0, g, b)
            for d in range(2, self.RADIUS + 1, 2):
                x = self.CX + int(d * math.cos(angle))
                y = self.CY + int(d * math.sin(angle))
                if 0 <= x < PANEL_W and 0 <= y < 25:
                    self.buf.set_pixel(x, y, color)

        # ── Draw sweep line ──
        for d in range(1, self.RADIUS + 1):
            x = self.CX + int(d * math.cos(self.sweep_angle))
            y = self.CY + int(d * math.sin(self.sweep_angle))
            if 0 <= x < PANEL_W and 0 <= y < 25:
                color = self.CYAN if d > self.RADIUS * 2 // 3 else GREEN
                self.buf.set_pixel(x, y, color)

        # Center dot 2x2 white
        for dx in range(2):
            for dy in range(2):
                self.buf.set_pixel(self.CX + dx, self.CY + dy, WHITE)

        # ── Draw blips ──
        for net in self.networks:
            d = int(net["distance"] * self.RADIUS)
            if d < 2:
                d = 2
            x = self.CX + int(d * math.cos(net["angle"]))
            y = self.CY + int(d * math.sin(net["angle"]))
            if not (0 <= x < PANEL_W and 0 <= y < 25):
                continue

            color = self._rssi_glow_color(net["rssi"], net["glow"])
            self.buf.set_pixel(x, y, color)

            # Bigger blips for strong signals
            if net["rssi"] > -60 and net["glow"] > 100:
                if x + 1 < PANEL_W: self.buf.set_pixel(x + 1, y, color)
                if y + 1 < 25:      self.buf.set_pixel(x, y + 1, color)
            if net["rssi"] > -45 and net["glow"] > 150:
                if x - 1 >= 0:      self.buf.set_pixel(x - 1, y, color)
                if y - 1 >= 0:      self.buf.set_pixel(x, y - 1, color)

        # ── Info strip (y=25..31) ──
        # Separator line
        for x in range(PANEL_W):
            self.buf.set_pixel(x, 25, self.DIM_CYAN)

        # "RADAR" label + count
        self.font.draw_string(1, 26, "RADAR", GREEN)
        count_str = str(len(self.networks))
        cw = self.font.string_width(count_str)
        self.font.draw_string(PANEL_W - cw - 1, 26, count_str, self.CYAN)

        # Scrolling SSID
        if self.networks:
            if now - self.last_scroll >= 0.05:
                self.last_scroll = now
                self.scroll_x -= 1
                net = self.networks[self.display_idx % len(self.networks)]
                info = f"{net['ssid']} {net['rssi']}dBm"
                tw = self.font.string_width(info)
                if self.scroll_x < -tw:
                    self.scroll_x = PANEL_W
                    self.display_idx = (self.display_idx + 1) % len(self.networks)

            net = self.networks[self.display_idx % len(self.networks)]
            info = f"{net['ssid']} {net['rssi']}dBm"
            text_color = self.CYAN if net["rssi"] > -60 else GREEN
            self.font.draw_string(self.scroll_x, 26 + 6, info, text_color)
        else:
            dots = int((now * 2.5) % 4)
            self.font.draw_string(1, 26 + 6, "SCANNING" + "." * dots, GREEN)

    def is_done(self):
        return False


class FlightMode:
    def __init__(self, buf, font, poller):
        self.buf = buf
        self.font = font
        self.poller = poller
        self.scanning = True
        self.scan_start = 0

    def init(self):
        self.scanning = True
        self.scan_start = time.time()

    def update(self):
        self.buf.clear()
        flights = self.poller.get_flights()

        if self.scanning:
            self.font.draw_centered(8, "SCANNING...", GREEN)
            w = self.font.string_width("SCANNING...")
            cx = (PANEL_W + w) // 2 + 2
            self.font.draw_cursor(cx, 8, GREEN)
            elapsed = time.time() - self.scan_start
            if flights and elapsed > 1.5:
                self.scanning = False
            if not flights and elapsed > 5:
                self.scanning = False
            return

        if not flights:
            flights = ["DAL1234", "UAL567", "SWA890"]

        self.font.draw_string(1, 0, "DEPARTURES", GREEN)
        for x in range(PANEL_W):
            self.buf.set_pixel(x, 7, CYAN)

        y_pos = 10
        for i, callsign in enumerate(flights[:3]):
            self.font.draw_string(2, y_pos, callsign[:8].upper(), AMBER)
            y_pos += 7

    def is_done(self):
        return False


# ── Main ──

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("PIXELPULSE // SIMULATOR")
    clock = pygame.time.Clock()

    buf = PixelBuffer(screen)
    font = FontRenderer(buf)
    poller = ApiPoller(CONFIG)
    sniffer = NetworkSniffer()
    sniffer.start()

    # Build mode list
    boot = BootMode(buf, font)
    glitch = GlitchTransition(buf)
    modes = [
        InfoMode(buf, font, CONFIG["customer_name"]),
        WordClockMode(buf, font, CONFIG["customer_name"]),
        AnalogClockMode(buf),
        WeatherMode(buf, font, poller),
        CryptoMode(buf, font, poller),
        MatrixMode(buf, font),
        FsocietyLifeMode(buf),
        PixelArtMode(buf),
        RaveMode(buf, font),
        NetworkMode(buf, font, sniffer),
        WiFiRadarMode(buf, font),
        FlightMode(buf, font, poller),
    ]

    # State machine
    STATE_BOOT = 0
    STATE_GLITCH = 1
    STATE_MODE = 2
    state = STATE_BOOT
    current_mode = 0
    mode_start = 0
    mode_duration = 5  # Fast review mode — 5s per mode

    boot.init()
    poller.start()

    print("╔══════════════════════════╗")
    print("║  PIXELPULSE // SIMULATOR ║")
    print("╚══════════════════════════╝")
    print(f"[CONFIG] City: {CONFIG['city']}")
    print(f"[CONFIG] Crypto: {CONFIG['crypto']}")
    print(f"[CONFIG] ICAO: {CONFIG['icao']}")
    print(f"[CONFIG] Customer: {CONFIG['customer_name']}")
    print("[BOOT] >> HELLO FRIEND <<")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE:
                    # Skip to next mode
                    current_mode = (current_mode + 1) % len(modes)
                    state = STATE_GLITCH
                    glitch.init()
                if event.key == pygame.K_LEFT:
                    current_mode = (current_mode - 1) % len(modes)
                    state = STATE_GLITCH
                    glitch.init()
                if event.key == pygame.K_UP:
                    mode_duration = min(30, mode_duration + 2)
                    print(f"[TIMER] Mode duration: {mode_duration}s")
                if event.key == pygame.K_DOWN:
                    mode_duration = max(2, mode_duration - 2)
                    print(f"[TIMER] Mode duration: {mode_duration}s")

        if state == STATE_BOOT:
            boot.update()
            if boot.is_done():
                state = STATE_GLITCH
                glitch.init()

        elif state == STATE_GLITCH:
            glitch.update()
            if glitch.is_done():
                state = STATE_MODE
                modes[current_mode].init()
                mode_start = time.time()
                mode_name = type(modes[current_mode]).__name__
                print(f"[MODE] {mode_name} ({mode_duration}s)")
                pygame.display.set_caption(f"PIXELPULSE // {mode_name.upper()}")

        elif state == STATE_MODE:
            modes[current_mode].update()
            elapsed = time.time() - mode_start
            mode_name = type(modes[current_mode]).__name__
            long_modes = ("MatrixMode", "FsocietyLifeMode")
            this_duration = mode_duration * 3 if mode_name in long_modes else mode_duration
            if elapsed >= this_duration or modes[current_mode].is_done():
                current_mode = (current_mode + 1) % len(modes)
                # Skip glitch transition into Matrix — the rain IS the transition
                if type(modes[current_mode]).__name__ == "MatrixMode":
                    state = STATE_MODE
                    modes[current_mode].init()
                    mode_start = time.time()
                    mode_name = type(modes[current_mode]).__name__
                    print(f"[MODE] {mode_name} ({mode_duration * 3}s)")
                    pygame.display.set_caption(f"PIXELPULSE // {mode_name.upper()}")
                else:
                    state = STATE_GLITCH
                    glitch.init()

        buf.render()
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
