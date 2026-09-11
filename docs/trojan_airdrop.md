# Trojan Airdrop: Контракт Очищения

## Философия

Мы используем дегенеративность существующей системы против неё самой. Миллиарды долларов заперты в мем-коинах (DOGE, SHIB, PEPE, WIF и сотни тысяч других), которые обесцениваются со временем. Вместо того чтобы ждать, пока их владельцы поймут это, мы предлагаем им **обменять обесценивающиеся токены на статус**.

## Механика

```
[Пользователь] --(burn мем-коинов)--> [PurgeContract] --(swap через DEX)--> [USDC/USDT] --> [NEXUS Treasury] --> [ATECC608A + Servers]
                                            |
                                            +--(mint Founding Purger SBT)--> [Пользователь]
```

## Контракт PurgeContract

**Вход:** Любой ERC20 токен из списка поддерживаемых (мем-коины с низкой капитализацией).
**Выход:** USDC/USDT на казначейство NEXUS + Founding Purger SBT для пользователя.

### Ключевые защиты

1. **Honeypot Detection:** Тестовый свап 0.1% токена перед основной транзакцией. Если тест падает — транзакция отклоняется.
2. **Slippage Protection:** Максимально допустимый slippage — 5%. Пользователь указывает `minExpectedUSD`.
3. **Cooldown:** Один токен можно пушить раз в 24 часа (защита от wash trading).
4. **Multi-sig Treasury:** Средства выводятся только через Gnosis Safe (3-of-5).
5. **Emergency Pause:** В случае атаки контракт можно заморозить.

## Контракт FoundingPurger (SBT)

**Непередаваемый токен** с метаданными:
- `purgeTimestamp` — когда пользователь участвовал в очищении
- `purgeAmount` — сколько мусора он сжёг
- `oasisPriorityMultiplier` — множитель 10x для доступа к Оазисам

## Экономика

| Параметр | Значение |
|-----------|----------|
| Порог пуша | $100 эквивалент мусорных токенов |
| Максимальная эмиссия | 10,000 Founding Purger SBT |
| Максимальный slippage | 5% |
| Cooldown между пушами | 24 часа на один токен |
| Treasury Multi-sig | 3-of-5 Gnosis Safe |

## Риски и митигация

| Риск | Митигация |
|------|-----------|
| Honeypot-токены | Тестовый свап 0.1% перед основной транзакцией |
| Rug pull создателей токена | Whitelist только проверенных токенов, multi-sig добавление |
| Regulatory risk | No KYC, permissionless, jurisdiction-agnostic |
| Flash loan attack на пуше | Cooldown 24h, slippage protection |
| Treasury drain | Multi-sig 3-of-5, timelock 48h |

## Деплой

1. Deploy `FoundingPurger` на Ethereum mainnet / L2
2. Deploy `PurgeContract` с адресом FoundingPurger и NEXUS Treasury
3. Whitelist первые 50 мем-коинов через multi-sig
4. Запустить маркетинговую кампанию "Burn your bags, get status"

## Юридическое замечание

Контракт работает на уровне permissionless DeFi. Мы не предлагаем инвестиции, не гарантируем доход и не ответственны за действия пользователей. Всё происходит через публичные смарт-контракты.
