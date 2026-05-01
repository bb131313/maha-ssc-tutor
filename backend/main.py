from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import google.generativeai as genai
import os
from pathlib import Path
import json
from datetime import datetime, timedelta
import sqlite3
from typing import List, Optional, Dict
import threading
import time

app = FastAPI(title="Maharashtra SSC AI Tutor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path("static/audio")
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/audio", StaticFiles(directory="static/audio"), name="audio")

# ============ SESSION MANAGEMENT ============
SESSION_TIMEOUT_MINUTES = 120  # 2 hours
ACTIVE_SESSIONS: Dict[str, dict] = {}  # In-memory session store
SESSION_LOCK = threading.Lock()

def cleanup_expired_sessions():
    """Periodically clean up expired sessions"""
    while True:
        time.sleep(300)  # Run every 5 minutes
        with SESSION_LOCK:
            current_time = datetime.now()
            expired = [
                sid for sid, data in ACTIVE_SESSIONS.items()
                if (current_time - data['last_activity']).total_seconds() > SESSION_TIMEOUT_MINUTES * 60
            ]
            for sid in expired:
                del ACTIVE_SESSIONS[sid]

# Start session cleanup thread
session_cleanup_thread = threading.Thread(target=cleanup_expired_sessions, daemon=True)
session_cleanup_thread.start()

# Initialize SQLite Database for student progress
DB_PATH = "student_progress.db"
MAX_RETRIES = 3
RETRY_DELAY = 0.5  # seconds

def get_db_connection(timeout=5):
    """Get database connection with retry logic"""
    for attempt in range(MAX_RETRIES):
        try:
            conn = sqlite3.connect(DB_PATH, timeout=timeout)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.OperationalError as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                raise

def init_db():
    """Initialize SQLite database with retry logic"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Students table
        cursor.execute('''CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        # Progress tracking
        cursor.execute('''CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            subject TEXT,
            chapter TEXT,
            completed BOOLEAN DEFAULT 0,
            completion_date TIMESTAMP,
            time_spent_minutes INTEGER DEFAULT 0,
            FOREIGN KEY(student_id) REFERENCES students(student_id)
        )''')

        # Quiz results
        cursor.execute('''CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            subject TEXT,
            quiz_id TEXT,
            score INTEGER,
            total_questions INTEGER,
            percentage REAL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            answers_text TEXT,
            FOREIGN KEY(student_id) REFERENCES students(student_id)
        )''')

        # Learning history
        cursor.execute('''CREATE TABLE IF NOT EXISTS learning_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            subject TEXT,
            chapter TEXT,
            question_asked TEXT,
            explanation_received TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(student_id) REFERENCES students(student_id)
        )''')

        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

init_db()

# Use Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)
MODEL_CANDIDATES = [
    os.getenv("GEMINI_MODEL_NAME"),
    "models/gemini-2.5-flash",
    "models/gemini-flash-latest",
    "models/gemini-2.0-flash",
    "models/gemini-pro-latest",
]
MODEL_CANDIDATES = [name for name in MODEL_CANDIDATES if name]

def create_gemini_model():
    last_error = None
    for model_name in MODEL_CANDIDATES:
        try:
            # Test by generating content
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("test")
            return model_name
        except Exception as exc:
            last_error = exc
    raise RuntimeError(
        f"Unable to instantiate any Gemini model from {MODEL_CANDIDATES}: {last_error}"
    )

GEMINI_MODEL_NAME = create_gemini_model()

CURRICULUM = {
    "Mathematics": {"chapters": [
        {"id": 1, "title": "Linear Equations in Two Variables", "link": "https://www.ebalbharati.in/book-content/10/55/1/1"},
        {"id": 2, "title": "Quadratic Equations", "link": "https://www.ebalbharati.in/book-content/10/55/1/2"},
        {"id": 3, "title": "Arithmetic Progression", "link": "https://www.ebalbharati.in/book-content/10/55/1/3"},
        {"id": 4, "title": "Financial Planning", "link": "https://www.ebalbharati.in/book-content/10/55/1/4"},
        {"id": 5, "title": "Probability", "link": "https://www.ebalbharati.in/book-content/10/55/1/5"},
        {"id": 6, "title": "Statistics", "link": "https://www.ebalbharati.in/book-content/10/55/1/6"},
        {"id": 7, "title": "Geometry Triangles", "link": "https://www.ebalbharati.in/book-content/10/55/1/7"},
        {"id": 8, "title": "Coordinate Geometry", "link": "https://www.ebalbharati.in/book-content/10/55/1/8"},
        {"id": 9, "title": "Trigonometry", "link": "https://www.ebalbharati.in/book-content/10/55/1/9"},
        {"id": 10, "title": "Mensuration", "link": "https://www.ebalbharati.in/book-content/10/55/1/10"}
    ]},
    "Science": {"chapters": [
        {"id": 1, "title": "Gravitation", "link": "https://www.ebalbharati.in/book-content/10/56/1/1"},
        {"id": 2, "title": "Periodic Classification", "link": "https://www.ebalbharati.in/book-content/10/56/1/2"},
        {"id": 3, "title": "Chemical Reactions", "link": "https://www.ebalbharati.in/book-content/10/56/1/3"},
        {"id": 4, "title": "Effects of Electric Current", "link": "https://www.ebalbharati.in/book-content/10/56/1/4"},
        {"id": 5, "title": "Refraction of Light", "link": "https://www.ebalbharati.in/book-content/10/56/1/5"},
        {"id": 6, "title": "Lenses", "link": "https://www.ebalbharati.in/book-content/10/56/1/6"},
        {"id": 7, "title": "Carbon Compounds", "link": "https://www.ebalbharati.in/book-content/10/56/1/7"},
        {"id": 8, "title": "Metals and Non-metals", "link": "https://www.ebalbharati.in/book-content/10/56/1/8"},
        {"id": 9, "title": "Biological Processes", "link": "https://www.ebalbharati.in/book-content/10/56/1/9"},
        {"id": 10, "title": "Heredity and Evolution", "link": "https://www.ebalbharati.in/book-content/10/56/1/10"}
    ]},
    "English": {"chapters": [
        {"id": 1, "title": "The Song of the Rain", "link": "https://www.ebalbharati.in/book-content/10/59/1/1"},
        {"id": 2, "title": "The Last Labyrinth", "link": "https://www.ebalbharati.in/book-content/10/59/1/2"},
        {"id": 3, "title": "Subha-Saraswati Yojana", "link": "https://www.ebalbharati.in/book-content/10/59/1/3"},
        {"id": 4, "title": "Uncle's Dream", "link": "https://www.ebalbharati.in/book-content/10/59/1/4"},
        {"id": 5, "title": "The Attic", "link": "https://www.ebalbharati.in/book-content/10/59/1/5"},
        {"id": 6, "title": "Technology with a Human Face", "link": "https://www.ebalbharati.in/book-content/10/59/1/6"}
    ]},
    "Marathi": {"chapters": [
        {"id": 1, "title": "Bharat Ratna", "link": "https://www.ebalbharati.in/book-content/10/57/1/1"},
        {"id": 2, "title": "Saambhawalya", "link": "https://www.ebalbharati.in/book-content/10/57/1/2"},
        {"id": 3, "title": "Mazi Aai", "link": "https://www.ebalbharati.in/book-content/10/57/1/3"},
        {"id": 4, "title": "Tic-Tac-Toe", "link": "https://www.ebalbharati.in/book-content/10/57/1/4"},
        {"id": 5, "title": "Babal", "link": "https://www.ebalbharati.in/book-content/10/57/1/5"}
    ]},
    "Hindi": {"chapters": [
        {"id": 1, "title": "Bahut Girevo Na Chowk", "link": "https://www.ebalbharati.in/book-content/10/58/1/1"},
        {"id": 2, "title": "Gadbad Aatmagya", "link": "https://www.ebalbharati.in/book-content/10/58/1/2"},
        {"id": 3, "title": "Maa", "link": "https://www.ebalbharati.in/book-content/10/58/1/3"},
        {"id": 4, "title": "Kalam Ki Chai", "link": "https://www.ebalbharati.in/book-content/10/58/1/4"}
    ]},
    "Social Science": {"chapters": [
        {"id": 1, "title": "Imperialism", "link": "https://www.ebalbharati.in/book-content/10/60/1/1"},
        {"id": 2, "title": "Indian War of Independence 1857", "link": "https://www.ebalbharati.in/book-content/10/60/1/2"},
        {"id": 3, "title": "Indian National Movement", "link": "https://www.ebalbharati.in/book-content/10/60/1/3"},
        {"id": 4, "title": "Indian Physiographic Divisions", "link": "https://www.ebalbharati.in/book-content/10/60/2/1"},
        {"id": 5, "title": "Energy Resources", "link": "https://www.ebalbharati.in/book-content/10/60/2/2"},
        {"id": 6, "title": "Indian Constitution", "link": "https://www.ebalbharati.in/book-content/10/60/3/1"},
        {"id": 7, "title": "Parliament", "link": "https://www.ebalbharati.in/book-content/10/60/3/2"}
    ]}
}

class LearnReq(BaseModel):
    subject: str
    chapter: str
    language: str = "mr"

class StudentRegister(BaseModel):
    student_id: str
    name: str
    email: str

class UpdateProgress(BaseModel):
    student_id: str
    subject: str
    chapter: str
    time_spent: int

class QuizSubmission(BaseModel):
    student_id: str
    subject: str
    quiz_id: str
    answers: dict
    time_taken: int

class DetailedExplainReq(BaseModel):
    subject: str
    chapter: str
    topic: str
    language: str = "en"

# ============ DATABASE HELPERS ============

def register_student(student_id: str, name: str, email: str):
    """Register a new student"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO students VALUES (?, ?, ?, ?)''',
                      (student_id, name, email, datetime.now()))
        conn.commit()
        conn.close()
        
        # Create session for student
        create_session(student_id, name)
        
        return {"status": "success", "message": "Student registered"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def create_session(student_id: str, name: str):
    """Create a new session for student"""
    with SESSION_LOCK:
        ACTIVE_SESSIONS[student_id] = {
            'student_id': student_id,
            'name': name,
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'learning_history': []
        }

def update_session_activity(student_id: str):
    """Update last activity timestamp for session"""
    with SESSION_LOCK:
        if student_id in ACTIVE_SESSIONS:
            ACTIVE_SESSIONS[student_id]['last_activity'] = datetime.now()

def get_session(student_id: str) -> Optional[dict]:
    """Get session data if valid"""
    with SESSION_LOCK:
        if student_id not in ACTIVE_SESSIONS:
            return None
        session = ACTIVE_SESSIONS[student_id]
        current_time = datetime.now()
        if (current_time - session['last_activity']).total_seconds() > SESSION_TIMEOUT_MINUTES * 60:
            del ACTIVE_SESSIONS[student_id]
            return None
        return session

def mark_chapter_complete(student_id: str, subject: str, chapter: str):
    """Mark a chapter as completed"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO progress (student_id, subject, chapter, completed, completion_date)
                         VALUES (?, ?, ?, 1, ?)''',
                      (student_id, subject, chapter, datetime.now()))
        conn.commit()
        conn.close()
        
        # Update session
        update_session_activity(student_id)
        return True
    except Exception as e:
        return False

def get_student_progress(student_id: str):
    """Get student's progress summary"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get completed chapters
        cursor.execute('''SELECT subject, COUNT(*) as completed FROM progress 
                         WHERE student_id = ? AND completed = 1 
                         GROUP BY subject''', (student_id,))
        subjects_progress = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Get quiz performance  
        cursor.execute('''SELECT subject, AVG(percentage) as avg_score FROM quiz_results
                         WHERE student_id = ? 
                         GROUP BY subject''', (student_id,))
        quiz_scores = {row[0]: round(row[1], 2) for row in cursor.fetchall()}
        
        conn.close()
        return {"subjects_progress": subjects_progress, "quiz_scores": quiz_scores}
    except Exception as e:
        return {"subjects_progress": {}, "quiz_scores": {}, "error": str(e)}

def save_quiz_result(student_id: str, subject: str, quiz_id: str, score: int, total: int, answers):
    """Save quiz result"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        percentage = (score / total) * 100 if total > 0 else 0
        cursor.execute('''INSERT INTO quiz_results 
                         (student_id, subject, quiz_id, score, total_questions, percentage, answers_text)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (student_id, subject, quiz_id, score, total, percentage, json.dumps(answers)))
        conn.commit()
        conn.close()
        
        # Update session
        update_session_activity(student_id)
        return True
    except Exception as e:
        return False

def get_gemini_response(prompt, model="models/gemini-2.0-flash"):
    model = genai.GenerativeModel(model)
    response = model.generate_content(prompt)
    return response.text

@app.get("/")
def root():
    return {
        "app": "Maharashtra SSC AI Tutor",
        "status": "active",
        "model": GEMINI_MODEL_NAME,
    }

@app.get("/health")
def health_check():
    """Health check endpoint - returns immediately"""
    try:
        conn = get_db_connection(timeout=2)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "api": "responsive"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "timestamp": datetime.now().isoformat(),
            "database": "disconnected",
            "error": str(e)
        }

@app.post("/api/session/create")
def create_session_endpoint(student: StudentRegister):
    """Create a new session for student"""
    try:
        result = register_student(student.student_id, student.name, student.email)
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Session created",
                "student_id": student.student_id,
                "session_timeout_minutes": SESSION_TIMEOUT_MINUTES,
                "timestamp": datetime.now().isoformat()
            }
        raise HTTPException(400, result["message"])
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/session/validate/{student_id}")
def validate_session(student_id: str):
    """Validate if session is still active"""
    session = get_session(student_id)
    if session:
        update_session_activity(student_id)
        return {
            "valid": True,
            "student_id": student_id,
            "name": session['name'],
            "remaining_minutes": SESSION_TIMEOUT_MINUTES,
            "timestamp": datetime.now().isoformat()
        }
    return {
        "valid": False,
        "message": "Session expired. Please login again.",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/session/close/{student_id}")
def close_session(student_id: str):
    """Close session when student is done"""
    with SESSION_LOCK:
        if student_id in ACTIVE_SESSIONS:
            del ACTIVE_SESSIONS[student_id]
    return {"status": "success", "message": "Session closed"}

@app.get("/api/curriculum")
def get_curriculum():
    return CURRICULUM

@app.get("/api/subjects")
def get_subjects():
    return {"subjects": list(CURRICULUM.keys())}

# Question Bank - Previous Maharashtra Board Question Papers
QUESTION_BANK = {
    "Mathematics": {
        "Linear Equations in Two Variables": [
            {"id": "m1_q1", "question": "Find two numbers whose sum is 27 and product is 182.", "options": ["13, 14", "12, 15", "10, 17", "11, 16"], "correct": 0, "marks": 1},
            {"id": "m1_q2", "question": "A man travels 370 km in part by train and part by car. By train he travels 250 km and by car 120 km, taking 4 hours. What is the average speed?", "options": ["90 km/h", "92.5 km/h", "95 km/h", "80 km/h"], "correct": 1, "marks": 2},
            {"id": "m1_q3", "question": "Solve: 2x + 3y = 13 and x + y = 5", "options": ["x=2, y=3", "x=3, y=2", "x=4, y=1", "x=1, y=4"], "correct": 0, "marks": 1},
        ],
        "Quadratic Equations": [
            {"id": "m2_q1", "question": "Find the roots of x² - 5x + 6 = 0", "options": ["2, 3", "1, 6", "2.5, 2.5", "-2, -3"], "correct": 0, "marks": 1},
            {"id": "m2_q2", "question": "A rectangular field has area 60 m². If length is 7m more than width, find dimensions.", "options": ["5m × 12m", "4m × 15m", "6m × 10m", "3m × 20m"], "correct": 0, "marks": 2},
            {"id": "m2_q3", "question": "If roots of ax² + bx + c = 0 are equal, then discriminant = ?", "options": ["Positive", "Zero", "Negative", "Cannot determine"], "correct": 1, "marks": 1},
        ],
        "Arithmetic Progression": [
            {"id": "m3_q1", "question": "In AP: 2, 5, 8, 11... find 10th term", "options": ["29", "31", "33", "35"], "correct": 0, "marks": 1},
            {"id": "m3_q2", "question": "Sum of first 20 natural numbers = ?", "options": ["200", "210", "190", "220"], "correct": 1, "marks": 1},
        ],
    },
    "Science": {
        "Gravitation": [
            {"id": "s1_q1", "question": "What is the SI unit of gravitational force?", "options": ["Newton", "Dyne", "Kg", "Joule"], "correct": 0, "marks": 1},
            {"id": "s1_q2", "question": "If mass of earth is M and radius is R, acceleration due to gravity = ?", "options": ["GM/R", "GM/R²", "MR/G", "G/MR²"], "correct": 1, "marks": 2},
            {"id": "s1_q3", "question": "At what height from earth's surface, g = g/4?", "options": ["R", "R/2", "2R", "R/4"], "correct": 2, "marks": 2},
        ],
        "Refraction of Light": [
            {"id": "s2_q1", "question": "Which phenomenon shows that light travels in straight line?", "options": ["Refraction", "Reflection", "Shadow formation", "Diffraction"], "correct": 2, "marks": 1},
            {"id": "s2_q2", "question": "Refractive index of glass is 1.5. Find critical angle.", "options": ["30°", "41.8°", "45°", "60°"], "correct": 1, "marks": 2},
        ],
        "Chemical Reactions": [
            {"id": "s3_q1", "question": "In a combination reaction, two substances join to form...", "options": ["More than one product", "One product", "Multiple products", "Same substance"], "correct": 1, "marks": 1},
            {"id": "s3_q2", "question": "Combustion is a type of __ reaction.", "options": ["Endothermic", "Exothermic", "Reversible", "Decomposition"], "correct": 1, "marks": 1},
        ],
    },
    "English": {
        "The Song of the Rain": [
            {"id": "e1_q1", "question": "Who wrote 'The Song of the Rain'?", "options": ["William Wordsworth", "Rabindranath Tagore", "John Keats", "Samuel Coleridge"], "correct": 1, "marks": 1},
            {"id": "e1_q2", "question": "What does rain symbolize in the poem?", "options": ["Sadness", "Renewal and life", "Destruction", "Darkness"], "correct": 1, "marks": 2},
        ],
        "Technology with a Human Face": [
            {"id": "e2_q1", "question": "What is the main theme of 'Technology with a Human Face'?", "options": ["Technology is harmful", "Technology should serve humanity", "Humans should avoid technology", "Technology is too complex"], "correct": 1, "marks": 2},
        ],
    }
}

@app.post("/api/learn")
def learn(req: LearnReq):
    """Learn endpoint with session validation and error recovery"""
    try:
        if not GEMINI_API_KEY:
            raise HTTPException(500, "GEMINI_API_KEY not set. Get free key at https://aistudio.google.com")
        
        lang_map = {
            "mr": "in simple Marathi language (मराठी)",
            "hi": "in simple Hindi language (हिंदी)", 
            "en": "in simple and clear English"
        }
        
        prompt = f"""You are a friendly Maharashtra Board SSC 10th class teacher. Student is learning '{req.chapter}' in {req.subject}.

Explain {lang_map.get(req.language, 'in English')} in very simple words that 15-year-old students can easily understand.

Include exactly this format:
1. **Simple Explanation**: Explain what this topic is about in 3-4 simple sentences
2. **Why Learn This**: Why is this important for their exam and life? (2 sentences)
3. **Easy Example**: Give 1 real-world example they can relate to
4. **Board Question**: Share 1 typical Maharashtra Board question on this topic
5. **Memory Trick**: Give 1 memory tip to remember this concept easily
6. **Common Mistake**: What mistake do students usually make?

Keep language simple, friendly, and encouraging. Use easy words. Be like a teaching friend, not a textbook."""
        
        for attempt in range(MAX_RETRIES):
            try:
                explanation = get_gemini_response(prompt, GEMINI_MODEL_NAME)
                
                chapters = CURRICULUM.get(req.subject, {}).get("chapters", [])
                link = next((c["link"] for c in chapters if c["title"] == req.chapter), "")
                
                return {
                    "explanation": explanation, 
                    "audio_url": None, 
                    "textbook_link": link,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as inner_e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
                else:
                    raise inner_e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to generate explanation: {str(e)}")

@app.post("/api/detailed-explain")
def detailed_explain(req: DetailedExplainReq):
    """Get very detailed explanation of a specific topic with error recovery"""
    try:
        if not GEMINI_API_KEY:
            raise HTTPException(500, "GEMINI_API_KEY not set")
        
        prompt = f"""You are an expert Maharashtra Board SSC teacher. 
Student wants to understand '{req.topic}' from '{req.chapter}' chapter of {req.subject}.

Prepare a VERY DETAILED but EASY TO UNDERSTAND explanation in {req.language}:

1. **What is it?** - Simple definition (1-2 sentences)
2. **How does it work?** - Step-by-step process with examples
3. **Formula/Rule** - If applicable, write it clearly
4. **Real-life Examples** - Give 2-3 examples from daily life
5. **Board Questions** - Give 2 sample Maharashtra Board questions with answers
6. **Tips to Remember** - 3 tips to remember this concept forever
7. **Common Mistakes** - 3 mistakes students make and how to avoid them

Write in very simple language. Imagine explaining to a 15-year-old friend. Use bullet points and simple formatting."""
        
        for attempt in range(MAX_RETRIES):
            try:
                explanation = get_gemini_response(prompt, GEMINI_MODEL_NAME)
                return {"detailed_explanation": explanation}
            except Exception as inner_e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
                else:
                    raise inner_e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to generate detailed explanation: {str(e)}")

@app.post("/api/register-student")
def register_student_api(student: StudentRegister):
    """Register a new student"""
    try:
        result = register_student(student.student_id, student.name, student.email)
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Welcome to Maharashtra SSC Tutor!",
                "student_id": student.student_id,
                "session_timeout_minutes": SESSION_TIMEOUT_MINUTES,
                "timestamp": datetime.now().isoformat()
            }
        raise HTTPException(400, result["message"])
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/mark-complete")
def mark_complete_api(progress: UpdateProgress):
    """Mark a chapter as complete"""
    try:
        # Validate session
        update_session_activity(progress.student_id)
        
        success = mark_chapter_complete(progress.student_id, progress.subject, progress.chapter)
        if success:
            return {
                "status": "success",
                "message": f"Great! '{progress.chapter}' marked as complete!",
                "timestamp": datetime.now().isoformat()
            }
        return {
            "status": "warning",
            "message": "Could not save progress, but you can continue learning",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/student-progress/{student_id}")
def get_progress_api(student_id: str):
    """Get student's progress summary"""
    try:
        # Validate session
        update_session_activity(student_id)
        
        progress = get_student_progress(student_id)
        return {
            "student_id": student_id,
            "progress": progress,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/quiz/{subject}/{chapter}")
def get_quiz(subject: str, chapter: str):
    """Get quiz questions for a chapter from board papers"""
    if subject not in QUESTION_BANK:
        raise HTTPException(404, f"Subject '{subject}' not found")
    
    if chapter not in QUESTION_BANK[subject]:
        raise HTTPException(404, f"Chapter '{chapter}' not found in {subject}")
    
    questions = QUESTION_BANK[subject][chapter]
    
    # Return questions without answers (for security)
    quiz_data = []
    for q in questions:
        quiz_data.append({
            "id": q["id"],
            "question": q["question"],
            "options": q["options"],
            "marks": q["marks"]
        })
    
    return {
        "subject": subject,
        "chapter": chapter,
        "total_questions": len(quiz_data),
        "total_marks": sum(q["marks"] for q in questions),
        "questions": quiz_data
    }

@app.post("/api/submit-quiz")
def submit_quiz(submission: QuizSubmission):
    """Submit quiz answers and get results with session management"""
    try:
        # Validate session
        update_session_activity(submission.student_id)
        
        subject = submission.subject
        chapter_title = None
        
        # Find chapter name from answers
        if subject not in QUESTION_BANK:
            raise HTTPException(404, f"Subject not found")
        
        # Get the actual chapter
        for chapter_name, questions in QUESTION_BANK[subject].items():
            for q in questions:
                if q["id"] in submission.answers:
                    chapter_title = chapter_name
                    break
            if chapter_title:
                break
        
        if not chapter_title:
            raise HTTPException(400, "Invalid quiz submission")
        
        questions = QUESTION_BANK[subject][chapter_title]
        score = 0
        total_marks = 0
        results = []
        
        # Grade answers
        for question in questions:
            total_marks += question["marks"]
            student_answer = submission.answers.get(question["id"])
            
            if student_answer is not None:
                # Check if answer is correct
                is_correct = (student_answer == question["correct"])
                if is_correct:
                    score += question["marks"]
                
                results.append({
                    "question_id": question["id"],
                    "question": question["question"],
                    "student_answer": question["options"][student_answer] if student_answer < len(question["options"]) else "No answer",
                    "correct_answer": question["options"][question["correct"]],
                    "is_correct": is_correct,
                    "marks": question["marks"] if is_correct else 0
                })
        
        # Save result to database with retry
        for attempt in range(MAX_RETRIES):
            try:
                save_quiz_result(submission.student_id, subject, submission.quiz_id, score, total_marks, submission.answers)
                break
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    # Log but don't fail - let student see results
                    print(f"Warning: Could not save quiz result: {e}")
        
        percentage = (score / total_marks * 100) if total_marks > 0 else 0
        
        return {
            "student_id": submission.student_id,
            "subject": subject,
            "chapter": chapter_title,
            "score": score,
            "total_marks": total_marks,
            "percentage": round(percentage, 2),
            "passed": percentage >= 50,
            "message": f"Great effort! You scored {score}/{total_marks} ({percentage:.1f}%)" if percentage >= 50 else f"You scored {score}/{total_marks}. Keep practicing!",
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error processing quiz: {str(e)}")

@app.get("/api/ask-question")
def ask_question(student_id: str, subject: str, chapter: str, question: str, language: str = "en"):
    """Student can ask any question about a chapter with session management"""
    try:
        # Validate and update session
        update_session_activity(student_id)
        
        if not GEMINI_API_KEY:
            raise HTTPException(500, "API key not configured")
        
        prompt = f"""You are a helpful Maharashtra Board SSC teacher. 
A student asked about '{chapter}' in {subject}:
"{question}"

Answer in this language: {language}

Provide a clear, simple answer in points. Use examples. Make it easy to understand for a 10th class student."""
        
        for attempt in range(MAX_RETRIES):
            try:
                answer = get_gemini_response(prompt, GEMINI_MODEL_NAME)
                return {
                    "question": question,
                    "answer": answer,
                    "subject": subject,
                    "chapter": chapter,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as inner_e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
                else:
                    raise inner_e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error answering question: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
