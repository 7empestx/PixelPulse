#pragma once
#include <Arduino.h>
#include <vector>
#include "Display.h"
#include "FontRenderer.h"

class Mode {
public:
    virtual ~Mode() {}
    virtual const char* getName() = 0;
    virtual void init() = 0;
    virtual void update() = 0;
    virtual bool isDone() = 0;
};

class ModeManager {
public:
    void begin(Display* display, FontRenderer* font);
    void addMode(Mode* mode);
    void update();
    void showBootScreen();
    void setBooted() { _booted = true; }

    // Dashboard API
    int getCurrentModeIndex() const { return _currentMode; }
    const char* getCurrentModeName() const;
    int getModeCount() const { return (int)_modes.size(); }
    const char* getModeName(int index) const;
    void setMode(int index);
    void nextMode();
    void prevMode();
    void setPaused(bool paused);
    bool isPaused() const { return _paused; }

private:
    void glitchTransition();

    Display* _display = nullptr;
    FontRenderer* _font = nullptr;
    std::vector<Mode*> _modes;
    int _currentMode = -1;
    unsigned long _modeStartTime = 0;
    bool _booted = false;
    bool _transitioning = false;
    unsigned long _transitionStart = 0;
    bool _paused = false;
};
