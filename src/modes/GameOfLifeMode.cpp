#include "GameOfLifeMode.h"

GameOfLifeMode::GameOfLifeMode(Display* display)
    : _display(display) {}

void GameOfLifeMode::init() {
    for (int y = 0; y < PANEL_HEIGHT; y++) {
        for (int x = 0; x < PANEL_WIDTH; x++) {
            _grid[y][x] = random(100) < 25;
        }
    }
    _generation = 0;
    _lastStep = millis();
}

void GameOfLifeMode::update() {
    unsigned long now = millis();
    if (now - _lastStep < STEP_MS) return;
    _lastStep = now;

    // Compute next generation
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

    // Swap and draw
    _display->clear();
    for (int y = 0; y < PANEL_HEIGHT; y++) {
        for (int x = 0; x < PANEL_WIDTH; x++) {
            _grid[y][x] = _next[y][x];
            if (_grid[y][x]) {
                _display->drawPixel(x, y, COLOR_GREEN);
            }
        }
    }

    _generation++;
}

int GameOfLifeMode::countNeighbors(int x, int y) {
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

bool GameOfLifeMode::isDone() {
    return false;
}
