#include "ModeManager.h"
#include "Config.h"

void ModeManager::begin(Display* display, FontRenderer* font) {
    _display = display;
    _font = font;
}

void ModeManager::addMode(Mode* mode) {
    _modes.push_back(mode);
}

void ModeManager::showBootScreen() {
    _display->clear();
    const char* msg = "HELLO FRIEND";
    _font->drawStringCentered(12, msg, COLOR_GREEN, FONT_6x8);
    delay(BOOT_PAUSE_MS);
    glitchTransition();
    _booted = true;
}

void ModeManager::glitchTransition() {
    unsigned long start = millis();
    while (millis() - start < GLITCH_DURATION_MS) {
        for (int i = 0; i < 200; i++) {
            int x = random(PANEL_WIDTH);
            int y = random(PANEL_HEIGHT);
            uint32_t color = random(2) ? COLOR_GREEN : (random(2) ? COLOR_WHITE : COLOR_BLACK);
            _display->drawPixel(x, y, color);
        }
        delay(10);
    }
    _display->clear();
}

void ModeManager::update() {
    if (!_booted || _modes.empty()) return;

    if (_transitioning) {
        if (millis() - _transitionStart >= GLITCH_DURATION_MS) {
            _transitioning = false;
            _display->clear();
            _modes[_currentMode]->init();
            _modeStartTime = millis();
        } else {
            for (int i = 0; i < 200; i++) {
                int x = random(PANEL_WIDTH);
                int y = random(PANEL_HEIGHT);
                uint32_t color = random(2) ? COLOR_GREEN : (random(2) ? COLOR_WHITE : COLOR_BLACK);
                _display->drawPixel(x, y, color);
            }
        }
        return;
    }

    // First mode
    if (_currentMode < 0) {
        _currentMode = 0;
        _modes[_currentMode]->init();
        _modeStartTime = millis();
        return;
    }

    // Check if time to switch (skip if paused)
    if (_paused) {
        _modes[_currentMode]->update();
        return;
    }

    bool timeUp = (millis() - _modeStartTime) >= MODE_DURATION_MS;
    bool done = _modes[_currentMode]->isDone();

    if (timeUp || done) {
        _currentMode = (_currentMode + 1) % _modes.size();
        _transitioning = true;
        _transitionStart = millis();
        return;
    }

    _modes[_currentMode]->update();
}

const char* ModeManager::getCurrentModeName() const {
    if (_currentMode >= 0 && _currentMode < (int)_modes.size())
        return _modes[_currentMode]->getName();
    return "NONE";
}

const char* ModeManager::getModeName(int index) const {
    if (index >= 0 && index < (int)_modes.size())
        return _modes[index]->getName();
    return "NONE";
}

void ModeManager::setMode(int index) {
    if (index < 0 || index >= (int)_modes.size()) return;
    if (_transitioning) return;
    _currentMode = index;
    _transitioning = true;
    _transitionStart = millis();
}

void ModeManager::nextMode() {
    if (_modes.empty() || _transitioning) return;
    _currentMode = (_currentMode + 1) % _modes.size();
    _transitioning = true;
    _transitionStart = millis();
}

void ModeManager::prevMode() {
    if (_modes.empty() || _transitioning) return;
    _currentMode = (_currentMode - 1 + _modes.size()) % _modes.size();
    _transitioning = true;
    _transitionStart = millis();
}

void ModeManager::setPaused(bool paused) {
    _paused = paused;
    if (!_paused) _modeStartTime = millis();
}
