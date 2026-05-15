#include <Arduino.h>
#include "schedules.h"
#include <ESP32-HUB75-MatrixPanel-I2S-DMA.h>
#include <Adafruit_GFX.h>
#include "font3pt7b.h"
#include "RTClib.h"
#include "bitmaps.h"  // Include your uploaded file

MatrixPanel_I2S_DMA* display = nullptr;
RTC_DS3231 rtc;
static unsigned long lastUpdate = 0;  // Moved here from the bottom
#define WHITE display->color565(255, 255, 255)
#define RED display->color565(255, 0, 0)
#define BLUE display->color565(0, 0, 255)
#define GREEN display->color565(0, 255, 0)
#define YELLOW display->color565(255, 215, 0)
// Your existing pin configuration
HUB75_I2S_CFG::i2s_pins _pins = {
  42, 41, 40, 38, 39, 37,
  45, 36, 48, 35, -1,
  47, 14, 2
};

int currentTimeTop = 0;
int currentTimeBot = 0;

int scrollIdxTop = 0;
int scrollIdxBot = 0;
String lastTopWord = "";
String lastBotWord = "";
unsigned long lastScrollMove = 0;
unsigned long lastScrollMoveBot = 0;
const int scrollSpeed = 250;  // milliseconds between shifts
unsigned long scrollStartTop = 0;
unsigned long scrollStartBot = 0;
bool isScrollingTop = false;
bool isScrollingBot = false;
String previousTopStatus = "";
String previousBotStatus = "";

int logoIndex = 0;  // Tracks which logo is currently at the top
const int totalLogos = 9;

const Set* stageSchedules[] = {
  FRIDAY_B, FRIDAY_M, FRIDAY_C, FRIDAY_K, FRIDAY_J, FRIDAY_N, FRIDAY_Q, FRIDAY_W, FRIDAY_S
};

const Set* satSchedules[] = {
  SATURDAY_B, SATURDAY_M, SATURDAY_C, SATURDAY_K, SATURDAY_J, SATURDAY_N, SATURDAY_Q, SATURDAY_W, SATURDAY_S
};

const Set* sunSchedules[] = {
  SUNDAY_B, SUNDAY_M, SUNDAY_C, SUNDAY_K, SUNDAY_J, SUNDAY_N, SUNDAY_Q, SUNDAY_W, SUNDAY_S
};

void clearLogo(int x) {
  if (x == 1) {  // top
    display->fillRect(2, 2, 12, 12, 0);
  } else {
    display->fillRect(16, 10, 12, 12, 0);
  }
}

void clearText(int x) {
  if (x == 1) {
    display->fillRect(15, 5, 7, 40, 0);
  } else {
    display->fillRect(15, 20, 7, 40, 0);
  }
}

String getScrollWindow(String word, int& index) {
  if (word.length() <= 8) return word;

  String loopString = word + " -- " + word;
  String displayPart = loopString.substring(index, index + 8);

  index++;
  // FIX: Reset when index reaches the length of word + the 4 spaces
  if (index >= word.length() + 4) {
    index = 0;
  }

  return displayPart;
}

