# 🌍 NEXUS: The KORNET Core Protocol

**NEXUS** is an open-source, decentralized operating system for planetary repair, resource balancing, and gamified volunteering. We replace political bureaucracy with cybernetic logistics (OGAS 2.0) and speculative capitalism with a Phase Economy.

## 🎯 The Vision
We are building a global P2P infrastructure where creation (saving lives, ecological restoration, scientific breakthroughs) becomes the sole generator of value. Nexus connects DePIN (Decentralized Physical Infrastructure), AI Oracle Verification, and Zero-Knowledge Proofs to create a trustless ecosystem for human evolution.

## v0.2 Status

The repository currently provides a stable, fail-closed prototype. Python, Rust,
Go, Solidity, and ESP32 firmware checks are wired into the development workflow.
Unconfigured ZK, hardware-attestation, and DEX adapters reject requests instead
of accepting unverifiable data or silently discarding funds. Production use still
requires audited cryptographic verifiers, a hardware-key registry, and an audited
DEX adapter.

## ⚙️ Core Architecture (The 4 Vectors of Resilience)

1. **Proof-of-Good & Hardware Root of Trust:** Physical actions (planting trees, building infrastructure) are verified not just by AI, but via cryptographic signatures integrated directly into IoT sensor microchips to prevent Deepfake/Generative AI attacks.
2. **Dynamic Reputation Decay ($R(t)$):** Status is a Soulbound Token (SBT) that cannot be bought or transferred. It exponentially decays over time if a user stops contributing, eliminating the risk of "digital oligarchy."
3. **ZK-Privacy (Zero-Knowledge Proofs):** We do not build a Panopticon. Users prove their actions and identity using zk-SNARKs. The system verifies the good deed without revealing the user's GPS coordinates, real name, or face.
4. **Mesh-Network Autonomy:** The protocol is designed to survive internet shutdowns. IoT sensors and Oasis nodes communicate via LoRaWAN/Libp2p, ensuring the physical survival floor remains operational offline.

## 🧬 Systemic Extensions (Day 0+)

### Graceful Degradation (Viable System Model)
Every local node must survive total isolation. `core-engine/graceful_degradation.py` implements:
- **Kalman Filter** for anomaly detection in sensor streams
- **Historical baselines** for deterministic extrapolation during adversarial attacks
- **Island Mode**: local clusters switch to autonomous Leontief matrix + Raft/Tendermint consensus when global network fails

### Entropy Filter (Thermodynamics of Status)
Status is kinetic energy, not potential. `core-engine/entropy_filter.py` implements:
- **dR/dt = UsefulContribution(t) - λ * R(t)**
- Category-specific decay rates (life_saved: 0.0001, art_created: 0.003, sports: 0.004)
- **Anti-gerontocracy mechanism**: reputations decay, clearing space for new minds
- **Creative/Sports/Utilitarian balance** tracking

### Osmotic Membrane (Legacy Integration)
Oases act as cells with semi-permeable membranes. `docs/osmotic_membrane.md` describes:
- **Trade & Treasury Gateway**: export cheap energy/robotics, import raw materials
- **Economic dumping**: 50-80% below market price due to elimination of speculative margins
- **Phase transition**: external enterprises self-integrate into KORNET to access stable logistics and clean energy

### AI Core (Neural Governance)
`docs/ai_core.md` describes 4 federated neural networks:
- **Production Optimizer**: maximizes output, minimizes input via Leontief constraints
- **Education Neural Net**: personalized learning trajectories based on ambidexterity profiles
- **Resource Balancer**: GPU-accelerated simplex optimization for global resource distribution
- **Infrastructure Sentinel**: anomaly detection + predictive maintenance + threat assessment

### Schools of Universalists
`docs/schools_of_universalists.md` — education system for post-scarcity minds:
- **Ambidexterity focus**: synchronized left/right hemisphere development
- **No grades, no standardized tests**: Skill Graph + Karma Index + Creativity Score
- **3 phases**: Seed (0-12), Forge (12-18), Nexus Academy (18+)
- Goal: humans who can fix engines, write symphonies, program neural nets, and grow gardens

### Guerrilla Manufacturing (Decentralized Micro-Factories)
No central factory to bomb or arrest. `docs/guerilla_manufacturing.md` + `core-engine/proof_of_assembly.py`:
- **Stealth logistics**: components declared as "Educational STEM kits"
- **Assembly Guilds**: 50,000 garages worldwide solder NEXUS hardware from open schematics
- **Proof-of-Assembly**: device attests ATECC608A chip, signs mesh handshake, assembler earns Karma + stable
- Result: an army of "kulibins" manufacturing the eyes and ears of the system

### Ambidexter Academy (RPG IRL Skill Tree)
`docs/ambidexter_academy.md` + `core-engine/skill_tree.py`:
- **Skill Tree**: branches are Bio-Engineering, Quantum Logistics, Neuro-Architecture — not "Math" or "Lit"
- **Synthesis Multiplier**: single-skill grinding grows status slowly; cross-hemisphere synthesis makes R(t) skyrocket
- **Master-Teacher Royalties**: mentors earn 10% of student's lifetime status — teaching geniuses becomes the most profitable act on Earth

## 🚀 Trojan Airdrop (Funding Mechanism)
We don't ask VCs for money. We use the degeneracy of the old system against itself:
users burn their worthless meme coins through our **Purge Contract** and receive **Founding Purger SBT** — a soulbound badge that grants priority access to Oasis infrastructure.

## 📁 Repository Map
- `/core-engine` - Genesis Protocol, Reputation Decay, Entropy Filter, Graceful Degradation, Resource Balancer, Proof-of-Assembly, Skill Tree, config
- `/identity-zkp` - Sybil-resistance and privacy layers
- `/validators` - AI and peer-review Oracle mechanisms
- `/smart-contracts` - Purge Contract + Founding Purger SBT
- `/iot-depin-network` - Firmware for offline Mesh grids
- `/docs` - Mathematical models, AI Core, Osmotic Membrane, Schools, Guerrilla Manufacturing, Ambidexter Academy
- `/scripts` - Deployment automation

## 🤝 Join the Architecture
We need Rust/Go engineers, cryptographers, AI vision specialists, hardware makers, and educators. 
Read `CONTRIBUTING.md` and choose your vector.

*The future is not a place we are going to, but one we are creating.*
