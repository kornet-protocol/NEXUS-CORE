# 📦 NEXUS-CORE Hardware Spec: Oasis Seed Node (v0.4)
## Autonomous Biosphere & Workshop Automation Unit
**Target Budget:** ≤ $1,500 USD  
**Capacity:** Micro-Oasis (10–30 people, 100m² greenhouse + garage fablab)  
**Philosophy:** Commodity Hardware + Algorithmic Fault Tolerance (TMR) + Hardware Root of Trust

---

### 1. Compute & Mesh Gateway Core (~$140)
- **Primary Controller (SBC):** Orange Pi 5 (8GB) or Raspberry Pi 4 Model B (Runs Core Engine, SQLite WAL, Leontief balancer, HTTP gateway). ~$75
- **Local Storage:** 128GB High-Endurance MicroSD (SanDisk Extreme / Samsung PRO Endurance) for SQLite WAL resilience. ~$20
- **Mesh Base Station:** ESP32-WROOM-32U + Semtech SX1262 LoRa module (868/915 MHz, +22dBm) + 5dBi Omni-directional fiberglass antenna. ~$25
- **Power Management (SBC):** 12V to 5V 5A Step-down DC-DC buck converter (Mean Well or LM2596 HV) with low ripple. ~$20

### 2. Cryptographic Security Layer (~$15)
- **Hardware Root of Trust:** Microchip ATECC608A-TNGTLS / ATECC608B (SOIC-8 breakout via I2C). 
  - *Function:* Cryptographic signing of telemetry frames and Proof-of-Assembly handshake.
  - *Unit Cost:* ~$1.20/chip. 5 units for cluster nodes = ~$6.
- **I2C Bus Isolator & Pull-ups:** PCA9306 level translator + I2C noise filter for long wire runs. ~$9

### 3. Greenhouse Environmental Sensing Cluster (TMR Redundancy) (~$165)
*All critical metrics utilize Triple Modular Redundancy (TMR: 3 sensors per vector, median filtering).*
- **Air Temperature & Humidity (3x):** Bosch BME280 (I2C/SPI) sealed in radiation-shielded gills. ~$12 total ($4/ea)
- **Soil Moisture & Temp (3x):** Capacitive Soil Moisture Sensor v2.0 (Corrosion-resistant, analog/RS485) + DS18B20 stainless waterproof thermal probes. ~$18 total
- **Water Quality Loop (2x):** Industrial-grade Analog pH Sensor kit (BNC probe) + Analog TDS (Total Dissolved Solids) sensor. ~$45 total
- **Solar Irradiance / Photosynthesis (PAR) (2x):** BH1750 ambient light lux sensors + TSL2591 high dynamic range. ~$10 total
- **CO2 & Air Composition (1x):** Sensirion SCD30 (True NDIR CO2, temp, RH) for metabolic respiration loop. ~$45
- **Water Level & Flow (2x):** Ultrasonic JSN-SR04T waterproof distance sensor (tank volume) + Hall effect flow meter. ~$35 total

### 4. Actuation, Relays & Life-Support Control (~$180)
- **Microcontroller Actuators:** 2x ESP32 NodeMCU dev boards (Optocoupler-isolated execution). ~$10 total
- **Relay Matrix:** 16-Channel 12V Relay Module with Optocoupler isolation (Drives solenoid irrigation valves, ventilation fans, peristaltic nutrient pumps, grow lights). ~$25
- **Irrigation Solenoids:** 4x 12V DC 1/2" Normally Closed Food-Grade Solenoid Valves. ~$40 total
- **Nutrient Dosing:** 3x 12V Peristaltic Dosing Pumps (Automated N-P-K & pH balancing). ~$45 total
- **Ventilation Actuation:** 2x 12V Linear Actuators (stroke 150mm) for automated greenhouse roof vents. ~$60 total

### 5. Off-Grid Power Subsystem (12V DC Native) (~$720)
- **Solar PV Generation:** 2x 200W Monocrystalline Solar Panels (400W total array). ~$260 total
- **Charge Controller:** 30A MPPT Solar Charge Controller (EPEVER Tracer-AN or Victron SmartSolar) with RS485 telemetry output. ~$120
- **Energy Storage:** 12.8V 100Ah (1.28 kWh) LiFePO4 (LFP) Battery with built-in Smart BMS (Bluetooth/UART telemetry: cycles, cell balance, SoC). ~$300
- **Protection & Cabling:** DC circuit breakers (40A, 20A), solar MC4 cables, fuses, and waterproof junction box. ~$40

### 6. Local Workshop (Garage FabLab) Tooling (~$280)
- **Digital Fabrication Workhorse:** Open-source 3D Printer (Ender-3 V3 SE / Elegoo Neptune 4) for printing sensor enclosures, replacement pipe fittings, and bracketry. ~$200
- **Soldering & Flashing Station:** Pinecil / TS100 portable smart soldering iron + ESP32 flashing jig + USB-UART bridge. ~$50
- **Diagnostic Meter:** Aneng AN8008 True-RMS digital multimeter + logic analyzer clone (8-channel 24MHz) for I2C debugging. ~$30

---

### Grand Total BOM Cost: ~$1,500 USD

### 7. Triple Modular Redundancy (TMR) Software Invariant
Include an architecture section explaining how `core-engine/graceful_degradation.py` and `SyntheticStateProvider` consume these 3x sensor clusters:
- If 1 sensor drifts beyond 2σ (e.g. heated with lighter or corroded) → Soft weight $w \to 0$, Median filter ignores outlier.
- If 2 sensors fail → Cluster switches to 1 sensor + $X_{\text{synthetic}}$ blend.
- If 3 sensors fail → Cluster runs on 100% $X_{\text{synthetic}}$ diurnal profile + emits `MaintenanceOrder`.