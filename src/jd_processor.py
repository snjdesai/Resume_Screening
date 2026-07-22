import re
import pandas as pd
import os

class JDProcessor:

    def __init__(self):
        # 1. Dynamically track down the absolute root project folder path
        current_file_path = os.path.abspath(__file__)                    # Path to src/jd_processor.py
        src_folder = os.path.dirname(current_file_path)                  # Path to src/
        project_root = os.path.dirname(src_folder)                       # Path to Resume_Screening/
        
        # 2. Safely stitch the path together for the container system
        skills_path = os.path.join(project_root, "data", "skills.csv")
        
        # 3. Read the file cleanly
        self.skills = pd.read_csv(skills_path)

    def read_jd(self, filepath):
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read()

    def extract_skills(self, text):
        extracted = []
        text = text.lower()
        for skill in self.skills:
            if skill.lower() in text:
                extracted.append(skill)
        return list(set(extracted))

    def extract_experience(self, text):
        return re.findall( r'(\d+)\+?\s*(?:years?|yrs?)', text.lower())

    def extract_education(self, text):
        education = []
        keywords = ["bachelor","master", "phd", "b.tech", "m.tech", "b.e", "mba"]
        text = text.lower()

        for word in keywords:
            if word in text:
                education.append(word)
        return education

    def extract_certification(self,text):
        certs=[]
        keywords = ["aws", "azure", "gcp", "certified",]

        text=text.lower()
        for word in keywords:
            if word in text:
                certs.append(word)
        return certs


    def extract_responsibilities(self,text):
        responsibilities = []
        lines = text.split("\n")

        for line in lines:
            if len(line)>20:
                responsibilities.append(line)
        return responsibilities

    def process(self, text):
        return{
            "skills":self.extract_skills(text),
            "experience":self.extract_experience(text),
            "education":self.extract_education(text),
            "certifications":self.extract_certification(text),
            "responsibilities":self.extract_responsibilities(text)

        }