void updateScrollingText(String topWord, String botWord) {
  unsigned long now = millis();

  // TOP ROW
  if (topWord.length() > 0) {
    if (!isScrollingTop) {
      scrollStartTop = now;
      isScrollingTop = true;
      scrollIdxTop = 0;
    }

    // Logic: Scroll if > 8 chars, otherwise just print static text
    if (topWord.length() > 8) {
      if (now - lastScrollMove > scrollSpeed) {
        lastScrollMove = now;
        String topPart = getScrollWindow(topWord, scrollIdxTop);
        display->fillRect(15, 4, 31, 8, 0);  // Height 8 to clear the "line" [cite: 14]
        display->setCursor(15, 10);
        display->print(topPart);
      }
    } else {
      if (topWord != lastTopWord) {
        display->fillRect(15, 4, 31, 8, 0);  // Clear once [cite: 25]
        display->setCursor(15, 10);
        display->print(topWord);
        lastTopWord = topWord;  // Update the state
      }
    }
  }

  // BOTTOM ROW
  if (botWord.length() > 0) {
    if (!isScrollingBot) {
      scrollStartBot = now;
      isScrollingBot = true;
      scrollIdxBot = 0;
    }

    if (botWord.length() > 8) {
      if (now - lastScrollMoveBot > scrollSpeed) {
        lastScrollMoveBot = now;
        String botPart = getScrollWindow(botWord, scrollIdxBot);
        display->fillRect(15, 20, 31, 8, 0);  // Lowered y and increased height
        display->setCursor(15, 26);
        display->print(botPart);
      }
    } else {
      if (botWord != lastBotWord) {
        display->fillRect(15, 20, 31, 8, 0);  // Clear once
        display->setCursor(15, 26);
        display->print(botWord);
        lastBotWord = botWord;  // Update the state
      }
    }
  }
}
void renderTime(bool top, int time) {
  display->setTextColor(YELLOW);
  int y = top ? 10 : 26;

  // Clear the entire time area regardless of previous digit count
  // This prevents artifacts from previous artists/times
  display->fillRect(44, y - 5, 19, 7, 0);
  if (time == -1) {
    display->setCursor(51, y);
    display->setTextColor(RED);
    display->print("CYA");
    display->setTextColor(WHITE);
  } else {
    int x = (time < 10) ? 49 : 45;
    display->setCursor(x, y);
    display->print(time);
    display->print("min");

    // Update tracking for next call
    if (top) currentTimeTop = time;
    else currentTimeBot = time;
    display->setTextColor(WHITE);
  }
}

// Updated Status Logic: Prioritizes upcoming sets starting in <= 15 minutes
void getStageStatus(const Set* schedule, uint16_t currentMins, String& artist, String& timeStr) {
  int i = 0;
  while (schedule[i].artist != NULL) {
    // 1. Check if this specific set is currently performing
    if (currentMins >= schedule[i].startMins && currentMins < schedule[i].endMins) {

      // 2. PRIORITY CHECK: Look at the NEXT artist in the schedule
      if (schedule[i + 1].artist != NULL) {
        int minsUntilNext = schedule[i + 1].startMins - currentMins;
        // Serial.print("Artist: " + String(schedule[i + 1].artist) + " ");
        // Serial.print("Time left: ");
        // Serial.println(minsUntilNext);


        // If the next set starts in 15 minutes or less, prioritize it
        if (minsUntilNext <= 19) {
          // Serial.println("Yes its less than 29 " + String(minsUntilNext));
          artist = String(schedule[i + 1].artist);
          timeStr = String(minsUntilNext);  // Returns minutes for renderTime()
          return;
        }
      }

      // If no upcoming set is within 15 mins, show the current set
      artist = String(schedule[i].artist);
      timeStr = "NOW";
      return;
    }

    // 3. Standard logic for when no set is currently active
    if (currentMins < schedule[i].startMins) {
      artist = String(schedule[i].artist);
      int diff = schedule[i].startMins - currentMins;
      timeStr = String(diff);
      return;
    }
    i++;
  }
  artist = "DONE";
  timeStr = "-1";
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  if (!rtc.begin()) {
    Serial.println("Couldn't find RTC");
    Serial.flush();
    while (1) delay(10);
  }
  // DateTime compileTime = DateTime(F(__DATE__), F(__TIME__));
  // DateTime pacificTime = compileTime - TimeSpan(0, 3, 0, 0);
  // rtc.adjust(pacificTime);

  HUB75_I2S_CFG mxconfig(64, 32, 1, _pins);
  mxconfig.clkphase = false;
  mxconfig.latch_blanking = 1;

  display = new MatrixPanel_I2S_DMA(mxconfig);
  display->begin();
  display->clearScreen();
  display->setFont(&font3pt7b);
  display->setTextSize(1);
  display->setTextColor(WHITE);

  // 1. Render the 64x32 background base
  display->drawRGBBitmap(0, 0, logo_mta_base, 64, 32);

  // 2. Render a 12x12 icon (e.g., 'B') at a specific coordinate
  // Syntax: drawRGBBitmap(x, y, data, width, height)
  display->drawRGBBitmap(2, 2, logo_B, 12, 12);

  // 3. Render another icon (e.g., 'S') next to it
  display->drawRGBBitmap(2, 18, logo_M, 12, 12);
  display->setCursor(15, 10);  // (x,y)
  // display->print("");
  // renderTime(true, 5);
}
void renderClock(DateTime now) {
  // Set color (maybe a different color like Cyan to stand out)
  display->setTextColor(display->color565(0, 255, 255));

  // Create HH:MM string
  char buffer[6];
  sprintf(buffer, "%02d:%02d", now.hour(), now.minute());

  // Positioning:
  // Your display is 64x32.
  // Top row text is at y=10 [cite: 22], bottom row at y=26[cite: 28].
  // y=18 is the vertical center.
  display->fillRect(22, 14, 20, 7, 0);  // Clear middle area
  display->setCursor(22, 18);
  display->print(buffer);
}

