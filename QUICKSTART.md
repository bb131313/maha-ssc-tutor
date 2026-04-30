# 🚀 Quick Start Guide

## 30-Second Setup

```bash
# 1. Clone or open the project
cd maha-ssc-tutor

# 2. Run setup script
bash setup.sh

# 3. Open browser
http://localhost:3000
```

Done! ✅

---

## Step-by-Step Setup

### Step 1: Get Gemini API Key (FREE)
- Go to https://aistudio.google.com
- Click "Get API Key"
- Click "Create new API key"
- Copy the key (you'll need this in Step 3)

### Step 2: Check Requirements
- ✅ Docker installed? → https://docker.com/products/docker-desktop
- ✅ At least 4GB RAM available?
- ✅ Internet connection?

### Step 3: Run Setup Script

**On Linux/Mac:**
```bash
bash setup.sh
```

**On Windows (Git Bash or WSL):**
```bash
bash setup.sh
```

**Or Manually:**
```bash
# Set environment variable
export GEMINI_API_KEY="your-key-here"

# Start services
docker-compose up -d

# Wait 1-2 minutes, then open:
# http://localhost:3000
```

### Step 4: First Login
- **Roll Number:** SSC001 (or any student ID)
- **Name:** Your name
- **Email:** Your email
- Click **"Start Learning"**

### Step 5: Start Learning!
1. Select a **Subject** (left side)
2. Click a **Chapter**
3. Read **AI Explanation**
4. Change **Language** if you want
5. **Mark Complete** when done
6. Track your **Progress**
7. Take **Quizzes** to test knowledge

---

## Commands Reference

### Start App
```bash
docker-compose up -d
```

### Stop App
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Check Health
```bash
curl http://localhost:8000/health
curl http://localhost:3000
```

### Restart Services
```bash
docker-compose restart
```

### Clean Everything
```bash
docker-compose down
docker-compose up -d
```

---

## Troubleshooting

### "API Key is wrong"
- Check key at https://aistudio.google.com
- Make sure to copy the full key
- Check for extra spaces

### "Port 3000 already in use"
```bash
# Kill process using port 3000
lsof -i :3000  # Find process
kill -9 <PID>   # Kill it

# Or use different port
docker-compose down
PORT=3001 docker-compose up -d
```

### "Can't connect to Docker"
- Install Docker: https://docker.com/products/docker-desktop
- On Windows, enable WSL 2
- Restart Docker desktop

### "Services won't start"
```bash
docker-compose logs backend
docker-compose logs frontend
```

Check for obvious errors (API key, network, disk space)

### "Blank page in browser"
- Wait 1-2 minutes for first build
- Check: http://localhost:3000
- Refresh browser (Ctrl+R)
- Check logs: `docker-compose logs -f`

---

## Default Credentials

**NO LOGIN REQUIRED!**

Just enter any:
- Student ID (e.g., SSC001)
- Your Name
- Your Email

Each student gets their own progress tracking automatically.

---

## Features Overview

### 📚 Learning
- Select any subject
- Choose any chapter
- Get AI explanation
- Change language (3 options)
- Access textbook links

### 📊 Progress
- Chapters completed (tracking)
- Quiz scores (by subject)
- Learning history
- Time spent tracking

### ✏️ Testing
- Take quizzes per chapter
- Questions from board exams
- Instant grading
- Detailed feedback

### 🎯 Session Management
- 2-hour session timeout
- Auto-save everything
- Session warning before logout
- Manual logout option

---

## File Structure

```
maha-ssc-tutor/
├── backend/              # FastAPI backend
│   ├── main.py          # Backend API
│   ├── requirements.txt  # Python packages
│   └── Dockerfile       # Backend container
├── frontend/            # React frontend
│   ├── src/App.js       # Main app
│   ├── package.json     # Dependencies
│   └── Dockerfile       # Frontend container
├── docker-compose.yml   # Container orchestration
├── README.md            # Full documentation
├── FEATURES.md          # Feature details
├── DEPLOYMENT.md        # Production guide
└── setup.sh             # Automated setup
```

---

## Ports Used

- **3000** - Frontend (React app)
- **8000** - Backend API
- **5432** - Database (PostgreSQL, if using advanced setup)

If ports are in use, docker-compose will fail. Check and free ports or use different ports.

---

## Browser Support

✅ Works on:
- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge
- Mobile browsers

Best experience on desktop (1920x1080 or higher)

---

## Internet Requirements

- **Download:** 50MB (one-time setup)
- **Usage:** ~1MB per lesson viewed
- **Quiz:** ~100KB per submission
- **Minimum Speed:** 1Mbps recommended

---

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 4 cores |
| RAM | 2GB | 8GB |
| Disk | 5GB free | 20GB free |
| Network | 1Mbps | 10Mbps |

---

## Getting Help

### Check These:
1. **Logs:** `docker-compose logs`
2. **Health:** `curl http://localhost:8000/health`
3. **Internet:** Ping google.com
4. **Disk:** `docker system df`

### Common Issues:
- Port in use → Use different port
- API key error → Check trailing spaces
- Services won't start → Check disk space
- App won't load → Wait 2 minutes, refresh

### Report Issues:
Check logs first:
```bash
docker-compose logs backend > backend.log
docker-compose logs frontend > frontend.log
```

---

## Next Steps

1. ✅ Run setup script
2. ✅ Open http://localhost:3000
3. ✅ Register with any student ID
4. ✅ Select a subject and chapter
5. ✅ Read explanation and mark complete
6. ✅ Take a quiz
7. ✅ Check your progress

**That's it! You're all set! 🎓**

---

**Happy Learning! Made with ❤️ for Maharashtra Board Students**
