"""
CLI Entry point for Parallel AI Job Analyzer.
Provides high-performance batch analysis directly in the terminal with rich formatting.
"""
import sys
import os
import argparse
import asyncio
import time
from pathlib import Path

# Ensure UTF-8 output on Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv
load_dotenv()

from src.config import settings
from src.schemas.models import CandidateProfile, JobPosting
from src.parsers.resume_parser import ResumeParser
from src.parsers.job_parser import JobParser
from src.engine.analyzer import ParallelJobAnalyzer
from src.exporters.report_generator import ReportGenerator
from src.data.sample_data import SAMPLE_CANDIDATE_DATA_ANALYST, SAMPLE_JOBS_BATCH

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich import print as rprint
    console = Console(force_terminal=True, legacy_windows=False)
except ImportError:
    Console = None
    console = None


def print_banner():
    """Print welcoming CLI banner."""
    if console:
        console.print(
            Panel.fit(
                "[bold cyan]⚡ PARALLEL AI JOB ANALYZER[/bold cyan] [bold yellow]v1.0.0[/bold yellow]\n"
                "[dim]High-Throughput Parallel Evaluation | Groq LLM Inference | ATS & Career Tailoring[/dim]",
                border_style="cyan"
            )
        )
    else:
        print("=" * 60)
        print("⚡ PARALLEL AI JOB ANALYZER v1.0.0")
        print("High-Throughput Parallel Evaluation | Groq LLM Inference")
        print("=" * 60)


