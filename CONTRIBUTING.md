# Contributing to NEXUS

## Code of Conduct
Be respectful. Be rigorous. Be kind.

## How to Contribute
1. Fork the repository
2. Create a feature branch
3. Write tests for your changes
4. Submit a pull request

## Vector Assignments

| Vector | Threat | Module |
|--------|--------|--------|
| **A** | Sybil / Bot farms | `identity-zkp/web_of_trust.py`, `zkp_action_verifier.rs` |
| **B** | Oracle / Deepfake | `validators/infrastructure_scan.py`, `dispute_arbiter.py` |
| **C** | Panopticon | `identity-zkp/zkp_action_verifier.rs`, `genesis_protocol.py` |
| **D** | Internet shutdown | `iot-depin-network/lora_mesh_node.cpp`, `telemetry_aggregator.go` |
| **E** | Sensor failure | `core-engine/graceful_degradation.py` (Kalman + Island Mode) |
| **F** | Gerontocracy | `core-engine/entropy_filter.py` (dR/dt thermodynamics) |
| **G** | Legacy integration | `docs/osmotic_membrane.md` (Trade & Treasury Gateway) |
| **H** | AI governance | `docs/ai_core.md` (Production Optimizer, Education Net, Sentinel) |
| **I** | Education | `docs/schools_of_universalists.md` (Ambidexterity + Universalists) |
| **J** | Funding | `smart-contracts/PurgeContract.sol`, `FoundingPurger.sol` |
| **K** | Hardware production | `docs/guerilla_manufacturing.md`, `core-engine/proof_of_assembly.py` |
| **L** | Skill synthesis | `docs/ambidexter_academy.md`, `core-engine/skill_tree.py` |

## Core-Engine Modules

| Module | Responsibility |
|--------|---------------|
| `config.py` | Single source of truth for weights, lambdas, thresholds |
| `genesis_protocol.py` | ZKP-enabled verification gateway + Hardware Root of Trust |
| `reputation_decay.py` | R_i(t) decay model with anti-collusion Gini damping |
| `entropy_filter.py` | Thermodynamics of status (dR/dt) + gerontocracy guard |
| `graceful_degradation.py` | VSM + Kalman filter + Island Mode autarky |
| `resource_balancer.rs` | Leontief Input-Output matrix + simplex optimization |
| `proof_of_assembly.py` | Proof-of-Assembly for micro-factory guilds |
| `skill_tree.py` | RPG IRL skill tree + ambidexterity multiplier |

## Build Status
- Python: `make test` or `python3 -m py_compile <file>`
- Rust: `cargo check`
- C++: `g++ -std=c++17 -fsyntax-only <file>`
- Solidity: `forge build` (when Foundry is installed)
- Go: `go build ./...`

## Prerequisites
- Python 3.10+
- Rust 1.70+
- Go 1.22+
- PlatformIO (for Arduino C++)
- Foundry (for Solidity)
