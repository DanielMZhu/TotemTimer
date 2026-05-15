#include "TotemManager.h"

TotemManager::TotemManager(MatrixPanel_I2S_DMA* display, RTC_DS3231* rtc) 
    : _display(display), _rtc(rtc) {
    _mutex = xSemaphoreCreateMutex();
}

void TotemManager::begin() {
    _state.currentLogo = logo_allArray[0];
    _state.needsLogoRedraw = true;
    _state.needsFullRedraw = true; // <--- ADD THIS
}

void TotemManager::updateSchedule() {
    // Rotate logos every 5 seconds
    if (millis() - _lastRotationMillis >= 5000) {
        if (xSemaphoreTake(_mutex, pdMS_TO_TICKS(10))) {
            _logoIndex = (_logoIndex + 1) % 9; 
            _state.currentLogo = logo_allArray[_logoIndex];
            _state.needsLogoRedraw = true;
            _lastRotationMillis = millis();
            xSemaphoreGive(_mutex);
        }
    }
}

void TotemManager::renderFrame() {
    if (xSemaphoreTake(_mutex, pdMS_TO_TICKS(25))) {
        
        // Use the flag we added to the header
        if (_state.needsFullRedraw) {
            // Draw the background (logo_allArray[9])
            _display->drawRGBBitmap(0, 0, logo_allArray[9], 64, 32);
            _state.needsFullRedraw = false;
        }

        // Only redraw the logo if it changed
        if (_state.needsLogoRedraw) {
            // Re-draw the background section behind the logo first to "clear" it
            // Then draw the new logo at your desired coordinates
            _display->drawRGBBitmap(26, 10, _state.currentLogo, 12, 12);
            _state.needsLogoRedraw = false;
        }

        // RTC Handling
        DateTime now = _rtc->now();
        if (now.year() < 2025) { 
             // If we see 149:149, it shows as a year like 2165 or 2000
             // Don't draw the time if the data is garbage
        } else {
            // Draw the clock
            _display->setCursor(2, 22);
            _display->setTextColor(_display->color565(255, 255, 255));
            
            // ERASE the old numbers only
            _display->fillRect(2, 22, 60, 10, 0); 
            
            _display->printf("%02d:%02d:%02d", now.hour(), now.minute(), now.second());
        }

        xSemaphoreGive(_mutex);
    }
}