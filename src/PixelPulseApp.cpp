#include "PixelPulseApp.h"
#include <WiFi.h>

#ifndef PIXELPULSE_OWM_API_KEY
#define PIXELPULSE_OWM_API_KEY ""
#endif

#ifndef PIXELPULSE_WIFI_SSID
#define PIXELPULSE_WIFI_SSID ""
#endif

#ifndef PIXELPULSE_WIFI_PASS
#define PIXELPULSE_WIFI_PASS ""
#endif

void PixelPulseApp::begin() {
    Serial.begin(115200);
    Serial.println();
    Serial.println("╔══════════════════════════╗");
    Serial.println("║  PIXELPULSE // BOOTING   ║");
    Serial.println("╚══════════════════════════╝");

    // Check crash counter — enter safe mode after 3 consecutive crashes
    _safeMode = checkSafeMode();
    if (_safeMode) {
        Serial.println("[SAFE] Too many crashes — display init skipped");
    }

    // Load config early — no hardware dependency
    _configManager.begin();
    PixelPulseConfig cfg;
    if (_configManager.isConfigured()) {
        cfg = _configManager.getConfig();
        if (cfg.owmApiKey.length() == 0 && String(PIXELPULSE_OWM_API_KEY).length() > 0) {
            cfg.owmApiKey = PIXELPULSE_OWM_API_KEY;
            _configManager.saveConfig(cfg);
            Serial.println("[CONFIG] OWM API key restored from build secret");
        }
        Serial.println("[CONFIG] Loaded from NVS");
    } else {
        cfg.city = "Salt Lake City";
        cfg.crypto = "BTC";
        cfg.icao = "KSLC";
        cfg.customerName = "GRANT";
        cfg.owmApiKey = PIXELPULSE_OWM_API_KEY;
        _configManager.saveConfig(cfg);
        Serial.println("[CONFIG] First boot — defaults saved");
    }

    // WiFi + OTA before display so recovery works even if panel crashes
    connectWiFi(PIXELPULSE_WIFI_SSID, PIXELPULSE_WIFI_PASS);
    if (_wifiConnected) {
        initOTA();
    }

    // Display init — the risky part
    if (!_safeMode) {
        incrementCrashCounter();
        initDisplay();
        if (_dma) {
            showBootScreen();
        }
    }

    if (_dma) {
        initModes(cfg);
    }

    if (_wifiConnected) {
        _apiPoller.begin(cfg);
        _dashboard.begin(&_modeManager, &_apiPoller, &_configManager, &_display);
    }

    // If we got here without crashing, reset the counter
    resetCrashCounter();
    Serial.println("[BOOT] Ready");
}

void PixelPulseApp::update() {
    if (_wifiConnected) {
#ifndef QEMU_BUILD
        ArduinoOTA.handle();
#endif
        _apiPoller.update();
        _dashboard.update();
    }
    if (_dma) {
        _modeManager.update();
    }
    yield();
}

PixelPulseApp::~PixelPulseApp() {
    delete _wordClock;
    delete _weather;
    delete _crypto;
    delete _pixelArt;
    delete _flight;
    delete _analogClock;
    delete _gameOfLife;
    delete _wifiRadar;
    delete _dma;
}

void PixelPulseApp::initDisplay() {
#ifdef QEMU_BUILD
    _dma = nullptr;
    Serial.println("[DISPLAY] DMA skipped in QEMU mode");
    return;
#else
    HUB75_I2S_CFG::i2s_pins pins = {
        R1_PIN, G1_PIN, B1_PIN,
        R2_PIN, G2_PIN, B2_PIN,
        A_PIN, B_PIN, C_PIN, D_PIN, E_PIN,
        LAT_PIN, OE_PIN, CLK_PIN
    };

    HUB75_I2S_CFG mxconfig(PANEL_WIDTH, PANEL_HEIGHT, 1, pins);
    mxconfig.clkphase = true;
    mxconfig.driver = HUB75_I2S_CFG::SHIFTREG;

    _dma = new MatrixPanel_I2S_DMA(mxconfig);
    if (!_dma->begin()) {
        Serial.println("[DISPLAY] DMA init failed");
        delete _dma;
        _dma = nullptr;
        return;
    }

    _dma->setBrightness8(BRIGHTNESS);
    _dma->fillScreenRGB888(0, 0, 0);
    _display.begin(_dma);
    _font.begin(&_display);
    Serial.println("[DISPLAY] Panel ready");
#endif
}

