#include "Display.h"

void Display::begin(MatrixPanel_I2S_DMA* dma) {
    _dma = dma;
}

bool Display::ready() {
    unsigned long now = millis();
    if (now - _lastFrame < FRAME_MS) return false;
    _lastFrame = now;
    return true;
}

void Display::clear() {
    if (!_dma) return;
    _dma->fillScreenRGB888(0, 0, 0);
}

void Display::drawPixel(int x, int y, uint32_t rgb888) {
    if (!_dma) return;
    if (x < 0 || x >= PANEL_WIDTH || y < 0 || y >= PANEL_HEIGHT) return;
    uint8_t r = (rgb888 >> 16) & 0xFF;
    uint8_t g = (rgb888 >> 8) & 0xFF;
    uint8_t b = rgb888 & 0xFF;
    _dma->drawPixel(x, y, _dma->color565(r, g, b));
}
