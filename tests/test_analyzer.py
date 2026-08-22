"""
Unit and integration tests for Parallel Job Analyzer.
"""
import pytest
from src.schemas.models import CandidateProfile, JobPosting
from src.engine.analyzer import ParallelJobAnalyzer
from src.data.sample_data import SAMPLE_CANDIDATE_DATA_ANALYST, SAMPLE_JOBS_BATCH


@pytest.mark.asyncio
async def test_parallel_batch_analysis_execution():
    analyzer = ParallelJobAnalyzer(
        model_name="openai/gpt-oss-120b",
        concurrency_limit=3
    )

    # Use first 2 sample jobs
    test_jobs = SAMPLE_JOBS_BATCH[:2]
    
    progress_updates = []
    def on_progress(completed, total, res):
        progress_updates.append(completed)

    report = await analyzer.analyze_batch_parallel(
        candidate=SAMPLE_CANDIDATE_DATA_ANALYST,
        jobs=test_jobs,
        progress_callback=on_progress
    )

    assert report.total_jobs_analyzed == 2
    assert report.successful_analyses >= 1
    assert len(report.results) == 2
    assert len(report.comparison_table) == 2
    assert report.total_batch_duration_seconds > 0.0
    assert report.best_matching_job is not None
    assert len(progress_updates) == 2

