#include <Arduino.h>
#include "PixelPulseApp.h"

PixelPulseApp app;

void setup() { app.begin(); }
void loop()  { app.update(); }
