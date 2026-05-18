#pragma once
#include "../ModeManager.h"

class AnalogClockMode : public Mode {
public:
    AnalogClockMode(Display* display);
    const char* getName() override { return "AnalogClock"; }
    void init() override;
    void update() override;
    bool isDone() override;

private:
    void drawHand(float angle, int length, uint32_t color);

    Display* _display;
    static constexpr float CX = 31.5f;
    static constexpr float CY = 15.5f;
    static constexpr int RADIUS = 14;
};
