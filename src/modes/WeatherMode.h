#pragma once
#include "../ModeManager.h"
#include "../ApiPoller.h"

class WeatherMode : public Mode {
public:
    WeatherMode(Display* display, FontRenderer* font, ApiPoller* poller);
    const char* getName() override { return "Weather"; }
    void init() override;
    void update() override;
    bool isDone() override;

private:
    void drawWeatherIcon(int x, int y, const String& condition);
    uint32_t tempColor(float tempF);

    Display* _display;
    FontRenderer* _font;
    ApiPoller* _poller;
    unsigned long _startTime = 0;

    // Animation
    int _animFrame = 0;
    unsigned long _lastAnimTime = 0;
};
