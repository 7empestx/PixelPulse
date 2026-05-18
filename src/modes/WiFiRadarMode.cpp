#include "WiFiRadarMode.h"
#include "../Config.h"
#include <math.h>
#include <algorithm>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif
#ifndef TWO_PI
#define TWO_PI (2.0 * M_PI)
#endif

WiFiRadarMode::WiFiRadarMode(Display* display, FontRenderer* font)
    : _display(display), _font(font) {}

static float bssidToAngle(const String& bssid) {
    uint32_t hash = 5381;
    for (int i = 0; i < (int)bssid.length(); i++) {
        hash = ((hash << 5) + hash) + (uint8_t)bssid[i];
    }
    return (hash % 3600) * TWO_PI / 3600.0f;
}

static float rssiToDistance(int32_t rssi) {
    float d = (float)(-rssi - 30) / 60.0f;
    if (d < 0.15f) d = 0.15f;
    if (d > 1.0f)  d = 1.0f;
    return d;
}

void WiFiRadarMode::init() {
    _display->clear();
    _sweepAngle = 0.0f;
    _startTime = millis();
    _lastScanTime = 0;
    _scanning = false;
    _scrollX = 64;
    _displayIdx = 0;
    memset(_trail, 0, sizeof(_trail));
    _networks.clear();
    startScan();
}

void WiFiRadarMode::update() {
    if (!_display->ready()) return;
    unsigned long now = millis();

    // Check for scan results
    if (_scanning) {
        int result = WiFi.scanComplete();
        if (result >= 0) {
            _scanning = false;
            parseScanResults();
        }
    }

    // Trigger periodic re-scan
    if (!_scanning && (now - _lastScanTime >= SCAN_INTERVAL_MS)) {
        startScan();
    }

    // Advance sweep
    _sweepAngle += SWEEP_SPEED;
    if (_sweepAngle >= TWO_PI) _sweepAngle -= TWO_PI;

    // Update phosphor trail
    int sweepBucket = (int)(_sweepAngle / TWO_PI * TRAIL_SLICES) % TRAIL_SLICES;
    for (int i = 0; i < TRAIL_SLICES; i++) {
        if (i == sweepBucket) {
            _trail[i] = 255;
        } else {
            if (_trail[i] > 8) _trail[i] -= 8;
            else _trail[i] = 0;
        }
    }

    // Update blip glow
    for (auto& net : _networks) {
        float angleDiff = fabs(_sweepAngle - net.angle);
        if (angleDiff > M_PI) angleDiff = TWO_PI - angleDiff;
        if (angleDiff < 0.15f) {
            net.glow = 255;
            net.lastSwept = now;
        } else {
            unsigned long elapsed = now - net.lastSwept;
            if (elapsed < 1000) {
                net.glow = 255 - (uint8_t)(elapsed * 200 / 1000);
                if (net.glow < 55) net.glow = 55;
            } else {
                net.glow = 55;
            }
        }
    }

    // Draw everything
    _display->clear();
    drawRangeRings();
    drawPhosphorTrail();
    drawSweepLine();
    drawBlips();
    drawInfoStrip();
}

bool WiFiRadarMode::isDone() {
    return false;
}

void WiFiRadarMode::startScan() {
    WiFi.scanNetworks(true);
    _scanning = true;
    _lastScanTime = millis();
}

void WiFiRadarMode::parseScanResults() {
    int n = WiFi.scanComplete();
    if (n < 0) return;

    _networks.clear();
    for (int i = 0; i < n; i++) {
        NetworkBlip blip;
        blip.ssid = WiFi.SSID(i);
        blip.rssi = WiFi.RSSI(i);
        blip.angle = bssidToAngle(WiFi.BSSIDstr(i));
        blip.distance = rssiToDistance(blip.rssi);
        blip.glow = 55;
        blip.lastSwept = 0;
        _networks.push_back(blip);
    }

    WiFi.scanDelete();

    std::sort(_networks.begin(), _networks.end(),
              [](const NetworkBlip& a, const NetworkBlip& b) {
                  return a.rssi > b.rssi;
              });
}

void WiFiRadarMode::drawRangeRings() {
    for (int ring = 1; ring <= 3; ring++) {
        int r = (RADIUS * ring) / 3;
        for (int a = 0; a < 360; a += 3) {
            float rad = a * M_PI / 180.0f;
            int x = CX + (int)(r * cosf(rad));
            int y = CY + (int)(r * sinf(rad));
            _display->drawPixel(x, y, COLOR_DIM_GREEN);
        }
    }

    for (int i = -RADIUS; i <= RADIUS; i += 2) {
        _display->drawPixel(CX + i, CY, COLOR_DIM_GREEN);
        _display->drawPixel(CX, CY + i, COLOR_DIM_GREEN);
    }
}

