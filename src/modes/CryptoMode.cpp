#include "CryptoMode.h"
#include <math.h>

CryptoMode::CryptoMode(Display* display, FontRenderer* font, ApiPoller* poller)
    : _display(display), _font(font), _poller(poller) {}

void CryptoMode::init() {
    _startTime = millis();
    _historyCount = 0;
    _lastPrice = 0;
    _lastSampleTime = 0;
    _flashing = false;
    _flashStart = 0;
    memset(_priceHistory, 0, sizeof(_priceHistory));
    _display->clear();
}

void CryptoMode::update() {
    if (!_display->ready()) return;
    unsigned long now = millis();

    _display->clear();

    CryptoData c = _poller->getCrypto();
    if (!c.valid) {
        _font->drawStringCentered(10, "LOADING...", COLOR_GREEN, FONT_4x6);
        _font->drawCursor(52, 10, COLOR_GREEN, FONT_4x6);
        return;
    }

    // Sample price into history
    if (now - _lastSampleTime > 500 && c.price > 0) {
        _lastSampleTime = now;

        if (_lastPrice > 0 && fabs(c.price - _lastPrice) > 0.001f) {
            _flashing = true;
            _flashStart = now;
        }

        if (_historyCount < CRYPTO_HISTORY_SIZE) {
            _priceHistory[_historyCount] = c.price;
            _historyCount++;
        } else {
            memmove(_priceHistory, _priceHistory + 1, (CRYPTO_HISTORY_SIZE - 1) * sizeof(float));
            _priceHistory[CRYPTO_HISTORY_SIZE - 1] = c.price;
        }
        _lastPrice = c.price;
    }

    // Symbol header
    String sym = c.symbol;
    sym.toUpperCase();
    _font->drawStringCentered(0, sym.c_str(), COLOR_WHITE, FONT_6x8);

    // Dotted separator
    for (int x = 0; x < PANEL_WIDTH; x += 2) {
        _display->drawPixel(x, 9, COLOR_DIM_GREEN);
    }

    // Price — color-coded
    char priceBuf[32];
    if (c.price >= 1000) {
        snprintf(priceBuf, sizeof(priceBuf), "$%.0f", c.price);
    } else if (c.price >= 1) {
        snprintf(priceBuf, sizeof(priceBuf), "$%.2f", c.price);
    } else {
        snprintf(priceBuf, sizeof(priceBuf), "$%.4f", c.price);
    }

    uint32_t priceColor;
    if (_flashing && (now - _flashStart < 500)) {
        bool flashOn = ((now - _flashStart) / 80) % 2 == 0;
        priceColor = flashOn ? COLOR_WHITE : ((c.change24h >= 0) ? COLOR_GREEN : COLOR_RED);
    } else {
        _flashing = false;
        priceColor = (c.change24h >= 0) ? COLOR_GREEN : COLOR_RED;
    }
    _font->drawStringCentered(11, priceBuf, priceColor, FONT_4x6);

    // Delta with arrow
    char deltaBuf[32];
    if (c.change24h >= 0) {
        snprintf(deltaBuf, sizeof(deltaBuf), " +%.2f%%", c.change24h);
    } else {
        snprintf(deltaBuf, sizeof(deltaBuf), " %.2f%%", c.change24h);
    }
    uint32_t deltaColor = (c.change24h >= 0) ? COLOR_GREEN : COLOR_RED;

    int deltaW = _font->getStringWidth(deltaBuf, FONT_4x6);
    int arrowW = 5;
    int totalW = arrowW + deltaW;
    int deltaX = (PANEL_WIDTH - totalW) / 2;

    drawArrow(deltaX, 19, c.change24h >= 0, deltaColor);
    _font->drawString(deltaX + arrowW, 19, deltaBuf, deltaColor, FONT_4x6);

    // Sparkline
    drawSparkline();
}

void CryptoMode::drawSparkline() {
    if (_historyCount < 2) return;

    float minP = _priceHistory[0], maxP = _priceHistory[0];
    for (int i = 1; i < _historyCount; i++) {
        if (_priceHistory[i] < minP) minP = _priceHistory[i];
        if (_priceHistory[i] > maxP) maxP = _priceHistory[i];
    }

    float range = maxP - minP;
    if (range < 0.001f) range = 0.001f;

    int chartHeight = 6;
    int chartY = 25;

    bool positive = _priceHistory[_historyCount - 1] >= _priceHistory[0];
    uint32_t lineColor = positive ? COLOR_GREEN : COLOR_RED;

    int startCol = PANEL_WIDTH - _historyCount;
    if (startCol < 0) startCol = 0;

    for (int i = 0; i < _historyCount; i++) {
        int col = startCol + i;
        if (col >= PANEL_WIDTH) break;

        float normalized = (_priceHistory[i] - minP) / range;
        int row = chartY + chartHeight - 1 - (int)(normalized * (chartHeight - 1));

        _display->drawPixel(col, row, (i == _historyCount - 1) ? COLOR_WHITE : lineColor);
    }
}

void CryptoMode::drawArrow(int x, int y, bool up, uint32_t color) {
    if (up) {
        // Triangle pointing up
        _display->drawPixel(x+2, y, color);
        _display->drawPixel(x+1, y+1, color);
        _display->drawPixel(x+2, y+1, color);
        _display->drawPixel(x+3, y+1, color);
        _display->drawPixel(x, y+2, color);
        _display->drawPixel(x+1, y+2, color);
        _display->drawPixel(x+2, y+2, color);
        _display->drawPixel(x+3, y+2, color);
        _display->drawPixel(x+4, y+2, color);
    } else {
        // Triangle pointing down
        _display->drawPixel(x, y, color);
        _display->drawPixel(x+1, y, color);
        _display->drawPixel(x+2, y, color);
        _display->drawPixel(x+3, y, color);
        _display->drawPixel(x+4, y, color);
        _display->drawPixel(x+1, y+1, color);
        _display->drawPixel(x+2, y+1, color);
        _display->drawPixel(x+3, y+1, color);
        _display->drawPixel(x+2, y+2, color);
    }
}

bool CryptoMode::isDone() {
    return false;
}
