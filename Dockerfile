# 1. Start with an official, stable, and lightweight Python base image
FROM python:3.10-slim


# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy ONLY the requirements file first to utilize Docker layer caching
COPY requirements.txt .

# 4. Install the packages (Docker will cache this step)
RUN pip install --no-cache-dir -r requirements.txt
    

# 2. Set environment variables to keep Python clean inside the container
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 3. Set the active working directory inside the container virtual file structure
WORKDIR /app

# 4. Install system level dependencies required to compile tools like FAISS
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN python -m nltk.downloader punkt stopwords
RUN python -m spacy download en_core_web_sm

# 6. Install the exact Python tracking packages clean without storing cache artifacts
# 6. Install core package directly using an official wheel mirror
# RUN pip install --no-cache-dir streamlit --index-url https://pypi.org


# 7. Copy the entire remaining local directory assets into the working container directory
COPY . .

# 8. Create empty data directories to prevent temporary buffering runtime file path exceptions
RUN mkdir -p data/resumes data/jd assets

# 9. Inform Docker that the container will listen on Streamlit's default network port
EXPOSE 8501

# 10. Configure an automated health check to monitor app stability status
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 11. Define the executable runtime instruction command to launch the app natively
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
