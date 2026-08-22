"""
FastAPI Production REST API Server for Parallel AI Job Analyzer.
"""
from typing import List, Optional
import io
import time
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel

from src.config import settings
from src.schemas.models import (
    CandidateProfile,
    JobPosting,
    BatchJobInput,
    JobAnalysisResult,
    BatchAnalysisReport
)
from src.parsers.resume_parser import ResumeParser
from src.parsers.job_parser import JobParser
from src.engine.analyzer import ParallelJobAnalyzer
from src.engine.llm_factory import LLMFactory
from src.exporters.report_generator import ReportGenerator

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="High-Throughput Parallel AI Job Description & Resume Analyzer powered by Groq LLMs."
)

# Enable CORS for frontend integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Root info endpoint."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
        "health_check": f"{settings.API_PREFIX}/health"
    }


@app.get(f"{settings.API_PREFIX}/health", tags=["System"])
async def health_check():
    """System health check and available Groq models."""
    return {
        "status": "healthy",
        "default_model": settings.DEFAULT_MODEL,
        "available_models": LLMFactory.get_available_models(),
        "max_allowed_concurrency": settings.MAX_ALLOWED_CONCURRENCY,
        "groq_api_configured": bool(settings.GROQ_API_KEY)
    }


@app.post(f"{settings.API_PREFIX}/parse-resume", response_model=CandidateProfile, tags=["Ingestion"])
async def parse_resume_upload(
    file: UploadFile = File(...),
    candidate_name: Optional[str] = Form(None)
):
    """Upload and parse a resume file (PDF, DOCX, TXT) into a structured CandidateProfile."""
    try:
        content = await file.read()
        profile = ResumeParser.parse_to_profile(
            raw_text_or_file=content,
            filename=file.filename,
            candidate_name=candidate_name
        )
        return profile
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse resume: {str(e)}")


@app.post(f"{settings.API_PREFIX}/analyze-single", response_model=JobAnalysisResult, tags=["Analysis"])
async def analyze_single_job(
    candidate: CandidateProfile,
    job: JobPosting,
    model: Optional[str] = Query(None, description="Groq model name")
):
    """Analyze a single candidate against one job description."""
    analyzer = ParallelJobAnalyzer(model_name=model)
    result = await analyzer.analyze_single_job_async(candidate, job)
    return result


@app.post(f"{settings.API_PREFIX}/analyze-batch", response_model=BatchAnalysisReport, tags=["Analysis"])
async def analyze_batch_jobs(
    payload: BatchJobInput
):
    """
    Execute parallel analysis of multiple job postings against a candidate profile.
    Leverages async concurrency bounded by the specified concurrency_limit.
    """
    if not payload.jobs:
        raise HTTPException(status_code=400, detail="No jobs provided in batch request.")

    analyzer = ParallelJobAnalyzer(
        model_name=payload.model_override,
        concurrency_limit=payload.concurrency_limit or settings.DEFAULT_MAX_CONCURRENCY
    )

    report = await analyzer.analyze_batch_parallel(
        candidate=payload.candidate,
        jobs=payload.jobs
    )
    return report


@app.post(f"{settings.API_PREFIX}/export/pdf", tags=["Export"])
async def export_report_to_pdf(
    report: BatchAnalysisReport
):
    """Generate and return a downloadable PDF executive briefing."""
    try:
        pdf_bytes = ReportGenerator.to_pdf_bytes(report)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=job_analysis_{int(time.time())}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")


@app.post(f"{settings.API_PREFIX}/export/csv", tags=["Export"])
async def export_report_to_csv(
    report: BatchAnalysisReport
):
    """Generate and return a downloadable CSV comparison table."""
    try:
        csv_text = ReportGenerator.to_csv(report)
        return Response(
            content=csv_text,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=job_comparison_{int(time.time())}.csv"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV generation error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