void PixelPulseApp::showBootScreen() {
    _display.clear();
    _font.drawStringCentered(4, "HELLO", COLOR_GREEN, FONT_6x8);
    _font.drawStringCentered(14, "FRIEND", COLOR_GREEN, FONT_6x8);
    _font.drawStringCentered(26, "PIXELPULSE V1", COLOR_GREEN, FONT_4x6);
    delay(BOOT_PAUSE_MS);
    _display.clear();
}

void PixelPulseApp::connectWiFi(const char* ssid, const char* pass) {
#ifdef QEMU_BUILD
    (void)ssid;
    (void)pass;
    _wifiConnected = false;
    Serial.println("[WIFI] Skipped in QEMU mode");
    return;
#else
    Serial.printf("[WIFI] Connecting to %s...\n", ssid);
    WiFi.begin(ssid, pass);

    if (_dma) {
        _font.drawStringCentered(14, "CONNECTING...", COLOR_GREEN, FONT_4x6);
    }

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        attempts++;
    }

    if (_dma) {
        _display.clear();
    }

    if (WiFi.status() == WL_CONNECTED) {
        _wifiConnected = true;
        Serial.printf("[WIFI] Connected: %s\n", WiFi.localIP().toString().c_str());

        configTzTime("MST7MDT,M3.2.0,M11.1.0", "pool.ntp.org", "time.nist.gov");
        struct tm timeinfo;
        int ntpAttempts = 0;
        while (!getLocalTime(&timeinfo) && ntpAttempts < 10) {
            delay(500);
            ntpAttempts++;
        }
        Serial.println(ntpAttempts < 10 ? "[NTP] Time synced" : "[NTP] Sync failed");
    } else {
        Serial.println("[WIFI] Offline mode");
    }
#endif
}

void PixelPulseApp::initModes(const PixelPulseConfig& cfg) {
    _modeManager.begin(&_display, &_font);

    _wordClock   = new WordClockMode(&_display, &_font, cfg.customerName);
    _analogClock = new AnalogClockMode(&_display);
    _weather     = new WeatherMode(&_display, &_font, &_apiPoller);
    _crypto      = new CryptoMode(&_display, &_font, &_apiPoller);
    _pixelArt    = new PixelArtMode(&_display);
    _flight      = new FlightMode(&_display, &_font, &_apiPoller);
    _gameOfLife  = new GameOfLifeMode(&_display);
    _wifiRadar   = new WiFiRadarMode(&_display, &_font);

    _modeManager.addMode(_wordClock);
    _modeManager.addMode(_analogClock);
    _modeManager.addMode(_weather);
    _modeManager.addMode(_crypto);
    _modeManager.addMode(_pixelArt);
    _modeManager.addMode(_flight);
    _modeManager.addMode(_gameOfLife);
    _modeManager.addMode(_wifiRadar);

    _modeManager.setBooted();
}

void PixelPulseApp::initOTA() {
#ifndef QEMU_BUILD
    ArduinoOTA.setHostname("pixelpulse");
    ArduinoOTA.begin();
    Serial.println("[OTA] Ready");
#endif
}

bool PixelPulseApp::checkSafeMode() {
    Preferences prefs;
    prefs.begin("crashes", true);
    int count = prefs.getInt("count", 0);
    prefs.end();
    return count >= 3;
}

void PixelPulseApp::incrementCrashCounter() {
    Preferences prefs;
    prefs.begin("crashes", false);
    int count = prefs.getInt("count", 0);
    prefs.putInt("count", count + 1);
    Serial.printf("[BOOT] Crash counter: %d\n", count + 1);
    prefs.end();
}

void PixelPulseApp::resetCrashCounter() {
    Preferences prefs;
    prefs.begin("crashes", false);
    prefs.putInt("count", 0);
    prefs.end();
}
