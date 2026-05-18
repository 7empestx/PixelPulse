#include "WordClockMode.h"
#include <TimeWords.h>
#include <time.h>
#include <math.h>

WordClockMode::WordClockMode(Display* display, FontRenderer* font, const String& customerName)
    : _display(display), _font(font), _customerName(customerName) {}

void WordClockMode::wrapText(const String& text, int maxWidth, std::vector<String>& lines) {
    lines.clear();
    String remaining = text;
    remaining.trim();

    while (remaining.length() > 0) {
        int w = _font->getStringWidth(remaining.c_str(), FONT_4x6);
        if (w <= maxWidth) {
            lines.push_back(remaining);
            break;
        }

        int lastSpace = -1;
        for (int i = 0; i < (int)remaining.length(); i++) {
            String sub = remaining.substring(0, i + 1);
            if (_font->getStringWidth(sub.c_str(), FONT_4x6) > maxWidth) {
                break;
            }
            if (remaining[i] == ' ') {
                lastSpace = i;
            }
        }

        if (lastSpace > 0) {
            lines.push_back(remaining.substring(0, lastSpace));
            remaining = remaining.substring(lastSpace + 1);
        } else {
            lines.push_back(remaining.substring(0, 10));
            remaining = remaining.substring(10);
        }
    }
}

void WordClockMode::init() {
    struct tm timeinfo;
    String timeText;
    if (getLocalTime(&timeinfo)) {
        std::string words = pixelpulse::timeToWords(timeinfo.tm_hour, timeinfo.tm_min);
        timeText = String(words.c_str());
    } else {
        timeText = "NO TIME";
    }

    wrapText(timeText, PANEL_WIDTH - 4, _timeLines);

    _totalTimeChars = 0;
    for (const auto& line : _timeLines) {
        _totalTimeChars += line.length();
    }

    _subLine = "> " + _customerName;
    _subLine.toUpperCase();
    _charsRevealed = 0;
    _subCharsRevealed = 0;
    _lastCharTime = millis();
    _textDone = false;
    _subDone = false;
    _doneTime = 0;
    _breathing = false;
    _breathStart = 0;
    _display->clear();
}

void WordClockMode::update() {
    if (!_display->ready()) return;
    unsigned long now = millis();

    if (!_textDone) {
        if (now - _lastCharTime >= CHAR_TYPE_DELAY_MS) {
            _charsRevealed++;
            _lastCharTime = now;
            if (_charsRevealed >= _totalTimeChars) {
                _textDone = true;
            }
        }
    } else if (!_subDone) {
        if (now - _lastCharTime >= CHAR_TYPE_DELAY_MS) {
            _subCharsRevealed++;
            _lastCharTime = now;
            if (_subCharsRevealed >= (int)_subLine.length()) {
                _subDone = true;
                _doneTime = now;
                _breathing = true;
                _breathStart = now;
            }
        }
    }

    _display->clear();

    // Calculate vertical layout
    int lineHeight = _font->getFontHeight(FONT_4x6) + 2;
    int totalLines = _timeLines.size() + 1;
    int totalHeight = totalLines * lineHeight;
    int startY = (PANEL_HEIGHT - totalHeight) / 2;
    if (startY < 0) startY = 0;

    // Breathing color
    uint32_t textColor = COLOR_GREEN;
    if (_breathing) {
        float t = (now - _breathStart) / 1000.0f;
        float brightness = 0.5f + 0.5f * sin(t * 2.0f * PI);
        uint8_t g = 60 + (uint8_t)(brightness * 195);
        uint8_t b_val = (uint8_t)(brightness * 0x41);
        textColor = ((uint32_t)g << 8) | b_val;
    }

    // Draw time lines with typewriter + glow trail
    int charsUsed = 0;
    for (int i = 0; i < (int)_timeLines.size(); i++) {
        int y = startY + i * lineHeight;
        int lineLen = _timeLines[i].length();
        int charsToShow = _charsRevealed - charsUsed;
        if (charsToShow <= 0) {
            charsUsed += lineLen;
            continue;
        }
        if (charsToShow > lineLen) charsToShow = lineLen;

        int fullWidth = _font->getStringWidth(_timeLines[i].c_str(), FONT_4x6);
        int lineX = (PANEL_WIDTH - fullWidth) / 2;

        for (int c = 0; c < charsToShow; c++) {
            uint32_t charColor;
            int distFromHead = charsToShow - 1 - c;

            if (_breathing) {
                charColor = textColor;
            } else if (!_textDone && distFromHead == 0) {
                charColor = COLOR_WHITE;
            } else if (!_textDone && distFromHead <= 2) {
                charColor = 0x00FF60;
            } else {
                charColor = COLOR_GREEN;
            }

            lineX += _font->drawChar(lineX, y, _timeLines[i][c], charColor, FONT_4x6);
        }

        if (!_textDone && charsToShow < lineLen && charsToShow == (_charsRevealed - charsUsed)) {
            _font->drawCursor(lineX, y, COLOR_GREEN, FONT_4x6);
        }

        charsUsed += lineLen;
    }

    // Sub line
    int subY = startY + (int)_timeLines.size() * lineHeight;
    if (_textDone) {
        int subCharsToShow = _subCharsRevealed;
        if (subCharsToShow > (int)_subLine.length()) subCharsToShow = _subLine.length();

        int subFullW = _font->getStringWidth(_subLine.c_str(), FONT_4x6);
        int subX = (PANEL_WIDTH - subFullW) / 2;

        for (int c = 0; c < subCharsToShow; c++) {
            uint32_t charColor;
            int distFromHead = subCharsToShow - 1 - c;

            if (_breathing) {
                charColor = (c == 0) ? COLOR_CYAN : textColor;
            } else if (c == 0) {
                charColor = COLOR_CYAN;
            } else if (distFromHead == 0) {
                charColor = COLOR_WHITE;
            } else if (distFromHead <= 2) {
                charColor = 0x00FF60;
            } else {
                charColor = COLOR_GREEN;
            }

            subX += _font->drawChar(subX, subY, _subLine[c], charColor, FONT_4x6);
        }

        _font->drawCursor(subX, subY, COLOR_GREEN, FONT_4x6);
    }
}

bool WordClockMode::isDone() {
    return _subDone && (millis() - _doneTime > 3000);
}
