"""
Pydantic v2 schemas for Candidate Profiles, Job Postings, and Analysis Results.
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    """Structured representation of a candidate profile or parsed resume."""
    name: Optional[str] = Field(default="Candidate", description="Full name of candidate")
    target_title: Optional[str] = Field(default=None, description="Target job title")
    years_of_experience: Optional[float] = Field(default=0.0, description="Total years of professional experience")
    skills: List[str] = Field(default_factory=list, description="Extracted technical and soft skills")
    experience_highlights: List[str] = Field(default_factory=list, description="Key career responsibilities and accomplishments")
    education: List[str] = Field(default_factory=list, description="Degrees, universities, certifications")
    raw_text: str = Field(..., description="Raw resume text or candidate bio")


class JobPosting(BaseModel):
    """Job posting specification."""
    id: str = Field(..., description="Unique job identifier")
    title: str = Field(..., description="Job Title")
    company: Optional[str] = Field(default="Target Company", description="Hiring organization")
    location: Optional[str] = Field(default="Remote / Flexible", description="Job location")
    experience_required: Optional[str] = Field(default="Not specified", description="Required experience level")
    skills_required: List[str] = Field(default_factory=list, description="Key required skills")
    raw_text: str = Field(..., description="Full job description text")


class BatchJobInput(BaseModel):
    """Batch input of multiple jobs against a candidate."""
    candidate: CandidateProfile
    jobs: List[JobPosting]
    concurrency_limit: Optional[int] = Field(default=5, ge=1, le=20, description="Concurrent analysis workers")
    model_override: Optional[str] = Field(default=None, description="Optional custom Groq model name")


class SkillMatchBreakdown(BaseModel):
    """Detailed breakdown of skill matches and gaps."""
    matched_skills: List[str] = Field(default_factory=list, description="Skills possessed that meet JD requirements")
    missing_critical_skills: List[str] = Field(default_factory=list, description="Mandatory or dealbreaker skills missing")
    missing_nice_to_have: List[str] = Field(default_factory=list, description="Bonus/preferred skills missing")
    transferable_skills: List[str] = Field(default_factory=list, description="Candidate skills that can transfer to missing requirements")
    skill_match_score: float = Field(..., ge=0.0, le=100.0, description="Score for technical & domain skill match")


class AtsOptimizationDetails(BaseModel):
    """ATS (Applicant Tracking System) compatibility assessment."""
    ats_score: float = Field(..., ge=0.0, le=100.0, description="Estimated ATS pass probability")
    missing_keywords: List[str] = Field(default_factory=list, description="High-frequency JD keywords missing from resume")
    formatting_recommendations: List[str] = Field(default_factory=list, description="ATS layout and keyword formatting tips")
    bullet_point_improvements: List[str] = Field(default_factory=list, description="Specific phrasing suggestions to pass filters")


class InterviewPrepQuestion(BaseModel):
    """Tailored interview question based on candidate gaps."""
    question: str = Field(..., description="Likely interview question addressing a gap or key requirement")
    category: str = Field(..., description="Technical, Behavioral, or System Design")
    recommended_talking_point: str = Field(..., description="How the candidate should frame their answer")


class ApplicationKit(BaseModel):
    """Actionable materials to apply for this specific job."""
    tailored_resume_bullets: List[str] = Field(
        default_factory=list, 
        description="STAR-method bullet points tailored to this job's core requirements"
    )
    elevator_pitch: str = Field(
        ..., 
        description="2-3 sentence personalized pitch for recruiters or cover letter opening"
    )
    interview_questions: List[InterviewPrepQuestion] = Field(
        default_factory=list, 
        description="Top interview questions with strategic talking points"
    )


class JobAnalysisResult(BaseModel):
    """Comprehensive evaluation result for a single candidate-job pair."""
    job_id: str = Field(..., description="ID of the analyzed job")
    job_title: str = Field(..., description="Job Title")
    company: str = Field(..., description="Company Name")
    
    # Quantitative Scores (0-100)
    overall_match_score: float = Field(..., ge=0.0, le=100.0, description="Weighted composite score")
    skill_score: float = Field(..., ge=0.0, le=100.0, description="Skill match component")
    experience_score: float = Field(..., ge=0.0, le=100.0, description="Experience & Seniority component")
    ats_score: float = Field(..., ge=0.0, le=100.0, description="ATS Keyword compatibility")
    domain_score: float = Field(..., ge=0.0, le=100.0, description="Education & Industry Domain fit")
    
    # Qualitative Classifications
    match_tier: Literal["🔥 High Fit", "⚡ Medium Fit", "⚠️ Stretch / Low Fit"] = Field(
        ..., description="Overall categorization"
    )
    executive_summary: str = Field(..., description="Concise assessment summary of the candidate's fit")
    key_strengths: List[str] = Field(default_factory=list, description="Top candidate advantages for this role")
    risk_factors_or_gaps: List[str] = Field(default_factory=list, description="Major red flags or hurdles")
    
    # Detailed Modules
    skills_breakdown: SkillMatchBreakdown
    ats_optimization: AtsOptimizationDetails
    application_kit: ApplicationKit
    
    # Processing Metrics
    execution_time_seconds: float = Field(default=0.0, description="Time taken to process this analysis")
    model_used: str = Field(default="openai/gpt-oss-120b", description="Groq model employed")
    error: Optional[str] = Field(default=None, description="Error message if analysis failed")


class AnalysisComparisonItem(BaseModel):
    """Summary item for leaderboard comparison table."""
    job_id: str
    job_title: str
    company: str
    overall_score: float
    skill_score: float
    experience_score: float
    ats_score: float
    match_tier: str
    top_missing_skills: List[str]
    processing_time: float


class BatchAnalysisReport(BaseModel):
    """Aggregate report comparing multiple jobs for a single candidate."""
    candidate_name: str
    total_jobs_analyzed: int
    successful_analyses: int
    failed_analyses: int
    average_match_score: float
    best_matching_job: Optional[AnalysisComparisonItem] = None
    results: List[JobAnalysisResult] = Field(default_factory=list)
    comparison_table: List[AnalysisComparisonItem] = Field(default_factory=list)
    total_batch_duration_seconds: float = 0.0

