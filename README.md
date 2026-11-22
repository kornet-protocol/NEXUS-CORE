<p align="center">
  <img src="assets/logo.svg" alt="NEXUS-CORE Logo: faceted green sprout inside a symmetrical geodesic cybernetic dome" width="128" height="128" />
</p>

# NEXUS: The KORNET Core Protocol

**NEXUS** is an open-source, decentralized operating system for planetary repair, resource balancing, and the emergence of a post-scarcity civilization. We replace political bureaucracy with cybernetic logistics (**OGAS 2.0**) and speculative capitalism with a **Phase Economy** where value derives solely from verified physical creation.

> **The Core Insight:** You cannot build a sane civilization with damaged minds in a scarcity trap. NEXUS simultaneously solves the *material crisis* (energy, food, shelter) and the *psychological crisis* (trauma, fragmentation, survival anxiety) through a unified protocol of automated abundance and ambidextrous education.

---

## 🎯 The Vision: Why We Exist

We are building a global P2P infrastructure where **creation** — saving lives, restoring ecosystems, achieving scientific breakthroughs, building infrastructure, transmitting knowledge, raising children — becomes the **sole generator of value**. NEXUS connects:

| Layer | Technology | Purpose |
|-------|------------|---------|
| **DePIN** | Environmental sensors, energy grids, manufacturing nodes | Measure physical reality, not human behavior |
| **AI Oracle** | Federated neural governance (PROMT, OBRAZ, OGAS, STRAZH) | Optimize production, education, logistics, infrastructure |
| **ZK-Privacy** | zk-SNARKs (arkworks/Groth16/BN254) | Prove deeds without exposing identity |
| **Status Escrow** | Cross-domain stasis with slashing | Protect multi-year R&D from reputational decay |

---

## 📊 v0.4 Status: Fail-Closed Prototype

| Layer | Status | Key Modules |
|-------|--------|-------------|
| **Core Engine (Python + Rust)** | ✅ Tested | Genesis Protocol, Reputation Decay, Entropy Filter, **Graceful Degradation v0.4 (Soft Kalman + Synthetic State)**, **Status Stasis**, Resource Balancer (Leontief), Proof-of-Assembly, Skill Tree |
| **Identity & ZKP (Rust/arkworks)** | 🏗️ Scaffold | Web of Trust (Sybil resistance), ZK-SNARK circuit — requires trusted setup ceremony |
| **Validators (Python)** | ✅ Tested | Dispute Arbiter (7-day challenge), Eco-Bio Vision, Infrastructure Scan, Science Peer Review, Social Awakening |
| **Smart Contracts (Solidity)** | ✅ Compiled | SoulboundToken (on-chain decay), DEX Adapters — *PurgeContract archived* |
| **IoT / DePIN (C++ / Go / ESP32)** | ✅ Compiled | Air/Water/Soil firmware (ATECC608A-signed), LoRa Mesh (SX1262), Telemetry Aggregator (Go HTTP) |
| **Hardware Spec** | ✅ Documented | `docs/hardware/BOM_oasis_seed.md` — $1,500 Seed Node with 3× TMR redundancy |
| **Documentation** | ✅ Complete | Mathematical models, AI Core, Osmotic Membrane, Schools of Universalists, Guerrilla Manufacturing, Ambidexter Academy |

**Production requires:** audited ZK verifiers, hardware-key registry (HSM/KMS), audited DEX adapter, formal verification of consensus.

---

## ⚙️ Core Architecture: The 4 Vectors of Resilience

### 1. Proof-of-Good & Environmental Proof-of-Impact
Physical actions (planting trees, building hospitals, cleaning rivers, restoring soil) are verified via **cryptographic signatures from IoT environmental sensors** (air, water, soil, energy) using **ATECC608A Secure Element**. This prevents Deepfake/Generative AI spoofing of sensor data.  
**No human biometrics. No cameras on people. Ever.**

### 2. Dynamic Reputation Decay R(t) — Thermodynamics of Status
Status is a **Soulbound Token (SBT)** — non-transferable, non-inheritable, non-speculative. It follows the thermodynamic law:

