#include "ApiPoller.h"
#include <HTTPClient.h>
#include <WiFi.h>

void ApiPoller::begin(const PixelPulseConfig& config) {
    _config = config;
    _lastWeather = 0;
    _lastCrypto  = 0;
    _lastFlight  = 0;
}

void ApiPoller::update() {
    if (WiFi.status() != WL_CONNECTED) return;

    unsigned long now = millis();

    if (now - _lastWeather >= WEATHER_INTERVAL_MS || _lastWeather == 0) {
        fetchWeather();
        _lastWeather = millis();
    }

    if (now - _lastCrypto >= CRYPTO_INTERVAL_MS || _lastCrypto == 0) {
        fetchCrypto();
        _lastCrypto = millis();
    }

    if (now - _lastFlight >= FLIGHT_INTERVAL_MS || _lastFlight == 0) {
        fetchFlights();
        _lastFlight = millis();
    }
}

WeatherData ApiPoller::getWeather() { return _weather; }
CryptoData  ApiPoller::getCrypto()  { return _crypto; }
FlightData  ApiPoller::getFlights() { return _flights; }

void ApiPoller::fetchWeather() {
    if (_config.owmApiKey.length() == 0 || _config.city.length() == 0) return;

    HTTPClient http;
    String city = _config.city;
    city.replace(" ", "%20");
    String url = "http://api.openweathermap.org/data/2.5/weather?q="
                 + city + "&appid=" + _config.owmApiKey + "&units=metric";

    http.begin(url);
    http.setTimeout(5000);
    int code = http.GET();

    if (code == 200) {
        String payload = http.getString();
        JsonDocument doc;
        DeserializationError err = deserializeJson(doc, payload);
        if (!err) {
            _weather.tempC = doc["main"]["temp"].as<float>();
            _weather.tempF = _weather.tempC * 9.0f / 5.0f + 32.0f;
            _weather.condition = doc["weather"][0]["main"].as<String>();
            _weather.icon = doc["weather"][0]["icon"].as<String>();
            _weather.valid = true;
        }
    } else {
        Serial.printf("[API] Weather fetch failed: HTTP %d\n", code);
    }
    http.end();
}

void ApiPoller::fetchCrypto() {
    if (_config.crypto.length() == 0) return;

    HTTPClient http;
    String coinId = _config.crypto;
    coinId.toLowerCase();
    if (coinId == "btc") coinId = "bitcoin";
    else if (coinId == "eth") coinId = "ethereum";
    else if (coinId == "sol") coinId = "solana";
    else if (coinId == "ada") coinId = "cardano";
    else if (coinId == "doge") coinId = "dogecoin";
    else if (coinId == "xrp") coinId = "ripple";
    else if (coinId == "dot") coinId = "polkadot";
    else if (coinId == "ltc") coinId = "litecoin";

    String url = "https://api.coingecko.com/api/v3/simple/price?ids="
                 + coinId + "&vs_currencies=usd&include_24hr_change=true";

    http.begin(url);
    http.setTimeout(5000);
    int code = http.GET();

    if (code == 200) {
        String payload = http.getString();
        JsonDocument doc;
        DeserializationError err = deserializeJson(doc, payload);
        if (!err && doc[coinId]["usd"].is<float>()) {
            _crypto.price = doc[coinId]["usd"].as<float>();
            _crypto.change24h = doc[coinId]["usd_24h_change"].as<float>();
            _crypto.symbol = _config.crypto;
            _crypto.valid = true;
        }
    } else {
        Serial.printf("[API] Crypto fetch failed: HTTP %d\n", code);
    }
    http.end();
}

void ApiPoller::fetchFlights() {
    if (_config.icao.length() == 0) return;

    HTTPClient http;
    time_t epoch;
    time(&epoch);
    long begin = epoch - 3600;
    long end = epoch;

    String url = "https://opensky-network.org/api/flights/departure?airport="
                 + _config.icao + "&begin=" + String(begin) + "&end=" + String(end);

    http.begin(url);
    http.setTimeout(8000);
    int code = http.GET();

    if (code == 200) {
        String payload = http.getString();
        JsonDocument doc;
        DeserializationError err = deserializeJson(doc, payload);
        if (!err) {
            _flights.flights.clear();
            JsonArray arr = doc.as<JsonArray>();
            int count = 0;
            for (JsonObject obj : arr) {
                if (count >= 5) break;
                FlightEntry f;
                f.callsign = obj["callsign"].as<String>();
                f.callsign.trim();
                f.origin = obj["estDepartureAirport"].as<String>();
                f.altitude = 0;
                _flights.flights.push_back(f);
                count++;
            }
            _flights.valid = true;
        }
    } else {
        Serial.printf("[API] Flights fetch failed: HTTP %d\n", code);
    }
    http.end();
}
