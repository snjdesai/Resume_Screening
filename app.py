import sys
import os
import json
import streamlit as st

# 1. Point directly to your Resume_Screening root directory
project_root = r"C:\Users\Sanjay Desai\Resume_Screening"
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 2. Force load configuration constants to access APP_TITLE, LAYOUT, etc.
try:
    from config import *
    from utils.helper import load_css
except ModuleNotFoundError as e:
    # Safe fallback if config files aren't found yet
    APP_TITLE = "AI Resume Screening System"
    PAGE_ICON = "🎯"
    LAYOUT = "wide"
    SIDEBAR_STATE = "expanded"

# 3. 🚨 FIX: st.set_page_config MUST run BEFORE any other pipeline logic
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state=SIDEBAR_STATE
)

# 4. Import the rest of your backend classes safely
if 'src.ranking' in sys.modules:
    del sys.modules['src.ranking']

try:
    from src.parser import ResumeParser
    from src.preprocess import TextPreprocessor
    from src.extractor import ResumeExtractor
    from src.jd_processor import JDProcessor
    from src.embedding import EmbeddingGenerator
    from src.ranking import ResumeRanker
    
    # Initialize your pipeline class objects once
    parser = ResumeParser()
    preprocessor = TextPreprocessor()
    resume_extractor = ResumeExtractor()
    jd = JDProcessor()
    embedder = EmbeddingGenerator()
    ranker = ResumeRanker() 

except ModuleNotFoundError as e:
    st.error(f"Critical Backend Import Error: {e}")
    st.stop()

# 5. --- UI Styling & Theme Loading ---
try:
    css = load_css(r"C:\Users\Sanjay Desai\Resume_Screening\assets\style.css")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
except Exception:
    pass # Graceful fallback if asset file is empty

st.markdown('<p class="main-title">AI Resume Screening System</p>', unsafe_allow_html=True)
st.divider()

# 6. --- Sidebar Navigation Setup ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page", ["Dashboard", "Upload Files", "Results"])

# 7. --- Page Routing Logic ---
if page == "Dashboard":
    st.header("Project Overview")
    st.write('''
    This application performs end-to-end automated talent matching by combining structural keyword matching with deep semantic vector representations.
    ''')

    # 🚨 FIX: Moved summary cards inside Dashboard view so they don't leak onto other pages
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Uploaded Resumes", 0)
    with col2:
        st.metric("Job Description", "Not Uploaded")
    with col3:
        st.metric("Best ATS Score", "0%")
    with col4:
        st.metric("Candidates Ranked", 0)

    st.subheader("System Workflow Processing Steps")
    st.write('''
    1️⃣ Upload Job Description  
    2️⃣ Upload Multiple Resumes  
    3️⃣ Resume Parsing  
    4️⃣ Text Cleaning  
    5️⃣ Information Extraction  
    6️⃣ Embedding Generation  
    7️⃣ ATS Score Calculation  
    8️⃣ Resume Ranking  
    ''')

# elif page == "Upload Files":
#     st.header("📂 Data Ingestion Layer")
#     st.write("Upload incoming candidate records and match specifications below.")
    
#     # 🚨 FIX: Instead of risky exec(), handle your layout directly or import clean page functions
#     col_jd, col_res = st.columns(2)
#     with col_jd:
#         st.subheader("📋 Step 1: Provide Job Requirements")
#         uploaded_jd = st.file_uploader("Upload JD Text template file (.txt)", type=["txt"])
#     with col_res:
#         st.subheader("📄 Step 2: Upload Resumes")
#         uploaded_resumes = st.file_uploader("Upload Candidate Profiles (.pdf)", type=["pdf"], accept_multiple_files=True)


