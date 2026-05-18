#pragma once
#include <string>

namespace pixelpulse {

inline const char* hourWord(int h) {
    static const char* hours[] = {
        "TWELVE","ONE","TWO","THREE","FOUR","FIVE",
        "SIX","SEVEN","EIGHT","NINE","TEN","ELEVEN"
    };
    return hours[((h % 12) + 12) % 12];
}

inline std::string minuteWord(int m) {
    switch (m) {
        case 0:  return "";
        case 5:  return "FIVE PAST ";
        case 10: return "TEN PAST ";
        case 15: return "QUARTER PAST ";
        case 20: return "TWENTY PAST ";
        case 25: return "TWENTY FIVE PAST ";
        case 30: return "HALF PAST ";
        case 35: return "TWENTY FIVE TO ";
        case 40: return "TWENTY TO ";
        case 45: return "QUARTER TO ";
        case 50: return "TEN TO ";
        case 55: return "FIVE TO ";
        default: {
            int rounded = ((m + 2) / 5) * 5;
            if (rounded == 60) rounded = 0;
            return minuteWord(rounded);
        }
    }
}

inline int roundMinutes(int m) {
    int rounded = ((m + 2) / 5) * 5;
    return (rounded == 60) ? 0 : rounded;
}

inline std::string timeToWords(int hour, int minute) {
    int rounded = roundMinutes(minute);

    if (rounded == 0) {
        int h = (minute >= 58) ? hour + 1 : hour;
        return std::string(hourWord(h)) + " O'CLOCK";
    }
    if (rounded <= 30) {
        return minuteWord(rounded) + hourWord(hour);
    }
    return minuteWord(rounded) + hourWord(hour + 1);
}

inline std::string coinIdFromSymbol(const std::string& symbol) {
    if (symbol == "BTC" || symbol == "btc") return "bitcoin";
    if (symbol == "ETH" || symbol == "eth") return "ethereum";
    if (symbol == "SOL" || symbol == "sol") return "solana";
    if (symbol == "ADA" || symbol == "ada") return "cardano";
    if (symbol == "DOGE" || symbol == "doge") return "dogecoin";
    if (symbol == "XRP" || symbol == "xrp") return "ripple";
    if (symbol == "DOT" || symbol == "dot") return "polkadot";
    if (symbol == "LTC" || symbol == "ltc") return "litecoin";
    // Default: lowercase the symbol
    std::string lower = symbol;
    for (auto& c : lower) c = tolower(c);
    return lower;
}

} // namespace pixelpulse
