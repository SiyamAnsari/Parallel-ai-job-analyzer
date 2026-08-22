"""
Multi-format report generator: PDF, CSV, and JSON.
"""
import io
import csv
import json
from typing import Union, Dict, Any, List
from pathlib import Path
from src.schemas.models import BatchAnalysisReport, JobAnalysisResult

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
except ImportError:
    letter = None


class ReportGenerator:
    """Generates enterprise-ready PDF, CSV, and JSON analysis reports."""

    @classmethod
    def to_csv(cls, report: BatchAnalysisReport) -> str:
        """Export batch comparison leaderboard to CSV string."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "Rank", "Job Title", "Company", "Overall Fit Score", "Match Tier",
            "Skill Score", "Experience Score", "ATS Score", "Missing Critical Skills",
            "Latency (s)"
        ])
        
        # Rows
        for i, item in enumerate(report.comparison_table, 1):
            writer.writerow([
                i,
                item.job_title,
                item.company,
                f"{item.overall_score}%",
                item.match_tier,
                f"{item.skill_score}%",
                f"{item.experience_score}%",
                f"{item.ats_score}%",
                "; ".join(item.top_missing_skills),
                f"{item.processing_time:.2f}s"
            ])
            
        return output.getvalue()

    @classmethod
    def to_json(cls, report: BatchAnalysisReport, indent: int = 2) -> str:
        """Export full analysis report to formatted JSON string."""
        return report.model_dump_json(indent=indent)

    @classmethod
    def to_pdf_bytes(cls, report: BatchAnalysisReport) -> bytes:
        """Generate a professionally styled PDF Executive Report using ReportLab."""
        if letter is None:
            raise ImportError("reportlab is required for PDF generation. Please install it.")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom typography styles
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#1E293B"),
            spaceAfter=6
        )
        
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=15
        )
        
        section_heading = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#0F172A"),
            spaceBefore=12,
            spaceAfter=8
        )
        
        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#334155")
        )
        
        bullet_style = ParagraphStyle(
            'ReportBullet',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#334155"),
            leftIndent=12
        )

        story = []

        # 1. Header Banner
        story.append(Paragraph(f"Parallel AI Job Analysis: Executive Brief", title_style))
        story.append(Paragraph(
            f"Candidate: <b>{report.candidate_name}</b> | Jobs Analyzed: <b>{report.total_jobs_analyzed}</b> | "
            f"Average Fit: <b>{report.average_match_score}%</b> | Batch Runtime: <b>{report.total_batch_duration_seconds:.2f}s</b>",
            subtitle_style
        ))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#E2E8F0"), spaceAfter=14))

        # 2. Executive Leaderboard Table
        story.append(Paragraph("1. Multi-Job Fit Leaderboard", section_heading))
        
        table_data = [
            ["Rank", "Job Title & Company", "Overall", "Tier", "Skills", "Exp.", "ATS"]
        ]
        
        for rank, item in enumerate(report.comparison_table, 1):
            table_data.append([
                str(rank),
                f"{item.job_title}\n({item.company})",
                f"{item.overall_score}%",
                item.match_tier,
                f"{item.skill_score}%",
                f"{item.experience_score}%",
                f"{item.ats_score}%"
            ])

        leaderboard_table = Table(table_data, colWidths=[35, 230, 50, 95, 45, 45, 40])
        leaderboard_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('FONTSIZE', (0, 1), (-1, -1), 8.5),
        ]))
        story.append(leaderboard_table)
        story.append(Spacer(1, 15))

        # 3. Detailed Per-Job Breakdowns
        story.append(Paragraph("2. Detailed Job Fit & Tailoring Kits", section_heading))
        
        for res in report.results:
            job_block = []
            
            # Job Header
            tier_color = "#10B981" if "High" in res.match_tier else ("#F59E0B" if "Medium" in res.match_tier else "#EF4444")
            job_block.append(Paragraph(
                f"<b>{res.job_title}</b> — <font color='{tier_color}'><b>{res.overall_match_score}% ({res.match_tier})</b></font><br/>"
                f"<font color='#64748B'>{res.company} | Latency: {res.execution_time_seconds:.2f}s</font>",
                ParagraphStyle('JobSubHead', parent=styles['Heading3'], fontSize=11, leading=14, spaceBefore=8, spaceAfter=4)
            ))
            
            # Summary
            job_block.append(Paragraph(f"<b>Summary:</b> {res.executive_summary}", body_style))
            job_block.append(Spacer(1, 4))
            
            # Key Strengths & Gaps
            if res.key_strengths:
                job_block.append(Paragraph(f"<b>✅ Strengths:</b> {', '.join(res.key_strengths[:3])}", body_style))
            if res.skills_breakdown.missing_critical_skills:
                job_block.append(Paragraph(
                    f"<b>❌ Critical Gaps:</b> {', '.join(res.skills_breakdown.missing_critical_skills[:3])}",
                    body_style
                ))
            if res.ats_optimization.missing_keywords:
                job_block.append(Paragraph(
                    f"<b>🎯 ATS Keywords to Add:</b> {', '.join(res.ats_optimization.missing_keywords[:4])}",
                    body_style
                ))

            # Application Pitch
            if res.application_kit.elevator_pitch:
                job_block.append(Spacer(1, 3))
                job_block.append(Paragraph(
                    f"<b>💼 Recommended Pitch:</b> <i>\"{res.application_kit.elevator_pitch}\"</i>",
                    body_style
                ))

            # Tailored Bullets
            if res.application_kit.tailored_resume_bullets:
                job_block.append(Spacer(1, 3))
                job_block.append(Paragraph("<b>📝 Tailored Resume Bullets:</b>", body_style))
                for bullet in res.application_kit.tailored_resume_bullets[:2]:
                    job_block.append(Paragraph(f"• {bullet}", bullet_style))

            job_block.append(Spacer(1, 8))
            job_block.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0"), spaceAfter=8))
            
            story.append(KeepTogether(job_block))

        doc.build(story)
        return buffer.getvalue()

