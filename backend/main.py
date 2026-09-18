from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.recommender import JobRecommender


app = FastAPI(
    title="Career Radar API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


recommender = JobRecommender()


class RecommendationRequest(BaseModel):
    skills: List[str]
    category: Optional[str] = None
    location: Optional[str] = None
    experience: Optional[str] = None


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "message": "Career Radar API is running"
    }


@app.get("/api/jobs")
def get_jobs():
    return recommender.get_all_jobs()


@app.post("/api/recommend")
def recommend_jobs(request: RecommendationRequest):

    recommendations = recommender.recommend(
        request.skills,
        top_n=20
    )

    if request.category:
        recommendations = [
            job for job in recommendations
            if job["category"].lower() == request.category.lower()
        ]

    if request.location:
        recommendations = [
            job for job in recommendations
            if job["location"].lower() == request.location.lower()
        ]

    if request.experience:
        recommendations = [
            job for job in recommendations
            if job["experience"].lower() == request.experience.lower()
        ]

    recommendations = recommendations[:6]

    skill_gap = recommender.get_skill_gap_summary(
        recommendations
    )

    # -----------------------------------------
    # CAREER PROFILE ANALYSIS
    # -----------------------------------------

    categories = {}

    for job in recommendations:
        category = job["category"]

        categories[category] = (
            categories.get(category, 0) + 1
        )

    top_categories = sorted(
        categories.items(),
        key=lambda item: item[1],
        reverse=True
    )

    top_categories = [
        category
        for category, count in top_categories[:3]
    ]

    average_match = 0

    if recommendations:
        average_match = round(
            sum(
                job["match_percent"]
                for job in recommendations
            ) / len(recommendations),
            1
        )

    if average_match >= 70:
        profile_strength = "Strong"
    elif average_match >= 50:
        profile_strength = "Good"
    elif average_match >= 30:
        profile_strength = "Developing"
    else:
        profile_strength = "Early Stage"

    career_profile = {
        "skills_detected": len(request.skills),
        "recommended_roles": len(recommendations),
        "average_match": average_match,
        "profile_strength": profile_strength,
        "top_categories": top_categories
    }

    return {
        "submitted_skills": request.skills,

        "filters": {
            "category": request.category,
            "location": request.location,
            "experience": request.experience
        },

        "career_profile": career_profile,

        "recommendations": recommendations,

        "skill_gap": skill_gap
    }
if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 8000))

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=port
    )