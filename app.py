"""
Streamlit Production Web Dashboard for Parallel AI Job Analyzer.
"""
import asyncio
import time
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.config import settings
from src.schemas.models import CandidateProfile, JobPosting, BatchAnalysisReport, JobAnalysisResult
from src.parsers.resume_parser import ResumeParser
from src.parsers.job_parser import JobParser
from src.engine.analyzer import ParallelJobAnalyzer
from src.engine.llm_factory import LLMFactory
from src.exporters.report_generator import ReportGenerator
from src.data.sample_data import (
    SAMPLE_CANDIDATE_DATA_ANALYST,
    SAMPLE_CANDIDATE_FULL_STACK,
    SAMPLE_JOBS_BATCH
)

st.set_page_config(
    page_title="Parallel AI Job Analyzer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    .badge-high {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
    }
    .badge-med {
        background-color: #FEF08A;
        color: #713F12;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
    }
    .badge-low {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Session State
if "candidate" not in st.session_state:
    st.session_state.candidate = SAMPLE_CANDIDATE_DATA_ANALYST

if "jobs" not in st.session_state:
    st.session_state.jobs = list(SAMPLE_JOBS_BATCH)

if "analysis_report" not in st.session_state:
    st.session_state.analysis_report = None


# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/lightning-bolt.png", width=64)
    st.title("Settings & Controls")
    
    selected_model = st.selectbox(
        "Groq LLM Model",
        options=LLMFactory.get_available_models(),
        index=0,
        help="Select the Groq model for parallel inference"
    )
    
    concurrency_limit = st.slider(
        "Parallel Concurrency",
        min_value=1,
        max_value=10,
        value=5,
        help="Number of jobs evaluated simultaneously via asyncio"
    )
    
    api_key_input = st.text_input(
        "Groq API Key (optional override)",
        value="",
        type="password",
        help="Leave blank to use GROQ_API_KEY from .env"
    )
    
    st.divider()
    st.subheader("⚡ Quick Presets")
    
    col_pre1, col_pre2 = st.columns(2)
    with col_pre1:
        if st.button("📊 Data Analyst", use_container_width=True):
            st.session_state.candidate = SAMPLE_CANDIDATE_DATA_ANALYST
            st.session_state.jobs = list(SAMPLE_JOBS_BATCH)
            st.session_state.analysis_report = None
            st.success("Loaded Data Analyst Demo!")
            st.rerun()
            
    with col_pre2:
        if st.button("💻 Full Stack Dev", use_container_width=True):
            st.session_state.candidate = SAMPLE_CANDIDATE_FULL_STACK
            st.session_state.analysis_report = None
            st.success("Loaded Full Stack Profile!")
            st.rerun()

    st.divider()
    st.caption("Parallel AI Job Analyzer v1.0.0 • Production Ready")


# Header Banner
st.markdown('<div class="main-header">⚡ Parallel AI Job Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">High-Throughput Concurrent Job Matching, ATS Optimization & Career Tailoring</div>', unsafe_allow_html=True)

# Main Navigation Tabs
tab_cand, tab_jobs, tab_run, tab_lead, tab_detail, tab_export = st.tabs([
    "👤 1. Candidate Profile",
    "💼 2. Job Descriptions",
    "🚀 3. Parallel Execution",
    "📊 4. Match Leaderboard",
    "🔍 5. Deep-Dive & Action Kit",
    "📥 6. Export Center"
])


# ================= TAB 1: CANDIDATE PROFILE =================
with tab_cand:
    st.subheader("Candidate Resume & Credentials")
    
    col_up, col_info = st.columns([1, 1])
    
    with col_up:
        uploaded_file = st.file_uploader(
            "Upload Resume (PDF, DOCX, TXT)",
            type=["pdf", "docx", "txt"],
            help="Upload your existing resume to automatically parse skills and experience"
        )
        if uploaded_file is not None:
            try:
                parsed_profile = ResumeParser.parse_to_profile(
                    raw_text_or_file=uploaded_file.getvalue(),
                    filename=uploaded_file.name
                )
                st.session_state.candidate = parsed_profile
                st.success(f"Successfully extracted profile from {uploaded_file.name}!")
            except Exception as e:
                st.error(f"Error parsing uploaded file: {e}")

        cand_name = st.text_input("Candidate Name", value=st.session_state.candidate.name or "")
        target_title = st.text_input("Target Title", value=st.session_state.candidate.target_title or "")
        cand_exp = st.number_input("Years of Experience", min_value=0.0, max_value=40.0, value=float(st.session_state.candidate.years_of_experience or 0.0), step=0.5)

    with col_info:
        raw_text_val = st.text_area(
            "Resume Text / Bio",
            value=st.session_state.candidate.raw_text,
            height=260,
            help="Full text extracted or pasted from resume"
        )
        
        # Save edits to session state
        st.session_state.candidate.name = cand_name
        st.session_state.candidate.target_title = target_title
        st.session_state.candidate.years_of_experience = cand_exp
        st.session_state.candidate.raw_text = raw_text_val

    st.markdown("##### Extracted Key Skills")
    if st.session_state.candidate.skills:
        st.write(" ".join(f"`{s}`" for s in st.session_state.candidate.skills))
    else:
        st.info("No explicit skills extracted yet.")


# ================= TAB 2: JOB DESCRIPTIONS =================
with tab_jobs:
    st.subheader("Target Job Descriptions Queue")
    
    col_j_list, col_j_add = st.columns([1.2, 1])
    
    with col_j_add:
        st.markdown("##### ➕ Add / Import Jobs")
        add_method = st.radio("Input Mode", ["Manual Entry", "Upload CSV / JSON", "Bulk Text Paste"], horizontal=True)
        
        if add_method == "Manual Entry":
            new_title = st.text_input("Job Title", placeholder="e.g. Senior Data Engineer")
            new_company = st.text_input("Company", placeholder="e.g. Acme Cloud Corp")
            new_text = st.text_area("Job Description Details", height=150, placeholder="Paste the job description here...")
            if st.button("Add Job to Queue", use_container_width=True):
                if new_text.strip():
                    new_job = JobParser.parse_single_text(new_text, title=new_title or None, company=new_company or None)
                    st.session_state.jobs.append(new_job)
                    st.success(f"Added {new_job.title} to batch!")
                    st.rerun()
                else:
                    st.warning("Please provide job description text.")
                    
        elif add_method == "Upload CSV / JSON":
            job_file = st.file_uploader("Upload Jobs File", type=["csv", "json"])
            if job_file is not None:
                if st.button("Import Jobs from File", use_container_width=True):
                    try:
                        content = job_file.getvalue()
                        if job_file.name.endswith(".csv"):
                            imported = JobParser.parse_from_csv(content)
                        else:
                            imported = JobParser.parse_from_json(content)
                        st.session_state.jobs.extend(imported)
                        st.success(f"Imported {len(imported)} jobs!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to import: {e}")
                        
        elif add_method == "Bulk Text Paste":
            bulk_text = st.text_area("Paste multiple JDs separated by '---' or 'Job 1:', 'Job 2:'", height=180)
            if st.button("Parse Bulk Jobs", use_container_width=True):
                parsed = JobParser.parse_multiple_from_text(bulk_text)
                st.session_state.jobs.extend(parsed)
                st.success(f"Parsed and added {len(parsed)} jobs!")
                st.rerun()

    with col_j_list:
        st.markdown(f"##### 📋 Current Queue ({len(st.session_state.jobs)} Jobs)")
        if st.session_state.jobs:
            for idx, j in enumerate(st.session_state.jobs):
                with st.expander(f"{idx+1}. {j.title} @ {j.company} (ID: {j.id})", expanded=(idx == 0)):
                    st.write(f"**Experience:** {j.experience_required}")
                    st.write(f"**Key Skills:** {', '.join(j.skills_required) if j.skills_required else 'Extracted in analysis'}")
                    st.caption(j.raw_text[:200] + "..." if len(j.raw_text) > 200 else j.raw_text)
                    if st.button(f"🗑 Remove Job #{idx+1}", key=f"del_{idx}"):
                        st.session_state.jobs.pop(idx)
                        st.rerun()
            
            if st.button("Clear All Jobs Queue", type="secondary"):
                st.session_state.jobs = []
                st.rerun()
        else:
            st.info("No jobs in queue. Add jobs using the form on the right or click 'Data Analyst' in the sidebar.")


# ================= TAB 3: PARALLEL EXECUTION =================
with tab_run:
    st.subheader("⚡ High-Throughput Parallel Batch Analyzer")
    
    st.write(
        f"Ready to evaluate **{len(st.session_state.jobs)} jobs** concurrently for **{st.session_state.candidate.name}** "
        f"using **{selected_model}** with **{concurrency_limit} concurrent workers**."
    )
    
    if len(st.session_state.jobs) == 0:
        st.warning("Please add at least 1 job to the queue in Tab 2.")
    else:
        if st.button("🚀 Run Parallel AI Analysis", type="primary", use_container_width=True):
            progress_bar = st.progress(0.0)
            status_text = st.empty()
            
            analyzer = ParallelJobAnalyzer(
                model_name=selected_model,
                concurrency_limit=concurrency_limit,
                api_key=api_key_input if api_key_input else None
            )

            # Define async callback
            def progress_hook(completed, total, result):
                ratio = completed / total
                progress_bar.progress(ratio)
                status_text.markdown(f"⚡ **Evaluated {completed}/{total}**: *{result.job_title}* ({result.execution_time_seconds:.2f}s)")

            with st.spinner("Processing jobs in parallel across Groq async workers..."):
                report = asyncio.run(
                    analyzer.analyze_batch_parallel(
                        candidate=st.session_state.candidate,
                        jobs=st.session_state.jobs,
                        progress_callback=progress_hook
                    )
                )
                st.session_state.analysis_report = report
            
            progress_bar.progress(1.0)
            status_text.success(f"✔ Completed {report.total_jobs_analyzed} jobs in {report.total_batch_duration_seconds:.2f} seconds!")
            st.rerun()

    # Show live summary if report exists
    if st.session_state.analysis_report:
        rep: BatchAnalysisReport = st.session_state.analysis_report
        st.divider()
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Jobs Analyzed", rep.total_jobs_analyzed)
        m2.metric("Average Match Score", f"{rep.average_match_score}%")
        m3.metric("Batch Processing Time", f"{rep.total_batch_duration_seconds:.2f}s")
        if rep.best_matching_job:
            m4.metric("Top Matching Role", f"{rep.best_matching_job.overall_score}%", help=f"{rep.best_matching_job.job_title} @ {rep.best_matching_job.company}")


# ================= TAB 4: MATCH LEADERBOARD =================
with tab_lead:
    st.subheader("📊 Comparative Match Leaderboard")
    
    if not st.session_state.analysis_report:
        st.info("Run parallel analysis in Tab 3 to see the comparison leaderboard.")
    else:
        rep = st.session_state.analysis_report
        
        # Build DataFrame
        df_rows = []
        for i, item in enumerate(rep.comparison_table, 1):
            df_rows.append({
                "Rank": i,
                "Job Title": item.job_title,
                "Company": item.company,
                "Overall Score (%)": item.overall_score,
                "Match Tier": item.match_tier,
                "Skill Match (%)": item.skill_score,
                "Experience Match (%)": item.experience_score,
                "ATS Compatibility (%)": item.ats_score,
                "Top Gaps": ", ".join(item.top_missing_skills) if item.top_missing_skills else "None",
                "Latency (s)": f"{item.processing_time:.2f}s"
            })
            
        df = pd.DataFrame(df_rows)
        
        # Plotly Bar Chart
        fig = px.bar(
            df,
            x="Job Title",
            y="Overall Score (%)",
            color="Overall Score (%)",
            color_continuous_scale="Viridis",
            text="Overall Score (%)",
            hover_data=["Company", "Match Tier", "Skill Match (%)", "ATS Compatibility (%)"],
            title="Overall Fit Score by Job Posting"
        )
        fig.update_layout(xaxis_tickangle=-25, height=380)
        st.plotly_chart(fig, use_container_width=True)
        
        # Interactive Table
        st.dataframe(df, use_container_width=True, hide_index=True)


# ================= TAB 5: DEEP DIVE & ACTION KIT =================
with tab_detail:
    st.subheader("🔍 In-Depth Fit Analysis & Tailoring Application Kit")
    
    if not st.session_state.analysis_report or not st.session_state.analysis_report.results:
        st.info("Run analysis in Tab 3 to inspect detailed job breakdowns.")
    else:
        rep = st.session_state.analysis_report
        
        job_options = {f"{r.job_title} @ {r.company} ({r.overall_match_score}%)": r.job_id for r in rep.results}
        selected_label = st.selectbox("Select Role to Inspect", list(job_options.keys()))
        selected_id = job_options[selected_label]
        
        res: JobAnalysisResult = next(r for r in rep.results if r.job_id == selected_id)
        
        # Scores Radar & Metrics
        c_score, c_summary = st.columns([1, 1.5])
        
        with c_score:
            categories = ['Skills', 'Experience', 'ATS Compatibility', 'Domain & Education']
            scores_vals = [res.skill_score, res.experience_score, res.ats_score, res.domain_score]
            
            radar_fig = go.Figure()
            radar_fig.add_trace(go.Scatterpolar(
                r=scores_vals + [scores_vals[0]],
                theta=categories + [categories[0]],
                fill='toself',
                name='Fit Dimensions',
                line_color='#2563EB'
            ))
            radar_fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False,
                height=300,
                margin=dict(l=30, r=30, t=20, b=20)
            )
            st.plotly_chart(radar_fig, use_container_width=True)
            
        with c_summary:
            tier_class = "badge-high" if "High" in res.match_tier else ("badge-med" if "Medium" in res.match_tier else "badge-low")
            st.markdown(f"### {res.job_title}")
            st.markdown(f"**Company:** {res.company} | **Overall Match:** <span class='{tier_class}'>{res.overall_match_score}% - {res.match_tier}</span>", unsafe_allow_html=True)
            st.write(f"**Executive Assessment:** {res.executive_summary}")
            
            if res.key_strengths:
                st.markdown("**🌟 Key Strengths:**")
                for s in res.key_strengths:
                    st.markdown(f"- {s}")

        st.divider()

        # Skill & ATS Grid
        col_sk, col_ats = st.columns(2)
        with col_sk:
            st.markdown("#### 🛠 Skill Match Matrix")
            st.write(f"**Matched Skills:**")
            if res.skills_breakdown.matched_skills:
                st.write(" ".join(f"`{s}`" for s in res.skills_breakdown.matched_skills))
            else:
                st.write("None explicitly matched.")
                
            st.write(f"**Critical Missing Skills:**")
            if res.skills_breakdown.missing_critical_skills:
                for gap in res.skills_breakdown.missing_critical_skills:
                    st.markdown(f"- 🔴 **{gap}**")
            else:
                st.write("No major critical skill gaps identified!")
                
            if res.skills_breakdown.missing_nice_to_have:
                st.write(f"**Bonus / Preferred Gaps:**")
                for b in res.skills_breakdown.missing_nice_to_have:
                    st.markdown(f"- 🟡 {b}")

        with col_ats:
            st.markdown("#### 🎯 ATS Compatibility & Keywords")
            st.metric("ATS Pass Probability", f"{res.ats_optimization.ats_score}%")
            if res.ats_optimization.missing_keywords:
                st.write("**Keywords to Add to Resume:**")
                st.write(" ".join(f"`{k}`" for k in res.ats_optimization.missing_keywords))
            
            if res.ats_optimization.formatting_recommendations:
                st.write("**Formatting & Layout Tips:**")
                for rec in res.ats_optimization.formatting_recommendations:
                    st.markdown(f"- 💡 {rec}")

        st.divider()

        # Application Kit
        st.markdown("#### 💼 Tailored Application Kit")
        
        # Pitch
        st.markdown("##### 1. Elevator Pitch / Cover Letter Opening")
        st.info(f"\"{res.application_kit.elevator_pitch}\"")
        
        # Resume Bullets
        st.markdown("##### 2. STAR-Method Tailored Resume Bullets")
        for idx, bullet in enumerate(res.application_kit.tailored_resume_bullets, 1):
            st.markdown(f"- **Bullet {idx}:** {bullet}")
            
        # Interview Prep
        st.markdown("##### 3. Tailored Interview Prep Questions & Strategy")
        for q_idx, q in enumerate(res.application_kit.interview_questions, 1):
            with st.expander(f"Question #{q_idx} [{q.category}]: {q.question}"):
                st.markdown(f"**Recommended Talking Point Strategy:**\n\n{q.recommended_talking_point}")


