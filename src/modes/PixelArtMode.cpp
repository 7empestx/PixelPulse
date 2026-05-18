#include "PixelArtMode.h"
#include "../data/fsociety.h"
#include <math.h>

PixelArtMode::PixelArtMode(Display* display) : _display(display) {}

void PixelArtMode::init() {
    _phase = 0;
    _phaseStart = millis();
    _scanRow = 0;
    _lastScanTime = millis();
    _lastLifeStep = 0;
    memset(_grid, 0, sizeof(_grid));
    memset(_next, 0, sizeof(_next));
    _display->clear();
}

void PixelArtMode::update() {
    if (!_display->ready()) return;
    unsigned long now = millis();

    if (_phase == 0) {
        // Phase 0: Scanline reveal — one row every 60ms
        if (now - _lastScanTime >= 60) {
            _lastScanTime = now;

            if (_scanRow < PANEL_HEIGHT) {
                // Draw previous scanline row in green (was white)
                if (_scanRow > 0) {
                    int prevRow = _scanRow - 1;
                    for (int x = 0; x < PANEL_WIDTH; x++) {
                        int byteIdx = (prevRow * PANEL_WIDTH + x) / 8;
                        int bitIdx = 7 - ((prevRow * PANEL_WIDTH + x) % 8);
                        if (FSOCIETY_SPRITE[byteIdx] & (1 << bitIdx)) {
                            _display->drawPixel(x, prevRow, COLOR_GREEN);
                        }
                    }
                }

                // Draw current scanline row in bright white
                for (int x = 0; x < PANEL_WIDTH; x++) {
                    int byteIdx = (_scanRow * PANEL_WIDTH + x) / 8;
                    int bitIdx = 7 - ((_scanRow * PANEL_WIDTH + x) % 8);
                    if (FSOCIETY_SPRITE[byteIdx] & (1 << bitIdx)) {
                        _display->drawPixel(x, _scanRow, COLOR_WHITE);
                    }
                }

                _scanRow++;
            }

            if (_scanRow >= PANEL_HEIGHT) {
                // Recolor last row to green
                int lastRow = PANEL_HEIGHT - 1;
                for (int x = 0; x < PANEL_WIDTH; x++) {
                    int byteIdx = (lastRow * PANEL_WIDTH + x) / 8;
                    int bitIdx = 7 - ((lastRow * PANEL_WIDTH + x) % 8);
                    if (FSOCIETY_SPRITE[byteIdx] & (1 << bitIdx)) {
                        _display->drawPixel(x, lastRow, COLOR_GREEN);
                    }
                }
                _phase = 1;
                _phaseStart = now;
            }
        }

    } else if (_phase == 1) {
        // Phase 1: Hold with breathing pulse (3 seconds)
        float t = (now - _phaseStart) / 1000.0f;
        float brightness = 0.5f + 0.5f * sin(t * 2.0f * PI);
        uint8_t g = 60 + (uint8_t)(brightness * 195);
        uint8_t b = (uint8_t)(brightness * 0x41);
        uint32_t color = ((uint32_t)g << 8) | b;

        _display->clear();
        for (int y = 0; y < PANEL_HEIGHT; y++) {
            for (int x = 0; x < PANEL_WIDTH; x++) {
                int byteIdx = (y * PANEL_WIDTH + x) / 8;
                int bitIdx = 7 - ((y * PANEL_WIDTH + x) % 8);
                if (FSOCIETY_SPRITE[byteIdx] & (1 << bitIdx)) {
                    _display->drawPixel(x, y, color);
                }
            }
        }

        if (now - _phaseStart > 3000) {
            // Seed Game of Life grid from sprite
            for (int y = 0; y < PANEL_HEIGHT; y++) {
                for (int x = 0; x < PANEL_WIDTH; x++) {
                    int byteIdx = (y * PANEL_WIDTH + x) / 8;
                    int bitIdx = 7 - ((y * PANEL_WIDTH + x) % 8);
                    _grid[y][x] = (FSOCIETY_SPRITE[byteIdx] & (1 << bitIdx)) != 0;
                }
            }
            _phase = 2;
            _phaseStart = now;
            _lastLifeStep = now;
        }

    } else {
        // Phase 2: Game of Life dissolve
        if (now - _lastLifeStep >= 120) {
            _lastLifeStep = now;
            stepLife();

            _display->clear();
            for (int y = 0; y < PANEL_HEIGHT; y++) {
                for (int x = 0; x < PANEL_WIDTH; x++) {
                    if (_grid[y][x]) {
                        int dx = x - PANEL_WIDTH / 2;
                        int dy = y - PANEL_HEIGHT / 2;
                        uint32_t c = (dx * dx + dy * dy < 200) ? COLOR_GREEN : COLOR_DIM_GREEN;
                        _display->drawPixel(x, y, c);
                    }
                }
            }
        }
    }
}

void PixelArtMode::stepLife() {
    for (int y = 0; y < PANEL_HEIGHT; y++) {
        for (int x = 0; x < PANEL_WIDTH; x++) {
            int n = countNeighbors(x, y);
            if (_grid[y][x]) {
                _next[y][x] = (n == 2 || n == 3);
            } else {
                _next[y][x] = (n == 3);
            }
        }
    }
    memcpy(_grid, _next, sizeof(_grid));
}

int PixelArtMode::countNeighbors(int x, int y) {
    int count = 0;
    for (int dy = -1; dy <= 1; dy++) {
        for (int dx = -1; dx <= 1; dx++) {
            if (dx == 0 && dy == 0) continue;
            int nx = (x + dx + PANEL_WIDTH) % PANEL_WIDTH;
            int ny = (y + dy + PANEL_HEIGHT) % PANEL_HEIGHT;
            if (_grid[ny][nx]) count++;
        }
    }
    return count;
}

bool PixelArtMode::isDone() {
    return false;
}
