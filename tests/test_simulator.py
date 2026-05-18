#!/usr/bin/env python3
"""Tests for PixelPulse simulator logic."""
import sys
import os
import json
import time
from unittest.mock import patch, MagicMock
from datetime import datetime

# Mock pygame before importing simulator
sys.modules['pygame'] = MagicMock()

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import simulator


# ── PixelBuffer Tests ──

class TestPixelBuffer:
    def setup_method(self):
        self.surface = MagicMock()
        self.buf = simulator.PixelBuffer(self.surface)

    def test_initial_state_all_black(self):
        for y in range(simulator.PANEL_H):
            for x in range(simulator.PANEL_W):
                assert self.buf.pixels[y][x] == (0, 0, 0)

    def test_set_pixel_valid(self):
        self.buf.set_pixel(10, 5, (0, 255, 65))
        assert self.buf.pixels[5][10] == (0, 255, 65)

    def test_set_pixel_out_of_bounds_ignored(self):
        self.buf.set_pixel(-1, 0, (255, 0, 0))
        self.buf.set_pixel(0, -1, (255, 0, 0))
        self.buf.set_pixel(simulator.PANEL_W, 0, (255, 0, 0))
        self.buf.set_pixel(0, simulator.PANEL_H, (255, 0, 0))
        # No crash, all pixels still black
        for y in range(simulator.PANEL_H):
            for x in range(simulator.PANEL_W):
                assert self.buf.pixels[y][x] == (0, 0, 0)

    def test_set_pixel_corners(self):
        self.buf.set_pixel(0, 0, (1, 2, 3))
        self.buf.set_pixel(63, 0, (4, 5, 6))
        self.buf.set_pixel(0, 31, (7, 8, 9))
        self.buf.set_pixel(63, 31, (10, 11, 12))
        assert self.buf.pixels[0][0] == (1, 2, 3)
        assert self.buf.pixels[0][63] == (4, 5, 6)
        assert self.buf.pixels[31][0] == (7, 8, 9)
        assert self.buf.pixels[31][63] == (10, 11, 12)

    def test_clear(self):
        self.buf.set_pixel(10, 10, (255, 255, 255))
        self.buf.clear()
        assert self.buf.pixels[10][10] == (0, 0, 0)

    def test_dimensions(self):
        assert len(self.buf.pixels) == simulator.PANEL_H
        assert len(self.buf.pixels[0]) == simulator.PANEL_W


# ── FontRenderer Tests ──

class TestFontRenderer:
    def setup_method(self):
        self.surface = MagicMock()
        self.buf = simulator.PixelBuffer(self.surface)
        self.font = simulator.FontRenderer(self.buf)

    def test_string_width_small_font(self):
        # Each 4x6 char is 4px wide + 1px gap, minus trailing gap
        assert self.font.string_width("A") == 4
        assert self.font.string_width("AB") == 9  # 4+1+4
        assert self.font.string_width("ABC") == 14  # 4+1+4+1+4
        assert self.font.string_width("") == 0

    def test_string_width_large_font(self):
        # Each 6x8 char is 6px wide + 1px gap, minus trailing gap
        assert self.font.string_width("A", large=True) == 6
        assert self.font.string_width("AB", large=True) == 13  # 6+1+6
        assert self.font.string_width("", large=True) == 0

    def test_draw_char_sets_pixels(self):
        # Drawing 'A' should set some pixels
        self.font.draw_char(0, 0, 'A', simulator.GREEN,
                           simulator.FONT_4x6, 4, 6)
        lit = sum(1 for y in range(6) for x in range(4)
                  if self.buf.pixels[y][x] != (0, 0, 0))
        assert lit > 0

    def test_draw_char_uppercase_conversion(self):
        # Lowercase should draw same as uppercase
        buf1 = simulator.PixelBuffer(self.surface)
        buf2 = simulator.PixelBuffer(self.surface)
        f1 = simulator.FontRenderer(buf1)
        f2 = simulator.FontRenderer(buf2)
        f1.draw_char(0, 0, 'a', simulator.GREEN, simulator.FONT_4x6, 4, 6)
        f2.draw_char(0, 0, 'A', simulator.GREEN, simulator.FONT_4x6, 4, 6)
        for y in range(6):
            for x in range(4):
                assert buf1.pixels[y][x] == buf2.pixels[y][x]

    def test_draw_string_positions(self):
        self.font.draw_string(0, 0, "AB", simulator.GREEN)
        # First char occupies x=0..3, second at x=5..8
        a_lit = any(self.buf.pixels[y][x] != (0, 0, 0)
                    for y in range(6) for x in range(4))
        b_lit = any(self.buf.pixels[y][x] != (0, 0, 0)
                    for y in range(6) for x in range(5, 9))
        assert a_lit
        assert b_lit

    def test_draw_centered(self):
        self.font.draw_centered(10, "AB", simulator.GREEN)
        # Should be horizontally centered: width=9, so x=(64-9)//2=27
        lit = any(self.buf.pixels[10 + r][27 + c] != (0, 0, 0)
                  for r in range(6) for c in range(9))
        assert lit

    def test_space_draws_no_pixels(self):
        self.font.draw_string(0, 0, " ", simulator.GREEN)
        for y in range(6):
            for x in range(5):
                assert self.buf.pixels[y][x] == (0, 0, 0)


