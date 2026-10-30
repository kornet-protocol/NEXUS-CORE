// =====================================================================
// NEXUS KORNET ENGINE: Arduino Air Sensor Node
// Measures CO2, PM2.5, temperature and signs data with hardware key
// =====================================================================

#include <Arduino.h>
#include <SparkFun_ATECCX08a_Arduino_Library.h>
#include <Wire.h>
#include <cstring>

struct TelemetryPacket {
  uint32_t timestamp;
  float co2;
  float pm25;
  float temperature;
  uint8_t signature[64];
};

constexpr uint8_t CO2_ADC_PIN = 34;
constexpr uint8_t PM25_ADC_PIN = 35;
constexpr uint8_t TEMPERATURE_ADC_PIN = 32;

class AirSensorNode {
private:
  ATECCX08A crypto;
  TelemetryPacket packet;

public:
  bool begin() {
    Wire.begin();
    return crypto.begin();
  }

  TelemetryPacket readAndSign() {
    packet.timestamp = millis();
    packet.co2 = analogRead(CO2_ADC_PIN) * (5.0 / 4095.0) * 1000.0;
    packet.pm25 = analogRead(PM25_ADC_PIN) * (5.0 / 4095.0) * 500.0;
    packet.temperature = analogRead(TEMPERATURE_ADC_PIN) * (5.0 / 4095.0) * 100.0 - 50.0;

    uint8_t hash[32];
    if (!crypto.sha256(reinterpret_cast<uint8_t*>(&packet), sizeof(packet) - sizeof(packet.signature), hash)) {
      memset(packet.signature, 0, sizeof(packet.signature));
      return packet;
    }
    if (!crypto.createSignature(hash)) {
      memset(packet.signature, 0, sizeof(packet.signature));
      return packet;
    }
    memcpy(packet.signature, crypto.signature, sizeof(packet.signature));

    return packet;
  }

};