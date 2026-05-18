#pragma once
#include "../ModeManager.h"

class PixelArtMode : public Mode {
public:
    PixelArtMode(Display* display);
    const char* getName() override { return "PixelArt"; }
    void init() override;
    void update() override;
    bool isDone() override;

private:
    void stepLife();
    int countNeighbors(int x, int y);

    Display* _display;
    unsigned long _phaseStart = 0;

    // Phase 0: scanline reveal
    int _scanRow = 0;
    unsigned long _lastScanTime = 0;

    // Phase 1: hold with breathing
    // Phase 2: Game of Life dissolve
    bool _grid[PANEL_HEIGHT][PANEL_WIDTH];
    bool _next[PANEL_HEIGHT][PANEL_WIDTH];
    unsigned long _lastLifeStep = 0;

    int _phase = 0;  // 0=scanline, 1=hold, 2=life
};
