import os
import shutil
import json
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

# Enable connection between Frontend and Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# AI Setup
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
client = OpenAI(
    base_url="https://api.groq.com/openai/v1", 
    api_key=GROQ_API_KEY
)

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# ==========================================
# 1. DATA MODELS
# ==========================================
class ScenarioRequest(BaseModel):
    user_id: str
    salary: int
    skills: str
    is_remote: bool

class CareerProfile(BaseModel):
    user_id: str
    education: List[str] = []
    skills: List[str] = []
    certifications: List[str] = []
    projects: List[str] = []
    career_goals: List[str] = []
    work_experience: List[str] = []

class TwinChatRequest(BaseModel):
    user_id: str
    question: str

class ATSAnalysisRequest(BaseModel):
    user_id: str
    job_description: str

class CoverLetterRequest(BaseModel):
    user_id: str
    company_name: str
    job_title: str
    job_description: str

class SaveResumeVersionRequest(BaseModel):
    user_id: str
    version_name: str
    resume_data: dict

# --- NEW MODELS ---

# Career
class SkillGapRequest(BaseModel):
    user_id: str
    dream_job: str

class InterviewChatRequest(BaseModel):
    user_id: str
    message: str
    role: str # "HR" or "Technical"
    history: List[Dict[str, str]] = []

class PortfolioMentorRequest(BaseModel):
    user_id: str
    tech_stack: str

# Education
class StudentProfile(BaseModel):
    user_id: str
    course_branch: str
    semester: str
    subjects: List[str] = []
    goals: List[str] = []
    learning_style: str # "Visual" | "Text" | "Interactive"

class StudyPlannerRequest(BaseModel):
    user_id: str
    exam_countdown_days: int = 30

class DoubtSolverRequest(BaseModel):
    user_id: str
    doubt: str
    difficulty: str # "Easy" | "Medium" | "Hard"

class QuizRequest(BaseModel):
    user_id: str
    subject: str

class ExamStrategyRequest(BaseModel):
    user_id: str
    subject: str
    days_to_exam: int = 7

class SmartRevisionRequest(BaseModel):
    user_id: str
    subject: str

class LectureAssistantRequest(BaseModel):
    user_id: str
    lecture_text: str

class ResearchAssistantRequest(BaseModel):
    user_id: str
    paper_text: str
    citation_format: str = "APA" # APA | MLA | Chicago

class LearningTwinRequest(BaseModel):
    user_id: str
    message: str
    chat_history: List[Dict[str, str]] = []

class GamesDataRequest(BaseModel):
    user_id: str
    action: str # "get" | "add_xp" | "unlock_badge" | "complete_mission"
    xp_amount: int = 0
    badge_name: str = ""
    mission_name: str = ""

class FocusSessionRequest(BaseModel):
    user_id: str
    duration_mins: int
    focus_score: int
    ambient_sound: str

class StudyCircleRequest(BaseModel):
    user_id: str
    action: str # "list" | "create" | "join" | "post"
    circle_name: str = ""
    post_content: str = ""

# Money
class FinancialProfile(BaseModel):
    user_id: str
    income: int
    expenses: int
    savings: int
    goals: List[str] = []
    loans: List[str] = []

class MoneyAdvisorRequest(BaseModel):
    user_id: str
    question: str
    transactions: List[Dict[str, Any]] = []

class DecisionSimulatorRequest(BaseModel):
    user_id: str
    item_name: str
    price: int
    category: str = "Electronics"

class ScamScannerRequest(BaseModel):
    user_id: str
    message_text: str

class SmartShoppingRequest(BaseModel):
    user_id: str
    product_name: str

class SubscriptionOptimizerRequest(BaseModel):
    user_id: str
    subscriptions: List[Dict[str, Any]] = []

class MoneyTwinRequest(BaseModel):
    user_id: str
    message: str
    chat_history: List[Dict[str, str]] = []

# Health
class HealthProfile(BaseModel):
    user_id: str
    age: int
    height: int # in cm
    weight: int # in kg
    allergies: List[str] = []
    conditions: List[str] = []
    goals: List[str] = []

class HealthTrackerRequest(BaseModel):
    user_id: str
    steps: int
    water_ml: int
    sleep_hours: float
    exercise_mins: int
    mood: str

# Life
class LifeProfile(BaseModel):
    user_id: str
    name: str
    emergency_contacts: List[str] = []
    family_info: List[str] = []
    preferences: List[str] = []

class GovtSchemesRequest(BaseModel):
    user_id: str
    age: int
    state: str
    income: int

class TravelRequest(BaseModel):
    user_id: str
    destination: str
    duration_days: int


# ==========================================
# 2. HELPER PERSISTENCE FUNCTIONS
# ==========================================
def save_json(filename: str, data: dict):
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def read_json(filename: str, default: dict = None) -> dict:
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                return json.load(f)
            except Exception:
                return default or {}
    return default or {}


