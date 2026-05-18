#pragma once
#include <cstdint>
#include <cstddef>

namespace pixelpulse {

inline bool spritePixelAt(const uint8_t* sprite, int width, int x, int y) {
    int idx = y * width + x;
    int byteIdx = idx / 8;
    int bitIdx = 7 - (idx % 8);
    return (sprite[byteIdx] >> bitIdx) & 1;
}

inline size_t spriteByteCount(int width, int height) {
    return (width * height + 7) / 8;
}

} // namespace pixelpulse
