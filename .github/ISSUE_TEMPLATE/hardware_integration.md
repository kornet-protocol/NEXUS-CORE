---
name: "[Hardware] ZKP Sensor Integration"
about: Hardware module integration for fake resistance (Root of Trust)
title: "[HW] ATECC608A chip integration in C++ node"
labels: hardware, help wanted, good first issue
assignees: ''

---

### Current Problem
In `iot-depin-network/arduino_air_sensor.cpp`, software SHA-256 (hardcoded secret) is used, vulnerable to key extraction and hardware-level Sybil attacks.

### Required Solution
1. Integrate CryptoAuthLib.
2. Initialize I2C connection with ATECC608A chip.
3. Implement raw sensor data signing via Ed25519 curve (Secure Enclave).

**Reward (Karma):** Highest priority. You are building the system's hardware armor.

### Acceptance Criteria
- [ ] ATECC608A chip initializes via I2C
- [ ] Raw sensor data hashed with SHA256 on device
- [ ] Hash signed with private key stored in Secure Enclave
- [ ] Signature verified on validator side (`infrastructure_scan.py`)