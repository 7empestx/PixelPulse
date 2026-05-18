#pragma once

namespace pixelpulse {

inline int stringWidth4x6(const char* str) {
    int len = 0;
    while (*str++) len++;
    return (len > 0) ? len * 4 + (len - 1) : 0;
}

inline int stringWidth6x8(const char* str) {
    int len = 0;
    while (*str++) len++;
    return (len > 0) ? len * 6 + (len - 1) : 0;
}

inline int centerX(int panelWidth, int stringWidth) {
    return (panelWidth - stringWidth) / 2;
}

} // namespace pixelpulse
