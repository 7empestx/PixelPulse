#include "FlightMode.h"
#include <math.h>

FlightMode::FlightMode(Display* display, FontRenderer* font, ApiPoller* poller)
    : _display(display), _font(font), _poller(poller) {}

void FlightMode::init() {
    _startTime = millis();
    _scanning = true;
    _scanStart = millis();
    _radarAngle = 0;
    _lastRadarStep = millis();
    _scrollOffset = 0;
    _lastScrollTime = millis();
    _blinkOn = true;
    _lastBlinkTime = millis();
    memset(_radarTrail, 0, sizeof(_radarTrail));
    _display->clear();
}

void FlightMode::update() {
    if (!_display->ready()) return;
    unsigned long now = millis();

    _display->clear();

    FlightData f = _poller->getFlights();

    // Toggle blink every 500ms
    if (now - _lastBlinkTime >= 500) {
        _blinkOn = !_blinkOn;
        _lastBlinkTime = now;
    }

    if (_scanning) {
        drawRadar();
        _font->drawStringCentered(26, "SCANNING", COLOR_GREEN, FONT_4x6);

        if (f.valid && (now - _scanStart > 1500)) {
            _scanning = false;
        }
        if (!f.valid && (now - _scanStart > 5000)) {
            _scanning = false;
        }
        return;
    }

    if (!f.valid || f.flights.empty()) {
        _font->drawStringCentered(8, "NO FLIGHTS", COLOR_GREEN, FONT_4x6);
        _font->drawStringCentered(18, "DETECTED", COLOR_GREEN, FONT_4x6);
        return;
    }

    // Header with airplane icon
    drawAirplaneIcon(1, 0, COLOR_GREEN);
    _font->drawString(8, 0, "DEPARTURES", COLOR_GREEN, FONT_4x6);

    // Flight count
    char countBuf[4];
    snprintf(countBuf, sizeof(countBuf), "%d", (int)f.flights.size());
    int countW = _font->getStringWidth(countBuf, FONT_4x6);
    _font->drawString(PANEL_WIDTH - countW - 1, 0, countBuf, COLOR_CYAN, FONT_4x6);

    // Separator
    for (int x = 0; x < PANEL_WIDTH; x++) {
        _display->drawPixel(x, 7, COLOR_DIM_GREEN);
    }

    // Auto-scroll
    int totalFlights = (int)f.flights.size();
    int maxVisible = 3;
    if (totalFlights > maxVisible) {
        if (now - _lastScrollTime > 2000) {
            _scrollOffset++;
            if (_scrollOffset > totalFlights - maxVisible) {
                _scrollOffset = 0;
            }
            _lastScrollTime = now;
        }
    }

    // Flight list with blinking dots
    int yPos = 9;
    for (int i = 0; i < maxVisible; i++) {
        int idx = _scrollOffset + i;
        if (idx >= totalFlights) break;

        String callsign = f.flights[idx].callsign;
        callsign.toUpperCase();
        if (callsign.length() > 8) callsign = callsign.substring(0, 8);

        if (_blinkOn) {
            _display->drawPixel(1, yPos + 1, COLOR_GREEN);
            _display->drawPixel(2, yPos + 1, COLOR_GREEN);
            _display->drawPixel(1, yPos + 2, COLOR_GREEN);
            _display->drawPixel(2, yPos + 2, COLOR_GREEN);
        }

        _font->drawString(5, yPos, callsign.c_str(), COLOR_GREEN, FONT_4x6);
        yPos += 8;
    }
}

void FlightMode::drawRadar() {
    unsigned long now = millis();

    if (now - _lastRadarStep >= 40) {
        _radarAngle += 6.0f * (PI / 180.0f);
        if (_radarAngle >= 2.0f * PI) _radarAngle -= 2.0f * PI;
        _lastRadarStep = now;
    }

    int cx = 32;
    int cy = 12;
    int radius = 10;

    // Fade trail
    for (int y = 0; y < PANEL_HEIGHT; y++) {
        for (int x = 0; x < PANEL_WIDTH; x++) {
            if (_radarTrail[y][x] > 0) {
                _radarTrail[y][x] = (_radarTrail[y][x] > 15) ? _radarTrail[y][x] - 15 : 0;
            }
        }
    }

    // Sweep line
    for (int r = 2; r <= radius; r++) {
        int sx = cx + (int)(r * cos(_radarAngle));
        int sy = cy + (int)(r * sin(_radarAngle));
        if (sx >= 0 && sx < PANEL_WIDTH && sy >= 0 && sy < PANEL_HEIGHT) {
            _radarTrail[sy][sx] = 255;
        }
    }

    // Circle outline
    for (int a = 0; a < 360; a += 5) {
        float rad = a * PI / 180.0f;
        int px = cx + (int)(radius * cos(rad));
        int py = cy + (int)(radius * sin(rad));
        _display->drawPixel(px, py, COLOR_DIM_GREEN);
    }

    // Crosshair
    _display->drawPixel(cx, cy - radius - 1, COLOR_DIM_GREEN);
    _display->drawPixel(cx, cy + radius + 1, COLOR_DIM_GREEN);
    _display->drawPixel(cx - radius - 1, cy, COLOR_DIM_GREEN);
    _display->drawPixel(cx + radius + 1, cy, COLOR_DIM_GREEN);

    // Trail pixels
    for (int y = 0; y < PANEL_HEIGHT; y++) {
        for (int x = 0; x < PANEL_WIDTH; x++) {
            if (_radarTrail[y][x] > 0) {
                uint8_t g = _radarTrail[y][x];
                uint32_t c = ((uint32_t)g << 8) | (g / 4);
                _display->drawPixel(x, y, c);
            }
        }
    }

    // Center dot
    _display->drawPixel(cx, cy, COLOR_GREEN);
}

void FlightMode::drawAirplaneIcon(int x, int y, uint32_t color) {
    _display->drawPixel(x+2, y, color);
    _display->drawPixel(x, y+1, color);
    _display->drawPixel(x+1, y+1, color);
    _display->drawPixel(x+2, y+1, color);
    _display->drawPixel(x+3, y+1, color);
    _display->drawPixel(x+4, y+1, color);
    _display->drawPixel(x+2, y+2, color);
}

bool FlightMode::isDone() {
    return false;
}
