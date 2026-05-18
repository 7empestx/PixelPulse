#pragma once
#include <Arduino.h>
#include <ArduinoJson.h>
#include <vector>
#include "Config.h"

struct WeatherData {
    float tempC = 0;
    float tempF = 0;
    String condition = "";
    String icon = "";     // OWM icon code
    bool valid = false;
};

struct CryptoData {
    float price = 0;
    float change24h = 0;  // percentage
    String symbol = "";
    bool valid = false;
};

struct FlightEntry {
    String callsign;
    String origin;
    float altitude;       // meters
};

struct FlightData {
    std::vector<FlightEntry> flights;
    bool valid = false;
};

class ApiPoller {
public:
    void begin(const PixelPulseConfig& config);
    void update();

    WeatherData getWeather();
    CryptoData  getCrypto();
    FlightData  getFlights();

private:
    void fetchWeather();
    void fetchCrypto();
    void fetchFlights();

    PixelPulseConfig _config;

    WeatherData _weather;
    CryptoData  _crypto;
    FlightData  _flights;

    unsigned long _lastWeather = 0;
    unsigned long _lastCrypto  = 0;
    unsigned long _lastFlight  = 0;
};
