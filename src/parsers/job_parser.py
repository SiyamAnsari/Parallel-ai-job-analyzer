"""
Job Description parser supporting raw text, CSV files, JSON payloads, and URL scraping.
"""
import io
import csv
import json
import re
import uuid
from typing import List, Dict, Any, Optional, Union
from src.schemas.models import JobPosting

try:
    import httpx
    from bs4 import BeautifulSoup
except ImportError:
    httpx = None
    BeautifulSoup = None


class JobParser:
    """Production-grade job posting parser and normalizer."""

    @classmethod
    def parse_single_text(cls, text: str, job_id: Optional[str] = None, title: Optional[str] = None, company: Optional[str] = None) -> JobPosting:
        """Parse a single job description string into a structured JobPosting."""
        cleaned_text = text.strip()
        extracted_id = job_id or f"job-{uuid.uuid4().hex[:8]}"
        extracted_title = title or cls._extract_title_from_text(cleaned_text)
        extracted_company = company or cls._extract_company_from_text(cleaned_text)
        extracted_skills = cls._extract_key_skills(cleaned_text)
        extracted_exp = cls._extract_experience_requirement(cleaned_text)

        return JobPosting(
            id=extracted_id,
            title=extracted_title,
            company=extracted_company,
            experience_required=extracted_exp,
            skills_required=extracted_skills,
            raw_text=cleaned_text
        )

    @classmethod
    def parse_multiple_from_text(cls, text: str) -> List[JobPosting]:
        """Parse multiple jobs separated by headers like '--- Job X ---' or 'Job 1:', 'Job 2:'."""
        # Find matches for delimiters like '--- ... ---' or 'Job X:' or '=== ... ==='
        delimiter_pattern = r"(?:^|\n)\s*([-=]{3,}[^\n]+[-=]{3,}|Job\s*\d+\s*:|Position\s*\d+\s*:|===+\s*)"
        
        # Split while retaining delimiter headers
        parts = re.split(delimiter_pattern, text, flags=re.IGNORECASE)
        jobs = []
        
        if len(parts) > 1:
            current_header = ""
            for part in parts:
                cleaned = part.strip()
                if not cleaned:
                    continue
                # Check if this part is a header delimiter
                if re.match(r"^[-=]{3,}|^(?:Job|Position)\s*\d+\s*:", cleaned, re.IGNORECASE):
                    current_header = cleaned.strip("-= :")
                else:
                    # Body text
                    combined_text = f"{current_header}\n{cleaned}" if current_header else cleaned
                    extracted_title = None
                    if current_header:
                        # e.g., 'Job 1: Backend Developer' -> 'Backend Developer'
                        header_title_match = re.search(r"(?:Job|Position)?\s*\d*\s*[:\-]?\s*(.+)", current_header, re.IGNORECASE)
                        if header_title_match and header_title_match.group(1).strip():
                            extracted_title = header_title_match.group(1).strip()
                    
                    job = cls.parse_single_text(combined_text, job_id=f"job-{len(jobs)+1}", title=extracted_title)
                    jobs.append(job)
                    current_header = ""
        
        if not jobs and text.strip():
            # If no delimiters found, treat as 1 job
            jobs.append(cls.parse_single_text(text.strip(), job_id="job-1"))
            
        return jobs

    @classmethod
    def parse_from_csv(cls, csv_content: Union[str, bytes]) -> List[JobPosting]:
        """Parse jobs from CSV content with columns like title, company, description, etc."""
        if isinstance(csv_content, bytes):
            csv_text = csv_content.decode("utf-8", errors="ignore")
        else:
            csv_text = csv_content

        reader = csv.DictReader(io.StringIO(csv_text))
        jobs = []
        for i, row in enumerate(reader):
            # Normalize keys to lowercase
            norm_row = {k.strip().lower(): v.strip() for k, v in row.items() if k}
            
            title = norm_row.get("title") or norm_row.get("job_title") or norm_row.get("position") or f"Role #{i+1}"
            company = norm_row.get("company") or norm_row.get("company_name") or norm_row.get("employer") or "Hiring Company"
            desc = (
                norm_row.get("description") 
                or norm_row.get("job_description") 
                or norm_row.get("jd") 
                or norm_row.get("details") 
                or " ".join(norm_row.values())
            )
            job_id = norm_row.get("id") or norm_row.get("job_id") or f"job-{i+1}"
            
            if desc and len(desc.strip()) > 20:
                jobs.append(cls.parse_single_text(desc, job_id=job_id, title=title, company=company))

        return jobs

    @classmethod
    def parse_from_json(cls, json_content: Union[str, bytes, List[Dict[str, Any]]]) -> List[JobPosting]:
        """Parse jobs from JSON list of dictionaries."""
        if isinstance(json_content, bytes):
            data = json.loads(json_content.decode("utf-8"))
        elif isinstance(json_content, str):
            data = json.loads(json_content)
        else:
            data = json_content

        if isinstance(data, dict):
            data = data.get("jobs", [data])

        jobs = []
        for i, item in enumerate(data):
            title = item.get("title") or item.get("job_title") or f"Role #{i+1}"
            company = item.get("company") or item.get("company_name") or "Hiring Company"
            desc = item.get("description") or item.get("raw_text") or str(item)
            job_id = str(item.get("id", f"job-{i+1}"))
            
            if desc:
                jobs.append(cls.parse_single_text(desc, job_id=job_id, title=title, company=company))

        return jobs

    @classmethod
    async def fetch_and_parse_url(cls, url: str) -> JobPosting:
        """Fetch a job posting from a public web URL and extract content."""
        if httpx is None or BeautifulSoup is None:
            raise ImportError("httpx and beautifulsoup4 are required for URL scraping.")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            html = resp.text

        soup = BeautifulSoup(html, "html.parser")
        
        # Remove scripts, styles, navigations
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        title_tag = soup.find("h1") or soup.find("title")
        title = title_tag.get_text().strip() if title_tag else "Scraped Job Posting"
        
        # Extract main text
        body_text = soup.get_text(separator="\n")
        clean_text = "\n".join(line.strip() for line in body_text.split("\n") if line.strip())

        return cls.parse_single_text(clean_text, title=title[:80], company="Online Posting")

    @staticmethod
    def _extract_title_from_text(text: str) -> str:
        """Extract job title from header or first line."""
        match = re.search(r"(?:Job Title|Position|Role|Title)\s*:\s*([^\n]+)", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        first_line = [l.strip() for l in text.split("\n") if l.strip()][0]
        if len(first_line) < 60:
            return first_line
        return "Target Position"

    @staticmethod
    def _extract_company_from_text(text: str) -> str:
        """Extract company name."""
        match = re.search(r"(?:Company|Employer|Organization|Hiring Organization)\s*:\s*([^\n]+)", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return "Confidential / Hiring Co."

    @staticmethod
    def _extract_experience_requirement(text: str) -> str:
        """Extract required years of experience."""
        match = re.search(r"(\d+\+?\s*(?:-\s*\d+)?\s*(?:years|yrs)\s*(?:of\s*)?experience)", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return "Not explicitly specified"

    @staticmethod
    def _extract_key_skills(text: str) -> List[str]:
        """Extract technical and domain skills required in JD."""
        keywords = [
            "python", "sql", "excel", "power bi", "tableau", "aws", "azure", "gcp",
            "docker", "kubernetes", "fastapi", "react", "machine learning", "deep learning",
            "llm", "statistics", "data modeling", "etl", "snowflake", "spark", "git",
            "ci/cd", "rest api", "postgresql", "data pipelines", "jira", "communication"
        ]
        found = []
        lower = text.lower()
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}\b", lower):
                found.append(kw.title() if len(kw) > 3 else kw.upper())
        return found[:15]

