# AUDIT CHECKLIST — NEXUS-CORE v0.2
## Pre-audit requirements (independent researchers must verify)

### 1. Smart Contracts
- [ ] `SoulboundToken.sol`: verify in-contract decay math matches off-chain `reputation_decay.py`
- [ ] `FoundingPurger.sol`: verify soulbound override does not allow transfers/burns
- [ ] `PurgeContract.sol`: verify `IDexAdapter` interface implementation
- [ ] `OneInchArbitrumAdapter.sol`: verify slippage protection, honeypot detection, reentrancy guards
- [ ] Run Slither, Mythril, Securify automated analysis
- [ ] Verify `onlyMultisig` / `onlyOwner` access controls on all admin functions
- [ ] Check for missing events on state changes

### 2. ZK Circuits
- [ ] Verify `GoodDeedCircuit` constraint count and gas estimates
- [ ] Verify trusted setup parameters (powers of tau) are from verified ceremony
- [ ] Verify proof verification key matches circuit
- [ ] Test edge cases: overflow, underflow, negative timestamps
- [ ] Verify Merkle path verification logic in circuit

### 3. Core Engine (Python)
- [ ] Verify `reputation_decay.py` formula matches `phase_decay_math.md`
- [ ] Verify `graceful_degradation.py` Kalman filter implementation
- [ ] Verify `persistence.py` SQLite WAL mode is safe for concurrent writes
- [ ] Verify `production_config.py` fails closed on missing env vars in production
- [ ] Run `bandit` for security vulnerabilities

### 4. Validators
- [ ] Verify `dispute_arbiter.py` slashing logic has due process
- [ ] Verify `social_awakening.py` no longer has attribute access bugs
- [ ] Verify `web_of_trust.py` sybil resistance parameters (min_endorsements, max_path_depth)

### 5. Go Telemetry
- [ ] Verify `telemetry_aggregator.go` packet validation logic
- [ ] Verify SHA-256 hex validation and timestamp window
- [ ] Verify HTTP client timeout and retry logic

### 6. IoT/Embedded
- [ ] Verify ATECC608A signature verification in `water_quality_node.cpp`
- [ ] Verify LoRa mesh routing implementation
- [ ] Verify hardware RNG usage for key generation

### 7. General
- [ ] Verify no private keys or secrets in repository
- [ ] Verify CI/CD pipeline has no credential leaks
- [ ] Verify Docker images run as non-root user
- [ ] Verify all TODO/stubs are either implemented or documented as "not for production"