void loop() {
  DateTime now = rtc.now();

  // 1. Day Selection [cite: 54, 55, 56, 57]
  const Set** dayStages;
  int effectiveDay = now.dayOfTheWeek();
  if (now.hour() < 7) {
    effectiveDay = (effectiveDay == 0) ? 6 : effectiveDay - 1;
  }

  if (effectiveDay == 6) dayStages = satSchedules;
  else if (effectiveDay == 0) dayStages = sunSchedules;
  else dayStages = stageSchedules;

  uint16_t currentMins = (now.hour() < 7 ? now.hour() + 24 : now.hour()) * 60 + now.minute();

  // 2. Logic for refreshing indices [cite: 62, 63, 64]
  static int lastMinute = -1;
  bool timeChanged = (now.minute() != lastMinute);
  bool stageSwapReady = (millis() - lastUpdate > 10000);

  if (stageSwapReady || timeChanged) {
    if (timeChanged) {
      lastMinute = now.minute();
      // renderClock(now);
    }
    if (stageSwapReady) {
      lastUpdate = millis();
      logoIndex = (logoIndex + 2) % 9;  // Skip by 2 [cite: 65, 66]
    }

    // --- RE-FETCH DATA IMMEDIATELY AFTER INDEX CHANGE ---
    int topStageIdx = logoIndex;
    int botStageIdx = (logoIndex + 1) % 9;
    String topArtist, topStatus, botArtist, botStatus;

    getStageStatus(dayStages[topStageIdx], currentMins, topArtist, topStatus);
    getStageStatus(dayStages[botStageIdx], currentMins, botArtist, botStatus);

    // --- RENDER EVERYTHING IN SYNC ---

    // Logos [cite: 66, 67]
    display->fillRect(2, 2, 12, 12, 0);
    display->drawRGBBitmap(2, 2, logo_allArray[logoIndex], 12, 12);
    display->fillRect(2, 18, 12, 12, 0);
    display->drawRGBBitmap(2, 18, logo_allArray[(logoIndex + 1) % 9], 12, 12);

    // Top Status [cite: 68, 69]
    if (topStatus == "NOW") {
      display->setTextColor(GREEN);
      display->fillRect(44, 5, 17, 6, 0);
      display->setCursor(51, 10);
      display->print("NOW");
      display->setTextColor(WHITE);
    } else {
      renderTime(true, topStatus.toInt());
    }

    // Bottom Status (Fixed Independent Logic) [cite: 70, 71]
    if (botStatus == "NOW") {
      display->setTextColor(GREEN);
      display->fillRect(44, 21, 17, 6, 0);
      display->setCursor(51, 26);
      display->print("NOW");
      display->setTextColor(WHITE);
    } else {
      renderTime(false, botStatus.toInt());
    }

    // Reset scrolling for the NEW names
    isScrollingTop = false;
    isScrollingBot = false;
    lastTopWord = "";
    lastBotWord = "";

    // IMPORTANT: We must also update the scrolling text once immediately
    // to show the new names instead of waiting for the next loop
    updateScrollingText(topArtist, botArtist);
  } else {
    // Regular loop: just update scrolling and fetch data for background tasks
    String topArtist, topStatus, botArtist, botStatus;
    getStageStatus(dayStages[logoIndex], currentMins, topArtist, topStatus);
    getStageStatus(dayStages[(logoIndex + 1) % 9], currentMins, botArtist, botStatus);
    updateScrollingText(topArtist, botArtist);
  }
}