#include "AnalogClockMode.h"
#include <math.h>
#include <time.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

AnalogClockMode::AnalogClockMode(Display* display)
    : _display(display) {}

void AnalogClockMode::init() {
    _display->clear();
}

void AnalogClockMode::update() {
    if (!_display->ready()) return;

    _display->clear();

    struct tm timeinfo;
    if (!getLocalTime(&timeinfo)) return;

    int h = timeinfo.tm_hour % 12;
    int m = timeinfo.tm_min;
    int s = timeinfo.tm_sec;

    // Clock face circle (dim green)
    for (int angle = 0; angle < 360; angle++) {
        float rad = angle * M_PI / 180.0f;
        int x = round(CX + RADIUS * cos(rad));
        int y = round(CY + RADIUS * sin(rad));
        _display->drawPixel(x, y, COLOR_DIM_GREEN);
    }

    // Hour tick marks
    for (int tick = 0; tick < 12; tick++) {
        float angle = (tick * 30 - 90) * M_PI / 180.0f;
        for (int r = RADIUS - 2; r <= RADIUS; r++) {
            int x = round(CX + r * cos(angle));
            int y = round(CY + r * sin(angle));
            _display->drawPixel(x, y, COLOR_GREEN);
        }
    }

    // Hour hand
    float hAngle = ((h + m / 60.0f) * 30 - 90) * M_PI / 180.0f;
    drawHand(hAngle, 7, COLOR_GREEN);

    // Minute hand
    float mAngle = ((m + s / 60.0f) * 6 - 90) * M_PI / 180.0f;
    drawHand(mAngle, 10, COLOR_GREEN);

    // Second hand (red)
    float sAngle = (s * 6 - 90) * M_PI / 180.0f;
    drawHand(sAngle, 12, COLOR_RED);

    // Center dot 2x2
    int cx = (int)CX, cy = (int)CY;
    _display->drawPixel(cx, cy, COLOR_WHITE);
    _display->drawPixel(cx + 1, cy, COLOR_WHITE);
    _display->drawPixel(cx, cy + 1, COLOR_WHITE);
    _display->drawPixel(cx + 1, cy + 1, COLOR_WHITE);
}

void AnalogClockMode::drawHand(float angle, int length, uint32_t color) {
    for (int i = 0; i <= length; i++) {
        int x = round(CX + i * cos(angle));
        int y = round(CY + i * sin(angle));
        _display->drawPixel(x, y, color);
    }
}

bool AnalogClockMode::isDone() {
    return false;
}
