---
name: "[ZKP] Privacy Layer Implementation"
about: Zero-Knowledge proof implementation for privacy
title: "[ZKP] Groth16 verifier implementation for action"
labels: cryptography, zk, help wanted, good first issue
assignees: ''

---

### Context
Vector C (Panopticon): we must not write users' GPS coordinates and faces to public blockchain. User must generate proof: "I performed useful action type X in region Y" without revealing exact geolocation.

### Required Solution
1. Write circuit (Circom / halo2) for proof-of-action.
2. Implement trusted setup ceremony for proving key.
3. Integrate verification into `identity-zkp/zkp_action_verifier.rs`.

**Reward (Karma):** You build the privacy layer protecting every system user.

### Acceptance Criteria
- [ ] Circuit compiles and passes tests
- [ ] Proof generation < 5 seconds on consumer hardware
- [ ] Proof verification < 100ms in `zkp_action_verifier.rs`
- [ ] Trusted setup documentation