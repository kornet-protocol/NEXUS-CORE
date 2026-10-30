# THREAT MODEL — NEXUS-CORE v0.2
## Security boundaries and assumed trust

### Trusted Parties
- **Genesis Protocol operator**: Can mint status, set consensus thresholds
- **DEX adapter operator**: Can update adapter address (multisig only)
- **Hardware manufacturers**: ATECC608A supply chain integrity
- **ZK trusted setup participants**: Powers of Tau ceremony contributors

### Untrusted Parties
- **End users**: Can submit actions, challenge decisions
- **Validators**: Can endorse actions, open disputes
- **IoT node operators**: Can submit telemetry, may be compromised
- **Smart contract interactions**: External tokens, DEX protocols

### Critical Assets
1. User reputation (SBT) — cannot be transferred, can decay
2. Treasury funds (USDC/USDT) — multisig controlled
3. ZK verification keys — must not be updated without ceremony
4. Hardware root of trust keys — must be provisioned in secure element

### Threat Scenarios

| Threat | Impact | Mitigation |
|--------|--------|------------|
| Sybil attack via fake hardware signatures | HIGH | ZK unique human proof + hardware attestation |
| Deepfake AI spoofing sensor data | HIGH | Hardware root of trust + mesh consensus |
| DEX honeypot token swap | HIGH | 1inch honeypot detection + slippage limits |
| Oracle slashing without due process | MEDIUM | Challenge window (7 days) + jury requirement |
| Gini collusion (circle of endorsements) | MEDIUM | Anti-collusion coefficient in reputation formula |
| Gerontocracy (status hoarding) | LOW | Exponential decay + cross-hemisphere synthesis bonus |
| Embedded firmware compromise | HIGH | Secure boot + ATECC608A secure element |
| Reentrancy in PurgeContract | HIGH | OpenZeppelin ReentrancyGuard + checks-effects-interactions |

### Security Boundaries
- **Fail-closed**: All verification stubs reject until real implementations connected
- **No backdoors**: Soulbound tokens are non-transferable by design
- **Transparent math**: All formulas documented in `docs/phase_decay_math.md`
- **Open hardware**: Schematics for Assembly Guild devices are public

### Known Limitations (pre-audit)
1. ZK circuit is scaffold only — not production hardened
2. DEX adapter requires external API/contract audit
3. ATECC608A integration needs HSM/KMS review
4. No formal verification of consensus protocol
5. Rust crates have empty `Cargo.toml` dependencies (scaffold only)
