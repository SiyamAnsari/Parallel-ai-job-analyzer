"""
Parallel asynchronous job analyzer evaluating candidate resumes against multiple jobs concurrently.
"""
import time
import json
import re
import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable, Awaitable
from src.config import settings
from src.schemas.models import (
    CandidateProfile,
    JobPosting,
    JobAnalysisResult,
    BatchAnalysisReport,
    AnalysisComparisonItem,
    SkillMatchBreakdown,
    AtsOptimizationDetails,
    ApplicationKit,
    InterviewPrepQuestion
)
from src.engine.llm_factory import LLMFactory
from src.engine.prompts import JOB_EVALUATION_SYSTEM_PROMPT, JOB_EVALUATION_USER_PROMPT, RESUME_EXTRACTION_PROMPT
from src.engine.scorer import Scorer
from src.engine.tailor import ApplicationTailor

logger = logging.getLogger(__name__)


class ParallelJobAnalyzer:
    """Production parallel AI orchestrator for high-throughput job fit evaluation."""

    def __init__(
        self,
        model_name: Optional[str] = None,
        concurrency_limit: int = 5,
        temperature: float = 0.0,
        api_key: Optional[str] = None
    ):
        self.model_name = model_name or settings.DEFAULT_MODEL
        self.concurrency_limit = min(max(concurrency_limit, 1), settings.MAX_ALLOWED_CONCURRENCY)
        self.temperature = temperature
        self.api_key = api_key
        self.llm = LLMFactory.get_chat_model(
            model_name=self.model_name,
            temperature=self.temperature,
            api_key=self.api_key
        )

    async def analyze_single_job_async(
        self,
        candidate: CandidateProfile,
        job: JobPosting
    ) -> JobAnalysisResult:
        """Analyze a single candidate-job pair asynchronously with performance timing and error isolation."""
        start_time = time.perf_counter()

        formatted_user_prompt = JOB_EVALUATION_USER_PROMPT.format(
            candidate_name=candidate.name or "Candidate",
            target_title=candidate.target_title or "Not specified",
            years_of_experience=candidate.years_of_experience or 0.0,
            skills=", ".join(candidate.skills) if candidate.skills else "See raw text",
            experience_highlights="\n".join(f"- {h}" for h in candidate.experience_highlights) if candidate.experience_highlights else "See raw text",
            education="\n".join(f"- {e}" for e in candidate.education) if candidate.education else "See raw text",
            candidate_raw_text=candidate.raw_text,
            job_id=job.id,
            job_title=job.title,
            company=job.company or "Hiring Co.",
            experience_required=job.experience_required or "Not specified",
            skills_required=", ".join(job.skills_required) if job.skills_required else "See full description",
            job_raw_text=job.raw_text
        )

        messages = [
            ("system", JOB_EVALUATION_SYSTEM_PROMPT),
            ("user", formatted_user_prompt)
        ]

        try:
            # Async invoke with timeout
            response = await asyncio.wait_for(
                self.llm.ainvoke(messages),
                timeout=settings.REQUEST_TIMEOUT_SECONDS
            )
            raw_content = response.content.strip()
        except Exception as api_err:
            # If rate limit or error on primary model, fallback to fast backup model
            logger.warning(f"Primary model {self.model_name} failed: {api_err}. Trying fallback model {settings.FAST_MODEL}...")
            try:
                fallback_llm = LLMFactory.get_chat_model(model_name=settings.FAST_MODEL, api_key=self.api_key)
                response = await asyncio.wait_for(
                    fallback_llm.ainvoke(messages),
                    timeout=settings.REQUEST_TIMEOUT_SECONDS
                )
                raw_content = response.content.strip()
            except Exception as fb_err:
                logger.error(f"Fallback model also failed: {fb_err}")
                duration = round(time.perf_counter() - start_time, 2)
                return self._build_fallback_result(candidate, job, error_msg=str(api_err), duration=duration)

        try:
            # Parse JSON from response
            data = self._extract_json_from_response(raw_content)
            
            # Extract and validate fields
            skill_score = float(data.get("skill_score", 70.0))
            exp_score = float(data.get("experience_score", 70.0))
            ats_score = float(data.get("ats_score", 70.0))
            domain_score = float(data.get("domain_score", 70.0))
            
            overall_score = data.get("overall_match_score")
            if overall_score is None:
                overall_score = Scorer.calculate_weighted_score(skill_score, exp_score, ats_score, domain_score)
            else:
                overall_score = float(overall_score)

            match_tier = data.get("match_tier") or Scorer.determine_match_tier(overall_score)
            
            # Skills breakdown
            sb_data = data.get("skills_breakdown", {})
            skills_breakdown = SkillMatchBreakdown(
                matched_skills=sb_data.get("matched_skills", []),
                missing_critical_skills=sb_data.get("missing_critical_skills", []),
                missing_nice_to_have=sb_data.get("missing_nice_to_have", []),
                transferable_skills=sb_data.get("transferable_skills", []),
                skill_match_score=float(sb_data.get("skill_match_score", skill_score))
            )
            
            # ATS Optimization
            ats_data = data.get("ats_optimization", {})
            ats_optimization = AtsOptimizationDetails(
                ats_score=float(ats_data.get("ats_score", ats_score)),
                missing_keywords=ats_data.get("missing_keywords", []),
                formatting_recommendations=ats_data.get("formatting_recommendations", []),
                bullet_point_improvements=ats_data.get("bullet_point_improvements", [])
            )
            
            # Application Kit
            app_data = data.get("application_kit", {})
            int_questions = []
            for q in app_data.get("interview_questions", []):
                int_questions.append(
                    InterviewPrepQuestion(
                        question=q.get("question", ""),
                        category=q.get("category", "General"),
                        recommended_talking_point=q.get("recommended_talking_point", "")
                    )
                )
            
            application_kit = ApplicationKit(
                tailored_resume_bullets=app_data.get("tailored_resume_bullets", []),
                elevator_pitch=app_data.get("elevator_pitch", "Excited to apply for this role!"),
                interview_questions=int_questions
            )

            duration = round(time.perf_counter() - start_time, 2)

            return JobAnalysisResult(
                job_id=job.id,
                job_title=job.title,
                company=job.company or "Target Company",
                overall_match_score=overall_score,
                skill_score=skill_score,
                experience_score=exp_score,
                ats_score=ats_score,
                domain_score=domain_score,
                match_tier=match_tier,
                executive_summary=data.get("executive_summary", "Detailed match analysis completed."),
                key_strengths=data.get("key_strengths", []),
                risk_factors_or_gaps=data.get("risk_factors_or_gaps", []),
                skills_breakdown=skills_breakdown,
                ats_optimization=ats_optimization,
                application_kit=application_kit,
                execution_time_seconds=duration,
                model_used=self.model_name
            )

        except Exception as e:
            logger.error(f"Error analyzing job {job.id} ({job.title}): {e}", exc_info=True)
            duration = round(time.perf_counter() - start_time, 2)
            
            # Fallback to robust heuristic computation
            return self._build_fallback_result(candidate, job, error_msg=str(e), duration=duration)

    async def analyze_batch_parallel(
        self,
        candidate: CandidateProfile,
        jobs: List[JobPosting],
        progress_callback: Optional[Callable[[int, int, JobAnalysisResult], Any]] = None
    ) -> BatchAnalysisReport:
        """Execute parallel batch analysis across multiple jobs with bounded concurrency."""
        batch_start_time = time.perf_counter()
        total_jobs = len(jobs)
        
        if total_jobs == 0:
            return BatchAnalysisReport(
                candidate_name=candidate.name or "Candidate",
                total_jobs_analyzed=0,
                successful_analyses=0,
                failed_analyses=0,
                average_match_score=0.0,
                total_batch_duration_seconds=0.0
            )

        semaphore = asyncio.Semaphore(self.concurrency_limit)
        completed_count = 0

        async def _bounded_analyze(job: JobPosting) -> JobAnalysisResult:
            nonlocal completed_count
            async with semaphore:
                result = await self.analyze_single_job_async(candidate, job)
                completed_count += 1
                if progress_callback:
                    try:
                        if asyncio.iscoroutinefunction(progress_callback):
                            await progress_callback(completed_count, total_jobs, result)
                        else:
                            progress_callback(completed_count, total_jobs, result)
                    except Exception as cb_err:
                        logger.warning(f"Progress callback error: {cb_err}")
                return result

        # Run all jobs concurrently bounded by semaphore
        tasks = [_bounded_analyze(job) for job in jobs]
        results: List[JobAnalysisResult] = await asyncio.gather(*tasks)

        # Calculate aggregates
        successful = [r for r in results if not r.error]
        failed = [r for r in results if r.error]
        
        avg_score = round(sum(r.overall_match_score for r in results) / total_jobs, 1) if total_jobs > 0 else 0.0
        
        # Build Leaderboard Comparison items
        comparison_items: List[AnalysisComparisonItem] = []
        for r in results:
            comparison_items.append(
                AnalysisComparisonItem(
                    job_id=r.job_id,
                    job_title=r.job_title,
                    company=r.company,
                    overall_score=r.overall_match_score,
                    skill_score=r.skill_score,
                    experience_score=r.experience_score,
                    ats_score=r.ats_score,
                    match_tier=r.match_tier,
                    top_missing_skills=r.skills_breakdown.missing_critical_skills[:3],
                    processing_time=r.execution_time_seconds
                )
            )

        # Sort leaderboard by overall score descending
        comparison_items.sort(key=lambda x: x.overall_score, reverse=True)
        best_match = comparison_items[0] if comparison_items else None
        total_duration = round(time.perf_counter() - batch_start_time, 2)

        return BatchAnalysisReport(
            candidate_name=candidate.name or "Candidate",
            total_jobs_analyzed=total_jobs,
            successful_analyses=len(successful),
            failed_analyses=len(failed),
            average_match_score=avg_score,
            best_matching_job=best_match,
            results=results,
            comparison_table=comparison_items,
            total_batch_duration_seconds=total_duration
        )

    def _extract_json_from_response(self, text: str) -> Dict[str, Any]:
        """Extract clean JSON dictionary from LLM string output."""
        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try markdown code block extraction
        code_block = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if code_block:
            try:
                return json.loads(code_block.group(1).strip())
            except json.JSONDecodeError:
                pass

        # Try bracket extraction
        json_match = re.search(r"\{[\s\S]*\}", text)
        if json_match:
            try:
                return json.loads(json_match.group(0).strip())
            except json.JSONDecodeError:
                pass

        raise ValueError("Failed to extract valid JSON from LLM response.")

    def _build_fallback_result(
        self,
        candidate: CandidateProfile,
        job: JobPosting,
        error_msg: str,
        duration: float
    ) -> JobAnalysisResult:
        """Construct a safe heuristic result if LLM inference or JSON parsing fails."""
        scores = Scorer.compute_heuristic_scores(candidate, job)
        tier = Scorer.determine_match_tier(scores["overall_match_score"])
        
        # Skill gap heuristic
        cand_skills_lower = set(s.lower() for s in candidate.skills)
        matched = [s for s in job.skills_required if s.lower() in cand_skills_lower]
        missing = [s for s in job.skills_required if s.lower() not in cand_skills_lower]

        app_kit = ApplicationTailor.generate_fallback_application_kit(candidate, job, missing)

        return JobAnalysisResult(
            job_id=job.id,
            job_title=job.title,
            company=job.company or "Target Company",
            overall_match_score=scores["overall_match_score"],
            skill_score=scores["skill_score"],
            experience_score=scores["experience_score"],
            ats_score=scores["ats_score"],
            domain_score=scores["domain_score"],
            match_tier=tier,
            executive_summary=f"Analysis computed using heuristic matching engine (Notice: {error_msg[:100]}).",
            key_strengths=[f"Strong alignment in {s}" for s in matched[:3]] or ["Relevant background experience"],
            risk_factors_or_gaps=[f"Missing experience with {s}" for s in missing[:3]] or ["Verify domain-specific requirements"],
            skills_breakdown=SkillMatchBreakdown(
                matched_skills=matched,
                missing_critical_skills=missing[:3],
                missing_nice_to_have=missing[3:],
                transferable_skills=[],
                skill_match_score=scores["skill_score"]
            ),
            ats_optimization=AtsOptimizationDetails(
                ats_score=scores["ats_score"],
                missing_keywords=missing[:5],
                formatting_recommendations=["Include explicit mentions of target job title and keywords in your resume header."],
                bullet_point_improvements=["Quantify achievements with metrics (e.g., % improvement, revenue generated)."]
            ),
            application_kit=app_kit,
            execution_time_seconds=duration,
            model_used=f"{self.model_name} (heuristic fallback)",
            error=None  # Cleared so report still renders smoothly with heuristic scores
        )

