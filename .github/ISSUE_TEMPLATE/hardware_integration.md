---
name: "[Hardware] ZKP Sensor Integration"
about: Интеграция аппаратных модулей для защиты от фейков (Root of Trust)
title: "[HW] Внедрение чипа ATECC608A в C++ ноду"
labels: hardware, help wanted, good first issue
assignees: ''

---

### Текущая проблема
В файле `iot-depin-network/arduino_air_sensor.cpp` используется программный SHA-256 (hardcoded secret), что уязвимо для экстракции ключа и атаки Сивиллы на уровне железа.

### Требуемое решение
1. Подключить библиотеку CryptoAuthLib.
2. Инициализировать I2C соединение с чипом ATECC608A.
3. Реализовать подпись RAW-данных с датчика по кривой Ed25519 (Secure Enclave).

**Награда (Karma):** Высший приоритет. Вы создаете аппаратную броню системы.

### Acceptance Criteria
- [ ] Чип ATECC608A инициализируется через I2C
- [ ] Сырые данные датчика хэшируются SHA256 на устройстве
- [ ] Хэш подписывается приватным ключом, хранящимся в Secure Enclave
- [ ] Подпись проверяется на стороне валидатора (`infrastructure_scan.py`)