elif page == "Upload Files":
    # with open(r"C:\Users\Sanjay Desai\Resume_Screening\Pages\upload.py","r",encoding="utf-8") as f:
    #     exec(f.read())
    st.header("📂 Data Ingestion & ATS Scoring Layer")
    st.write("Upload incoming candidate records and match specifications below.")
    
    col_jd, col_res = st.columns(2)
    
    with col_jd:
        st.subheader("📋 Step 1: Provide Job Requirements")
        uploaded_jd = st.file_uploader("Upload JD Text template file (.txt)", type=["txt"])
    
    with col_res:
        st.subheader("📄 Step 2: Upload Resumes")
        uploaded_resumes = st.file_uploader("Upload Candidate Profiles (.pdf)", type=["pdf"], accept_multiple_files=True)

    # 🚨 THE MATCHING ENGINE TRIGGER BUTTON
    if uploaded_jd and uploaded_resumes:
        st.markdown("---")
        if st.button("🚀 Run ATS Screening & Ranking Engine", use_container_width=True):
            with st.spinner("Processing documents, extracting fields, and running semantic matching..."):
                try:
                    # 1. Process the Job Description text directly from the uploader memory buffer [1]
                    jd_text = uploaded_jd.read().decode("utf-8")
                    jd_details = jd.process(jd_text)
                    structured_jd_input = jd_details if isinstance(jd_details, dict) else {"skills": [], "experience": 0}
                    
                    # Generate JD Embedding vector weight mapping
                    jd_embedding = embedder.generate_embedding(jd_details)

                    # Create a list to store batch candidate objects for sorting/display
                    processed_candidates = []

                    # 2. Loop through all uploaded resumes simultaneously
                    for resume_file in uploaded_resumes:
                        # Write the buffered stream to a temporary location for the PDF parser module [1]
                        temp_path = os.path.join(project_root, "data", "resumes", "temp_streamlit.pdf")
                        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                        with open(temp_path, "wb") as f:
                            f.write(resume_file.getbuffer())

                        # Run your verified parser and extraction steps
                        raw_resume = parser.read_pdf(temp_path)
                        clean_resume = preprocessor.preprocess(raw_resume)

                        structured_resume_input = {
                            "skills": resume_extractor.extract_skills(raw_resume),
                            "experience": resume_extractor.extract_experience(raw_resume),
                            "education": resume_extractor.extract_education(raw_resume),
                            "certification": resume_extractor.extract_certification(raw_resume)
                        }

                        # Generate Candidate Embedding vector
                        resume_embeddings = embedder.generate_embedding(clean_resume)

                        # Compute final scoring breakdowns using your fixed ranker
                        score_metrics = ranker.calculate_score(
                            resume=structured_resume_input,
                            jd=structured_jd_input,
                            resumee_embedding=resume_embeddings,
                            jd_embedding=jd_embedding
                        )

                        # Clean up the temporary file safely from disk
                        if os.path.exists(temp_path):
                            os.remove(temp_path)

                        # Save results to our data list
                        processed_candidates.append({
                            "Name": resume_extractor.extract_name(raw_resume) or resume_file.name,
                            "ATS Score": f"{score_metrics['ATS Score']}%",
                            "Skill Match": f"{score_metrics['Skill Score']}/40",
                            "Experience Match": f"{score_metrics['Experience Score']}/25",
                            "Semantic Similarity": f"{score_metrics['Semantic Score']}/10",
                            "Missing Skills": ", ".join(score_metrics['Missing skills'])
                        })

                    # 3. 🎉 DISPLAY THE INTERACTIVE OUTPUT LEADERBOARD RESULTS
                    st.success(f"Successfully evaluated and scored {len(processed_candidates)} candidate profiles!")
                    st.balloons()

                    # Sort candidates with the highest ATS scores at the top
                    processed_candidates = sorted(processed_candidates, key=lambda x: float(x['ATS Score'].replace('%', '')), reverse=True)

                    st.subheader("🏆 Candidate Ranking Leaderboard")
                    st.dataframe(processed_candidates, use_container_width=True)

                except Exception as pipeline_error:
                    st.error(f"An unexpected error occurred during processing: {pipeline_error}")
    else:
        st.info("💡 Please upload both a Job Description (.txt) and at least one Resume (.pdf) to unlock the screening button.")


elif page == "Results":
    st.header("📊 Analytical Ranking Rankings")
    st.write("The calculated multi-metric evaluation overview matrix will render below.")
    
    # Placeholder to execute your background parsing test values securely
    if st.checkbox("Run Pipeline System Core Health Test"):
        with st.spinner("Processing test dataset metrics..."):
            try:
                resume_text = parser.read_pdf(r"C:\Users\Sanjay Desai\Resume_Screening\data\resumes\SANJAY_DESAI.pdf")
                clean_resume = preprocessor.preprocess(resume_text)
                jd_text = jd.read_jd(r"C:\Users\Sanjay Desai\Resume_Screening\data\jd\ml_engineer_jd.txt")
                jd_details = jd.process(jd_text)
                
                st.success("Core Pipeline Status: Operational ✅")
                st.write(f"**Extracted Candidate:** {resume_extractor.extract_name(resume_text)}")
                st.write(f"**Extracted Skills:** {', '.join(resume_extractor.extract_skills(resume_text)[:6])}...")
            except Exception as test_err:
                st.error(f"Test Runtime Exception: {test_err}")

# 8. --- Persistent Global Footer Component ---
st.markdown("---")
st.markdown('''
    <div class='footer' style='text-align: center; color: gray;'>
    Developed using Python • Streamlit • NLP • Sentence Transformers • FAISS
    </div>
    ''', 
    unsafe_allow_html=True
)
