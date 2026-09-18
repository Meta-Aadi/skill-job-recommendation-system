import os
import re
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class JobRecommender:

    def __init__(self, csv_path=None):

        if csv_path is None:
            csv_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "data",
                "jobs.csv"
            )

        self.csv_path = csv_path

        self.jobs = pd.read_csv(csv_path)

        required_columns = [
            "title",
            "category",
            "location",
            "experience",
            "skills",
            "description"
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in self.jobs.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing columns in jobs.csv: {missing_columns}"
            )

        self.jobs["skills_text"] = (
            self.jobs["skills"]
            .fillna("")
            .astype(str)
        )

        # ------------------------------------------------
        # SKILL ALIASES
        # ------------------------------------------------
        #
        # These help the system understand that different
        # names can refer to similar technologies.
        #

        self.skill_aliases = {

            "py": "python",
            "python programming": "python",
            "python programming language": "python",

            "js": "javascript",
            "javascript programming": "javascript",

            "ts": "typescript",

            "ml": "machine learning",
            "machine-learning": "machine learning",

            "ai": "artificial intelligence",

            "dl": "deep learning",

            "sklearn": "scikit-learn",
            "scikit learn": "scikit-learn",

            "np": "numpy",

            "pd": "pandas",

            "postgres": "postgresql",
            "postgres sql": "postgresql",

            "mongo": "mongodb",

            "node": "node.js",
            "nodejs": "node.js",

            "reactjs": "react",
            "react.js": "react",

            "vuejs": "vue",

            "angularjs": "angular",

            "k8s": "kubernetes",

            "amazon web services": "aws",

            "google cloud": "gcp",
            "google cloud platform": "gcp",

            "microsoft azure": "azure",

            "natural language processing": "nlp",

            "computer vision": "computer vision"
        }

        # ------------------------------------------------
        # TF-IDF MODEL
        # ------------------------------------------------

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True
        )

        self.job_vectors = self.vectorizer.fit_transform(
            self.jobs["skills_text"]
        )

    # ----------------------------------------------------
    # NORMALIZE SKILL
    # ----------------------------------------------------

    def normalize_skill(self, skill):

        skill = str(skill).strip().lower()

        skill = re.sub(
            r"\s+",
            " ",
            skill
        )

        # Remove unnecessary punctuation around skill names
        skill = skill.strip(".,;: ")

        # Apply alias
        if skill in self.skill_aliases:
            skill = self.skill_aliases[skill]

        return skill

    # ----------------------------------------------------
    # GET SKILL LIST
    # ----------------------------------------------------

    def get_skill_list(self, skills_text):

        if pd.isna(skills_text):
            return []

        skills = []

        for skill in str(skills_text).split(","):

            skill = self.normalize_skill(skill)

            if skill:
                skills.append(skill)

        return skills

    # ----------------------------------------------------
    # CALCULATE SKILL GAP
    # ----------------------------------------------------

    def calculate_skill_gap(
        self,
        user_skills,
        job_skills
    ):

        normalized_user_skills = {
            self.normalize_skill(skill)
            for skill in user_skills
        }

        normalized_job_skills = [
            self.normalize_skill(skill)
            for skill in job_skills
        ]

        matched = []

        missing = []

        for job_skill in normalized_job_skills:

            if job_skill in normalized_user_skills:

                if job_skill not in matched:
                    matched.append(job_skill)

            else:

                if job_skill not in missing:
                    missing.append(job_skill)

        return matched, missing

    # ----------------------------------------------------
    # CREATE EXPLANATION
    # ----------------------------------------------------

    def create_explanation(
        self,
        matched_skills,
        missing_skills,
        similarity,
        coverage
    ):

        matched_count = len(matched_skills)

        missing_count = len(missing_skills)

        similarity_percent = round(
            similarity * 100
        )

        coverage_percent = round(
            coverage * 100
        )

        if matched_count == 0:

            return (
                "This role has limited direct skill overlap "
                "with your current profile. Consider learning "
                "the missing skills shown below."
            )

        if missing_count == 0:

            return (
                f"Strong skill coverage. You match all listed "
                f"required skills, with {similarity_percent}% "
                f"skill-text similarity."
            )

        if matched_count >= 4:

            return (
                f"Strong match with {matched_count} matching skills "
                f"and {coverage_percent}% direct skill coverage. "
                f"The remaining missing skills could improve your fit."
            )

        if matched_count >= 2:

            return (
                f"Good match because {matched_count} of the role's "
                f"skills overlap with your profile. Adding the missing "
                f"skills could improve your match."
            )

        return (
            f"This role shares {matched_count} skill"
            f"{'s' if matched_count != 1 else ''} with your profile. "
            f"Learning the missing skills would increase your coverage."
        )

    # ----------------------------------------------------
    # RECOMMEND JOBS
    # ----------------------------------------------------

    def recommend(
        self,
        user_skills,
        top_n=6
    ):

        if not user_skills:
            return []

        cleaned_user_skills = [

            self.normalize_skill(skill)

            for skill in user_skills

            if str(skill).strip()
        ]

        if not cleaned_user_skills:
            return []

        # Remove duplicate skills
        cleaned_user_skills = list(
            dict.fromkeys(cleaned_user_skills)
        )

        # User skill text
        user_text = " ".join(
            cleaned_user_skills
        )

        # Convert user skills into TF-IDF vector
        user_vector = self.vectorizer.transform(
            [user_text]
        )

        # Calculate cosine similarity
        similarities = cosine_similarity(
            user_vector,
            self.job_vectors
        )[0]

        recommendations = []

        for index, row in self.jobs.iterrows():

            job_skills = self.get_skill_list(
                row["skills"]
            )

            matched_skills, missing_skills = (
                self.calculate_skill_gap(
                    cleaned_user_skills,
                    job_skills
                )
            )

            # --------------------------------------------
            # DIRECT SKILL COVERAGE
            # --------------------------------------------

            if len(job_skills) > 0:

                coverage = (
                    len(matched_skills)
                    /
                    len(job_skills)
                )

            else:

                coverage = 0

            similarity = float(
                similarities[index]
            )

            # --------------------------------------------
            # FINAL MATCH SCORE
            # --------------------------------------------

            #
            # 60% = TF-IDF similarity
            # 40% = direct skill coverage
            #

            final_score = (
                similarity * 0.60
                +
                coverage * 0.40
            )

            match_percent = round(
                min(
                    final_score * 100,
                    99
                ),
                1
            )

            explanation = self.create_explanation(
                matched_skills,
                missing_skills,
                similarity,
                coverage
            )

            recommendations.append({

                "title": row["title"],

                "category": row["category"],

                "location": row["location"],

                "experience": row["experience"],

                "description": row["description"],

                "required_skills": job_skills,

                "matched_skills": matched_skills,

                "missing_skills": missing_skills,

                "match_percent": match_percent,

                "explanation": explanation

            })

        # Highest match first
        recommendations.sort(
            key=lambda x: x["match_percent"],
            reverse=True
        )

        return recommendations[:top_n]

    # ----------------------------------------------------
    # SKILL GAP SUMMARY
    # ----------------------------------------------------

    def get_skill_gap_summary(
        self,
        recommendations
    ):

        skill_frequency = {}

        for job in recommendations:

            for skill in job["missing_skills"]:

                skill_frequency[skill] = (
                    skill_frequency.get(
                        skill,
                        0
                    )
                    + 1
                )

        sorted_skills = sorted(
            skill_frequency.items(),
            key=lambda item: item[1],
            reverse=True
        )

        return [

            {
                "skill": skill,
                "appears_in_jobs": count
            }

            for skill, count in sorted_skills[:8]
        ]

    # ----------------------------------------------------
    # GET ALL JOBS
    # ----------------------------------------------------

    def get_all_jobs(self):

        jobs = []

        for _, row in self.jobs.iterrows():

            jobs.append({

                "title": row["title"],

                "category": row["category"],

                "location": row["location"],

                "experience": row["experience"],

                "skills": self.get_skill_list(
                    row["skills"]
                ),

                "description": row["description"]

            })

        return jobs