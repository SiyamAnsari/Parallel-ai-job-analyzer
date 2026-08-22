"""
Curated sample candidate profiles and job postings for testing and one-click demos.
"""
from typing import List, Dict
from src.schemas.models import CandidateProfile, JobPosting

# Sample Candidates
SAMPLE_CANDIDATE_DATA_ANALYST = CandidateProfile(
    name="Muhammad Ahmed",
    target_title="Data Analyst",
    years_of_experience=3.5,
    skills=[
        "Python", "SQL", "Power BI", "Excel", "Pandas", "Tableau", 
        "Data Modeling", "ETL", "PostgreSQL", "Statistics", "Business Intelligence"
    ],
    experience_highlights=[
        "Built automated monthly sales & revenue reporting dashboards in Power BI used by executive leadership.",
        "Engineered Python and SQL ETL pipelines reducing reporting turnaround time by 45%.",
        "Performed customer churn analysis on 250k+ records using Pandas and statistical modeling.",
        "Collaborated across product and marketing teams to establish key metric definitions and KPIs."
    ],
    education=[
        "B.S. in Computer Science - University of Engineering & Technology",
        "Microsoft Certified: Power BI Data Analyst Associate",
        "Google Data Analytics Professional Certificate"
    ],
    raw_text="""Muhammad Ahmed
Email: ahmed.analytics@example.com | Phone: +1-555-0199 | Location: New York, NY
LinkedIn: linkedin.com/in/muhammad-ahmed-data | Portfolio: github.com/mahmed-data

PROFESSIONAL SUMMARY
Results-driven Data Analyst with 3.5+ years of experience turning raw data into strategic business insights. Proven expertise in SQL, Python, and Power BI dashboard development. Adept at automating ETL pipelines, streamlining cross-departmental reporting, and optimizing complex database queries for enterprise datasets.

CORE SKILLS
- Technical: Python (Pandas, NumPy, Matplotlib), SQL (PostgreSQL, MySQL, BigQuery), Power BI (DAX, Power Query), Tableau, Advanced Excel
- Analytics & BI: ETL Pipelines, Data Modeling, Exploratory Data Analysis (EDA), KPI Dashboards, A/B Testing, Churn Modeling
- Soft Skills: Stakeholder Management, Cross-Functional Collaboration, Executive Presentation

PROFESSIONAL EXPERIENCE
Data Analyst | Nexus Analytics Corp (2022 - Present)
- Designed and maintained 15+ automated Power BI dashboards tracking sales, customer acquisition, and inventory metrics for executive teams.
- Optimized legacy SQL queries and automated daily ETL pipelines using Python, reducing processing runtime by 45%.
- Partnered with marketing to evaluate multi-channel campaign ROI, identifying $120K in cost optimization opportunities.
- Trained 20+ non-technical team members on self-service reporting best practices.

Junior Data Specialist | Insight Metrics Ltd (2020 - 2022)
- Cleaned, validated, and normalized customer transactional datasets containing over 500,000 records using Python and SQL.
- Assisted senior analysts in building weekly executive reporting decks in Excel and Tableau.

EDUCATION & CERTIFICATIONS
- Bachelor of Science in Computer Science | UET (2016 - 2020)
- Microsoft Certified: Power BI Data Analyst Associate (PL-300)
- Google Data Analytics Professional Certificate"""
)

SAMPLE_CANDIDATE_FULL_STACK = CandidateProfile(
    name="Sarah Chen",
    target_title="Full Stack Software Engineer",
    years_of_experience=5.0,
    skills=[
        "TypeScript", "React", "Node.js", "Python", "FastAPI", "PostgreSQL", 
        "Docker", "AWS", "GraphQL", "Redis", "CI/CD", "Git", "Tailwind CSS"
    ],
    experience_highlights=[
        "Architected scalable microservices using FastAPI and Node.js serving 500k+ MAU.",
        "Built responsive React web applications with state management and design systems.",
        "Implemented containerized CI/CD pipelines on AWS ECS, improving release velocity by 60%."
    ],
    education=[
        "B.S. in Software Engineering - University of California, Berkeley",
        "AWS Certified Solutions Architect - Associate"
    ],
    raw_text="""Sarah Chen
Full Stack Software Engineer | sarah.chen@example.dev | San Francisco, CA
GitHub: github.com/sarahchen-dev | LinkedIn: linkedin.com/in/sarahchen

SUMMARY
Passionate Full Stack Engineer with 5 years of experience building high-traffic web applications, microservices, and distributed cloud systems. Specialized in TypeScript, React, Python/FastAPI, Node.js, and AWS cloud infrastructure.

SKILLS
- Frontend: React, Next.js, TypeScript, JavaScript, Tailwind CSS, Redux Toolkit
- Backend: Python (FastAPI, Django), Node.js (Express, NestJS), RESTful APIs, GraphQL
- Databases: PostgreSQL, Redis, MongoDB
- Cloud & DevOps: AWS (ECS, S3, Lambda, RDS), Docker, GitHub Actions, Terraform

EXPERIENCE
Senior Software Engineer | CloudScale Tech (2023 - Present)
- Led frontend and backend architecture for SaaS analytics portal processing 10M events/day.
- Created reusable React component library and reduced bundle size by 35%.
- Implemented real-time WebSocket notifications with Redis Pub/Sub.

Software Engineer | Apex Solutions (2021 - 2023)
- Built REST APIs in Python/FastAPI and integrated PostgreSQL database models with SQLAlchemy.
- Deployed microservices into Docker containers managed with AWS ECS."""
)

