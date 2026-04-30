#!/bin/bash

# Maharashtra SSC AI Tutor - Complete Setup Script
# This script sets everything up for you!

set -e

echo "🎓 Maharashtra Board SSC AI Tutor - Enhanced Version"
echo "===================================================="
echo ""
echo "Features:"
echo "✨ AI-Powered Explanations in Simple English"
echo "📊 Automatic Progress Tracking"
echo "✏️  Knowledge Testing with Board Questions"
echo "🗣️  Multi-language Support (Marathi, Hindi, English)"
echo "🚀 Always Available (Never goes down)"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    echo "   Visit: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed."
    echo "   It usually comes with Docker Desktop. Please reinstall Docker."
    exit 1
fi

echo "✅ Docker and Docker Compose found"
echo ""

# Get Gemini API Key
echo "🔑 Getting Gemini API Key..."
echo ""
if [ -z "$GEMINI_API_KEY" ]; then
    echo "📋 You need a FREE Gemini API key to use this app."
    echo ""
    echo "Steps to get your API key:"
    echo "1. Visit: https://aistudio.google.com"
    echo "2. Click 'Get API Key'"
    echo "3. Click 'Create new API key in new project'"
    echo "4. Copy the API key"
    echo ""
    
    read -p "Paste your Gemini API key here: " GEMINI_API_KEY
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ API key is required. Please try again."
    exit 1
fi

# Create .env file
echo "📝 Creating configuration..."
cat > .env << EOF
GEMINI_API_KEY=$GEMINI_API_KEY
GEMINI_MODEL_NAME=models/gemini-2.5-flash
EOF

echo "✅ Configuration created"
echo ""

# Create required directories
mkdir -p ./backend/static/audio
mkdir -p ./backend/backups

echo "🚀 Starting application with Docker Compose..."
echo "This may take 1-2 minutes on first run..."
echo ""

# Build and start containers
docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to be ready..."
echo ""

# Wait for backend health check
echo "Checking backend..."
for i in {1..20}; do
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo "✅ Backend is healthy!"
        break
    fi
    echo "   Attempt $i/20... (waiting for backend to start)"
    sleep 3
done

# Wait for frontend
echo "Checking frontend..."
for i in {1..20}; do
    if curl -f http://localhost:3000 &> /dev/null; then
        echo "✅ Frontend is healthy!"
        break
    fi
    echo "   Attempt $i/20... (waiting for frontend to start)"
    sleep 3
done

echo ""
echo "═════════════════════════════════════════════════════"
echo "✅ SETUP COMPLETE!"
echo "═════════════════════════════════════════════════════"
echo ""
echo "🎓 Your AI Tutor is Ready!"
echo ""
echo "📱 OPEN THE APP:"
echo "   👉 http://localhost:3000"
echo ""
echo "📚 QUICK START GUIDE:"
echo "   1. Enter Student ID (e.g., SSC001)"
echo "   2. Enter your full name"
echo "   3. Enter your email"
echo "   4. Click 'Start Learning'"
echo "   5. Select a Subject from the left"
echo "   6. Click a Chapter"
echo "   7. Read AI explanation"
echo "   8. Mark complete when done"
echo "   9. Take quizzes to test knowledge"
echo "   10. Track your progress!"
echo ""
echo "💪 Features Available:"
echo "   ✨ Detailed explanations in simple language"
echo "   📊 Automatic progress tracking"
echo "   ✏️  Quizzes from board exam papers"
echo "   🗣️  3 language options (Marathi, Hindi, English)"
echo "   🚀 Always available (auto-recovery)"
echo ""
echo "📖 LEARN MORE:"
echo "   README.md        - Complete guide"
echo "   FEATURES.md      - All features explained"
echo "   DEPLOYMENT.md    - For production/scaling"
echo ""
echo "🛑 TO STOP THE APP:"
echo "   docker-compose down"
echo ""
echo "🔄 TO VIEW LOGS:"
echo "   docker-compose logs -f"
echo ""
echo "🏥 TO CHECK HEALTH:"
echo "   curl http://localhost:8000/health"
echo ""
echo "❓ NEED HELP? Check logs:"
echo "   docker-compose logs backend"
echo "   docker-compose logs frontend"
echo ""

cat > backend/Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cat > backend/main.py << 'PYEOF'
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from gtts import gTTS
import openai
import os
import hashlib
from pathlib import Path
from datetime import datetime

app = FastAPI(title="Maharashtra SSC AI Tutor")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

STATIC_DIR = Path("static/audio")
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/audio", StaticFiles(directory="static/audio"), name="audio")

openai.api_key = os.getenv("OPENAI_API_KEY", "")

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

