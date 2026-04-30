# 📚 Maharashtra Board SSC AI Tutor

A complete AI-powered learning platform for Maharashtra Board 10th Class students with voice support, progress tracking, and knowledge testing based on previous board exam questions.

## ✨ Features

### 🎓 Learning Features
- **Complete Maharashtra Board Curriculum** - All subjects, chapters, and topics
- **AI-Powered Explanations** - Simple, easy-to-understand explanations in plain English/Marathi/Hindi
- **Detailed Topic Breakdowns** - Get in-depth explanation of any concept with:
  - Simple definitions
  - Step-by-step processes with examples
  - Real-world examples to relate to
  - Formulas and rules clearly written
  - 3+ memory tricks to remember forever
  - Common mistakes to avoid (3 examples)

### 🗣️ Voice Features
- **Multi-language Support** - Learn in Marathi (मराठी), Hindi (हिंदी), or English
- **Simple Language** - Explanations written for 15-year-old students, not textbooks
- **Real-world Examples** - Teacher uses examples from daily life

### 📊 Progress Tracking
- **Automatic Progress Saving** - All learning is automatically tracked
- **Chapter Completion** - Mark chapters as complete
- **Progress Dashboard** - See your learning stats:
  - Chapters completed per subject
  - Quiz performance percentage
  - Subject-wise progress tracking
- **Session Management** - Maintain sessions for up to 2 hours
- **Learning History** - View your learning journey

### ✏️ Knowledge Testing
- **Board Question Bank** - Questions from previous Maharashtra SSC exam papers
- **Chapter-wise Quizzes** - Test knowledge on each chapter
- **Instant Grading** - Get immediate feedback with:
  - Your score and percentage
  - Correct answers explained
  - Detailed feedback on each question
- **Performance Tracking** - Track quiz performance by subject

### 🔄 Reliability & Always Available
- **Health Checks** - App monitors its own health every 30 seconds
- **Auto-Recovery** - Automatically recovers from temporary failures
- **Session Persistence** - Your session remains active for 2 hours of inactivity
- **Offline Resilience** - Gracefully handles connection issues
- **Zero Downtime** - Using Docker with restart policies ensures the app is always running

## 🚀 Quick Start

### Using Docker Compose (Recommended)

```bash
# 1. Set your Gemini API Key
export GEMINI_API_KEY="your-gemini-api-key-here"

# 2. Start both backend and frontend
docker-compose up

# 3. Open in browser
# Go to http://localhost:3000
```

### Manual Setup

#### Backend
```bash
cd backend
pip install -r requirements.txt
export GEMINI_API_KEY="your-gemini-api-key"
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
export REACT_APP_API_URL="http://localhost:8000"
npm start
```

## 📖 How to Use

### 1. **Register**
   - Enter Student ID (Roll Number)
   - Enter your name
   - Enter email
   - Click "Start Learning"

### 2. **Select Subject & Chapter**
   - Click a subject from left sidebar
   - Click a chapter to get AI explanation

### 3. **Learn**
   - Read AI-powered explanation
   - Change language using buttons at top
   - Open textbook link for reference
   - Mark chapter as complete

### 4. **Track Progress**
   - View progress card in sidebar
   - See chapters completed per subject
   - Check quiz performance

### 5. **Test Knowledge**
   - Take quizzes for each chapter
   - Answer from previous board papers
   - See instant results and explanations
   - Review correct answers

## 🏗️ Architecture

```
Maharashtra SSC AI Tutor
├── Backend (FastAPI)
│   ├── SQLite Database (Progress tracking)
│   ├── Gemini AI API (Explanations)
│   ├── Session Management (2-hour sessions)
│   └── Health Checks (30-second intervals)
├── Frontend (React)
│   ├── Session Management
│   ├── Auto-reconnect on failure
│   ├── Progress Dashboard
│   └── Quiz Interface
└── Docker Compose (Orchestration)
    ├── Container Auto-restart
    └── Health Check Monitoring
```

## 📚 Subjects & Topics Included