# ================= TAB 6: EXPORT CENTER =================
with tab_export:
    st.subheader("📥 Export Reports & Analytics")
    
    if not st.session_state.analysis_report:
        st.info("Run parallel analysis in Tab 3 to generate exportable reports.")
    else:
        rep = st.session_state.analysis_report
        
        c_pdf, c_csv, c_json = st.columns(3)
        
        with c_pdf:
            st.markdown("#### 📄 Executive Briefing PDF")
            st.write("Download a styled PDF executive report containing leaderboard and per-job kits.")
            try:
                pdf_bytes = ReportGenerator.to_pdf_bytes(rep)
                st.download_button(
                    label="⬇ Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"job_analysis_{rep.candidate_name.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"PDF generation error: {e}")
                
        with c_csv:
            st.markdown("#### 📊 Leaderboard CSV")
            st.write("Export tabular match scores and missing skill gaps to CSV.")
            csv_data = ReportGenerator.to_csv(rep)
            st.download_button(
                label="⬇ Download CSV Summary",
                data=csv_data,
                file_name=f"job_leaderboard_{rep.candidate_name.replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        with c_json:
            st.markdown("#### ⚙ Structured JSON")
            st.write("Export raw Pydantic JSON payload for downstream API or database ingestion.")
            json_data = ReportGenerator.to_json(rep)
            st.download_button(
                label="⬇ Download JSON Payload",
                data=json_data,
                file_name=f"job_analysis_{rep.candidate_name.replace(' ', '_')}.json",
                mime="application/json",
                use_container_width=True
            )