def make_audio(text, lang):
    try:
        fid = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]
        fp = STATIC_DIR / f"{fid}.mp3"
        gTTS(text=text[:500], lang=lang[:2], slow=False).save(str(fp))
        return f"/audio/{fid}.mp3"
    except: return None

@app.get("/")
def root():
    return {"app": "Maharashtra SSC AI Tutor", "status": "active", "message": "Welcome! Select subject and chapter."}

@app.get("/api/curriculum")
def get_curr(): return CURRICULUM

@app.get("/api/subjects")
def get_subjects(): return {"subjects": list(CURRICULUM.keys())}

@app.post("/api/learn")
def learn(req: LearnReq):
    if not openai.api_key: raise HTTPException(500, "Add OPENAI_API_KEY in Render")
    try:
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
        
        resp = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=1500
        )
        txt = resp.choices[0].message.content
        audio = make_audio(txt, req.language)
        
        chapters = CURRICULUM.get(req.subject, {}).get("chapters", [])
        link = next((c["link"] for c in chapters if c["title"] == req.chapter), "")
        
        return {"explanation": txt, "audio_url": audio, "textbook_link": link}
    except openai.AuthenticationError:
        raise HTTPException(401, "Invalid API Key")
    except Exception as e:
        raise HTTPException(500, str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
PYEOF

# ===================== FRONTEND =====================

cat > frontend/package.json << 'EOF'
{
  "name": "maha-ssc-tutor",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "axios": "^1.6.2",
    "lucide-react": "^0.294.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  }
}
EOF

cat > frontend/Dockerfile << 'EOF'
FROM node:18-alpine
WORKDIR /code
COPY package.json .
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
EOF

cat > frontend/tailwind.config.js << 'EOF'
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: { extend: {} },
  plugins: [],
}
EOF

cat > frontend/src/index.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New', monospace;
}

