# Phase Decay Mathematics

## Reputation Decay Function
R_i(t) = Σ_k [ Ω_k · V_k · e^(-λ_k(t-t_k)) · (1 - Gini(C_k)) ]

Where:
- Ω_k: base utility weight of task k
- V_k: verification score [0, 1]
- λ_k: decay coefficient (builders lower, influencers higher)
- Gini(C_k): collusion anti-trust coefficient

## Thermodynamics of Status (dR/dt)

Status is kinetic energy, not potential. The differential equation:

dR_i(t)/dt = UsefulContribution(t) - λ · R_i(t)

This is the Second Law of Thermodynamics applied to social structures:
- UsefulContribution(t): energy input from current actions
- λ · R_i(t): entropy production (status decays if not maintained)
- Equilibrium: R* = UsefulContribution / λ

### Anti-Gerontocracy Effect
If an engineer creates a fusion reactor (R_max = 1000), but rests for 5 years:
R(5y) = 1000 · e^(-λ · 5y)
With λ = 0.0001 (life_saved category), after 5 years R ≈ 995
With λ = 0.005 (influencer category), after 5 years R ≈ 975

But for a bridge_builder (λ = 0.0005):
R(5y) = 200 · e^(-0.0005 · 5y) ≈ 199.5

Lower λ for fundamental contributions preserves status longer, but it still decays. No one can coast forever.

### Category-Specific Decay Rates

| Category | λ (1/day) | Half-life (years) | Rationale |
|----------|-----------|-------------------|-----------|
| life_saved | 0.0001 | 19.1 | Fundamental, irreversible |
| hospital_built | 0.0003 | 6.4 | Long-term impact |
| bridge_built | 0.0005 | 3.8 | Infrastructure longevity |
| tree_planted | 0.001 | 1.9 | Ecological timescale |
| square_cleaned | 0.002 | 0.95 | Immediate, temporary |
| art_created | 0.003 | 0.63 | Cultural decay |
| sports_achievement | 0.004 | 0.48 | Ephemeral glory |
| teaching | 0.0004 | 4.8 | Knowledge propagation |
| mentoring | 0.0003 | 6.4 | Multiplicative effect |

## Anti-Collusion (Gini Coefficient)
If a circle of endorsements has zero entropy (everyone endorses everyone), Gini approaches 1 and rewards collapse to 0.