# Sample Jobs Batch for Data Analyst
SAMPLE_JOBS_BATCH: List[JobPosting] = [
    JobPosting(
        id="job-1",
        title="Senior Data Analyst - Business Intelligence",
        company="Fintech Innovators Inc.",
        location="Remote",
        experience_required="3-5 years",
        skills_required=["SQL", "Python", "Power BI", "DAX", "Fintech", "Data Modeling"],
        raw_text="""Position: Senior Data Analyst - Business Intelligence
Company: Fintech Innovators Inc.
Location: Remote (US / Global)

About the Role:
We are seeking an experienced and proactive Senior Data Analyst to join our Growth & Business Intelligence team. You will partner with business executives, product managers, and finance teams to transform complex transactional data into actionable business strategies.

Key Responsibilities:
- Build and optimize enterprise-scale Power BI dashboards using complex DAX and Power Query.
- Write highly performant SQL queries against PostgreSQL and Snowflake data warehouses.
- Use Python (Pandas, NumPy) for deep statistical analysis, anomaly detection, and customer lifecycle insights.
- Collaborate with data engineering to design robust data models and automated ETL workflows.
- Present quarterly performance metrics and forecasting models to C-suite leadership.

Qualifications & Requirements:
- 3+ years of hands-on data analysis and business intelligence experience.
- Advanced proficiency in SQL (joins, window functions, query optimization) and Python for data analysis.
- Proven track record building production-grade dashboards in Power BI or Tableau.
- Strong knowledge of relational databases (PostgreSQL) and data modeling principles.
- Outstanding communication and storytelling skills with non-technical stakeholders.
- Bachelor's degree in Computer Science, Statistics, Mathematics, or related field."""
    ),
    JobPosting(
        id="job-2",
        title="Data Engineer / Analytics Engineer",
        company="DataFlow Systems",
        location="Hybrid - New York, NY",
        experience_required="4+ years",
        skills_required=["Python", "SQL", "dbt", "Airflow", "Snowflake", "Spark", "AWS", "Docker"],
        raw_text="""Job Title: Analytics Engineer / Data Engineer
Company: DataFlow Systems
Location: New York, NY (Hybrid)

Overview:
DataFlow Systems is looking for a versatile Analytics Engineer to bridge the gap between business reporting and cloud infrastructure.

Responsibilities:
- Build and orchestrate production ETL/ELT pipelines using Apache Airflow and dbt.
- Maintain and scale cloud data warehouse infrastructure in Snowflake and AWS S3.
- Write modular, testable Python applications and PySpark batch jobs for large-scale data ingestion.
- Implement CI/CD pipelines using Docker and GitHub Actions for data transformations.
- Ensure data quality, lineage, and governance across all data pipelines.

Requirements:
- 4+ years of experience in data engineering, analytics engineering, or backend development.
- Deep expertise in dbt, Apache Airflow, and Snowflake.
- Strong programming skills in Python, PySpark, and advanced SQL.
- Experience with containerization (Docker) and AWS infrastructure (ECS, Lambda, S3).
- B.S. in Computer Science or equivalent."""
    ),
    JobPosting(
        id="job-3",
        title="Junior Data Scientist & BI Analyst",
        company="Alpha Health Analytics",
        location="Remote",
        experience_required="1-3 years",
        skills_required=["Python", "SQL", "Scikit-Learn", "Machine Learning", "Tableau", "Excel", "Statistics"],
        raw_text="""Job Title: Junior Data Scientist & BI Analyst
Company: Alpha Health Analytics
Location: Remote

Role Description:
Join our healthcare analytics team to develop predictive models and clinical reporting dashboards that impact patient care.

Key Duties:
- Develop predictive machine learning models in Python using Scikit-Learn for patient risk scoring.
- Perform exploratory data analysis and hypothesis testing on clinical and operational healthcare data.
- Build interactive reports in Tableau and Excel for medical staff and hospital administrators.
- Write SQL queries to extract data from electronic health records (EHR) databases.

Requirements:
- 1-3 years of experience in data analysis, data science, or healthcare informatics.
- Proficiency in Python (Pandas, Scikit-Learn, Statsmodels) and SQL.
- Familiarity with basic machine learning concepts (regression, classification, clustering).
- Strong Excel skills (Pivot Tables, formulas) and visualization tools (Tableau or Power BI).
- Degree in Data Science, Statistics, or Computer Science."""
    ),
    JobPosting(
        id="job-4",
        title="Product Operations & Reporting Specialist",
        company="SaaS Horizon",
        location="Austin, TX / Remote",
        experience_required="2+ years",
        skills_required=["Excel", "Power BI", "SQL", "Jira", "Stakeholder Communication", "SaaS Metrics"],
        raw_text="""Position: Product Operations & Reporting Specialist
Company: SaaS Horizon
Location: Austin, TX or Remote

Summary:
We are looking for an analytical Product Operations Specialist to track product usage KPIs, user churn, and customer feature adoption.

Responsibilities:
- Create weekly KPI decks and executive reports detailing MRR, Churn, and Feature Adoption.
- Maintain operational dashboards in Power BI and Google Sheets/Excel.
- Query SQL databases to validate product telemetry and user behavioral funnels.
- Manage ticketing and issue escalation workflows in Jira with cross-functional product teams.

Requirements:
- 2+ years of experience in product ops, business analytics, or SaaS operations.
- Strong SQL querying skills and proficiency in Power BI or Tableau.
- Expert-level Microsoft Excel skills.
- Great presentation and stakeholder management abilities."""
    )
]

