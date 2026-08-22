"""
Unit tests for the Scoring engine.
"""
import pytest
from src.engine.scorer import Scorer
from src.schemas.models import CandidateProfile, JobPosting


def test_weighted_score_calculation():
    # Weights: Skill (40%), Experience (30%), ATS (15%), Domain (15%)
    score = Scorer.calculate_weighted_score(
        skill_score=100.0,
        experience_score=100.0,
        ats_score=100.0,
        domain_score=100.0
    )
    assert score == 100.0

    score_mixed = Scorer.calculate_weighted_score(
        skill_score=80.0,
        experience_score=60.0,
        ats_score=70.0,
        domain_score=90.0
    )
    # (80*0.4)+(60*0.3)+(70*0.15)+(90*0.15) = 32 + 18 + 10.5 + 13.5 = 74.0
    assert score_mixed == 74.0


def test_determine_match_tier():
    assert Scorer.determine_match_tier(85.0) == "🔥 High Fit"
    assert Scorer.determine_match_tier(80.0) == "🔥 High Fit"
    assert Scorer.determine_match_tier(75.0) == "⚡ Medium Fit"
    assert Scorer.determine_match_tier(60.0) == "⚡ Medium Fit"
    assert Scorer.determine_match_tier(59.9) == "⚠️ Stretch / Low Fit"
    assert Scorer.determine_match_tier(30.0) == "⚠️ Stretch / Low Fit"


def test_heuristic_scoring():
    candidate = CandidateProfile(
        name="Alice Smith",
        target_title="Data Analyst",
        years_of_experience=4.0,
        skills=["Python", "SQL", "Power BI"],
        raw_text="Experienced Data Analyst with 4 years in Python, SQL, and Power BI."
    )
    job = JobPosting(
        id="job-1",
        title="Data Analyst",
        company="Analytics Pro",
        experience_required="3+ years",
        skills_required=["SQL", "Python", "Tableau"],
        raw_text="Looking for Data Analyst with 3+ years experience in Python and SQL."
    )

    scores = Scorer.compute_heuristic_scores(candidate, job)
    assert scores["overall_match_score"] > 60.0
    assert scores["skill_score"] > 50.0
    assert scores["experience_score"] >= 80.0

