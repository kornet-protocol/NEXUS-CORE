# Guerrilla Manufacturing: Partisan Production

## Philosophy

Just as Satoshi didn't ask the Fed for permission to launch Bitcoin, we don't ask corporations for permission to manufacture hardware. Build one factory in Asia — it gets shut down day one. So we create **Distributed Manufacturing** (Micro-Factories): 50,000 garages worldwide that cannot be raided simultaneously.

## Decentralized Assembly Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PURGE CONTRACT (Treasury)                      │
│              [USDC/USDT from burned meme coins]                   │
└───────────────────────────────┬─────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  STEALTH LOGISTICS     │
                    │  (Wholesale Procurement)│
                    │  • ATECC608A ($1/chip) │
                    │  • Lenses, batteries   │
                    │  • PCB, 3D cases       │
                    └───────────┬────────────┘
                                 │
                    Declared as:
                    "Educational STEM kits"
                                 │
                                 ▼
         ┌────────────────────────────────────────────────┐
         │     ASSEMBLER GUILDS (Proof-of-Assembly)       │
         │  Garages, hackerspaces, school labs            │
         │                                                │
         │  1. 3D-print case from open schematic          │
         │  2. Solder board (KiCad schema in repo)        │
         │  3. Flash NEXUS Core (secure boot)             │
         │  4. Activate in mesh network (LoRa handshake)  │
         └───────────────────┬────────────────────────────┘
                             │
                             ▼
               ┌───────────────────────────┐
               │  KARMA + STABLE REWARD    │
               │  Assembled camera → +R(t) │
               │  Activated → +USDC        │
               └───────────────────────────┘
```

## Implementation Stages

### 1. Raw Materials Procurement (PurgeContract Funds)
- Smart contract generates stablecoins via meme-coin swap on DEX
- Anonymous wholesale component purchase from distributors (LCSC, Mouser, Digi-Key)
- Batches fragmented to avoid attention

### 2. Logistics Stealth
| Package | Customs Declaration | Actual Contents |
|---------|---------------------|-----------------|
| Box A | "DIY Electronics Learning Kit" | PCB + ATECC608A + lenses |
| Box B | "3D Printing Filament Sample" | Camera cases |
| Box C | "Robotics Competition Parts" | Batteries + LoRa antennas |

No box contains ready-made "spy equipment." Only components for educational kits.

### 3. Assembler Guilds (Proof-of-Assembly)
In `app-frontend/ui` a quest appears:
- **Task:** "Assemble NEXUS Eye"
- **Blueprint:** `iot-depin-network/arduino_air_sensor.cpp` + KiCad files in repo
- **Verification:** Camera must sign challenge message with ATECC608A private key
- **Reward:** karma boost + treasury stablecoin share

### 4. Proof-of-Assembly Protocol
```python
class AssemblyGuild:
    def verify_assembly(self, device_id, signature, public_key_attestation):
        # 1. Verify chip is genuine ATECC608A (secure enclave challenge)
        if not self.attest_chip(device_id, public_key_attestation):
            return "REJECTED: Fake silicon"
        # 2. Verify board soldered to spec (BOM hash match)
        if not self.verify_bom_hash(device_id):
            return "REJECTED: Wrong components"
        # 3. Activate in mesh network
        self.activate_device(device_id, signature)
        return "ACCEPTED: Device online. Assembler rewarded."
```

## Why This Cannot Be Stopped

1. **No central factory** — nothing to bomb or arrest
2. **50,000 garages** — coordinated raid physically impossible
3. **Legal wrapper** — components = "educational kits"
4. **Army of "Kulibins"** — teens and geeks manufacture the system's eyes
5. **Self-funding** — PurgeContract pays for materials with meme coins

## Codebase Integration

| Component | File | Role |
|-----------|------|------|
| Treasury | `smart-contracts/PurgeContract.sol` | USDC generation |
| Schematics | `iot-depin-network/arduino_air_sensor.cpp` | Board blueprint |
| Mesh | `iot-depin-network/lora_mesh_node.cpp` | Device activation |
| Verification | `core-engine/genesis_protocol.py` | Hardware Root of Trust |
| Guild | `core-engine/proof_of_assembly.py` | Proof-of-Assembly logic |
| UI Quest | `app-frontend/ui/index.html` | Assembler interface |

## Risks & Mitigation

| Risk | Mitigation |
|------|------------|
| Customs blocks shipment | Fragment into micro-batches (< 10 boxes) |
| Chip counterfeiting | Attestation via ATECC608A secure enclave |
| Assembler doesn't activate device | Reward only after mesh activation |
| Corporate lawsuit | GPLv3 — schematics open, assembly legal |