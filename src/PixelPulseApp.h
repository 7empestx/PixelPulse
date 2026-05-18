#pragma once
#include <Arduino.h>
#ifndef QEMU_BUILD
#include <ArduinoOTA.h>
#endif
#include <ESP32-HUB75-MatrixPanel-I2S-DMA.h>
#include "Config.h"
#include "Display.h"
#include "FontRenderer.h"
#include "ModeManager.h"
#include "ApiPoller.h"
#include "WebDashboard.h"
#include "modes/WordClockMode.h"
#include "modes/WeatherMode.h"
#include "modes/CryptoMode.h"
#include "modes/PixelArtMode.h"
#include "modes/FlightMode.h"
#include "modes/AnalogClockMode.h"
#include "modes/GameOfLifeMode.h"
#include "modes/WiFiRadarMode.h"

class PixelPulseApp {
public:
    void begin();
    void update();
    ~PixelPulseApp();

private:
    MatrixPanel_I2S_DMA* _dma = nullptr;
    Display _display;
    FontRenderer _font;
    ModeManager _modeManager;
    ApiPoller _apiPoller;
    ConfigManager _configManager;
    WebDashboard _dashboard;
    bool _wifiConnected = false;
    bool _safeMode = false;

    WordClockMode* _wordClock = nullptr;
    WeatherMode*   _weather   = nullptr;
    CryptoMode*    _crypto    = nullptr;
    PixelArtMode*  _pixelArt  = nullptr;
    FlightMode*       _flight      = nullptr;
    AnalogClockMode*  _analogClock = nullptr;
    GameOfLifeMode*   _gameOfLife  = nullptr;
    WiFiRadarMode*    _wifiRadar   = nullptr;

    void initDisplay();
    void showBootScreen();
    void connectWiFi(const char* ssid, const char* pass);
    void initModes(const PixelPulseConfig& cfg);
    void initOTA();
    bool checkSafeMode();
    void incrementCrashCounter();
    void resetCrashCounter();
};
