"""
Scoring engine providing transparent, multi-factor calculations and heuristic evaluation.
"""
import re
from typing import List, Dict, Tuple, Set
from src.config import settings
from src.schemas.models import CandidateProfile, JobPosting, SkillMatchBreakdown, AtsOptimizationDetails


class Scorer:
    """Calculates weighted match scores and deterministic metrics."""

    @staticmethod
    def calculate_weighted_score(
        skill_score: float,
        experience_score: float,
        ats_score: float,
        domain_score: float
    ) -> float:
        """Calculate weighted composite score out of 100 based on configured weights."""
        weighted = (
            (skill_score * settings.WEIGHT_SKILLS) +
            (experience_score * settings.WEIGHT_EXPERIENCE) +
            (ats_score * settings.WEIGHT_ATS_KEYWORDS) +
            (domain_score * settings.WEIGHT_DOMAIN_EDUCATION)
        )
        return round(min(max(weighted, 0.0), 100.0), 1)

    @staticmethod
    def determine_match_tier(overall_score: float) -> str:
        """Classify overall score into clear tier labels."""
        if overall_score >= settings.HIGH_FIT_THRESHOLD:
            return "🔥 High Fit"
        elif overall_score >= settings.MEDIUM_FIT_THRESHOLD:
            return "⚡ Medium Fit"
        else:
            return "⚠️ Stretch / Low Fit"

    @classmethod
    def compute_heuristic_scores(cls, candidate: CandidateProfile, job: JobPosting) -> Dict[str, float]:
        """Compute baseline heuristic match scores using set intersection and text frequency."""
        cand_text = (candidate.raw_text + " " + " ".join(candidate.skills)).lower()
        job_text = (job.raw_text + " " + " ".join(job.skills_required)).lower()
        
        # 1. Skill Score
        job_skills = set(s.lower() for s in job.skills_required) if job.skills_required else cls._extract_keywords(job_text)
        cand_skills = set(s.lower() for s in candidate.skills) if candidate.skills else cls._extract_keywords(cand_text)
        
        if job_skills:
            matched_skills = job_skills.intersection(cand_skills)
            skill_score = (len(matched_skills) / len(job_skills)) * 100.0
        else:
            skill_score = 65.0
            
        # 2. Experience Score
        cand_exp = candidate.years_of_experience or 0.0
        job_exp = cls._parse_exp_years(job.experience_required or "")
        if job_exp <= 0:
            exp_score = 80.0
        elif cand_exp >= job_exp:
            exp_score = min(100.0, 85.0 + (cand_exp - job_exp) * 5.0)
        else:
            gap = job_exp - cand_exp
            exp_score = max(30.0, 80.0 - (gap * 15.0))
            
        # 3. ATS Keyword Density Match
        important_keywords = cls._extract_keywords(job_text)
        if important_keywords:
            found_keywords = sum(1 for kw in important_keywords if kw in cand_text)
            ats_score = (found_keywords / len(important_keywords)) * 100.0
        else:
            ats_score = 70.0

        # 4. Domain / Title Match
        domain_score = 70.0
        if candidate.target_title and candidate.target_title.lower() in job.title.lower():
            domain_score = 90.0
        elif any(w in job.title.lower() for w in (candidate.target_title or "").lower().split()):
            domain_score = 80.0
            
        # Composite
        overall = cls.calculate_weighted_score(skill_score, exp_score, ats_score, domain_score)
        
        return {
            "overall_match_score": overall,
            "skill_score": round(min(100.0, max(0.0, skill_score)), 1),
            "experience_score": round(min(100.0, max(0.0, exp_score)), 1),
            "ats_score": round(min(100.0, max(0.0, ats_score)), 1),
            "domain_score": round(min(100.0, max(0.0, domain_score)), 1)
        }

    @staticmethod
    def _extract_keywords(text: str) -> Set[str]:
        """Extract significant keywords from text."""
        words = re.findall(r"\b[a-zA-Z]{3,20}\b", text.lower())
        stopwords = {
            "the", "and", "with", "for", "that", "this", "from", "have", "will", "our",
            "you", "your", "are", "about", "work", "team", "role", "requirements",
            "experience", "years", "degree", "preferred", "looking", "candidate", "responsibilities"
        }
        filtered = [w for w in words if w not in stopwords]
        return set(filtered[:30])

    @staticmethod
    def _parse_exp_years(exp_str: str) -> float:
        """Parse numeric years from string like '3-5 years' or '4+ years'."""
        match = re.search(r"(\d+(?:\.\d+)?)", exp_str)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return 0.0