```
dR/dt = UsefulContribution(t) − λ × R(t)
```

- **Category-specific λ**: life_saved (0.0001), teaching (0.0004), art (0.003), sports (0.004)
- **Anti-gerontocracy**: reputation decays, clearing space for new minds
- **High-Water Mark (HWM)**: immutable peak reputation ledger — never decays, never deleted

### 3. ZK-Privacy (Zero-Knowledge Proofs)
We do not build a Panopticon. Users prove actions and identity via **zk-SNARKs**. The system verifies the deed without revealing GPS coordinates, real name, or face.

### 4. Mesh-Network Autonomy
Protocol survives internet shutdowns. IoT sensors and Oasis nodes communicate via **LoRaWAN (SX1262) / Libp2p / Bluetooth Mesh** — physical survival floor remains operational offline.

---

## 🧬 Systemic Extensions (v0.4 Canonical)

### Graceful Degradation v0.4 — Soft Kalman Weights + Synthetic State
`core-engine/graceful_degradation.py` implements **Stafford Beer's Viable System Model** with **continuous trust weights w ∈ [0,1]**:

- **Innovation-based anomaly scoring**: normalized Kalman residual → exponential weight decay `w = exp(−γ·(score−2))` for 2σ < score ≤ 5σ
- **SyntheticStateProvider**: 14-day hourly diurnal baselines per metric (temp, humidity, pH, PAR) — deterministic fallback when sensor cluster degrades
- **Zero DoS**: system **never shuts down** — gracefully blends sensor readings with synthetic extrapolation
- **MaintenanceOrder queue**: async work orders for physical calibration emitted when cluster weight W̄ < 0.3

### Status Stasis & Research Escrow — Protecting Long-Horizon R&D
`core-engine/status_stasis.py` implements **Status Escrow** for multi-year scientific/engineering cycles:

- **Cross-Domain Gini Anti-Collusion**: minimum 3 independent domains (Biology + Energy + Hardware); Gini threshold 0.65
- **Peer Stake Collusion Penalties**: backers stake R(t) + HWM; fraud triggers progressive slashing `multiplier = 1 + 0.5×CollusionIndex`
- **Dual-Layer Slashing**: Lead HWM cut (2×β), Peer HWM cut (1×β), Stake loss multiplied by collusion index
- **Hard Cap**: 24 months maximum; no extension without Milestone Proof audit

### Entropy Filter — Thermodynamics of Status
`core-engine/entropy_filter.py` — status as kinetic energy, not potential:
- Category-specific decay rates with half-life calculations
- Gerontocracy risk detection (inactivity > threshold years)
- Creative/Sports/Utilitarian balance tracking

### Osmotic Membrane — Legacy Integration
`docs/osmotic_membrane.md` — Oases as cells with semi-permeable membranes:
- **Export**: energy, roboticized production, open patents at pure cost (50–80% below market)
- **Import**: raw materials, expertise (transition phase only)
- **Phase Transition**: Islands → Oases → Clusters → Core Activation

### AI Core — Neural Governance (Federated)
`docs/ai_core.md` — 4 federated neural networks with ZK-proven training:
- **PROMT** (Production Optimizer) — Leontief-constrained PID setpoints
- **OBRAZ** (Education Neural Net) — ambidexterity-based personalized trajectories
- **OGAS** (Resource Balancer) — GPU-accelerated simplex for global distribution
- **STRAZH** (Infrastructure Sentinel) — Isolation Forest + Cox survival analysis

### Schools of Universalists — Education for Freedom
`docs/schools_of_universalists.md` + `validators/social_awakening.py`:
- **No grades, no standardized tests** — Skill Graph + Karma Index + Creativity Score
- **3 Phases**: Seed (0–12), Forge (12–18), Nexus Academy (18+)
- **Ambidexterity Foundation**: rhythmic gymnastics 2×/day, synchronized left/right hemisphere development
- **Goal**: humans who fix engines, write symphonies, program neural nets, grow gardens

