"""
Application tailoring module providing STAR-method bullet points, cover letter pitches, and interview prep.
"""
from typing import List, Dict, Any
from src.schemas.models import CandidateProfile, JobPosting, ApplicationKit, InterviewPrepQuestion


class ApplicationTailor:
    """Generates personalized resume bullets, elevator pitch, and interview talking points."""

    @classmethod
    def generate_fallback_application_kit(cls, candidate: CandidateProfile, job: JobPosting, missing_skills: List[str]) -> ApplicationKit:
        """Deterministic fallback generator for application kit when LLM output is partial."""
        # 1. Tailored Bullets
        bullets = []
        for highlight in candidate.experience_highlights[:2]:
            bullets.append(f"Accelerated business impact by leveraging {', '.join(candidate.skills[:3])} to {highlight.lower().strip('.')}.")
        if job.skills_required:
            bullets.append(f"Applied core principles of {', '.join(job.skills_required[:2])} to optimize workflow efficiency and cross-functional reporting.")
        if not bullets:
            bullets = [
                f"Led data-driven initiatives delivering measurable performance improvements using {', '.join(candidate.skills[:2])}.",
                "Collaborated with cross-functional stakeholders to translate requirements into scalable solutions."
            ]

        # 2. Elevator Pitch
        pitch = (
            f"As an experienced {candidate.target_title or 'professional'} with a proven background in "
            f"{', '.join(candidate.skills[:3])}, I bring hands-on experience driving measurable outcomes. "
            f"I am eager to apply my analytical and problem-solving skills to help {job.company} achieve its growth objectives as {job.title}."
        )

        # 3. Interview Questions
        questions = []
        if missing_skills:
            gap = missing_skills[0]
            questions.append(
                InterviewPrepQuestion(
                    question=f"This role requires experience with {gap}. Can you discuss how you would ramp up or apply related tools you have used?",
                    category="Technical / Gap Mitigation",
                    recommended_talking_point=f"Highlight your experience in {', '.join(candidate.skills[:2])} and demonstrate how rapidly you have mastered adjacent tools in past projects."
                )
            )
        questions.append(
            InterviewPrepQuestion(
                question=f"How do you prioritize complex deliverables when collaborating with cross-functional teams at {job.company}?",
                category="Behavioral",
                recommended_talking_point="Discuss structured requirement gathering, proactive stakeholder communication, and iterative delivery."
            )
        )
        questions.append(
            InterviewPrepQuestion(
                question=f"Walk us through your most impactful project related to {job.title}.",
                category="System & Delivery",
                recommended_talking_point="Follow the STAR method (Situation, Task, Action, Result) focusing on quantifiable business metrics and tool stack."
            )
        )

        return ApplicationKit(
            tailored_resume_bullets=bullets,
            elevator_pitch=pitch,
            interview_questions=questions
        )

