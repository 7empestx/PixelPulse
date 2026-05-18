#pragma once
#include <Arduino.h>
#include <Preferences.h>

// NVS keys
#define NVS_NAMESPACE    "pixelpulse"
#define KEY_CITY         "city"
#define KEY_CRYPTO       "crypto"
#define KEY_ICAO         "icao"
#define KEY_CUSTOMER     "customer_name"
#define KEY_OWM_KEY      "owm_key"

// Mr. Robot color palette
#define COLOR_GREEN        0x00FF41
#define COLOR_DIM_GREEN    0x003A0F
#define COLOR_RED          0xFF0000
#define COLOR_WHITE        0xFFFFFF
#define COLOR_BLACK        0x000000
#define COLOR_CYAN         0x00FFFF
#define COLOR_YELLOW       0xFFFF00
#define COLOR_BLUE         0x0080FF

// Display
#define PANEL_WIDTH   64
#define PANEL_HEIGHT  32
#define BRIGHTNESS    50

// HUB75 Pin Mapping — RGB Matrix Adapter Board (E) for ESP32-DevKitC V4
// Source: https://seengreat.com/wiki/186/rgb-matrix-adapter-board-e
#define R1_PIN  18
#define G1_PIN  25
#define B1_PIN  5
#define R2_PIN  17
#define G2_PIN  33
#define B2_PIN  16
#define A_PIN   4
#define B_PIN   3
#define C_PIN   0
#define D_PIN   21
#define E_PIN   32
#define CLK_PIN 2
#define LAT_PIN 19
#define OE_PIN  15

// Timing
#define MODE_DURATION_MS      15000
#define GLITCH_DURATION_MS    200
#define CHAR_TYPE_DELAY_MS    80
#define BOOT_PAUSE_MS         2000

// API intervals (ms)
#define WEATHER_INTERVAL_MS   600000   // 10 minutes
#define CRYPTO_INTERVAL_MS    120000   // 2 minutes
#define FLIGHT_INTERVAL_MS    300000   // 5 minutes

struct PixelPulseConfig {
    String city;
    String crypto;
    String icao;
    String customerName;
    String owmApiKey;
};

class ConfigManager {
public:
    void begin();
    bool isConfigured();
    void launchCaptivePortal();
    PixelPulseConfig getConfig();
    void saveConfig(const PixelPulseConfig& cfg);

private:
    Preferences _prefs;
    PixelPulseConfig _config;
    bool _configured = false;
};
