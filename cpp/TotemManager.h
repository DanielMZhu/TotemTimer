#ifndef TOTEM_MANAGER_H
#define TOTEM_MANAGER_H

#include <Arduino.h>
#include <ESP32-HUB75-MatrixPanel-I2S-DMA.h>
#include <RTClib.h>
#include "bitmaps.h"

struct TotemState {
    const uint16_t* currentLogo;
    bool needsLogoRedraw;
    bool needsFullRedraw; // <--- Add this
};

class TotemManager {
public:
    TotemManager(MatrixPanel_I2S_DMA* display, RTC_DS3231* rtc);
    void begin();
    void updateSchedule();
    void renderFrame();  

private:
    MatrixPanel_I2S_DMA* _display;
    RTC_DS3231* _rtc;
    SemaphoreHandle_t _mutex;
    TotemState _state;
    int _logoIndex = 0;
    unsigned long _lastRotationMillis = 0;
};

#endif