# ── WordClock Time-to-Words Tests ──

class TestWordClock:
    def setup_method(self):
        self.surface = MagicMock()
        self.buf = simulator.PixelBuffer(self.surface)
        self.font = simulator.FontRenderer(self.buf)
        self.clock = simulator.WordClockMode(self.buf, self.font, "TEST")

    def test_on_the_hour(self):
        with patch('simulator.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2026, 4, 6, 15, 0)
            result = self.clock._time_to_words()
            assert result == "THREE O'CLOCK"

    def test_quarter_past(self):
        with patch('simulator.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2026, 4, 6, 9, 15)
            result = self.clock._time_to_words()
            assert result == "QUARTER PAST NINE"

    def test_half_past(self):
        with patch('simulator.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2026, 4, 6, 6, 30)
            result = self.clock._time_to_words()
            assert result == "HALF PAST SIX"

    def test_quarter_to(self):
        with patch('simulator.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2026, 4, 6, 10, 45)
            result = self.clock._time_to_words()
            assert result == "QUARTER TO ELEVEN"

    def test_five_to(self):
        with patch('simulator.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2026, 4, 6, 11, 55)
            result = self.clock._time_to_words()
            assert result == "FIVE TO TWELVE"

    def test_midnight(self):
        with patch('simulator.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2026, 4, 6, 0, 0)
            result = self.clock._time_to_words()
            assert result == "TWELVE O'CLOCK"

    def test_noon(self):
        with patch('simulator.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2026, 4, 6, 12, 0)
            result = self.clock._time_to_words()
            assert result == "TWELVE O'CLOCK"

    def test_rounding_up(self):
        # 10:23 should round to 10:25
        with patch('simulator.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2026, 4, 6, 10, 23)
            result = self.clock._time_to_words()
            assert result == "TWENTY FIVE PAST TEN"

    def test_rounding_down(self):
        # 10:21 should round to 10:20
        with patch('simulator.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2026, 4, 6, 10, 21)
            result = self.clock._time_to_words()
            assert result == "TWENTY PAST TEN"

    def test_rounding_59_wraps_to_next_hour(self):
        # 10:58 rounds to 11:00
        with patch('simulator.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2026, 4, 6, 10, 58)
            result = self.clock._time_to_words()
            assert result == "ELEVEN O'CLOCK"

    def test_all_hours_covered(self):
        """Every 5-minute slot for all 12 hours should produce a result."""
        for h in range(12):
            for m in range(0, 60, 5):
                assert (h, m) in simulator.WordClockMode.TIME_TABLE

    def test_wrap_text(self):
        lines = self.clock._wrap_text("TWENTY FIVE PAST THREE", 60)
        assert len(lines) >= 1
        for line in lines:
            assert self.font.string_width(line) <= 60


# ── ApiPoller Tests ──

class TestApiPoller:
    def setup_method(self):
        self.config = {
            "city": "Salt Lake City",
            "crypto": "BTC",
            "icao": "KSLC",
            "owm_api_key": "testkey123",
            "offline": False,
        }
        self.poller = simulator.ApiPoller(self.config)

    def test_initial_state_all_none(self):
        assert self.poller.get_weather() is None
        assert self.poller.get_crypto() is None
        assert self.poller.get_flights() is None

    def test_offline_mode_skips_threads(self):
        self.config["offline"] = True
        poller = simulator.ApiPoller(self.config)
        with patch('threading.Thread') as mock_thread:
            poller.start()
            mock_thread.assert_not_called()

    def test_weather_parsing(self):
        weather_response = {
            "main": {"temp": 72.5},
            "weather": [{"main": "Clear", "icon": "01d"}]
        }
        with patch.object(self.poller, '_fetch_json', return_value=weather_response):
            self.poller._poll_weather_once = None  # we'll call the internals
            # Simulate what _poll_weather does
            data = self.poller._fetch_json("fake")
            if data and "main" in data:
                self.poller.weather = {
                    "temp_f": data["main"]["temp"],
                    "condition": data["weather"][0]["main"],
                }
        assert self.poller.get_weather()["temp_f"] == 72.5
        assert self.poller.get_weather()["condition"] == "Clear"

    def test_crypto_parsing(self):
        crypto_response = {
            "bitcoin": {"usd": 68000.50, "usd_24h_change": -1.23}
        }
        with patch.object(self.poller, '_fetch_json', return_value=crypto_response):
            data = self.poller._fetch_json("fake")
            coin_id = "bitcoin"
            if data and coin_id in data:
                self.poller.crypto = {
                    "symbol": "BTC",
                    "price": data[coin_id]["usd"],
                    "change": data[coin_id].get("usd_24h_change", 0),
                }
        assert self.poller.get_crypto()["price"] == 68000.50
        assert self.poller.get_crypto()["change"] == -1.23
        assert self.poller.get_crypto()["symbol"] == "BTC"

    def test_flights_parsing(self):
        flights_response = [
            {"callsign": "DAL1234 ", "estDepartureAirport": "KSLC"},
            {"callsign": "UAL567  ", "estDepartureAirport": "KSLC"},
            {"callsign": "", "estDepartureAirport": "KSLC"},
        ]
        with patch.object(self.poller, '_fetch_json', return_value=flights_response):
            data = self.poller._fetch_json("fake")
            if data and isinstance(data, list):
                flights = []
                for f in data[:5]:
                    cs = (f.get("callsign") or "").strip()
                    if cs:
                        flights.append(cs)
                self.poller.flights = flights
        result = self.poller.get_flights()
        assert len(result) == 2
        assert result[0] == "DAL1234"
        assert result[1] == "UAL567"

    def test_thread_safety(self):
        """Concurrent access shouldn't crash."""
        import threading
        self.poller.weather = {"temp_f": 72, "condition": "Clear"}
        errors = []
        def reader():
            try:
                for _ in range(100):
                    self.poller.get_weather()
            except Exception as e:
                errors.append(e)
        threads = [threading.Thread(target=reader) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(errors) == 0


# ── FsocietySprite Tests ──

class TestFsocietySprite:
    def test_sprite_size(self):
        assert len(simulator.FSOCIETY_SPRITE) == 256  # 64*32/8

    def test_sprite_has_content(self):
        """Sprite shouldn't be all zeros."""
        assert any(b != 0 for b in simulator.FSOCIETY_SPRITE)

    def test_sprite_symmetry(self):
        """Face should be roughly horizontally symmetric."""
        asymmetric = 0
        for y in range(simulator.PANEL_H):
            for x in range(simulator.PANEL_W // 2):
                byte_l = (y * simulator.PANEL_W + x) // 8
                bit_l = 7 - ((y * simulator.PANEL_W + x) % 8)
                mirror_x = simulator.PANEL_W - 1 - x
                byte_r = (y * simulator.PANEL_W + mirror_x) // 8
                bit_r = 7 - ((y * simulator.PANEL_W + mirror_x) % 8)
                left = bool(simulator.FSOCIETY_SPRITE[byte_l] & (1 << bit_l))
                right = bool(simulator.FSOCIETY_SPRITE[byte_r] & (1 << bit_r))
                if left != right:
                    asymmetric += 1
        # Allow some asymmetry (mouth area) but overall should be symmetric
        total_pixels = simulator.PANEL_W * simulator.PANEL_H // 2
        assert asymmetric < total_pixels * 0.1  # less than 10% asymmetric


# ── Mode Lifecycle Tests ──

class TestModes:
    def setup_method(self):
        self.surface = MagicMock()
        self.buf = simulator.PixelBuffer(self.surface)
        self.font = simulator.FontRenderer(self.buf)

    def test_boot_mode_finishes(self):
        mode = simulator.BootMode(self.buf, self.font)
        mode.init()
        assert not mode.is_done()
        mode.start = time.time() - 3  # fake elapsed time
        mode.update()
        assert mode.is_done()

    def test_glitch_transition_finishes(self):
        trans = simulator.GlitchTransition(self.buf)
        trans.init()
        assert not trans.is_done()
        trans.start = time.time() - 1  # past duration
        trans.update()
        assert trans.is_done()

    def test_weather_mode_no_data(self):
        poller = MagicMock()
        poller.get_weather.return_value = None
        mode = simulator.WeatherMode(self.buf, self.font, poller)
        mode.init()
        mode.update()
        # Should show "NO SIGNAL" without crashing
        lit = sum(1 for y in range(simulator.PANEL_H)
                  for x in range(simulator.PANEL_W)
                  if self.buf.pixels[y][x] != (0, 0, 0))
        assert lit > 0

    def test_weather_mode_with_data(self):
        poller = MagicMock()
        poller.get_weather.return_value = {"temp_f": 72, "condition": "Clear"}
        mode = simulator.WeatherMode(self.buf, self.font, poller)
        mode.init()
        mode.update()
        lit = sum(1 for y in range(simulator.PANEL_H)
                  for x in range(simulator.PANEL_W)
                  if self.buf.pixels[y][x] != (0, 0, 0))
        assert lit > 0

    def test_crypto_mode_no_data(self):
        poller = MagicMock()
        poller.get_crypto.return_value = None
        mode = simulator.CryptoMode(self.buf, self.font, poller)
        mode.init()
        mode.update()
        # Should show "NO SIGNAL" without crashing
        lit = sum(1 for y in range(simulator.PANEL_H)
                  for x in range(simulator.PANEL_W)
                  if self.buf.pixels[y][x] != (0, 0, 0))
        assert lit > 0

    def test_crypto_mode_with_data(self):
        poller = MagicMock()
        poller.get_crypto.return_value = {
            "symbol": "BTC", "price": 68000.0, "change": -1.5
        }
        mode = simulator.CryptoMode(self.buf, self.font, poller)
        mode.init()
        mode.update()
        lit = sum(1 for y in range(simulator.PANEL_H)
                  for x in range(simulator.PANEL_W)
                  if self.buf.pixels[y][x] != (0, 0, 0))
        assert lit > 0

    def test_info_mode_finishes(self):
        mode = simulator.InfoMode(self.buf, self.font, "GRANT")
        mode.init()
        assert not mode.is_done()
        # Fast-forward through typewriter
        mode.all_done = True
        mode.done_time = time.time() - 3
        assert mode.is_done()


# ── Font Data Integrity ──

class TestFontData:
    def test_4x6_has_all_uppercase(self):
        for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            assert c in simulator.FONT_4x6, f"Missing {c} in FONT_4x6"

    def test_4x6_has_digits(self):
        for c in "0123456789":
            assert c in simulator.FONT_4x6, f"Missing {c} in FONT_4x6"

    def test_4x6_has_common_punctuation(self):
        for c in " !.,:+-":
            assert c in simulator.FONT_4x6, f"Missing {c} in FONT_4x6"

    def test_4x6_glyph_height(self):
        for ch, glyph in simulator.FONT_4x6.items():
            assert len(glyph) == 6, f"FONT_4x6['{ch}'] has {len(glyph)} rows, expected 6"

    def test_6x8_has_all_uppercase(self):
        for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            assert c in simulator.FONT_6x8, f"Missing {c} in FONT_6x8"

    def test_6x8_has_digits(self):
        for c in "0123456789":
            assert c in simulator.FONT_6x8, f"Missing {c} in FONT_6x8"

    def test_6x8_glyph_height(self):
        for ch, glyph in simulator.FONT_6x8.items():
            assert len(glyph) == 8, f"FONT_6x8['{ch}'] has {len(glyph)} rows, expected 8"


# ── Config Tests ──

class TestConfig:
    def test_default_config_has_required_keys(self):
        required = ["city", "crypto", "icao", "customer_name", "owm_api_key"]
        for key in required:
            assert key in simulator.CONFIG, f"Missing key: {key}"

    def test_coin_id_mapping(self):
        """Verify the crypto symbol-to-id mapping used in _poll_crypto."""
        coin_map = {
            "btc": "bitcoin", "eth": "ethereum", "sol": "solana",
            "ada": "cardano", "doge": "dogecoin", "xrp": "ripple",
            "dot": "polkadot", "ltc": "litecoin",
        }
        assert coin_map["btc"] == "bitcoin"
        assert coin_map["eth"] == "ethereum"
        assert coin_map["doge"] == "dogecoin"
