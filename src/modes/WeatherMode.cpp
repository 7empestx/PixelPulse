#include "WeatherMode.h"

WeatherMode::WeatherMode(Display* display, FontRenderer* font, ApiPoller* poller)
    : _display(display), _font(font), _poller(poller) {}

void WeatherMode::init() {
    _startTime = millis();
    _animFrame = 0;
    _lastAnimTime = millis();
    _display->clear();
}

uint32_t WeatherMode::tempColor(float tempF) {
    if (tempF < 32.0f)  return COLOR_BLUE;
    if (tempF < 60.0f)  return COLOR_CYAN;
    if (tempF < 85.0f)  return COLOR_GREEN;
    return COLOR_RED;
}

void WeatherMode::update() {
    if (!_display->ready()) return;
    unsigned long now = millis();

    // Advance animation frame every 150ms
    if (now - _lastAnimTime >= 150) {
        _animFrame++;
        _lastAnimTime = now;
    }

    _display->clear();

    WeatherData w = _poller->getWeather();
    if (!w.valid) {
        _font->drawStringCentered(10, "LOADING...", COLOR_GREEN, FONT_4x6);
        _font->drawCursor(52, 10, COLOR_GREEN, FONT_4x6);
        return;
    }

    drawWeatherIcon(2, 2, w.condition);

    // Temperature — color-coded
    char tempBuf[16];
    snprintf(tempBuf, sizeof(tempBuf), "%.0fF", w.tempF);
    _font->drawString(30, 2, tempBuf, tempColor(w.tempF), FONT_6x8);

    // Separator line
    for (int x = 0; x < PANEL_WIDTH; x++) {
        _display->drawPixel(x, 16, COLOR_DIM_GREEN);
    }

    // Condition text
    String cond = w.condition;
    cond.toUpperCase();
    _font->drawStringCentered(20, cond.c_str(), COLOR_GREEN, FONT_4x6);
}

bool WeatherMode::isDone() {
    return false;
}

void WeatherMode::drawWeatherIcon(int x, int y, const String& condition) {
    String c = condition;
    c.toLowerCase();

    if (c.indexOf("clear") >= 0 || c.indexOf("sun") >= 0) {
        // Animated sun with rotating rays
        for (int i = 4; i <= 6; i++) {
            _display->drawPixel(x+i, y+3, COLOR_YELLOW);
            _display->drawPixel(x+i, y+5, COLOR_YELLOW);
        }
        _display->drawPixel(x+3, y+4, COLOR_YELLOW);
        _display->drawPixel(x+7, y+4, COLOR_YELLOW);
        _display->drawPixel(x+4, y+4, COLOR_YELLOW);
        _display->drawPixel(x+5, y+4, COLOR_YELLOW);
        _display->drawPixel(x+6, y+4, COLOR_YELLOW);

        int phase = _animFrame % 4;
        int offsets[4][2] = {{5, 0}, {10, 4}, {5, 9}, {0, 4}};
        for (int r = 0; r < 4; r++) {
            int ri = (r + phase) % 4;
            _display->drawPixel(x + offsets[ri][0], y + offsets[ri][1], COLOR_YELLOW);
        }
        int diagOffsets[4][2] = {{2, 1}, {8, 1}, {8, 7}, {2, 7}};
        for (int r = 0; r < 4; r++) {
            int ri = (r + phase) % 4;
            _display->drawPixel(x + diagOffsets[ri][0], y + diagOffsets[ri][1], COLOR_YELLOW);
        }

    } else if (c.indexOf("rain") >= 0 || c.indexOf("drizzle") >= 0) {
        // Cloud + animated rain
        for (int i = 3; i <= 8; i++) _display->drawPixel(x+i, y+1, COLOR_WHITE);
        for (int i = 2; i <= 9; i++) _display->drawPixel(x+i, y+2, COLOR_WHITE);
        for (int i = 2; i <= 9; i++) _display->drawPixel(x+i, y+3, COLOR_WHITE);

        int dropX[5] = {3, 5, 7, 4, 6};
        int dropStartY[5] = {5, 6, 5, 7, 6};
        int frame = _animFrame % 6;
        for (int d = 0; d < 5; d++) {
            int dy = (dropStartY[d] + frame) % 6;
            int drawY = y + 5 + dy;
            if (drawY < y + 11) {
                _display->drawPixel(x + dropX[d], drawY, COLOR_BLUE);
            }
        }

    } else if (c.indexOf("snow") >= 0) {
        // Animated drifting snowflakes
        int flakeX[7] = {3, 7, 5, 2, 8, 4, 6};
        int flakeBaseY[7] = {1, 2, 3, 4, 5, 6, 7};
        int frame = _animFrame % 8;
        for (int f = 0; f < 7; f++) {
            int fy = (flakeBaseY[f] + frame) % 8;
            int drift = ((frame + f) % 2 == 0) ? 0 : 1;
            _display->drawPixel(x + flakeX[f] + drift, y + fy + 1, COLOR_WHITE);
        }

    } else if (c.indexOf("thunder") >= 0 || c.indexOf("storm") >= 0) {
        // Cloud + flashing lightning
        for (int i = 3; i <= 8; i++) _display->drawPixel(x+i, y+1, COLOR_WHITE);
        for (int i = 2; i <= 9; i++) _display->drawPixel(x+i, y+2, COLOR_WHITE);

        bool showBolt = (_animFrame % 6) < 3;
        if (showBolt) {
            int boltX = (_animFrame % 12 < 6) ? 5 : 6;
            _display->drawPixel(x+boltX+1, y+3, COLOR_YELLOW);
            _display->drawPixel(x+boltX, y+4, COLOR_YELLOW);
            _display->drawPixel(x+boltX-1, y+5, COLOR_YELLOW);
            _display->drawPixel(x+boltX+1, y+5, COLOR_YELLOW);
            _display->drawPixel(x+boltX, y+6, COLOR_YELLOW);
            _display->drawPixel(x+boltX-1, y+7, COLOR_YELLOW);
        }

    } else if (c.indexOf("cloud") >= 0) {
        // Cloud with gentle drift
        int drift = (_animFrame / 3) % 2;
        int cx = x + drift;
        for (int i = 3; i <= 8; i++) _display->drawPixel(cx+i, y+2, COLOR_WHITE);
        for (int i = 2; i <= 9; i++) _display->drawPixel(cx+i, y+3, COLOR_WHITE);
        for (int i = 1; i <= 10; i++) _display->drawPixel(cx+i, y+4, COLOR_WHITE);
        for (int i = 1; i <= 10; i++) _display->drawPixel(cx+i, y+5, COLOR_WHITE);
        for (int i = 2; i <= 9; i++) _display->drawPixel(cx+i, y+6, COLOR_WHITE);

    } else {
        // Fog/mist — shifting lines
        int shift = _animFrame % 4;
        for (int i = 2; i <= 10; i++) _display->drawPixel(x+i+shift%2, y+2, COLOR_DIM_GREEN);
        for (int i = 1; i <= 9; i++)  _display->drawPixel(x+i-(shift/2)%2, y+4, COLOR_DIM_GREEN);
        for (int i = 3; i <= 11; i++) _display->drawPixel(x+i+shift%2, y+6, COLOR_GREEN);
    }
}
