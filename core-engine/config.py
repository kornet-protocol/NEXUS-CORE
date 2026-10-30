# =====================================================================
# NEXUS KORNET ENGINE: SHARED CONFIGURATION
# Single source of truth for weights, lambdas, and magic numbers
# =====================================================================

# Base utility weights (Omega_k)
CATEGORY_WEIGHTS = {
    "life_saved": 1000.0,
    "hospital_built": 500.0,
    "bridge_built": 200.0,
    "tree_planted": 10.0,
    "square_cleaned": 5.0,
    "scientific_breakthrough": 800.0,
    "art_created": 50.0,
    "sports_achievement": 30.0,
    "teaching": 150.0,
    "mentoring": 200.0,
    "infrastructure_maintained": 20.0,
    "disaster_relief": 400.0,
    "cybersecurity_defense": 300.0,
    "open_source_contribution": 80.0,
    "community_organization": 60.0,
}

# Decay coefficients (lambda_k) per category
CATEGORY_LAMBDAS = {
    "life_saved": 0.0001,
    "hospital_built": 0.0003,
    "bridge_built": 0.0005,
    "tree_planted": 0.001,
    "square_cleaned": 0.002,
    "scientific_breakthrough": 0.0002,
    "art_created": 0.003,
    "sports_achievement": 0.004,
    "teaching": 0.0004,
    "mentoring": 0.0003,
    "infrastructure_maintained": 0.0006,
    "disaster_relief": 0.0002,
    "cybersecurity_defense": 0.0005,
    "open_source_contribution": 0.0008,
    "community_organization": 0.0007,
}

# Caste-specific lambda overrides
CASTE_LAMBDAS = {
    "BUILDER": 0.0005,
    "MEDIC": 0.0008,
    "SCIENTIST": 0.0006,
    "INFLUENCER": 0.005,
    "ATHLETE": 0.003,
    "ARTIST": 0.002,
    "TEACHER": 0.0004,
}

DEFAULT_LAMBDA = 0.001

# Consensus thresholds
CONFIDENCE_THRESHOLD = 0.80
MIN_WITNESSES = 3
MIN_ENDORSEMENTS = 5

# Challenge window
CHALLENGE_WINDOW_DAYS = 7
