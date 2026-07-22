import re
import spacy
import pandas as pd
import os

nlp = spacy.load("en_core_web_sm")

class ResumeExtractor:
    
    # def __init__(self):

    def __init__(self):
        # 1. Dynamically find the absolute path to your project root folder
        current_file_path = os.path.abspath(__file__)                    # Path to src/extractor.py
        src_folder = os.path.dirname(current_file_path)                  # Path to src/
        project_root = os.path.dirname(src_folder)                       # Path to Resume_Screening/
        
        # 2. Safely join paths so it works perfectly on both Windows and Linux Docker
        skills_path = os.path.join(project_root, "data", "skills.csv")
        
        # 3. Read the file cleanly
        #self.skills = pd.read_csv(skills_path)
        self.skills = pd.read_csv(skills_path)["Skill"].dropna().astype(str).tolist()

        # self.skills = pd.read_csv(
        #     r"C:\Users\Sanjay Desai\Resume_Screening\data\skills.csv"
        # )["Skill"].tolist()

    def extract_name(self, text):

        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
               return ent.text
        return None 

    def extract_email(self, text):

        emails = re.findall(r'\S+@\S+', text)
        return emails[0] if emails else None

    def extract_phone(self, text):

        phones = re.findall(r'\+?\d[\d\s\-]{8,}\d', text)
        return phones[0] if phones else None

    def extract_skills(self, text):
        skills = []
        lower_text = text.lower()
        
        for skill in self.skills:
            skill_clean = skill.strip().lower()
            if not skill_clean:
                continue
                
            # Use regex boundaries so "C" or "Go" doesn't match inside random words
            # Escape skill name to prevent regex errors with special characters like C++
            pattern = r'\b' + re.escape(skill_clean) + r'\b'
            if re.search(pattern, lower_text):
                skills.append(skill.strip())
                
        return list(set(skills))

    def extract_education(self, text):
        keywords = ["b.tech", "b.e", "m.tech", "master", "mba", "phd", "bachelor", "university", "college"]
        edu = []
        
        # FIXED: Iterate line by line to extract only education rows, not the whole text
        for line in text.split("\n"):
            line_lower = line.lower().strip()
            if any(kw in line_lower for kw in keywords):
                if line.strip():  # Avoid adding empty lines
                    edu.append(line.strip())
        return list(set(edu)) # Deduplicate lines

    def extract_experience(self, text):
        return re.findall( r'(\d+)\+?\s*(?:years?|yrs?)', text.lower())

    
    def extract_certification(self, text):

        keywords = ["aws", "azure", "gcp", "certified",]
        certs = []
        lower = text.lower()

        for word in keywords:
            if word in lower:
                certs.append(word)
        return certs

    def extract_project(self, text):

        projects = []
        for line in text.split("\n"):
            if "project" in line.lower():
                projects.append(line)
        return projects

    # def extract(self, text):
    #     results = {}
    #     results["name"] = self.extract_name(text)
    #     results["email"] = self.extract_email(text)
    #     results["phone"] = self.extract_phone(text)
    #     results["skills"] = self.extract_skills(text)
    #     results["education"] = self.extract_education(text)
    #     results["experience"] = self.extract_experience(text)
    #     results["certifications"] = self.extract_certification(text)
    #     results["projects"] = self.extract_project(text)
    #     return results