const API_URL = "https://career-radar-api-zihz.onrender.com";

const skillsInput = document.getElementById("skillsInput");
const categoryFilter = document.getElementById("categoryFilter");
const locationFilter = document.getElementById("locationFilter");
const experienceFilter = document.getElementById("experienceFilter");
const recommendButton = document.getElementById("recommendButton");

const loading = document.getElementById("loading");
const resultsSection = document.getElementById("resultsSection");
const resultsContainer = document.getElementById("resultsContainer");
const resultCount = document.getElementById("resultCount");
const emptyState = document.getElementById("emptyState");


// =============================================
// MAIN SEARCH FUNCTION
// =============================================

async function searchJobs() {

    const skills = skillsInput.value
        .split(",")
        .map(skill => skill.trim())
        .filter(skill => skill.length > 0);

    const category = categoryFilter.value;
    const location = locationFilter.value;
    const experience = experienceFilter.value;


    // Don't search without skills
    if (skills.length === 0) {
        showToast("Please enter at least one skill.");
        return;
    }


    // Loading state
    recommendButton.disabled = true;
    recommendButton.textContent = "SCANNING...";

    loading.classList.remove("hidden");
    resultsSection.classList.add("hidden");


    try {

        const response = await fetch(
            `${API_URL}/api/recommend`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    skills: skills,
                    category: category || null,
                    location: location || null,
                    experience: experience || null
                })
            }
        );


        if (!response.ok) {
            throw new Error(
                `Server returned ${response.status}`
            );
        }


        const data = await response.json();


        console.log("API RESPONSE:", data);


        // Render everything
        renderCareerProfile(data.career_profile);

        renderSkillGap(data.skill_gap);

        renderRecommendations(data.recommendations);


        // Show results
        resultsSection.classList.remove("hidden");

        emptyState.classList.add("hidden");


    } catch (error) {

        console.error("Recommendation error:", error);

        showToast(
            "Could not connect to the Career Radar API."
        );

    } finally {

        loading.classList.add("hidden");

        recommendButton.disabled = false;

        recommendButton.textContent =
            "SCAN MY CAREER SIGNAL";
    }
}


// =============================================
// CAREER PROFILE
// =============================================

function renderCareerProfile(profile) {

    if (!profile) {
        return;
    }


    // Remove previous profile
    const oldProfile =
        document.getElementById("careerProfile");

    if (oldProfile) {
        oldProfile.remove();
    }


    const profileSection =
        document.createElement("section");

    profileSection.id = "careerProfile";
    profileSection.className = "career-profile";


    const categories =
        profile.top_categories &&
        profile.top_categories.length > 0

            ? profile.top_categories
                .map(category => `
                    <span class="profile-category">
                        ${escapeHTML(category)}
                    </span>
                `)
                .join("")

            : `
                <span class="profile-category">
                    No clear category yet
                </span>
            `;


    profileSection.innerHTML = `

        <div class="profile-header">

            <span class="section-label">
                CAREER PROFILE
            </span>

            <h2>
                Your career signal
            </h2>

            <p>
                A quick analysis of how your current
                skills align with available roles.
            </p>

        </div>


        <div class="profile-stats">

            <div class="profile-stat">

                <span class="stat-label">
                    SKILLS DETECTED
                </span>

                <strong>
                    ${profile.skills_detected}
                </strong>

            </div>


            <div class="profile-stat">

                <span class="stat-label">
                    AVG MATCH
                </span>

                <strong>
                    ${profile.average_match}%
                </strong>

            </div>


            <div class="profile-stat">

                <span class="stat-label">
                    ROLES FOUND
                </span>

                <strong>
                    ${profile.recommended_roles}
                </strong>

            </div>


            <div class="profile-stat">

                <span class="stat-label">
                    PROFILE SIGNAL
                </span>

                <strong>
                    ${escapeHTML(profile.profile_strength)}
                </strong>

            </div>

        </div>


        <div class="profile-categories">

            <span class="stat-label">
                TOP CAREER AREAS
            </span>

            <div class="category-list">
                ${categories}
            </div>

        </div>

    `;


    resultsSection.insertBefore(
        profileSection,
        resultsContainer
    );
}


// =============================================
// SKILL GAP SUMMARY
// =============================================

