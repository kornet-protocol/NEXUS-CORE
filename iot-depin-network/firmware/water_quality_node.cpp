// =====================================================================
// NEXUS KORNET ENGINE: Water Quality Node
// Monitors pH, turbidity, dissolved oxygen
// =====================================================================

#include <Arduino.h>
#include <SparkFun_ATECCX08a_Arduino_Library.h>
#include <Wire.h>
#include <cstring>

struct WaterTelemetry {
  uint32_t timestamp;
  float ph;
  float turbidity;
  float dissolved_oxygen;
  uint8_t signature[64];
};

class WaterQualityNode {
private:
  ATECCX08A crypto;

public:
  bool begin() {
    Wire.begin();
    return crypto.begin();
  }

  WaterTelemetry readSensors() {
    WaterTelemetry wt;
    wt.timestamp = millis();
    wt.ph = readPH();
    wt.turbidity = readTurbidity();
    wt.dissolved_oxygen = readDO();
    uint8_t hash[32];
    if (!crypto.sha256(reinterpret_cast<uint8_t*>(&wt), sizeof(wt) - sizeof(wt.signature), hash) ||
        !crypto.createSignature(hash)) {
      memset(wt.signature, 0, sizeof(wt.signature));
      return wt;
    }
    memcpy(wt.signature, crypto.signature, sizeof(wt.signature));
    return wt;
  }

private:
  float readPH() { return 7.0; }
  float readTurbidity() { return 0.5; }
  float readDO() { return 8.0; }
};