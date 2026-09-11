// =====================================================================
// NEXUS KORNET ENGINE: LoRa Mesh Node
// P2P telemetry relay without internet dependency
// =====================================================================

#include <LoRa.h>
#include <Arduino.h>

class LoRaMeshNode {
private:
  String node_id;
  int ss;
  int dio0;
  int rst;

public:
  LoRaMeshNode(String id, int ss_pin, int dio0_pin, int rst_pin)
    : node_id(id), ss(ss_pin), dio0(dio0_pin), rst(rst_pin) {}

  bool begin(long frequency = 433E6) {
    LoRa.setPins(ss, dio0, rst);
    return LoRa.begin(frequency);
  }

  void broadcast_telemetry(String payload) {
    LoRa.beginPacket();
    LoRa.print(node_id + ":" + payload);
    LoRa.endPacket();
  }

  String receive_packet() {
    int packet_size = LoRa.parsePacket();
    if (packet_size) {
      String incoming = "";
      while (LoRa.available()) {
        incoming += (char)LoRa.read();
      }
      return incoming;
    }
    return "";
  }
};