async def run_batch_cli(
    candidate: CandidateProfile,
    jobs: list[JobPosting],
    concurrency: int = 5,
    model: str = "openai/gpt-oss-120b",
    export_prefix: str = "job_analysis_report"
):
    """Run batch analysis and render rich console output."""
    analyzer = ParallelJobAnalyzer(
        model_name=model,
        concurrency_limit=concurrency
    )

    if console:
        console.print(f"\n[bold green]👤 Candidate:[/bold green] [bold]{candidate.name}[/bold] ({candidate.target_title or 'Candidate'})")
        console.print(f"[bold blue]💼 Jobs in Batch:[/bold blue] {len(jobs)} postings")
        console.print(f"[bold magenta]⚡ Concurrency:[/bold magenta] {concurrency} parallel workers")
        console.print(f"[bold yellow]🤖 Model:[/bold yellow] {model}\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task_id = progress.add_task("[cyan]Analyzing jobs concurrently...", total=len(jobs))

            def on_progress(completed, total, result):
                progress.update(task_id, completed=completed, description=f"[cyan]Completed {completed}/{total}: [bold]{result.job_title}[/bold]")

            report = await analyzer.analyze_batch_parallel(
                candidate=candidate,
                jobs=jobs,
                progress_callback=on_progress
            )
    else:
        print(f"\nAnalyzing {len(jobs)} jobs concurrently...")
        report = await analyzer.analyze_batch_parallel(candidate=candidate, jobs=jobs)

    # Display Leaderboard Table
    display_results(report)

    # Save exports
    csv_out = f"{export_prefix}.csv"
    json_out = f"{export_prefix}.json"
    
    Path(csv_out).write_text(ReportGenerator.to_csv(report), encoding="utf-8")
    Path(json_out).write_text(ReportGenerator.to_json(report), encoding="utf-8")

    try:
        pdf_out = f"{export_prefix}.pdf"
        pdf_bytes = ReportGenerator.to_pdf_bytes(report)
        Path(pdf_out).write_bytes(pdf_bytes)
        pdf_msg = f", PDF: [bold]{pdf_out}[/bold]"
    except Exception as e:
        pdf_msg = ""

    if console:
        console.print(f"\n[bold green]✔ Exports saved:[/bold green] CSV: [bold]{csv_out}[/bold], JSON: [bold]{json_out}[/bold]{pdf_msg}\n")
    else:
        print(f"\n✔ Exports saved: {csv_out}, {json_out}")

    return report


def display_results(report):
    """Display leaderboard and drilldown in terminal."""
    if not console:
        print(f"\n--- Results Summary (Average Match: {report.average_match_score}%) ---")
        for item in report.comparison_table:
            print(f"[{item.overall_score}%] {item.job_title} @ {item.company} | Tier: {item.match_tier} | Latency: {item.processing_time:.2f}s")
        return

    table = Table(title=f"📊 Multi-Job Match Leaderboard (Batch Duration: {report.total_batch_duration_seconds:.2f}s)", header_style="bold magenta")
    table.add_column("Rank", justify="center", style="dim")
    table.add_column("Job Title", style="bold")
    table.add_column("Company", style="cyan")
    table.add_column("Overall Fit", justify="center")
    table.add_column("Tier", justify="center")
    table.add_column("Skills", justify="center")
    table.add_column("Exp.", justify="center")
    table.add_column("ATS", justify="center")
    table.add_column("Top Missing Skills", style="red")
    table.add_column("Time", justify="right", style="dim")

    for rank, item in enumerate(report.comparison_table, 1):
        score_color = "green" if item.overall_score >= 80 else ("yellow" if item.overall_score >= 60 else "red")
        table.add_row(
            str(rank),
            item.job_title,
            item.company,
            f"[{score_color} bold]{item.overall_score}%[/{score_color} bold]",
            item.match_tier,
            f"{item.skill_score}%",
            f"{item.experience_score}%",
            f"{item.ats_score}%",
            ", ".join(item.top_missing_skills) or "None",
            f"{item.processing_time:.2f}s"
        )

    console.print(table)

    # Print top job highlight
    if report.best_matching_job:
        best = next((r for r in report.results if r.job_id == report.best_matching_job.job_id), None)
        if best:
            console.print(
                Panel(
                    f"[bold green]🏆 TOP MATCH:[/bold green] [bold]{best.job_title}[/bold] at [bold cyan]{best.company}[/bold cyan] ({best.overall_match_score}%)\n\n"
                    f"[bold]Executive Summary:[/bold] {best.executive_summary}\n\n"
                    f"[bold]Recommended Pitch:[/bold] [italic]\"{best.application_kit.elevator_pitch}\"[/italic]\n\n"
                    f"[bold]Tailored Bullet Point:[/bold] • {best.application_kit.tailored_resume_bullets[0] if best.application_kit.tailored_resume_bullets else 'N/A'}",
                    title="Strategic Recommendation",
                    border_style="green"
                )
            )


def main():
    """Main CLI handler."""
    parser = argparse.ArgumentParser(description="Parallel AI Job Analyzer CLI")
    parser.add_argument("--resume", "-r", type=str, help="Path to resume file (PDF, DOCX, TXT)")
    parser.add_argument("--jobs", "-j", type=str, help="Path to jobs CSV, JSON, or TXT file")
    parser.add_argument("--concurrency", "-c", type=int, default=5, help="Number of parallel workers (default: 5)")
    parser.add_argument("--model", "-m", type=str, default="openai/gpt-oss-120b", help="Groq LLM model name")
    parser.add_argument("--export", "-e", type=str, default="job_analysis_report", help="Export file prefix")
    parser.add_argument("--demo", action="store_true", help="Run with curated sample dataset")

    args = parser.parse_args()

    print_banner()

    # Determine candidate
    if args.resume:
        print(f"Loading resume from {args.resume}...")
        candidate = ResumeParser.parse_to_profile(args.resume)
    else:
        if not args.demo and sys.stdin.isatty() and not args.jobs:
            if console:
                console.print("[dim]No resume provided. Using curated sample candidate (Muhammad Ahmed - Data Analyst)...[/dim]")
        candidate = SAMPLE_CANDIDATE_DATA_ANALYST

    # Determine jobs
    if args.jobs:
        jobs_path = Path(args.jobs)
        print(f"Loading jobs from {args.jobs}...")
        if jobs_path.suffix.lower() == ".csv":
            jobs = JobParser.parse_from_csv(jobs_path.read_text(encoding="utf-8"))
        elif jobs_path.suffix.lower() == ".json":
            jobs = JobParser.parse_from_json(jobs_path.read_text(encoding="utf-8"))
        else:
            jobs = JobParser.parse_multiple_from_text(jobs_path.read_text(encoding="utf-8"))
    else:
        jobs = SAMPLE_JOBS_BATCH

    asyncio.run(
        run_batch_cli(
            candidate=candidate,
            jobs=jobs,
            concurrency=args.concurrency,
            model=args.model,
            export_prefix=args.export
        )
    )


if __name__ == "__main__":
    main()