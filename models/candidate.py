from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np


@dataclass
class Candidate:
    """
    Stores all extracted information about a candidate.
    """

    # -------------------------
    # Personal Information
    # -------------------------
    name: str = ""
    email: str = ""
    phone: str = ""

    # -------------------------
    # Resume Information
    # -------------------------
    skills: List[str] = field(default_factory=list)
    education: List[str] = field(default_factory=list)
    experience: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    projects: List[str] = field(default_factory=list)

    # Complete preprocessed resume text
    text: str = ""

    # -------------------------
    # AI / Embedding
    # -------------------------
    embedding: Optional[np.ndarray] = None

    # -------------------------
    # ATS Scores
    # -------------------------
    ats_score: float = 0.0
    skill_score: float = 0.0
    semantic_score: float = 0.0
    experience_score: float = 0.0
    education_score: float = 0.0
    certification_score: float = 0.0

    # -------------------------
    # Analysis
    # -------------------------
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "Name": self.name,
            "Email": self.email,
            "Phone": self.phone,
            "Skills": self.skills,
            "Education": self.education,
            "Experience": self.experience,
            "Certifications": self.certification,
            "Projects": self.project,
            "ATS Score": self.ats_score,
            "Skill Score": self.skill_score,
            "Semantic Score": self.semantic_score,
            "Experience Score": self.experience_score,
            "Education Score": self.education_score,
            "Certification Score": self.certification_score,
            "Matched Skills": self.matched_skills,
            "Missing Skills": self.missing_skills,
        }

    def __str__(self):
        return f"Candidate(name={self.name}, ATS={self.ats_score:.2f}%)"