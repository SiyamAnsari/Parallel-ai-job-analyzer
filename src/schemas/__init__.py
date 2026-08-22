"""
Data schemas and Pydantic models for Parallel AI Job Analyzer.
"""
from src.schemas.models import (
    CandidateProfile,
    JobPosting,
    BatchJobInput,
    SkillMatchBreakdown,
    AtsOptimizationDetails,
    ApplicationKit,
    JobAnalysisResult,
    BatchAnalysisReport,
    AnalysisComparisonItem,
)

__all__ = [
    "CandidateProfile",
    "JobPosting",
    "BatchJobInput",
    "SkillMatchBreakdown",
    "AtsOptimizationDetails",
    "ApplicationKit",
    "JobAnalysisResult",
    "BatchAnalysisReport",
    "AnalysisComparisonItem",
]

