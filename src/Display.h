#pragma once
#include <ESP32-HUB75-MatrixPanel-I2S-DMA.h>
#include "Config.h"

class Display {
public:
    void begin(MatrixPanel_I2S_DMA* dma);

    // Frame gating (~30fps). Returns false if too soon.
    bool ready();

    // Clear screen to black
    void clear();

    // Draw pixel using RGB888 color (matches COLOR_* defines)
    void drawPixel(int x, int y, uint32_t rgb888);

    // Access underlying DMA panel (for hardware init only)
    MatrixPanel_I2S_DMA* dma() { return _dma; }

private:
    MatrixPanel_I2S_DMA* _dma = nullptr;
    unsigned long _lastFrame = 0;
    static constexpr unsigned long FRAME_MS = 33;  // ~30fps
};
