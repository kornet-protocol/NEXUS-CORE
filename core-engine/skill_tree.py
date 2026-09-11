# =====================================================================
# NEXUS KORNET ENGINE: SKILL TREE MODULE v0.1
# RPG IRL: Ambidexterity multiplier for Universalist education
# =====================================================================

from __future__ import annotations

from typing import Dict, Set

# Базовые ветки навыков (левое / правое полушарие)
LEFT_HEMISPHERE = {
    "bio_engineering",
    "quantum_logistics",
    "robotics",
    "coding",
    "mathematics",
    "physics",
    "chemistry",
}

RIGHT_HEMISPHERE = {
    "music",
    "sculpture",
    "poetry",
    "painting",
    "dance",
    "spatial_design",
    "empathy",
}

SYNTHESIS_MULTIPLIER = 5.0


class SkillTree:
    def __init__(self) -> None:
        self.user_skills: Dict[str, Set[str]] = {}

    def add_skill(self, user_id: str, skill: str) -> None:
        self.user_skills.setdefault(user_id, set()).add(skill)

    def get_skills(self, user_id: str) -> Set[str]:
        return self.user_skills.get(user_id, set())

    def synthesize_bonus(self, user_id: str) -> float:
        """
        СИНТЕТИЧЕСКИЙ МУЛЬТИПЛИКАТОР (x5).
        Алгоритм параноидально поощряет кросс-полушарный синтез:
        - Только одна ветка (левая ИЛИ правая): множитель x1 (статус растёт медленно).
        - Хотя бы одна связь между полушариями (левая И правое): множитель x5.
        """
        skills = self.get_skills(user_id)
        left_count = len(skills & LEFT_HEMISPHERE)
        right_count = len(skills & RIGHT_HEMISPHERE)
        cross_links = min(left_count, right_count)
        return SYNTHESIS_MULTIPLIER if cross_links > 0 else 1.0

    def cross_link_score(self, user_id: str) -> int:
        skills = self.get_skills(user_id)
        left_count = len(skills & LEFT_HEMISPHERE)
        right_count = len(skills & RIGHT_HEMISPHERE)
        return min(left_count, right_count)

    def is_universal(self, user_id: str, threshold: int = 3) -> bool:
        """Универсал = минимум `threshold` связей между полушариями."""
        return self.cross_link_score(user_id) >= threshold

    def compute_skill_reputation(
        self,
        user_id: str,
        base_reputation: float,
    ) -> float:
        """
        Итоговый статус с учётом синтез-бонуса.
        R_synth = R_base × (1 + α · S)
        """
        bonus = self.synthesize_bonus(user_id)
        return base_reputation * bonus

    def mentor_royalty(
        self,
        student_achievement: float,
        royalty_rate: float = 0.10,
    ) -> float:
        """
        Rozłty наставника: 10% статуса студента пожизненно.
        """
        return student_achievement * royalty_rate
