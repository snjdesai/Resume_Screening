import os
import streamlit as st

from config import *
from utils.helper import create_folder, save_upload_file

from src.services.resume_service import ResumeService
from src.services.jd_service import JDService
from src.services.ats_service import ATSService
from src.services.embedding_service import EmbeddingService
from src.services.ranking_service import RankingService

# ---------------------------------------
# Initialize Services
# ---------------------------------------

resume_service = ResumeService()
jd_service = JDService()
ats_service = ATSService()
embedding_service = EmbeddingService()
ranking_service = RankingService()

# ---------------------------------------
# Create Required Folders
# ---------------------------------------

create_folder(RESUME_FOLDER)
create_folder(JD_FOLDER)

# ---------------------------------------
# Page Title
# ---------------------------------------

st.title("📄 Resume Upload")
st.write("Upload one Job Description and multiple resumes for ATS analysis.")

# ---------------------------------------
# Upload Job Description
# ---------------------------------------

st.subheader("Job Description")

jd = st.file_uploader(
    "Upload Job Description",
    type=ALLOWED_JD,
    accept_multiple_files=False
)

# ---------------------------------------
# Upload Resume
# ---------------------------------------

st.subheader("Candidate Resumes")

resumes = st.file_uploader(
    "Upload Resume(s)",
    type=ALLOWED_RESUME,
    accept_multiple_files=True
)

# ---------------------------------------
# Upload Button
# ---------------------------------------

if st.button("Upload Files"):

    # -----------------------------
    # Validation
    # -----------------------------

    if jd is None:
        st.error("Please upload Job Description.")
        st.stop()

    if not resumes:
        st.error("Please upload at least one resume.")
        st.stop()

    # -----------------------------
    # Save Job Description
    # -----------------------------

    jd_path = save_upload_file(jd, JD_FOLDER)

    # -----------------------------
    # Process JD
    # -----------------------------

    jd_text, jd_information = jd_service.process(jd_path)

    jd_embedding = embedding_service.jd_embedding(jd_text)
    st.session_state["jd_information"] = jd_information

    # -----------------------------
    # Process Resumes
    # -----------------------------

    parsed_resumes = []
    progress = st.progress(0)
    total = len(resumes)

    for index, resume in enumerate(resumes):
        resume_path = save_upload_file(resume,RESUME_FOLDER)
        candidate = resume_service.process_resume(resume_path)

        resume_embedding = embedding_service.resume_embedding(candidate.text)
        candidate.embedding = resume_embedding

        score = ranking_service.score(candidate, jd_information, resume_embedding, jd_embedding)

        candidate.ats_score = score["ATS Score"]
        candidate.skill_score = score["Skill Score"]
        candidate.semantic_score = score["Semantic Score"]
        candidate.experience_score = score["Experience Score"]
        candidate.education_score = score["Education Score"]
        candidate.certification_score = score["Certification Score"]
        candidate.matched_skills = score["Matched Skills"]
        candidate.missing_skills = score["Missing Skills"]    

        parsed_resumes.append(candidate)
        progress.progress((index + 1) / total)

    parsed_resumes = ranking_service.rank(parsed_resumes)

    st.session_state["parsed_resumes"] = parsed_resumes
    st.session_state["jd_information"] = jd_information
    st.success("Files Uploaded successfully.")

    st.metric("Candidates Processed", len(parsed_resumes))

    st.header("Job Description Summary")
    st.write("### Required Skills")
    st.write(jd_information["skills"])
    st.write("### Experience")
    st.write(jd_information["experience"])
    st.write("### Education")
    st.write(jd_information["education"])
    st.write("### Certifications")
    st.write(jd_information["certifications"])

    st.header("Resume Ranking")

    for rank, candidate in enumerate(parsed_resumes, start=1):
        with st.expander(f"🏆 Rank {rank} : {candidate.name}"):
            col1, col2 = st.columns(2)

            with col1:
                st.metric("ATS Score",f"{candidate.ats_score:.2f}%")
                st.progress(candidate.ats_score/100)

            with col2:
                st.metric("Semantic Score", f"{candidate.semantic_score:2f}%")

        st.markdown("---")

        st.subheader("Candidate Details")

        st.write("**Email:**", candidate.email)
        st.write("**Phone:**", candidate.phone)

        st.write("**Experience:**")
        st.write(candidate.experience)

        st.write("**Education:**")
        st.write(candidate.education)

        st.write("**Skills:**")
        st.write(candidate.skills)

        st.write("**Projects:**")
        st.write(candidate.projects)

        st.write("**Certifications:**")
        st.write(candidate.certifications)

        st.markdown("---")

        st.subheader("ATS Analysis")

        c1, c2 = st.columns(2)
        with c1:
            st.write("### Matched Skills")
            st.success(candidate.matched_skills)

        with c2:
            st.write("### Missing Skills")
            st.error(candidate.missing_skills)

        st.markdown("---")
        st.subheader("Score Breakdown")
        st.write(f"Skill Score : {candidate.skill_score:.2f}")
        st.write(f"Experience Score : {candidate.experience_score:.2f}")
        st.write(f"Education Score : {candidate.education_score:.2f}")
        st.write(f"Certification Score  : {candidate.certification_score:.2f}")
        st.write(f"Semantic Score : {candidate.semantic_score:.2f}")


  