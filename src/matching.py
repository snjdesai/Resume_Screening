class Matcher:

    def skill_match(self, resume, jd):

        resume_skills = set(map(str.lower, resume["skills"]))
        jd_skills = set(map(str.lower, jd["skills"]))

        matched = resume_skills.intersection(jd_skills)
        missing = jd_skills - resume_skills

        return {
            "matched": list(matched),
            "missing": list(missing),
            "score": round(len(matched)/len(jd_skills)*100,2)
        }

    