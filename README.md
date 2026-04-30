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
