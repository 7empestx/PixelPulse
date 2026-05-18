#pragma once
#include "../ModeManager.h"
#include "../ApiPoller.h"

class FlightMode : public Mode {
public:
    FlightMode(Display* display, FontRenderer* font, ApiPoller* poller);
    const char* getName() override { return "Flight"; }
    void init() override;
    void update() override;
    bool isDone() override;

private:
    void drawRadar();
    void drawAirplaneIcon(int x, int y, uint32_t color);

    Display* _display;
    FontRenderer* _font;
    ApiPoller* _poller;
    unsigned long _startTime = 0;

    // Scanning radar
    bool _scanning = true;
    unsigned long _scanStart = 0;
    float _radarAngle = 0;
    unsigned long _lastRadarStep = 0;
    uint8_t _radarTrail[PANEL_HEIGHT][PANEL_WIDTH];

    // Flight list scrolling
    int _scrollOffset = 0;
    unsigned long _lastScrollTime = 0;
    bool _blinkOn = true;
    unsigned long _lastBlinkTime = 0;
};
