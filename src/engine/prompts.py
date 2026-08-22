"""
Prompt definitions and templates for structured AI analysis and tailoring.
"""

JOB_EVALUATION_SYSTEM_PROMPT = """You are an elite Executive Talent Acquisition Director and Principal Technical Recruiter with 20+ years of experience evaluating candidate resumes against job descriptions for Fortune 500 and top tech companies.

Your task is to conduct an exhaustive, objective, and multi-dimensional match evaluation between the candidate's profile and the target job description.

Be rigorous, realistic, and constructive. Avoid hallucination: evaluate strictly based on the candidate's provided experience and the job's explicit requirements.

You must output your analysis strictly as a valid JSON object matching the requested schema with no extra conversational text or markdown delimiters outside the JSON."""

JOB_EVALUATION_USER_PROMPT = """Candidate Profile:
Name: {candidate_name}
Target Title: {target_title}
Years of Experience: {years_of_experience}
Skills: {skills}
Experience Highlights:
{experience_highlights}
Education & Certifications:
{education}

Raw Candidate Resume/Text:
\"\"\"
{candidate_raw_text}
\"\"\"

------------------------------------
Target Job Description:
Job ID: {job_id}
Job Title: {job_title}
Company: {company}
Experience Required: {experience_required}
Key Required Skills: {skills_required}

Full Job Description:
\"\"\"
{job_raw_text}
\"\"\"

------------------------------------
Perform an in-depth analysis and return a JSON object with the following EXACT structure:
{{
  "overall_match_score": <float between 0.0 and 100.0>,
  "skill_score": <float between 0.0 and 100.0>,
  "experience_score": <float between 0.0 and 100.0>,
  "ats_score": <float between 0.0 and 100.0>,
  "domain_score": <float between 0.0 and 100.0>,
  "match_tier": "<exactly one of: '🔥 High Fit', '⚡ Medium Fit', '⚠️ Stretch / Low Fit'>",
  "executive_summary": "<2-3 sentence strategic summary of the candidate fit>",
  "key_strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "risk_factors_or_gaps": ["<gap 1>", "<gap 2>", "<gap 3>"],
  "skills_breakdown": {{
    "matched_skills": ["<skill1>", "<skill2>"],
    "missing_critical_skills": ["<critical_missing_skill1>", "<critical_missing_skill2>"],
    "missing_nice_to_have": ["<nice_to_have_skill1>", "<nice_to_have_skill2>"],
    "transferable_skills": ["<candidate_skill -> job_requirement mapping>"],
    "skill_match_score": <float between 0.0 and 100.0>
  }},
  "ats_optimization": {{
    "ats_score": <float between 0.0 and 100.0>,
    "missing_keywords": ["<high_priority_keyword1>", "<high_priority_keyword2>"],
    "formatting_recommendations": ["<recommendation 1>", "<recommendation 2>"],
    "bullet_point_improvements": ["<bullet improvement suggestion 1>", "<bullet improvement suggestion 2>"]
  }},
  "application_kit": {{
    "tailored_resume_bullets": [
      "<STAR-method bullet point with action verb and metrics tailored to this JD>",
      "<STAR-method bullet point with action verb and metrics tailored to this JD>",
      "<STAR-method bullet point with action verb and metrics tailored to this JD>"
    ],
    "elevator_pitch": "<2-3 sentence personalized pitch for the cover letter or hiring manager message>",
    "interview_questions": [
      {{
        "question": "<High probability technical or situational question testing a key requirement or gap>",
        "category": "Technical",
        "recommended_talking_point": "<How candidate should frame past projects to answer effectively>"
      }},
      {{
        "question": "<High probability behavioral question testing collaboration or delivery>",
        "category": "Behavioral",
        "recommended_talking_point": "<Key talking point emphasizing ownership and impact>"
      }},
      {{
        "question": "<High probability domain question testing specific tools or methodology>",
        "category": "Domain & Problem Solving",
        "recommended_talking_point": "<Key talking point connecting transferable skills to this job>"
      }}
    ]
  }}
}}
"""

RESUME_EXTRACTION_PROMPT = """Extract the candidate profile information from the following resume text into a clean JSON structure:
Resume Text:
\"\"\"
{resume_text}
\"\"\"

Return ONLY a JSON object with keys:
- "name": candidate name (or "Candidate")
- "target_title": target or latest job title
- "years_of_experience": estimated years of experience (float)
- "skills": list of technical and professional skills
- "experience_highlights": list of 3-5 major achievements/responsibilities
- "education": list of degrees and certifications
"""