function renderSkillGap(skillGap) {

    const oldGap =
        document.getElementById("skillGapSummary");

    if (oldGap) {
        oldGap.remove();
    }


    const gapSection =
        document.createElement("section");

    gapSection.id = "skillGapSummary";
    gapSection.className = "skill-gap-summary";


    if (!skillGap || skillGap.length === 0) {

        gapSection.innerHTML = `

            <div class="skill-gap-header">

                <span class="section-label">
                    YOUR SKILL GAP
                </span>

                <h2>
                    No major skill gaps detected.
                </h2>

                <p>
                    Your current skills cover the requirements
                    of the recommended roles well.
                </p>

            </div>

        `;

    } else {

        const skillsHTML = skillGap
            .map(item => `

                <div class="gap-item">

                    <div class="gap-skill">
                        ${formatSkill(item.skill)}
                    </div>

                    <div class="gap-frequency">
                        Appears in
                        ${item.appears_in_jobs}
                        recommended
                        ${
                            item.appears_in_jobs === 1
                                ? "job"
                                : "jobs"
                        }
                    </div>

                </div>

            `)
            .join("");


        gapSection.innerHTML = `

            <div class="skill-gap-header">

                <span class="section-label">
                    YOUR SKILL GAP
                </span>

                <h2>
                    Skills worth learning next
                </h2>

                <p>
                    These skills repeatedly appear in the
                    requirements of your recommended jobs.
                </p>

            </div>


            <div class="skill-gap-list">
                ${skillsHTML}
            </div>

        `;
    }


    resultsSection.insertBefore(
        gapSection,
        resultsContainer
    );
}


// =============================================
// JOB RECOMMENDATIONS
// =============================================

function renderRecommendations(jobs) {

    resultsContainer.innerHTML = "";


    if (!jobs || jobs.length === 0) {

        resultCount.textContent = "0 MATCHES";


        resultsContainer.innerHTML = `

            <div class="no-results">

                <h3>
                    No matching jobs found.
                </h3>

                <p>
                    Try changing your skills or filters.
                </p>

            </div>

        `;

        return;
    }


    resultCount.textContent =
        `${jobs.length} MATCH${jobs.length === 1 ? "" : "ES"}`;


    jobs.forEach((job, index) => {

        const card =
            document.createElement("article");

        card.className = "job-card";


        const matchedSkills =
            (job.matched_skills || [])
                .map(skill => `
                    <span class="skill-tag matched">
                        ${formatSkill(skill)}
                    </span>
                `)
                .join("");


        const missingSkills =
            (job.missing_skills || [])
                .map(skill => `
                    <span class="skill-tag missing">
                        ${formatSkill(skill)}
                    </span>
                `)
                .join("");


        card.innerHTML = `

            <div class="job-top">

                <div>

                    <div class="job-number">
                        ${String(index + 1).padStart(2, "0")}
                    </div>

                    <h3 class="job-title">
                        ${escapeHTML(job.title)}
                    </h3>

                    <div class="job-meta">

                        ${escapeHTML(job.category)}

                        <span>•</span>

                        ${escapeHTML(job.location)}

                        <span>•</span>

                        ${escapeHTML(job.experience)}

                    </div>

                </div>


                <div class="match-score">

                    <strong>
                        ${job.match_percent}%
                    </strong>

                    <span>
                        MATCH
                    </span>

                </div>

            </div>


            <p class="job-description">
                ${escapeHTML(job.description)}
            </p>


            <div class="explanation-box">

                <div class="explanation-title">
                    WHY THIS MATCHED
                </div>

                <p>
                    ${
                        escapeHTML(
                            job.explanation ||
                            "This role has relevant skills for your profile."
                        )
                    }
                </p>

            </div>


            <div class="skills-section">

                <div class="skills-label">
                    MATCHED SKILLS
                </div>

                <div class="skills-list">

                    ${
                        matchedSkills ||
                        `<span class="empty-skill">
                            None yet
                        </span>`
                    }

                </div>

            </div>


            <div class="skills-section">

                <div class="skills-label">
                    SKILL GAP
                </div>

                <div class="skills-list">

                    ${
                        missingSkills ||
                        `<span class="empty-skill">
                            No major gaps
                        </span>`
                    }

                </div>

            </div>

        `;


        resultsContainer.appendChild(card);

    });
}


// =============================================
// FORMAT SKILLS
// =============================================

function formatSkill(skill) {

    return escapeHTML(
        String(skill)
            .split(" ")
            .map(word => {

                const lower =
                    word.toLowerCase();

                if (
                    lower === "sql" ||
                    lower === "api" ||
                    lower === "nlp" ||
                    lower === "aws" ||
                    lower === "etl"
                ) {
                    return word.toUpperCase();
                }


                return (
                    word.charAt(0).toUpperCase()
                    +
                    word.slice(1)
                );

            })
            .join(" ")
    );
}


// =============================================
// BASIC HTML SAFETY
// =============================================

function escapeHTML(value) {

    const div =
        document.createElement("div");

    div.textContent =
        String(value ?? "");

    return div.innerHTML;
}


// =============================================
// TOAST
// =============================================

function showToast(message) {

    let toast =
        document.getElementById("toast");


    if (!toast) {

        toast =
            document.createElement("div");

        toast.id = "toast";
        toast.className = "toast";

        document.body.appendChild(toast);
    }


    toast.textContent = message;

    toast.classList.add("show");


    setTimeout(() => {

        toast.classList.remove("show");

    }, 3000);
}


// =============================================
// BUTTON EVENT
// =============================================

recommendButton.addEventListener(
    "click",
    searchJobs
);


// =============================================
// ENTER KEY
// =============================================

skillsInput.addEventListener(
    "keydown",
    event => {

        if (event.key === "Enter") {
            searchJobs();
        }

    }
);