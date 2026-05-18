#pragma once
#include "../ModeManager.h"
#include <WiFi.h>
#include <vector>

struct NetworkBlip {
    float angle;        // radians, derived from BSSID hash
    float distance;     // 0.0 (center) to 1.0 (edge), mapped from RSSI
    int32_t rssi;
    String ssid;
    uint8_t glow;       // current brightness (0-255), pulses when swept
    unsigned long lastSwept;
};

class WiFiRadarMode : public Mode {
public:
    WiFiRadarMode(Display* display, FontRenderer* font);
    const char* getName() override { return "WiFiRadar"; }
    void init() override;
    void update() override;
    bool isDone() override;

private:
    void startScan();
    void parseScanResults();
    void drawRangeRings();
    void drawSweepLine();
    void drawPhosphorTrail();
    void drawBlips();
    void drawInfoStrip();
    Display* _display;
    FontRenderer* _font;

    // Radar geometry
    static constexpr int CX = 15;
    static constexpr int CY = 12;
    static constexpr int RADIUS = 11;

    // Sweep
    float _sweepAngle = 0.0f;
    static constexpr float SWEEP_SPEED = 0.07f;

    // Phosphor trail
    static constexpr int TRAIL_SLICES = 72;
    uint8_t _trail[TRAIL_SLICES] = {};

    // Networks
    std::vector<NetworkBlip> _networks;
    bool _scanning = false;
    unsigned long _lastScanTime = 0;
    static constexpr unsigned long SCAN_INTERVAL_MS = 10000;

    // Info strip scrolling
    int _scrollX = 64;
    unsigned long _lastScroll = 0;
    int _displayIdx = 0;

    unsigned long _startTime = 0;
};
