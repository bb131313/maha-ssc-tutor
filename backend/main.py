from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import google.genai as genai
import os
from pathlib import Path

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

# Use Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_API_KEY)
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
            response = client.models.generate_content(
                model=model_name,
                contents="test"
            )
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

def get_gemini_response(prompt, model="models/gemini-2.0-flash"):
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    return response.text

@app.get("/")
def root():
    return {
        "app": "Maharashtra SSC AI Tutor",
        "status": "active",
        "model": GEMINI_MODEL_NAME,
    }

@app.get("/api/curriculum")
def get_curriculum():
    return CURRICULUM

@app.get("/api/subjects")
def get_subjects():
    return {"subjects": list(CURRICULUM.keys())}

@app.post("/api/learn")
def learn(req: LearnReq):
    if not GEMINI_API_KEY:
        raise HTTPException(500, "GEMINI_API_KEY not set. Get free key at https://aistudio.google.com")
    
    lang_map = {
        "mr": "in Marathi (मराठी)",
        "hi": "in Hindi (हिंदी)", 
        "en": "in English"
    }
    
    prompt = f"""You are expert Maharashtra Board SSC 10th class teacher. Student is studying '{req.chapter}' in {req.subject}.
Respond {lang_map.get(req.language, 'in English')}.
Rules:
1. Simple explanation with examples
2. 2 real-world examples student can relate to
3. 1 common Maharashtra Board exam question about this topic
4. Memory tip for exam preparation
5. Be encouraging and friendly"""
    
    try:
        explanation = get_gemini_response(prompt, GEMINI_MODEL_NAME)
        
        chapters = CURRICULUM.get(req.subject, {}).get("chapters", [])
        link = next((c["link"] for c in chapters if c["title"] == req.chapter), "")
        
        return {
            "explanation": explanation, 
            "audio_url": None, 
            "textbook_link": link
        }
    except Exception as e:
        raise HTTPException(500, str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
