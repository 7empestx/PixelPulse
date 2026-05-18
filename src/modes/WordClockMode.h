#pragma once
#include "../ModeManager.h"
#include <vector>

class WordClockMode : public Mode {
public:
    WordClockMode(Display* display, FontRenderer* font, const String& customerName);
    const char* getName() override { return "WordClock"; }
    void init() override;
    void update() override;
    bool isDone() override;

private:
    void wrapText(const String& text, int maxWidth, std::vector<String>& lines);

    Display* _display;
    FontRenderer* _font;
    String _customerName;

    std::vector<String> _timeLines;
    String _subLine;

    // Total characters across all time lines for typewriter
    int _totalTimeChars = 0;
    int _charsRevealed = 0;
    int _subCharsRevealed = 0;
    unsigned long _lastCharTime = 0;
    bool _textDone = false;
    bool _subDone = false;
    unsigned long _doneTime = 0;

    // Breathing
    bool _breathing = false;
    unsigned long _breathStart = 0;
};