void WiFiRadarMode::drawPhosphorTrail() {
    for (int i = 0; i < TRAIL_SLICES; i++) {
        if (_trail[i] < 10) continue;

        float angle = (float)i / TRAIL_SLICES * TWO_PI;
        uint8_t g = _trail[i];
        uint8_t b = (g > 180) ? g / 8 : 0;
        uint32_t color = ((uint32_t)g << 8) | b;

        for (int d = 2; d <= RADIUS; d += 2) {
            int x = CX + (int)(d * cosf(angle));
            int y = CY + (int)(d * sinf(angle));
            _display->drawPixel(x, y, color);
        }
    }
}

void WiFiRadarMode::drawSweepLine() {
    for (int d = 1; d <= RADIUS; d++) {
        int px = CX + (int)roundf(d * cosf(_sweepAngle));
        int py = CY + (int)roundf(d * sinf(_sweepAngle));
        uint32_t color = (d > RADIUS * 2 / 3) ? COLOR_CYAN : COLOR_GREEN;
        _display->drawPixel(px, py, color);
    }

    _display->drawPixel(CX, CY, COLOR_WHITE);
    _display->drawPixel(CX + 1, CY, COLOR_WHITE);
    _display->drawPixel(CX, CY + 1, COLOR_WHITE);
    _display->drawPixel(CX + 1, CY + 1, COLOR_WHITE);
}

void WiFiRadarMode::drawBlips() {
    for (auto& net : _networks) {
        int d = (int)(net.distance * RADIUS);
        if (d < 2) d = 2;
        int x = CX + (int)(d * cosf(net.angle));
        int y = CY + (int)(d * sinf(net.angle));

        uint8_t br, bg, bb;
        if (net.rssi > -50) {
            br = 0; bg = net.glow; bb = net.glow;
        } else if (net.rssi > -70) {
            br = 0; bg = net.glow; bb = (uint8_t)(65 * net.glow / 255);
        } else if (net.rssi > -85) {
            br = net.glow; bg = (uint8_t)(170 * net.glow / 255); bb = 0;
        } else {
            br = net.glow; bg = (uint8_t)(32 * net.glow / 255); bb = 0;
        }
        uint32_t color = ((uint32_t)br << 16) | ((uint32_t)bg << 8) | bb;

        _display->drawPixel(x, y, color);

        if (net.rssi > -60 && net.glow > 100) {
            _display->drawPixel(x + 1, y, color);
            _display->drawPixel(x, y + 1, color);
        }
        if (net.rssi > -45 && net.glow > 150) {
            _display->drawPixel(x - 1, y, color);
            _display->drawPixel(x, y - 1, color);
        }
    }
}

void WiFiRadarMode::drawInfoStrip() {
    unsigned long now = millis();

    uint32_t dimCyan = 0x005050;
    for (int x = 0; x < PANEL_WIDTH; x++) {
        _display->drawPixel(x, 25, dimCyan);
    }

    _font->drawString(1, 26, "RADAR", COLOR_GREEN, FONT_4x6);

    int count = _networks.size();
    char countStr[8];
    snprintf(countStr, sizeof(countStr), "%d", count);
    int cw = _font->getStringWidth(countStr, FONT_4x6);
    _font->drawString(PANEL_WIDTH - cw - 1, 26, countStr, COLOR_CYAN, FONT_4x6);

    if (!_networks.empty()) {
        const NetworkBlip& net = _networks[_displayIdx % _networks.size()];
        char info[64];
        snprintf(info, sizeof(info), "%s %ddBm",
                 net.ssid.length() > 0 ? net.ssid.c_str() : "???",
                 (int)net.rssi);

        if (now - _lastScroll >= 50) {
            _lastScroll = now;
            _scrollX--;
            int textWidth = _font->getStringWidth(info, FONT_4x6);
            if (_scrollX < -textWidth) {
                _scrollX = PANEL_WIDTH;
                _displayIdx = (_displayIdx + 1) % _networks.size();
            }
        }

        uint32_t textColor = (net.rssi > -60) ? COLOR_CYAN : COLOR_GREEN;
        _font->drawString(_scrollX, 32 - 6, info, textColor, FONT_4x6);
    } else {
        const char* scanning = "SCANNING";
        int dots = (int)((now / 400) % 4);
        char buf[16];
        snprintf(buf, sizeof(buf), "%s", scanning);
        for (int d = 0; d < dots; d++) {
            int len = strlen(buf);
            buf[len] = '.';
            buf[len + 1] = '\0';
        }
        _font->drawString(1, 32 - 6, buf, COLOR_GREEN, FONT_4x6);
    }
}

