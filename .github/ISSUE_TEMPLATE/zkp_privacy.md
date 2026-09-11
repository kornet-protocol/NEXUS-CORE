---
name: "[ZKP] Privacy Layer Implementation"
about: Реализация Zero-Knowledge доказательств для приватности
title: "[ZKP] Реализация groth16 верификатора для действия"
labels: cryptography, zk, help wanted, good first issue
assignees: ''

---

### Контекст
Вектор C (Паноптикум): мы не должны записывать GPS-координаты и лица пользователей в открытый блокчейн. Нужно, чтобы пользователь генерировал доказательство: «Я совершил полезное действие типа X в регионе Y», не раскрывая точную геопозицию.

### Требуемое решение
1. Написать circuit (Circom / halo2) для-proof-of-action.
2. Реализовать trusted setup ceremony для proving key.
3. Интегрировать верификацию в `identity-zkp/zkp_action_verifier.rs`.

**Награда (Karma):** Вы создаете слой приватности, защищающий каждого пользователя системы.

### Acceptance Criteria
- [ ] Circuit компилируется и проходит тесты
- [ ] Proof generation < 5 секунд наconsumer hardware
- [ ] Proof verification < 100ms в `zkp_action_verifier.rs`
- [ ] Документация по trusted setup