# ==========================================
# 3. EXISTING CAREER ENDPOINTS
# ==========================================
@app.post("/update-profile")
async def update_profile(profile: CareerProfile):
    try:
        save_json(f"{profile.user_id}_profile.json", profile.model_dump())
        return {"status": "success", "message": "Career Profile updated securely."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-profile/{user_id}")
async def get_profile(user_id: str):
    data = read_json(f"{user_id}_profile.json", None)
    if data:
        return data
    return {"status": "not_found", "message": "Profile does not exist yet."}

@app.post("/ask-twin")
async def ask_twin(request: TwinChatRequest):
    try:
        profile_data = read_json(f"{request.user_id}_profile.json", {})
        profile_context = json.dumps(profile_data, indent=2) if profile_data else "No profile data filled out yet."
        
        system_instruction = f"""
        You are the 'AI Career Twin' and personalized mentor inside the AAROHA Human OS.
        Your job is to guide the user based strictly on their specific Career Profile background.
        
        Here is the user's current profile data:
        {profile_context}
        
        Be highly actionable, encouraging, and specific. Keep it brief.
        """
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": request.question}
            ]
        )
        return {"answer": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-smart-doc")
async def upload_smart_doc(file: UploadFile = File(...), user_id: str = Form(...)):
    try:
        file_content = await file.read()
        text_sample = file_content[:2000].decode('utf-8', errors='ignore')
        await file.seek(0)

        system_prompt = """
        You are an expert AI Document Organizer for the AAROHA Human OS.
        Analyze the provided filename and document text snippet.
        
        Tasks:
        1. Classify the document into exactly one of these categories: "resumes", "certificates", or "offer_letters".
        2. Extract the owner's name.
        3. Extract an expiration or document date if mentioned (format: YYYY-MM-DD). If no expiration date exists, return null.
        4. Write a brief 1-sentence summary.
        
        You MUST respond ONLY with a valid, clean JSON object matching this schema:
        {
            "category": "resumes" | "certificates" | "offer_letters",
            "owner": "string or Unknown",
            "expiry_date": "YYYY-MM-DD" or null,
            "summary": "string"
        }
        """
        user_prompt = f"Filename: {file.filename}\n\nDocument Text Content Sample:\n{text_sample}"

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        ai_analysis = json.loads(response.choices[0].message.content)
        detected_category = ai_analysis.get("category", "resumes")

        category_dir = os.path.join(UPLOAD_DIR, user_id, detected_category)
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)
            
        file_location = os.path.join(category_dir, file.filename)
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

        meta_location = f"{file_location}_meta.json"
        with open(meta_location, "w") as meta_file:
            json.dump(ai_analysis, meta_file, indent=4)

        return {
            "status": "success",
            "message": "AI successfully organized your document!",
            "analysis": ai_analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-doc")
async def upload_file(file: UploadFile = File(...), category: str = Form(...), user_id: str = Form(...)):
    try:
        category_dir = os.path.join(UPLOAD_DIR, user_id, category)
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)
            
        file_location = os.path.join(category_dir, file.filename)
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
            
        return {"status": "success", "info": f"File saved under {category}.", "path": file_location}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list-docs/{user_id}/{category}")
async def list_docs(user_id: str, category: str):
    category_dir = os.path.join(UPLOAD_DIR, user_id, category)
    if os.path.exists(category_dir):
        return {"files": [f for f in os.listdir(category_dir) if not f.endswith("_meta.json")]}
    return {"files": []}

@app.get("/list-files")
async def list_files_fallback():
    files = []
    for root, dirs, filenames in os.walk(UPLOAD_DIR):
        for f in filenames:
            if not f.endswith("_meta.json") and not f.endswith(".json"):
                files.append(f)
    return {"files": files}

