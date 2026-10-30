---
name: "[Mesh] LoRa/Libp2p P2P Networking"
about: Mesh network implementation for internet-free survival
title: "[Mesh] Gossip protocol implementation on Libp2p"
labels: networking, mesh, p2p, help wanted, good first issue
assignees: ''

---

### Context
Vector D (Censorship): if internet is shut down, Oases and sensors must continue exchanging telemetry via LoRaWAN / Libp2p / Bluetooth Mesh.

### Current Problem
`iot-depin-network/lora_mesh_node.cpp` only handles send/receive packets. Missing:
- Multi-hop packet routing (neighbor-to-neighbor)
- Telemetry aggregation and compression
- State sync on connectivity restoration

### Required Solution
1. Write gossip protocol on Libp2p (Go or Rust).
2. Implement store-and-forward for LoRa packets.
3. Add mutual node authentication via Ed25519.

**Reward (Karma):** You build the nervous system that doesn't depend on the internet.

### Acceptance Criteria
- [ ] Two LoRa nodes exchange data multi-hop (3+ hops)
- [ ] Packets delivered at 50% packet loss
- [ ] Node authentication via Ed25519
- [ ] Tests on 10+ nodes in simulation