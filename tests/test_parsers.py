"""
Unit tests for Resume and Job parsers.
"""
import pytest
from src.parsers.resume_parser import ResumeParser
from src.parsers.job_parser import JobParser


def test_resume_parser_from_text():
    sample_text = """John Doe
Senior Data Engineer | john.doe@example.com | San Francisco, CA

SUMMARY
5+ years of experience in distributed data processing, Python, SQL, and AWS.

SKILLS
Python, SQL, AWS, Docker, Snowflake, Spark, Airflow

EXPERIENCE
Lead Data Engineer at BigData Inc (2021 - Present)
- Engineered scalable batch ETL pipelines using Python and Spark.
- Reduced data warehouse costs by 30% through Snowflake query optimizations.

EDUCATION
B.S. in Computer Science, Stanford University
"""
    profile = ResumeParser.parse_to_profile(sample_text)
    assert profile.name == "John Doe"
    assert profile.years_of_experience >= 3.0
    assert any("python" in s.lower() for s in profile.skills)
    assert any("sql" in s.lower() for s in profile.skills)
    assert len(profile.experience_highlights) >= 1
    assert len(profile.education) >= 1


def test_job_parser_single_text():
    sample_jd = """Position: Senior Python Developer
Company: CloudTech Solutions
Experience Required: 4+ years of experience

We are looking for a Senior Python Developer with expertise in FastAPI, PostgreSQL, Docker, and AWS.
Responsibilities:
- Build high-throughput microservices.
- Optimize database queries.
"""
    job = JobParser.parse_single_text(sample_jd)
    assert "Python" in job.title or "Developer" in job.title
    assert "CloudTech Solutions" in job.company
    assert "4" in job.experience_required
    assert len(job.skills_required) > 0


def test_job_parser_csv():
    csv_data = """title,company,description,id
Data Analyst,Fintech Corp,"Seeking a Data Analyst with SQL and Power BI skills for sales dashboards.",job-101
Machine Learning Engineer,AI Labs,"Need PyTorch, Python and MLOps engineer for LLM deployment.",job-102
"""
    jobs = JobParser.parse_from_csv(csv_data)
    assert len(jobs) == 2
    assert jobs[0].id == "job-101"
    assert jobs[0].title == "Data Analyst"
    assert jobs[1].id == "job-102"
    assert jobs[1].company == "AI Labs"


def test_job_parser_multi_text():
    multi_text = """
--- Job 1: Backend Developer ---
Company: Stripe
Seeking Python and Django developer.

--- Job 2: Frontend Developer ---
Company: Vercel
Seeking React and Next.js developer.
"""
    jobs = JobParser.parse_multiple_from_text(multi_text)
    assert len(jobs) == 2

