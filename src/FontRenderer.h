#pragma once
#include <Arduino.h>
#include "Display.h"

// Font sizes
enum FontSize {
    FONT_4x6,
    FONT_6x8
};

class FontRenderer {
public:
    void begin(Display* display);

    // Draw a single character, returns x advance
    int drawChar(int x, int y, char c, uint32_t color, FontSize size = FONT_4x6);

    // Draw a string
    void drawString(int x, int y, const char* str, uint32_t color, FontSize size = FONT_4x6);

    // Draw string centered horizontally
    void drawStringCentered(int y, const char* str, uint32_t color, FontSize size = FONT_4x6);

    // Get string width in pixels
    int getStringWidth(const char* str, FontSize size = FONT_4x6);

    // Get font height
    int getFontHeight(FontSize size);

    // Draw blinking cursor at position
    void drawCursor(int x, int y, uint32_t color, FontSize size = FONT_4x6);

private:
    Display* _display = nullptr;

    void drawPixel(int x, int y, uint32_t color);
    int charWidth(FontSize size);
    int charHeight(FontSize size);
    const uint8_t* getGlyph4x6(char c);
    const uint8_t* getGlyph6x8(char c);
};
