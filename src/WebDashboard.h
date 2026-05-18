#pragma once
#include <Arduino.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include "ModeManager.h"
#include "ApiPoller.h"
#include "Config.h"

class WebDashboard {
public:
    void begin(ModeManager* modeManager, ApiPoller* apiPoller,
               ConfigManager* configManager, Display* display);
    void update();

private:
    WebServer _server{80};
    ModeManager* _modeManager = nullptr;
    ApiPoller* _apiPoller = nullptr;
    ConfigManager* _configManager = nullptr;
    Display* _display = nullptr;
    unsigned long _startTime = 0;
    uint8_t _brightness = BRIGHTNESS;

    void handleRoot();
    void handleGetStatus();
    void handleGetModes();
    void handleSetMode();
    void handleNextMode();
    void handlePrevMode();
    void handleSetPaused();
    void handleSetBrightness();
    void handleGetConfig();
    void handleSetConfig();
    void handleGetData();
    void handleNotFound();
};