- **Mathematics** - Equations, Quadratic, Progressions, Probability, Statistics, Geometry, Trigonometry, Mensuration
- **Science** - Gravitation, Periodic Classification, Chemical Reactions, Electricity, Optics, Organic Chemistry, Metals/Non-metals, Biology, Heredity
- **English** - Literature and comprehension from board-approved textbooks
- **Marathi** - Literature and comprehension in Marathi
- **Hindi** - Literature and comprehension in Hindi
- **Social Science** - History, Geography, Civics, Economics

## 🔌 API Endpoints

### Session Management
- `POST /api/session/create` - Register and create session
- `GET /api/session/validate/{student_id}` - Check if session is active
- `POST /api/session/close/{student_id}` - Close session

### Learning
- `POST /api/learn` - Get AI explanation for a chapter
- `POST /api/detailed-explain` - Get detailed explanation of a topic
- `GET /api/ask-question` - Ask any question about a topic

### Progress
- `POST /api/mark-complete` - Mark chapter as complete
- `GET /api/student-progress/{student_id}` - Get student progress

### Quiz/Testing
- `GET /api/quiz/{subject}/{chapter}` - Get quiz questions
- `POST /api/submit-quiz` - Submit and grade quiz

### Health
- `GET /health` - Health check endpoint
- `GET /` - API status

## 💾 Database Schema

The app uses SQLite with these tables:
- **students** - Student registration (ID, name, email, created_at)
- **progress** - Chapter completion tracking (student_id, subject, chapter, completed, completion_date, time_spent)
- **quiz_results** - Quiz performance (student_id, subject, score, percentage, completed_at)
- **learning_history** - Questions asked and explanations received

## 🛠️ Configuration

### Environment Variables
```bash
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL_NAME=models/gemini-2.5-flash
REACT_APP_API_URL=http://localhost:8000
```

### Session Configuration
- **Session Timeout**: 120 minutes of inactivity
- **Health Check Interval**: 30 seconds
- **Retry Attempts**: 5 before giving up
- **Timeout Warning**: 10 seconds before session expires

## 📱 Browser Compatibility
- Chrome/Chromium (Recommended)
- Firefox
- Safari
- Edge
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🚨 What Happens When Connection is Lost?

1. **Frontend** - Shows "Offline" status, retries automatically
2. **Backend** - Health check fails, Docker restarts container automatically
3. **Session** - Your session remains active for 2 hours
4. **Progress** - All saved progress is retained in database
5. **Recovery** - When connection is restored, you continue where you left off

## 🌐 Deployment

### Using Docker Compose (Recommended for Production)
```bash
docker-compose -f docker-compose.yml up -d
```

### Using Render.com (Backend)
1. Create new Web Service
2. Connect GitHub repo
3. Root Directory: `backend`
4. Build: `pip install -r requirements.txt`
5. Start: `uvicorn main:app --host 0.0.0.0 --port 8000`
6. Add `GEMINI_API_KEY` environment variable

### Using Vercel (Frontend)
1. Create new project
2. Import GitHub repo
3. Root Directory: `frontend`
4. Add `REACT_APP_API_URL` environment variable pointing to your backend

## 🔑 Getting API Keys

### Gemini API (Free)
1. Go to https://aistudio.google.com
2. Click "Get API Key"
3. Create new API key
4. Set as `GEMINI_API_KEY` environment variable

## 🤝 Support

For issues or suggestions:
1. Check the health endpoint: `GET /health`
2. Verify GEMINI_API_KEY is set
3. Check browser console for errors
4. Ensure backend and frontend are connected

## 📝 Example Usage

### Get AI Explanation
```bash
curl -X POST http://localhost:8000/api/learn \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Mathematics",
    "chapter": "Linear Equations in Two Variables",
    "language": "en"
  }'
```

### Submit Quiz
```bash
curl -X POST http://localhost:8000/api/submit-quiz \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "SSC001",
    "subject": "Mathematics",
    "quiz_id": "math_quiz_1",
    "answers": {"m1_q1": 0, "m1_q2": 1},
    "time_taken": 600
  }'
```

## 📄 License

Built for Maharashtra Board SSC Students

---

**Happy Learning! 🎓**

* Select a subject
* Choose a chapter
* Get AI-powered explanation
* Test your knowledge
* Track your progress
* Always save automatically!

