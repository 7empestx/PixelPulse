#include "Config.h"
#include <WiFiManager.h>

void ConfigManager::begin() {
    _prefs.begin(NVS_NAMESPACE, false);
    _config.city         = _prefs.getString(KEY_CITY, "");
    _config.crypto       = _prefs.getString(KEY_CRYPTO, "");
    _config.icao         = _prefs.getString(KEY_ICAO, "");
    _config.customerName = _prefs.getString(KEY_CUSTOMER, "");
    _config.owmApiKey    = _prefs.getString(KEY_OWM_KEY, "");
    _configured = _config.city.length() > 0 && _config.customerName.length() > 0;
}

bool ConfigManager::isConfigured() {
    return _configured;
}

PixelPulseConfig ConfigManager::getConfig() {
    return _config;
}

void ConfigManager::saveConfig(const PixelPulseConfig& cfg) {
    _prefs.putString(KEY_CITY, cfg.city);
    _prefs.putString(KEY_CRYPTO, cfg.crypto);
    _prefs.putString(KEY_ICAO, cfg.icao);
    _prefs.putString(KEY_CUSTOMER, cfg.customerName);
    _prefs.putString(KEY_OWM_KEY, cfg.owmApiKey);
    _config = cfg;
    _configured = true;
}

void ConfigManager::launchCaptivePortal() {
    WiFiManager wm;
    wm.setTitle("PIXELPULSE // SYSTEM CONFIG");
    wm.setDarkMode(true);

    WiFiManagerParameter paramCity("city", "City (e.g. Salt Lake City)", "", 64);
    WiFiManagerParameter paramCrypto("crypto", "Crypto (e.g. BTC)", "BTC", 16);
    WiFiManagerParameter paramIcao("icao", "Airport ICAO (e.g. KSLC)", "", 8);
    WiFiManagerParameter paramName("name", "Your Name", "", 32);
    WiFiManagerParameter paramOwm("owm", "OpenWeatherMap API Key", "", 64);

    wm.addParameter(&paramCity);
    wm.addParameter(&paramCrypto);
    wm.addParameter(&paramIcao);
    wm.addParameter(&paramName);
    wm.addParameter(&paramOwm);

    wm.setConfigPortalTimeout(300);

    if (wm.startConfigPortal("PIXELPULSE-SETUP")) {
        PixelPulseConfig cfg;
        cfg.city         = String(paramCity.getValue());
        cfg.crypto       = String(paramCrypto.getValue());
        cfg.icao         = String(paramIcao.getValue());
        cfg.customerName = String(paramName.getValue());
        cfg.owmApiKey    = String(paramOwm.getValue());
        saveConfig(cfg);
    }
}