@app.get("/view-doc/{user_id}/{category}/{filename}")
async def view_file(user_id: str, category: str, filename: str):
    file_path = os.path.join(UPLOAD_DIR, user_id, category, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Requested file could not be found.")

@app.get("/check-expiries/{user_id}")
async def check_expiries(user_id: str):
    reminders = []
    user_dir = os.path.join(UPLOAD_DIR, user_id)
    if not os.path.exists(user_dir):
        return {"reminders": []}
    
    for category in ["resumes", "certificates", "offer_letters"]:
        cat_dir = os.path.join(user_dir, category)
        if os.path.exists(cat_dir):
            for file in os.listdir(cat_dir):
                if file.endswith("_meta.json"):
                    meta_path = os.path.join(cat_dir, file)
                    try:
                        with open(meta_path, "r") as f:
                            meta_data = json.load(f)
                        if meta_data.get("expiry_date"):
                            reminders.append({
                                "filename": file.replace("_meta.json", ""),
                                "category": category,
                                "expiry_date": meta_data["expiry_date"],
                                "owner": meta_data.get("owner", "Unknown"),
                                "summary": meta_data.get("summary", "")
                            })
                    except Exception:
                        continue
    return {"reminders": reminders}

@app.post("/analyze-ats")
async def analyze_ats(request: ATSAnalysisRequest):
    try:
        profile_path = os.path.join(UPLOAD_DIR, f"{request.user_id}_profile.json")
        profile_context = "No profile data filled out yet."
        if os.path.exists(profile_path):
            with open(profile_path, "r") as f:
                profile_context = json.dumps(json.load(f), indent=2)

        system_prompt = """
        You are an expert Applicant Tracking System (ATS) and an elite corporate recruiter.
        Analyze the user's profile against the provided Job Description.
        
        Tasks:
        1. Calculate a realistic ATS Match Score (0 to 100) based on keyword matching, skills, and depth of experience.
        2. Identify specific Missing Keywords/Skills.
        3. Provide concrete, actionable structural recommendations to improve the resume.
        
        You MUST respond ONLY with a valid JSON object matching this schema:
        {
            "ats_score": 75,
            "missing_keywords": ["Kubernetes", "CI/CD pipelines", "System Architecture"],
            "improvements": [
                "Quantify your experience under projects by adding metrics (e.g., improved load times by 20%).",
                "Explicitly detail your Node.js experience in the work experience segment."
            ]
        }
        """
        user_prompt = f"User Career Profile:\n{profile_context}\n\nTarget Job Description:\n{request.job_description}"

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-cover-letter")
async def generate_cover_letter(request: CoverLetterRequest):
    try:
        profile_path = os.path.join(UPLOAD_DIR, f"{request.user_id}_profile.json")
        profile_context = ""
        if os.path.exists(profile_path):
            with open(profile_path, "r") as f:
                profile_context = json.dumps(json.load(f), indent=2)

        system_prompt = f"You are a professional career coach. Write a highly tailored, compelling cover letter for a position as a {request.job_title} at {request.company_name}. Align the user's background skills and achievements directly with the requirements of the job description. Maintain a highly professional, confident, and persuasive tone."
        user_prompt = f"User Background Profile:\n{profile_context}\n\nTarget Job Description:\n{request.job_description}"

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return {"cover_letter": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save-resume-version")
async def save_resume_version(request: SaveResumeVersionRequest):
    try:
        versions_path = os.path.join(UPLOAD_DIR, f"{request.user_id}_resume_versions.json")
        versions = {}
        if os.path.exists(versions_path):
            with open(versions_path, "r") as f:
                versions = json.load(f)
        
        versions[request.version_name] = request.resume_data
        with open(versions_path, "w") as f:
            json.dump(versions, f, indent=4)
        return {"status": "success", "message": f"Version '{request.version_name}' securely cataloged."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list-resume-versions/{user_id}")
async def list_resume_versions(user_id: str):
    versions_path = os.path.join(UPLOAD_DIR, f"{user_id}_resume_versions.json")
    if os.path.exists(versions_path):
        with open(versions_path, "r") as f:
            return json.load(f)
    return {}

@app.post("/analyze-scenario")
async def analyze(request: ScenarioRequest):
    try:
        prompt = f"Analyze this job: Salary: {request.salary}, Skills: {request.skills}, Remote: {request.is_remote}"
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return {"decision": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# 4. NEW PORTAL ENDPOINTS
# ==========================================

# --- CAREER BRAIN ---
@app.post("/career/skill-gap")
async def skill_gap(request: SkillGapRequest):
    try:
        profile = read_json(f"{request.user_id}_profile.json", {})
        system_prompt = """
        You are AAROHA's Career Skill Gap Analyzer.
        Compare the user's profile skills/education against their dream job.
        
        Output EXACTLY a JSON structure matching:
        {
            "missing_skills": ["skill1", "skill2"],
            "recommended_courses": ["Course Title on Coursera/Udemy", "Course Title"],
            "recommended_projects": ["Project Name: Brief implementation task details"],
            "estimated_time": "3-4 Months (8 hrs/week)"
        }
        """
        user_prompt = f"Profile Context: {json.dumps(profile)}\nDream Job: {request.dream_job}"
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/career/jobs")
async def match_jobs(request: SkillGapRequest): # Reuses user_id/dream_job
    try:
        profile = read_json(f"{request.user_id}_profile.json", {})
        system_prompt = """
        You are AAROHA's Job & Internship Finder.
        Suggest 3 hyper-personalized mock job or internship roles the user should apply to based on their profile.
        
        Output EXACTLY a JSON structure matching:
        {
            "jobs": [
                {
                    "title": "Software Engineer Intern",
                    "company": "Google",
                    "match_reason": "Matches your Python & Data structures skillset.",
                    "deadline": "2026-09-15"
                }
            ]
        }
        """
        user_prompt = f"Profile Context: {json.dumps(profile)}\nTarget Focus: {request.dream_job}"
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/career/interview-chat")
async def interview_chat(request: InterviewChatRequest):
    try:
        profile = read_json(f"{request.user_id}_profile.json", {})
        system_prompt = f"""
        You are AAROHA's Elite AI Interview Coach. 
        You are conducting a simulated {request.role} interview.
        User profile: {json.dumps(profile)}
        
        Review the user's latest response and context history.
        Provide constructive feedback, score their answer out of 100, and ask the NEXT single, highly focused interview question.
        
        Respond with EXACTLY a JSON structure:
        {{
            "feedback": "Your answer was accurate, but could benefit from explaining the time complexity.",
            "score": 85,
            "next_question": "Explain how a hash map handles collisions."
        }}
        """
        messages = [{"role": "system", "content": system_prompt}]
        for msg in request.history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": request.message})

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=messages
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/career/portfolio-mentor")
async def portfolio_mentor(request: PortfolioMentorRequest):
    try:
        profile = read_json(f"{request.user_id}_profile.json", {})
        system_prompt = """
        You are AAROHA's Project & Portfolio Mentor.
        Evaluate the user's tech stack and suggest customized portfolio-building projects and portfolio layout tips.
        
        Output EXACTLY a JSON structure matching:
        {
            "projects": [
                {
                    "name": "Project Name",
                    "description": "Short explanation of architecture and execution steps."
                }
            ],
            "portfolio_tips": [
                "Tip 1: Quantify achievements",
                "Tip 2: Add interactive UI demos"
            ]
        }
        """
        user_prompt = f"Profile Context: {json.dumps(profile)}\nTarget Stack: {request.tech_stack}"
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- EDUCATION BRAIN ---
@app.post("/education/student-profile")
async def update_student_profile(profile: StudentProfile):
    try:
        save_json(f"{profile.user_id}_student_profile.json", profile.model_dump())
        return {"status": "success", "message": "Student Profile updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/education/student-profile/{user_id}")
async def get_student_profile(user_id: str):
    data = read_json(f"{user_id}_student_profile.json", None)
    if data:
        return data
    return {"status": "not_found", "message": "Profile does not exist."}

@app.post("/education/study-planner")
async def study_planner(request: StudyPlannerRequest):
    try:
        profile = read_json(f"{request.user_id}_student_profile.json", {})
        system_prompt = f"""
        You are AAROHA's AI Study Planner. 
        Generate a personalized study roadmap and daily schedule leading up to an exam in {request.exam_countdown_days} days.
        
        Respond with EXACTLY a JSON structure:
        {{
            "schedule": [
                {{"day": "Day 1-5", "topic": "Core Fundamentals Revision", "hours": 3}}
            ],
            "countdown": "{request.exam_countdown_days} Days Remaining",
            "revision_plan": [
                "Review flashcards for key subjects.",
                "Take weekly mock tests."
            ]
        }}
        """
        user_prompt = f"Student Profile: {json.dumps(profile)}"
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/education/doubt-solver")
async def doubt_solver(request: DoubtSolverRequest):
    try:
        profile = read_json(f"{request.user_id}_student_profile.json", {})
        system_prompt = f"""
        You are AAROHA's AI Doubt Solver.
        Explain the concept or resolve the user's doubt at a {request.difficulty} difficulty level.
        Student Profile Preferred Style: {profile.get("learning_style", "Interactive")}
        
        Respond with EXACTLY a JSON structure:
        {{
            "explanation": "Provide a complete explanation suitable for the user's difficulty preference.",
            "steps": [
                "Step 1: Focus on basis definitions.",
                "Step 2: Solve math formulation."
            ]
        }}
        """
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.doubt}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/education/quiz-generator")
async def quiz_generator(request: QuizRequest):
    try:
        system_prompt = f"""
        You are AAROHA's Quiz Generator.
        Generate 5 multiple-choice questions on the subject: {request.subject}.
        
        Respond with EXACTLY a JSON structure matching this schema:
        {{
            "quiz": [
                {{
                    "question": "What is the time complexity of binary search?",
                    "options": ["O(N)", "O(log N)", "O(N log N)", "O(1)"],
                    "answer": "O(log N)"
                }}
            ]
        }}
        """
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create quiz for {request.subject}"}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/education/learning-hub/{user_id}")
async def learning_hub(user_id: str):
    try:
        profile = read_json(f"{user_id}_student_profile.json", {})
        system_prompt = """
        You are AAROHA's Learning Hub Advisor.
        Recommend customized books, courses, YouTube search keywords, and roadmap tips.
        
        Respond with EXACTLY a JSON structure:
        {
            "courses": ["Intro to Algorithms (Coursera)", "Advanced DB Systems (Udemy)"],
            "books": ["Introduction to Algorithms by Cormen"],
            "videos": ["Crash Course Computer Science", "MIT OpenCourseWare Lectures"],
            "roadmap": ["Build 2 projects in current semester", "Complete basic certifications"]
        }
        """
        user_prompt = f"Student Profile: {json.dumps(profile)}"
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/education/upload-notes")
async def upload_notes(file: UploadFile = File(...), user_id: str = Form(...)):
    try:
        file_content = await file.read()
        text_sample = file_content[:4000].decode('utf-8', errors='ignore')
        await file.seek(0)

        system_prompt = """
        You are an expert AI Study Assistant for AAROHA's Education Brain.
        Analyze the uploaded study notes or lecture text snippet.
        
        Generate:
        1. A concise, professional summary (2-3 sentences).
        2. A list of 3-4 key bullet points.
        3. A list of 3 flashcards. Each flashcard must have a "question" and an "answer".
        
        You MUST respond ONLY with a valid, clean JSON object matching this schema:
        {
            "summary": "Concise summary of the notes...",
            "key_points": [
                "Key learning point 1...",
                "Key learning point 2..."
            ],
            "flashcards": [
                {"question": "Question text...", "answer": "Answer text..."}
            ]
        }
        """
        user_prompt = f"Filename: {file.filename}\n\nNotes Content Sample:\n{text_sample}"

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        ai_analysis = json.loads(response.choices[0].message.content)
        
        notes_dir = os.path.join(UPLOAD_DIR, user_id, "notes")
        if not os.path.exists(notes_dir):
            os.makedirs(notes_dir)
            
        file_location = os.path.join(notes_dir, file.filename)
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

        meta_location = f"{file_location}_meta.json"
        with open(meta_location, "w") as meta_file:
            json.dump(ai_analysis, meta_file, indent=4)

        return {
            "status": "success",
            "filename": file.filename,
            "analysis": ai_analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/education/notes/{user_id}")
async def list_notes(user_id: str):
    notes_dir = os.path.join(UPLOAD_DIR, user_id, "notes")
    if os.path.exists(notes_dir):
        files = [f for f in os.listdir(notes_dir) if not f.endswith("_meta.json")]
        return {"notes": files}
    return {"notes": []}

@app.get("/education/notes/{user_id}/{filename}/meta")
async def get_notes_meta(user_id: str, filename: str):
    meta_path = os.path.join(UPLOAD_DIR, user_id, "notes", f"{filename}_meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            return json.load(f)
    raise HTTPException(status_code=404, detail="Notes metadata not found.")

@app.post("/education/exam-strategy")
async def exam_strategy(request: ExamStrategyRequest):
    try:
        profile = read_json(f"{request.user_id}_student_profile.json", {})
        system_prompt = f"""
        You are AAROHA's AI Exam Strategy Generator. 
        Create a highly structured exam strategy plan for the subject '{request.subject}' with the exam being {request.days_to_exam} days away.
        
        Respond with EXACTLY a JSON structure matching this schema:
        {{
            "subject": "{request.subject}",
            "days_remaining": {request.days_to_exam},
            "study_order": ["Chapter/Topic 1", "Chapter/Topic 2"],
            "high_weightage_topics": ["Topic A (Expected weight: 20%)", "Topic B (Expected weight: 15%)"],
            "time_allocation": "Allocate 3 hours daily: 2 hours for reading, 1 hour for testing.",
            "last_day_checklist": ["Revise flashcards", "Attempt one final mock test", "Get 8 hours of sleep"]
        }}
        """
        user_prompt = f"Student profile context: {json.dumps(profile)}"
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/education/smart-revision")
async def smart_revision(request: SmartRevisionRequest):
    try:
        profile = read_json(f"{request.user_id}_student_profile.json", {})
        system_prompt = f"""
        You are AAROHA's Smart Revision Advisor.
        Based on the student's learning profile and subject '{request.subject}', identify:
        1. Weak topics requiring urgent attention.
        2. Frequently forgotten concepts.
        3. High-weightage exam topics.
        4. Best time to revise (based on learning style).
        
        Respond with EXACTLY a JSON structure matching this schema:
        {{
            "weak_topics": ["Topic X", "Topic Y"],
            "forgotten_concepts": ["Concept 1 details", "Concept 2 details"],
            "high_weightage_topics": ["High-weightage topic A", "High-weightage topic B"],
            "best_time_to_revise": "Morning (6 AM - 8 AM) - high cognitive retention slot"
        }}
        """
        user_prompt = f"Student profile context: {json.dumps(profile)}"
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/education/lecture-assistant")
async def lecture_assistant(request: LectureAssistantRequest):
    try:
        system_prompt = """
        You are AAROHA's AI Lecture Assistant. 
        Convert the provided lecture transcript/text into auto-notes, a summary, highlighted important topics, and a revision notes list.
        
        Respond with EXACTLY a JSON structure matching this schema:
        {{
            "notes": ["Structured note point 1", "Structured note point 2"],
            "summary": "Cohesive summary of the lecture contents.",
            "important_topics": ["Topic A - High weightage", "Topic B - Medium weightage"],
            "revision_notes": ["Revision key point 1", "Revision key point 2"]
        }}
        """
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.lecture_text}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/education/research-assistant")
async def research_assistant(request: ResearchAssistantRequest):
    try:
        system_prompt = f"""
        You are AAROHA's AI Research Assistant.
        Analyze the provided research paper text sample.
        Tasks:
        1. Summarize the research paper snippet.
        2. Explain key technical terms.
        3. Generate a citation in '{request.citation_format}' format.
        4. Compare multiple sources or arguments from the text.
        
        Respond with EXACTLY a JSON structure matching this schema:
        {{
            "summary": "Academic summary of the paper...",
            "technical_terms": {{"Term 1": "Definition 1", "Term 2": "Definition 2"}},
            "citation": "Author, A. A. (Year). Title of paper. Journal, Vol(No), p-p.",
            "argument_comparison": ["Argument 1: Perspective description", "Argument 2: Perspective description"]
        }}
        """
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.paper_text}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/education/learning-twin")
async def learning_twin_chat(request: LearningTwinRequest):
    try:
        profile = read_json(f"{request.user_id}_student_profile.json", {})
        system_prompt = f"""
        You are AAROHA's AI Learning Twin, the personalized learning coach.
        You understand the user's habits (based on their profile) and proactively guide them.
        Here is the student's profile: {json.dumps(profile)}
        
        Respond in a friendly, conversational, and highly motivating manner. Let's keep it under 3-4 sentences.
        """
        messages = [{"role": "system", "content": system_prompt}]
        for msg in request.chat_history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": request.message})
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )
        return {"answer": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/education/games-data")
async def games_data(request: GamesDataRequest):
    try:
        filename = f"{request.user_id}_games_data.json"
        data = read_json(filename, {
            "xp": 120,
            "level": 1,
            "badges": ["Quiz Starter"],
            "missions": [
                {"id": "daily_quiz", "title": "Complete 1 Subject Quiz", "completed": False, "xp": 50},
                {"id": "pomodoro", "title": "Complete a 25-min Focus session", "completed": False, "xp": 100}
            ]
        })
        
        if request.action == "add_xp":
            data["xp"] += request.xp_amount
            data["level"] = (data["xp"] // 300) + 1
        elif request.action == "unlock_badge":
            if request.badge_name and request.badge_name not in data["badges"]:
                data["badges"].append(request.badge_name)
        elif request.action == "complete_mission":
            for m in data["missions"]:
                if m["id"] == request.mission_name or m["title"] == request.mission_name:
                    if not m["completed"]:
                        m["completed"] = True
                        data["xp"] += m["xp"]
                        data["level"] = (data["xp"] // 300) + 1
                        
        save_json(filename, data)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/education/focus-session")
async def focus_session(request: FocusSessionRequest):
    try:
        filename = f"{request.user_id}_focus_sessions.json"
        history = read_json(filename, {"sessions": [], "total_focus_score": 0, "total_focus_time_mins": 0})
        
        new_session = {
            "duration_mins": request.duration_mins,
            "focus_score": request.focus_score,
            "ambient_sound": request.ambient_sound,
            "timestamp": "Recent"
        }
        history["sessions"].append(new_session)
        history["total_focus_score"] = int(sum(s["focus_score"] for s in history["sessions"]) / len(history["sessions"])) if history["sessions"] else 0
        history["total_focus_time_mins"] += request.duration_mins
        
        save_json(filename, history)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/education/study-circle")
async def study_circle(request: StudyCircleRequest):
    try:
        filename = "study_circles.json"
        circles = read_json(filename, {
            "CS Study Circle": {
                "members": ["test_user", "rahul_cs"],
                "posts": [
                    {"user": "rahul_cs", "content": "Shared networks revision notes for next week's test!"}
                ]
            },
            "DSA Warriors": {
                "members": ["test_user"],
                "posts": [
                    {"user": "test_user", "content": "Practicing Heap questions today, join study room!"}
                ]
            }
        })
        
        if request.action == "list":
            return {"circles": circles}
            
        elif request.action == "create":
            if request.circle_name and request.circle_name not in circles:
                circles[request.circle_name] = {
                    "members": [request.user_id],
                    "posts": []
                }
                
        elif request.action == "join":
            if request.circle_name in circles:
                if request.user_id not in circles[request.circle_name]["members"]:
                    circles[request.circle_name]["members"].append(request.user_id)
                    
        elif request.action == "post":
            if request.circle_name in circles:
                circles[request.circle_name]["posts"].append({
                    "user": request.user_id,
                    "content": request.post_content
                })
                
        save_json(filename, circles)
        return {"status": "success", "circles": circles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- MONEY BRAIN ---
@app.post("/money/financial-profile")
async def update_financial_profile(profile: FinancialProfile):
    try:
        save_json(f"{profile.user_id}_financial_profile.json", profile.model_dump())
        return {"status": "success", "message": "Financial Profile updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/money/financial-profile/{user_id}")
async def get_financial_profile(user_id: str):
    data = read_json(f"{user_id}_financial_profile.json", None)
    if data:
        return data
    return {"status": "not_found", "message": "Profile does not exist."}

@app.post("/money/advisor")
async def money_advisor(request: MoneyAdvisorRequest):
    try:
        profile = read_json(f"{request.user_id}_financial_profile.json", {})
        system_prompt = f"""
        You are AAROHA's AI Financial Advisor. 
        Provide clear, mathematical, and logical explanations to the user's finance queries.
        User Profile financials: {json.dumps(profile)}
        Recent Transactions: {json.dumps(request.transactions)}
        
        Respond with a structured markdown explanation answering their question. Focus on budgeting and savings.
        """
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.question}
            ]
        )
        return {"answer": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/money/invest-mentor/{user_id}")
async def invest_mentor(user_id: str):
    try:
        profile = read_json(f"{user_id}_financial_profile.json", {})
        system_prompt = """
        You are AAROHA's Investment Learning Mentor.
        Provide beginner explanations, assess a simulated risk profile, and provide a dummy investment asset allocation map.
        
        Respond with EXACTLY a JSON structure matching:
        {
            "risk_assessment": "Moderate Risk - Suitable for balanced wealth growth.",
            "options": [
                {"vehicle": "Mutual Funds", "desc": "Diversified portfolio managed by pros. Recommended 50%"},
                {"vehicle": "Fixed Deposits", "desc": "Safe, guaranteed returns. Recommended 30%"},
                {"vehicle": "Gold / ETFs", "desc": "Inflation hedge. Recommended 20%"}
            ],
            "simulated_portfolio": [
                {"asset": "Equity", "allocation": 50},
                {"asset": "Debt", "allocation": 30},
                {"asset": "Commodity", "allocation": 20}
            ]
        }
        """
        user_prompt = f"Financial Genome: {json.dumps(profile)}"
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/money/decision-simulator")
async def decision_simulator(request: DecisionSimulatorRequest):
    try:
        profile = read_json(f"{request.user_id}_financial_profile.json", {})
        system_prompt = f"""
        You are AAROHA's AI Financial Decision Simulator.
        Evaluate the financial impact of purchasing '{request.item_name}' (Price: ₹{request.price}) in category '{request.category}'.
        
        Use the user's financial profile data: {json.dumps(profile)}
        
        Perform these tasks:
        1. Calculate simulated savings remaining after the purchase.
        2. Assess the status of their Emergency Fund (Safe vs. Compromised).
        3. Simulate how this purchase delays or affects their active financial goals.
        4. Offer 1-2 lower-cost alternatives.
        5. Give a final recommendation (Buy now, Wait, or Cancel).
        
        Respond with EXACTLY a JSON structure matching this schema:
        {{
            "item": "{request.item_name}",
            "price": {request.price},
            "savings_after": 35000,
            "emergency_fund": "Safe",
            "goal_impacts": [
                "Laptop goal: Completed",
                "Vacation goal: Delayed by 2 months"
            ],
            "alternatives": [
                "Wait 2 weeks for festival sale and save ₹8,000",
                "Buy refurbished model for ₹65,000"
            ],
            "recommendation": "Wait two weeks for the festival sale before purchasing."
        }}
        """
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Simulate purchase of {request.item_name}"}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/money/scam-scanner")
async def scam_scanner(request: ScamScannerRequest):
    try:
        system_prompt = """
        You are AAROHA's AI Scam and Fraud Detector.
        Analyze the text of the user's message, transaction warning, or SMS.
        
        Classify if this represents a financial threat (scam, phishing link, fake UPI request, lottery scam, QR fraud, etc.).
        
        Respond with EXACTLY a JSON structure matching this schema:
        {{
            "verdict": "Dangerous" | "Suspicious" | "Safe",
            "threat_score": 85,
            "scam_type": "UPI Fraud",
            "explanation": "Brief explanation of how the scam works and why this message is flagged.",
            "safety_tips": [
                "Do not click on the link.",
                "Never enter your UPI PIN to receive money.",
                "Report the phone number to National Cyber Crime Portal."
            ]
        }}
        """
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message_text}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/money/smart-shopping")
async def smart_shopping(request: SmartShoppingRequest):
    try:
        system_prompt = f"""
        You are AAROHA's Smart Shopping Price Tracker.
        Find price statistics and predictions for '{request.product_name}'.
        
        Respond with EXACTLY a JSON structure matching this schema:
        {{
            "product": "{request.product_name}",
            "current_average": 55000,
            "price_history": [58000, 56500, 55000],
            "stores": [
                {{"name": "Amazon", "price": 54500, "coupon": "SAVE500"}},
                {{"name": "Flipkart", "price": 55200, "coupon": "WELCOME10"}}
            ],
            "prediction": "Price is likely to drop by 8% during the upcoming Independence Day sale in 3 weeks.",
            "buy_or_wait": "Wait"
        }}
        """
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Track price of {request.product_name}"}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/money/subscription-optimizer")
async def subscription_optimizer(request: SubscriptionOptimizerRequest):
    try:
        system_prompt = """
        You are AAROHA's AI Subscription Optimizer.
        Evaluate the provided list of subscriptions and their usage metrics.
        Identify:
        1. Subscriptions that should be cancelled (low usage/value overlap).
        2. Potential monthly savings.
        3. Steps to cancel.
        
        Respond with EXACTLY a JSON structure matching this schema:
        {{
            "recommendations": [
                {{"subscription": "Streaming Service A", "action": "Cancel", "reason": "Used less than 1 hour in last 30 days."}}
            ],
            "estimated_savings": 299,
            "optimizer_tips": [
                "Share family plan where possible.",
                "Cancel auto-renewals on annual platforms."
            ]
        }}
        """
        user_prompt = f"Subscriptions context: {json.dumps(request.subscriptions)}"
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/money/money-twin")
async def money_twin_chat(request: MoneyTwinRequest):
    try:
        profile = read_json(f"{request.user_id}_financial_profile.json", {})
        system_prompt = f"""
        You are AAROHA's AI Money Twin, the personalized financial coach.
        You understand the user's financial habits (based on their profile) and proactively advise them.
        Here is the user's financial profile: {json.dumps(profile)}
        
        Respond in a helpful, friendly, and smart manner. Focus on savings and budget advice. Keep it under 3 sentences.
        """
        messages = [{"role": "system", "content": system_prompt}]
        for msg in request.chat_history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": request.message})
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )
        return {"answer": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- HEALTH BRAIN ---
@app.post("/health/health-profile")
async def update_health_profile(profile: HealthProfile):
    try:
        save_json(f"{profile.user_id}_health_profile.json", profile.model_dump())
        return {"status": "success", "message": "Health Profile updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health/health-profile/{user_id}")
async def get_health_profile(user_id: str):
    data = read_json(f"{user_id}_health_profile.json", None)
    if data:
        return data
    return {"status": "not_found", "message": "Profile does not exist."}

@app.post("/health/wellness")
async def health_wellness(request: HealthTrackerRequest):
    try:
        profile = read_json(f"{request.user_id}_health_profile.json", {})
        system_prompt = f"""
        You are AAROHA's AI Wellness Coach. 
        Evaluate the user's health profile and daily tracking metrics. Provide constructive recommendations.
        Note: DO NOT provide legal medical diagnoses. Include a basic wellness score out of 100 based on water/sleep compliance.
        
        Respond with EXACTLY a JSON structure matching:
        {{
            "wellness_score": 82,
            "tips": [
                "Your sleep of {request.sleep_hours} hrs is below target. Try winding down screen time 1 hr before bed.",
                "Your steps ({request.steps}) meet 80% of guidelines. Walk another 15 minutes today."
            ],
            "recommendations": [
                "Increase water intake to reach 3000ml goal.",
                "Perform light stretching to relieve stress."
            ]
        }}
        """
        user_prompt = f"Health profile: {json.dumps(profile)}"
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- LIFE BRAIN ---
@app.post("/life/life-profile")
async def update_life_profile(profile: LifeProfile):
    try:
        save_json(f"{profile.user_id}_life_profile.json", profile.model_dump())
        return {"status": "success", "message": "Life Profile updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/life/life-profile/{user_id}")
async def get_life_profile(user_id: str):
    data = read_json(f"{user_id}_life_profile.json", None)
    if data:
        return data
    return {"status": "not_found", "message": "Profile does not exist."}

@app.post("/life/govt-schemes")
async def govt_schemes(request: GovtSchemesRequest):
    try:
        system_prompt = """
        You are AAROHA's Government Scheme Finder (focused on Indian Civic Schemes).
        Find 2 relevant schemes based on age, state, and income.
        
        Respond with EXACTLY a JSON structure matching:
        {
            "schemes": [
                {
                    "name": "Pradhan Mantri Kaushal Vikas Yojana (PMKVY)",
                    "benefit": "Free skill development training and certification to youth.",
                    "apply_link": "https://www.pmkvyofficial.org/"
                }
            ]
        }
        """
        user_prompt = f"Demographics: Age: {request.age}, State: {request.state}, Monthly Income: ₹{request.income}"
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/life/travel")
async def travel_planner(request: TravelRequest):
    try:
        system_prompt = f"""
        You are AAROHA's Travel Assistant.
        Create a compact itinerary, travel reminders, packing list, and estimate a budget for a {request.duration_days}-day trip to {request.destination}.
        
        Respond with EXACTLY a JSON structure:
        {{
            "packing_checklist": ["Passport", "Chargers", "Weather-appropriate clothing"],
            "budget_estimate": "₹15,000 - ₹25,000",
            "itinerary_summary": [
                "Day 1: Arrival and local exploration.",
                "Day 2: Principal sightseeing landmarks.",
                "Day 3: Departure and souvenir transit."
            ]
        }}
        """
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Plan trip to {request.destination}"}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/life/daily-brief")
async def daily_brief(request: TwinChatRequest):
    try:
        career = read_json(f"{request.user_id}_profile.json", {})
        student = read_json(f"{request.user_id}_student_profile.json", {})
        money = read_json(f"{request.user_id}_financial_profile.json", {})
        health = read_json(f"{request.user_id}_health_profile.json", {})
        
        system_prompt = f"""
        You are AAROHA's AI Daily Assistant. 
        Review the user's connected profiles (Career, Student, Financials, Health).
        Generate a cohesive list of daily tasks to focus on, upcoming alerts, and calculate a daily productivity score (0-100).
        
        Respond with EXACTLY a JSON structure matching:
        {{
            "productivity_score": 85,
            "tasks": [
                "Check ATS matching suggestions for new resume variants",
                "Revise next study topic (Study Planner)",
                "Review budget limits - keep food expenses low today"
            ],
            "briefing": "Good morning Shash. Your overall health is steady. Focus on reviewing your resume score and setting up your daily trackers."
        }}
        """
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Generate today's focus brief."}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))