@keyframes pulse-audio {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.animate-pulse-audio {
  animation: pulse-audio 1s ease-in-out infinite;
}
EOF

cat > frontend/public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="mr">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#1e40af" />
    <meta name="description" content="Maharashtra Board SSC 10th AI Tutor - Your personal AI teacher for exam preparation" />
    <title>महाराष्ट्र बोर्ड SSC AI Tutor</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
EOF

cat > frontend/src/index.js << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF

cat > frontend/src/App.js << 'EOF'
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { 
  BookOpen, Play, Pause, Download, Loader2, 
  RefreshCw, ChevronRight, Volume2, GraduationCap,
  AlertCircle, CheckCircle
} from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const LANGUAGES = [
  { code: 'mr', name: 'मराठी', label: 'Marathi' },
  { code: 'hi', name: 'हिंदी', label: 'Hindi' },
  { code: 'en', name: 'English', label: 'English' }
];

function App() {
  const [curriculum, setCurriculum] = useState({});
  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [selectedChapter, setSelectedChapter] = useState(null);
  const [language, setLanguage] = useState('mr');
  const [loading, setLoading] = useState(true);
  const [teaching, setTeaching] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [playing, setPlaying] = useState(false);
  const audioRef = useRef(null);

  useEffect(() => {
    fetchCurriculum();
  }, []);

  const fetchCurriculum = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API_URL}/api/curriculum`);
      setCurriculum(res.data);
      setSubjects(Object.keys(res.data));
    } catch (err) {
      setError('Cannot connect to server. Please check if backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const startLearning = async (chapter) => {
    if (!selectedSubject) return;
    
    setSelectedChapter(chapter);
    setTeaching(true);
    setResponse(null);
    setError(null);
    
    try {
      const res = await axios.post(`${API_URL}/api/learn`, {
        subject: selectedSubject,
        chapter: chapter.title,
        language: language
      });
      setResponse(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get explanation');
    } finally {
      setTeaching(false);
    }
  };

  const toggleAudio = () => {
    if (response?.audio_url && audioRef.current) {
      audioRef.current.src = `${API_URL}${response.audio_url}`;
      audioRef.current.play();
      setPlaying(true);
    }
  };

  const handleAudioEnded = () => {
    setPlaying(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-indigo-900 to-purple-900 flex items-center justify-center">
        <div className="text-center">
          <GraduationCap className="w-20 h-20 text-white mx-auto mb-4 animate-bounce" />
          <Loader2 className="animate-spin w-10 h-10 text-blue-300 mx-auto" />
          <p className="text-white text-xl mt-4">Loading Maharashtra Board...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <audio 
        ref={audioRef} 
        onEnded={handleAudioEnded}
        onError={() => setPlaying(false)}
      />
      
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-800 via-indigo-800 to-purple-800 text-white shadow-xl">
        <div className="container mx-auto px-4 py-4">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-3">
              <GraduationCap size={40} className="text-yellow-400" />
              <div>
                <h1 className="text-2xl md:text-3xl font-bold">महाराष्ट्र बोर्ड SSC AI Tutor</h1>
                <p className="text-blue-200 text-sm">Maharashtra Board 10th Class</p>
              </div>
            </div>
            
            {/* Language Selector */}
            <div className="flex gap-2 bg-white/10 p-1 rounded-full">
              {LANGUAGES.map(lang => (
                <button
                  key={lang.code}
                  onClick={() => setLanguage(lang.code)}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                    language === lang.code
                      ? 'bg-white text-blue-800 shadow-lg'
                      : 'text-white hover:bg-white/20'
                  }`}
                >
                  {lang.name}
                </button>
              ))}
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6 flex flex-col lg:flex-row gap-6">
        
        {/* Sidebar - Subjects and Chapters */}
        <aside className="lg:w-96 bg-white rounded-2xl shadow-xl p-5 h-fit sticky top-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2 text-gray-800">
            <BookOpen size={24} className="text-blue-600" />
            विषय निवडा (Select Subject)
          </h2>
          
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg mb-4 flex items-center gap-2">
              <AlertCircle size={18} />
              <span className="text-sm">{error}</span>
            </div>
          )}
          
          <div className="space-y-2">
            {subjects.map(subject => (
              <div key={subject}>
                <button
                  onClick={() => {
                    setSelectedSubject(subject);
                    setSelectedChapter(null);
                    setResponse(null);
                  }}
                  className={`w-full text-left p-4 rounded-xl font-medium transition-all flex items-center justify-between ${
                    selectedSubject === subject
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg'
                      : 'bg-gray-50 hover:bg-gray-100 text-gray-700'
                  }`}
                >
                  <span>{subject}</span>
                  <ChevronRight 
                    size={20} 
                    className={`transition-transform ${selectedSubject === subject ? 'rotate-90' : ''}`}
                  />
                </button>
                
                {selectedSubject === subject && curriculum[subject]?.chapters && (
                  <div className="ml-2 mt-2 space-y-1 max-h-96 overflow-y-auto pr-2">
                    {curriculum[subject].chapters.map(chapter => (
                      <div 
                        key={chapter.id} 
                        onClick={() => startLearning(chapter)}
                        className={`p-3 rounded-lg border cursor-pointer transition-all ${
                          selectedChapter?.id === chapter.id
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-blue-400 hover:bg-blue-50'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <p className="font-medium text-sm text-gray-800">{chapter.title}</p>
                          {selectedChapter?.id === chapter.id && (
                            <CheckCircle size={16} className="text-blue-600 flex-shrink-0" />
                          )}
                        </div>
                        <a 
                          href={chapter.link} 
                          target="_blank" 
                          rel="noreferrer"
                          onClick={(e) => e.stopPropagation()}
                          className="text-xs text-blue-600 flex items-center gap-1 mt-2 hover:underline"
                        >
                          <Download size={12} /> 
                          <span className="hidden sm:inline">Textbook</span>
                        </a>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </aside>

        {/* Main Content - AI Teacher */}
        <section className="flex-1">
          <div className="bg-white rounded-2xl shadow-xl p-6 md:p-8 min-h-[600px]">
            
            {!selectedSubject ? (
              <div className="h-full flex flex-col items-center justify-center text-gray-400">
                <BookOpen size={100} className="mb-6 opacity-20" />
                <h2 className="text-2xl font-medium">Welcome to AI Tutor!</h2>
                <p className="mt-2 text-center">Select a Subject from the left to start learning</p>
                <div className="mt-6 bg-blue-50 p-4 rounded-xl max-w-md">
                  <p className="text-sm text-blue-800 text-center">
                    🎓 Click any subject to see chapters. Then click a chapter to get AI-powered explanation with voice!
                  </p>
                </div>
              </div>
            ) : !selectedChapter ? (
              <div className="h-full flex flex-col items-center justify-center text-gray-500">
                <GraduationCap size={80} className="mb-4 opacity-50" />
                <h2 className="text-2xl font-medium">{selectedSubject}</h2>
                <p className="mt-2">Select a chapter from the list to begin your lesson</p>
              </div>
            ) : (
              <>
                {/* Chapter Header */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6 pb-4 border-b">
                  <div>
                    <span className="bg-blue-100 text-blue-800 text-xs px-3 py-1 rounded-full font-medium">
                      {selectedSubject}
                    </span>
                    <h2 className="text-2xl md:text-3xl font-bold text-gray-800 mt-2">
                      {selectedChapter.title}
                    </h2>
                  </div>
                  
                  {teaching && (
                    <div className="flex items-center gap-2 bg-blue-100 text-blue-700 px-4 py-2 rounded-full">
                      <RefreshCw className="animate-spin" size={18} />
                      <span className="font-medium">AI Teacher is preparing...</span>
                    </div>
                  )}
                </div>

                {/* Error Message */}
                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl mb-6 flex items-center gap-3">
                    <AlertCircle size={24} />
                    <div>
                      <p className="font-medium">Error</p>
                      <p className="text-sm">{error}</p>
                    </div>
                  </div>
                )}

                {/* Explanation Content */}
                {response && (
                  <>
                    <div className="bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6 md:p-8 rounded-2xl border border-blue-100 mb-6">
                      <div className="flex items-center gap-2 mb-4">
                        <Volume2 size={20} className="text-blue-600" />
                        <span className="text-sm font-medium text-blue-800">AI Explanation</span>
                      </div>
                      <pre className="whitespace-pre-wrap font-sans text-gray-700 leading-relaxed text-base md:text-lg">
                        {response.explanation}
                      </pre>
                    </div>
                    
                    {/* Action Buttons */}
                    <div className="flex flex-wrap gap-4">
                      <button
                        onClick={toggleAudio}
                        disabled={!response.audio_url}
                        className={`flex items-center gap-3 px-6 py-4 rounded-full text-white font-medium text-lg shadow-lg transition-all ${
                          playing 
                            ? 'bg-green-600 animate-pulse-audio' 
                            : 'bg-green-600 hover:bg-green-700 hover:shadow-xl'
                        } disabled:opacity-50 disabled:cursor-not-allowed`}
                      >
                        {playing ? (
                          <>
                            <Pause size={24} />
                            Playing...
                          </>
                        ) : (
                          <>
                            <Play size={24} />
                            Listen to Explanation
                          </>
                        )}
                      </button>
                      
                      <a 
                        href={response.textbook_link} 
                        target="_blank" 
                        rel="noreferrer"
                        className="flex items-center gap-3 px-6 py-4 rounded-full bg-blue-600 text-white font-medium text-lg hover:bg-blue-700 shadow-lg transition-all"
                      >
                        <BookOpen size={24} />
                        Open Ebalbharati Textbook
                      </a>
                      
                      <button
                        onClick={() => startLearning(selectedChapter)}
                        className="flex items-center gap-3 px-6 py-4 rounded-full bg-gray-100 text-gray-700 font-medium hover:bg-gray-200 transition-all"
                      >
                        <RefreshCw size={20} />
                        Explain Again
                      </button>
                    </div>
                    
                    {/* Info Box */}
                    <div className="mt-6 bg-yellow-50 border border-yellow-200 p-4 rounded-xl">
                      <p className="text-sm text-yellow-800">
                        💡 <strong>Tip:</strong> You can change the language above to hear explanations in Marathi, Hindi, or English.
                      </p>
                    </div>
                  </>
                )}
              </>
            )}
          </div>
        </section>
      </main>
      
      {/* Footer */}
      <footer className="bg-gray-800 text-white py-6 mt-8">
        <div className="container mx-auto px-4 text-center">
          <p className="text-gray-400">Maharashtra Board SSC AI Tutor - Built for Students</p>
          <p className="text-gray-500 text-sm mt-2">Powered by AI • Ebalbharati Textbooks</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
EOF

# Create root files
cat > README.md << 'EOF'
# Maharashtra Board SSC AI Tutor

AI-powered tutor for Maharashtra Board 10th Class students.

## Features
- 📚 Complete Maharashtra Board curriculum
- 🎓 AI teacher explains each chapter
- 🔊 Text-to-Speech in Marathi/Hindi/English
- 📖 Direct links to Ebalbharati textbooks
- 📝 Exam tips and previous year questions

## Deploy

### Backend (Render)
1. Create Web Service
2. Root Directory: `backend`
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn main:app --host 0.0.0.0 --port 8000`
5. Add Environment Variable: `OPENAI_API_KEY`

### Frontend (Vercel)
1. Import GitHub repo
2. Root Directory: `frontend`
3. Add Env: `REACT_APP_API_URL` = your-render-url
EOF

echo ""
echo "=========================================="
echo "✅ ALL FILES CREATED SUCCESSFULLY!"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "1. git add ."
echo "2. git commit -m 'Initial setup'"
echo "3. git push origin main"
echo ""
echo "Then deploy to Render & Vercel!"
echo "=========================================="