### Guerrilla Manufacturing — Decentralized Micro-Factories
`docs/guerilla_manufacturing.md` + `core-engine/proof_of_assembly.py`:
- **50,000 garages worldwide** — no central factory to bomb/arrest
- **Stealth logistics**: components declared as "Educational STEM kits"
- **Proof-of-Assembly**: ATECC608A attestation + BOM hash match + mesh handshake → assembler earns Karma + stable
- **Self-funding**: Treasury pays for components

### Ambidexter Academy — RPG IRL Skill Tree
`docs/ambidexter_academy.md` + `core-engine/skill_tree.py`:
- **Skill Branches**: Bio-Engineering, Quantum Logistics, Neuro-Architecture (Left) / Music, Sculpture, Poetry, Empathy (Right)
- **Synthesis Multiplier ×5**: cross-hemisphere links unlock exponential status growth
- **Master-Teacher Royalties**: 10% of student's lifetime status — teaching geniuses becomes most profitable act on Earth

---

## 💰 Funding Paradigm: Pure Donations & The Hall of First Awakenings

### No Memecoins. No VCs. No Speculation.
We **completely reject** speculative tokenomics, "osmotic airdrops" of trash tokens, and venture capital capture. The PurgeContract mechanism has been **archived** as a historical experiment — it introduced perverse incentives contrary to our values.

### Pure Support
Development is funded **entirely through direct, voluntary donations**:

**Bitcoin (BTC):** `bc1qlg5pxgqjyns59ma9hxter8vc2znh5tqtu4y777`

### The Hall of First Awakenings (Immortalization)
Those who support the protocol in its earliest, darkest hours — before mass adoption, before institutional validation — are not "investors seeking ROI." They are the **First Awakened**.

Their names, digital contributions, and interactive AI avatars will be **permanently enshrined in the Historical Centers of the First Oases**, preserving their memory as the pioneers who broke the matrix and birthed a new civilization.

---

## 📁 Repository Map

```
NEXUS-CORE/
├── core-engine/           # Genesis Protocol, Reputation Decay, Entropy Filter,
│                          # Graceful Degradation v0.4, Status Stasis, Resource Balancer (Rust),
│                          # Proof-of-Assembly, Skill Tree, Config, Persistence, Logging, Serve
├── identity-zkp/          # Web of Trust (Python) + ZK-SNARK Circuit (Rust/arkworks)
├── validators/            # Dispute Arbiter, Eco-Bio Vision, Infrastructure Scan,
│                          # Science Peer Review, Social Awakening
├── smart-contracts/       # SoulboundToken, FoundingPurger SBT, DEX Adapters
├── iot-depin-network/     # Firmware (air/water/soil sensors, LoRa mesh), Aggregator (Go)
├── docs/                  # Mathematical models, AI Core, Osmotic Membrane,
│                          # Schools of Universalists, Guerrilla Manufacturing,
│                          # Ambidexter Academy, Phase Decay Math, Threat Model, Audit Checklist
│   └── hardware/
│       └── BOM_oasis_seed.md  # $1,500 Seed Node spec with 3× TMR
├── scripts/               # Deployment automation
├── tests/                 # 49 unit tests: security boundaries, event attestation,
│                          # status stasis (14), graceful degradation (18)
├── app-frontend/          # UI (Skill Tree, Guilds), AR Engine
└── assets/                # Logo, branding
```

---

## 🤝 Join the Architecture

We need **Rust/Go engineers**, **cryptographers**, **AI vision specialists**, **hardware makers**, **educators**, **farmers**, **medics**, **builders**.

Read `CONTRIBUTING.md` and choose your vector.

> *The future is not a place we are going to, but one we are creating.*

---

## 💎 Support the Architecture

This project is built by free people, for free people. We do not have venture investors because we will not sell your data or your future. If you believe in the NEXUS-KORNET Protocol, you can support the core development and hardware deployment.

**Bitcoin (BTC):** `bc1qlg5pxgqjyns59ma9hxter8vc2znh5tqtu4y777`

> *"There is only one constant, and that is change."*