#pragma once
#include "../ModeManager.h"
#include "../ApiPoller.h"

#define CRYPTO_HISTORY_SIZE 32

class CryptoMode : public Mode {
public:
    CryptoMode(Display* display, FontRenderer* font, ApiPoller* poller);
    const char* getName() override { return "Crypto"; }
    void init() override;
    void update() override;
    bool isDone() override;

private:
    void drawSparkline();
    void drawArrow(int x, int y, bool up, uint32_t color);

    Display* _display;
    FontRenderer* _font;
    ApiPoller* _poller;
    unsigned long _startTime = 0;

    // Sparkline price history
    float _priceHistory[CRYPTO_HISTORY_SIZE];
    int _historyCount = 0;
    float _lastPrice = 0;
    unsigned long _lastSampleTime = 0;

    // Price flash effect
    bool _flashing = false;
    unsigned long _flashStart = 0;
};
