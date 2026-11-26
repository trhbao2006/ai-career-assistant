"""Registry thống nhất cấu hình đa ngành (IT, Economics, Healthcare, Education, Other)."""

from dataclasses import dataclass
from typing import Dict, List, Set

from config.taxonomies.economics import (
    ECONOMICS_CORE_SKILLS,
    ECONOMICS_DOMAIN_TERMS,
    ECONOMICS_TARGET_COUNTS,
    ECONOMICS_TAXONOMY,
    ECONOMICS_WEIGHTS,
)
from config.taxonomies.education import (
    EDUCATION_CORE_SKILLS,
    EDUCATION_DOMAIN_TERMS,
    EDUCATION_TARGET_COUNTS,
    EDUCATION_TAXONOMY,
    EDUCATION_WEIGHTS,
)
from config.taxonomies.healthcare import (
    HEALTHCARE_CORE_SKILLS,
    HEALTHCARE_DOMAIN_TERMS,
    HEALTHCARE_TARGET_COUNTS,
    HEALTHCARE_TAXONOMY,
    HEALTHCARE_WEIGHTS,
)
from config.taxonomies.it_general import (
    IT_ACTION_VERBS,
    IT_GENERAL_CORE_SKILLS,
    IT_GENERAL_DOMAIN_TERMS,
    IT_GENERAL_TARGET_COUNTS,
    IT_GENERAL_TAXONOMY,
    IT_GENERAL_WEIGHTS,
)
from config.taxonomies.transferable import GENERAL_ACTION_VERBS, TRANSFERABLE_SKILLS


@dataclass(frozen=True)
class DomainConfig:
    name: str
    taxonomy: Dict[str, Dict[str, List[str]]]
    weights: Dict[str, float]
    core_skills: Dict[str, List[str]]
    target_counts: Dict[str, int]
    domain_terms: Set[str]
    action_verbs: List[str]
    is_tech_heavy: bool


DOMAIN_REGISTRY: Dict[str, DomainConfig] = {
    "it": DomainConfig(
        name="it",
        taxonomy=IT_GENERAL_TAXONOMY,
        weights=IT_GENERAL_WEIGHTS,
        core_skills=IT_GENERAL_CORE_SKILLS,
        target_counts=IT_GENERAL_TARGET_COUNTS,
        domain_terms=IT_GENERAL_DOMAIN_TERMS,
        action_verbs=IT_ACTION_VERBS,
        is_tech_heavy=True,
    ),
    "economics": DomainConfig(
        name="economics",
        taxonomy=ECONOMICS_TAXONOMY,
        weights=ECONOMICS_WEIGHTS,
        core_skills=ECONOMICS_CORE_SKILLS,
        target_counts=ECONOMICS_TARGET_COUNTS,
        domain_terms=ECONOMICS_DOMAIN_TERMS,
        action_verbs=GENERAL_ACTION_VERBS,
        is_tech_heavy=False,
    ),
    "healthcare": DomainConfig(
        name="healthcare",
        taxonomy=HEALTHCARE_TAXONOMY,
        weights=HEALTHCARE_WEIGHTS,
        core_skills=HEALTHCARE_CORE_SKILLS,
        target_counts=HEALTHCARE_TARGET_COUNTS,
        domain_terms=HEALTHCARE_DOMAIN_TERMS,
        action_verbs=GENERAL_ACTION_VERBS,
        is_tech_heavy=False,
    ),
    "education": DomainConfig(
        name="education",
        taxonomy=EDUCATION_TAXONOMY,
        weights=EDUCATION_WEIGHTS,
        core_skills=EDUCATION_CORE_SKILLS,
        target_counts=EDUCATION_TARGET_COUNTS,
        domain_terms=EDUCATION_DOMAIN_TERMS,
        action_verbs=GENERAL_ACTION_VERBS,
        is_tech_heavy=False,
    ),
    "other": DomainConfig(
        name="other",
        taxonomy={"transferable": TRANSFERABLE_SKILLS},
        weights={"transferable": 1.0},
        core_skills={"transferable": ["Communication", "Problem Solving", "Project Management", "MS Office & Productivity"]},
        target_counts={"transferable": 4},
        domain_terms=set(),
        action_verbs=GENERAL_ACTION_VERBS,
        is_tech_heavy=False,
    ),
}

DOMAIN_ALIASES = {
    "information-technology": "it",
    "tech": "it",
    "backend": "it",
    "frontend": "it",
    "fullstack": "it",
    "software": "it",
    "devops": "it",
    "data": "it",
    "qa": "it",
    "finance": "economics",
    "business": "economics",
    "business-development": "economics",
    "banking": "economics",
    "accountant": "economics",
    "sales": "economics",
    "consultant": "economics",
    "medical": "healthcare",
    "fitness": "healthcare",
    "teacher": "education",
    "engineering": "other",
    "aviation": "other",
    "automobile": "other",
    "design_media": "other",
    "designer": "other",
    "digital-media": "other",
    "public-relations": "other",
    "hr_admin": "other",
    "hr": "other",
    "bpo": "other",
    "transferable": "other",
}


def normalize_domain_name(domain: str = "it") -> str:
    key = (domain or "it").strip().lower()
    return DOMAIN_ALIASES.get(key, key) if key not in DOMAIN_REGISTRY else key


def get_domain_config(domain: str = "it") -> DomainConfig:
    key = normalize_domain_name(domain)
    return DOMAIN_REGISTRY.get(key, DOMAIN_REGISTRY["other"])


def list_supported_domains() -> List[str]:
    return list(DOMAIN_REGISTRY.keys())
