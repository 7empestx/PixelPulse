#pragma once
#include "../ModeManager.h"

class GameOfLifeMode : public Mode {
public:
    GameOfLifeMode(Display* display);
    const char* getName() override { return "GameOfLife"; }
    void init() override;
    void update() override;
    bool isDone() override;

private:
    int countNeighbors(int x, int y);

    Display* _display;
    bool _grid[PANEL_HEIGHT][PANEL_WIDTH];
    bool _next[PANEL_HEIGHT][PANEL_WIDTH];
    unsigned long _lastStep = 0;
    int _generation = 0;
    static constexpr unsigned long STEP_MS = 150;
};
