from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
import re

class ResumeRanker:

    def __init__(self):
        self.skill_weight = 40
        self.experience_weight = 25
        self.education_weight = 10
        self.certification_weight = 10
        self.semantic_weight = 20

    def _convert_to_list(self, data):
        """Converts strings, lists, or dirty text structures into a clean tokenized string list."""
        if not data:
            return []
        if isinstance(data, list):
            return [str(x).strip().lower() for x in data if x]
        if isinstance(data, str):
            # Split text by commas, semicolons, newlines, or bullets
            cleaned = re.sub(r'[•*-|:·]', ',', data)
            return [word.strip().lower() for word in re.split(r'[\n,\t;]', cleaned) if word.strip()]
        return []

    def _extract_skills(self, text):
        """Extracts words listed after core competencies or skills sections."""
        if not isinstance(text, str):
            return []
        
        skills_match = re.search(r'(?:CORE COMPETENCIES|SKILLS|TECHNICAL SKILLS)(.*?)(?:PROFESSIONAL EXPERIENCE|EXPERIENCE|PROJECTS|$)', text, re.DOTALL | re.IGNORECASE)
        if not skills_match:
            return self._convert_to_list(text) # Fallback: tokenize the whole text if no section found
            
        skills_block = skills_match.group(1)
        return self._convert_to_list(skills_block)

    def _extract_experience(self, text):
        # 1. Handle cases where the input is already a number
        if isinstance(text, (int, float)):
            return float(text)
            
        # 2. Check for empty or invalid inputs
        if not text or not isinstance(text, str):
            return 0.0
            
        # 3. Use regex to search for patterns like "4 years", "9+ yrs", "3-5 years"
        text_lower = text.lower()
        match = re.search(r'(\d+(?:\.\d+)?)\s*(?:year|yr|+/|-)', text_lower)
        
        if match:
            return float(match.group(1))
            
        # 4. Fallback: Search for the absolute first standalone number in the text
        backup_match = re.search(r'\d+(?:\.\d+)?', text)
        if backup_match:
            return float(backup_match.group(0))
            
        return 0.0

    def skill_score(self, resume_skills, jd_skills):
        # 1. Clean both inputs into uniform lowercase string arrays
        r_list = self.sanitize_to_pure_list(resume_skills)
        j_list = self.sanitize_to_pure_list(jd_skills)
        
        # If the JD doesn't require any skills, award full marks
        if not j_list:
            return self.skill_weight

        # 2. Join the candidate's skills into a single searchable text string
        resume_text_blob = " ".join(r_list)
        matched_count = 0

        # 3. Match using flexible substring logic
        for skill in j_list:
            # Check for both exact structural matches and phrase containment matches
            if skill in r_list or skill in resume_text_blob:
                matched_count += 1
                
        # 4. Calculate the score ratio against total JD skills
        score = matched_count / len(j_list)
        return score * self.skill_weight

    def experience_score(self, resume_exp, jd_exp):
        try:
            print("exps",resume_exp,jd_exp)
            r_exp = int(resume_exp[0])
            print("resume_exp",r_exp,type(r_exp))
            j_exp = int(jd_exp[0])
            print("jd_exp",j_exp)
        except (ValueError, TypeError):
            return 0

        if j_exp == 0:
            return self.experience_weight

        if r_exp >= j_exp:
            print("greater")
            return self.experience_weight
        else:
            print("lesser")
            return round((r_exp / j_exp) * self.experience_weight, 2)

    def education_score(self, resume_edu, jd_edu):
        r_list = set(self._convert_to_list(resume_edu))
        j_list = set(self._convert_to_list(jd_edu))
        
        if not j_list:
            return self.education_weight
            
        if len(r_list.intersection(j_list)) > 0:
            return self.education_weight
        return 0

    def certification_score(self, resume_certs, jd_certs):
        r_list = set(self._convert_to_list(resume_certs))
        j_list = set(self._convert_to_list(jd_certs))

        if not j_list:
            return self.certification_weight

        matched = r_list.intersection(j_list)
        return (len(matched) / len(j_list)) * self.certification_weight

    def semantic_score(self, resumee_embedding, jd_embedding):
        try:
            similarity = cosine_similarity([resumee_embedding], [jd_embedding])[0][0]
            # Ensure similarity is bound safely between 0 and 1
            similarity = max(0.0, min(float(similarity), 1.0))
            return similarity * self.semantic_weight
        except Exception:
            return 0.0

    def missing_skills(self, resume_skills, jd_skills):
        r_list = self._convert_to_list(resume_skills)
        j_list = self._convert_to_list(jd_skills)
        
        resume_text_blob = " ".join(r_list)
        missing = []
        for skill in j_list:
            if skill not in r_list and skill not in resume_text_blob:
                missing.append(skill)
        return missing

    def rank_candidates(self, candidates):
        return sorted(candidates, key=lambda x:x.ats_score, reverse=True)

    def sanitize_to_pure_list(self, input_data):
        """
        Safely converts a string representation of a list, a raw text blob,
        or a native Python list into a clean, lowercased array of strings.
        """
        if not input_data:
            return []
        
        # 1. If it's already a native Python list, clean and return it
        if isinstance(input_data, list):
            return [str(x).strip().lower() for x in input_data if x]
            
        # 2. If it's a string representation of a list (e.g. "['Git', 'AWS']"), parse it safely
        if isinstance(input_data, str):
            cleaned_str = input_data.strip()
            if cleaned_str.startswith('[') and cleaned_str.endswith(']'):
                try:
                    parsed_list = ast.literal_eval(cleaned_str)
                    if isinstance(parsed_list, list):
                        return [str(x).strip().lower() for x in parsed_list if x]
                except (ValueError, SyntaxError):
                    pass # Fallback to regex splits if evaluation fails
                    
            # 3. If it's a general raw text blob, remove punctuation/brackets and split
            normalized = re.sub(r"[\[\]'\"]", "", cleaned_str) # Strip brackets and quotes
            normalized = re.sub(r'[•*-|:·]', ',', normalized) # Convert bullet variations to commas
            return [word.strip().lower() for word in re.split(r'[\n,\t;]', normalized) if word.strip()]
            
        return []

    def calculate_score(self, resume, jd, resumee_embedding, jd_embedding):
        # 1. Normalize and parse Resume Data safely
        if isinstance(resume, dict) and 'skills' in resume and isinstance(resume['skills'], (list, str)) and len(str(resume['skills'])) > 0:
            # Check if the skills key accidentally contains a raw address instead of a real list
            resume_skills_str = str(resume['skills'])
            if "brigade" in resume_skills_str.lower() or "village" in resume_skills_str.lower() or "mob" in resume_skills_str.lower():
                # Data mismatch detected! Force extract skills from the text blob
                resume_data = {
                    "skills": self._extract_skills(resume_skills_str),
                    "experience": self._extract_experience(str(resume.get('experience', ''))),
                    "education": resume.get('education', []),
                    "certification": resume.get('certification', [])
                }
            else:
                resume_data = {
                    "skills": self.sanitize_to_pure_list(resume.get('skills', [])),
                    "experience": resume.get('experience', 0),
                    "education": resume.get('education', []),
                    "certification": resume.get('certification', [])
                }
        else:
            resume_str = str(resume)
            resume_data = {
                "skills": self._extract_skills(resume_str),
                "experience": self._extract_experience(resume_str),
                "education": ["degree"] if "bachelor" in resume_str.lower() or "b.tech" in resume_str.lower() else [],
                "certification": []
            }

        # 2. Normalize and parse Job Description (JD) Data safely
        if isinstance(jd, dict):
            jd_data = {
                "skills": self.sanitize_to_pure_list(jd.get('skills', [])),
                "experience": jd.get('experience', 0),
                "education": jd.get('education', []),
                "certification": jd.get('certifications', [])
            }
        else:
            jd_str = str(jd)
            jd_data = {
                "skills": self._extract_skills(jd_str),
                "experience": self._extract_experience(jd_str),
                "education": [],
                "certification": []
            }

        # 3. Calculate all standard metrics
        skills = self.skill_score(resume_data['skills'], jd_data["skills"])
        exp = self.experience_score(resume_data['experience'], jd_data['experience'])
        edu = self.education_score(resume_data['education'], jd_data['education'])
        cert = self.certification_score(resume_data['certification'], jd_data['certification'])
        semantic = self.semantic_score(resumee_embedding, jd_embedding)

        total = skills + exp + edu + cert + semantic

        return {
            "ATS Score": round(total, 2),
            "Skill Score": round(skills, 2),
            "Experience Score": round(exp, 2),
            "Education Score": round(edu, 2),
            "Certification Score": round(cert, 2),
            "Semantic Score": round(semantic, 2),
            "Missing skills": self.missing_skills(resume_data['skills'], jd_data["skills"])
        }
