"""
Maharashtra SSC AI Tutor - Main Entry Point

🎓 This is the enhanced version with:
- Voice features
- Detailed explanations
- Progress tracking
- Knowledge testing
- Session management
- Always-available architecture

📖 TO RUN:
   docker-compose up

🌐 OPEN:
   http://localhost:3000

📚 LEARN MORE:
   - README.md for complete guide
   - FEATURES.md for feature details
   - DEPLOYMENT.md for production setup

The actual backend API is in: ./backend/main.py
The frontend app is in: ./frontend/src/App.js
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse

app = FastAPI(title="Maharashtra SSC AI Tutor")

@app.get("/")
async def home():
    """Welcome page with setup instructions"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Maharashtra SSC AI Tutor - Welcome</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 0;
                padding: 20px;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 600px;
                text-align: center;
            }
            h1 {
                color: #667eea;
                margin: 0 0 20px 0;
            }
            p {
                color: #666;
                line-height: 1.6;
            }
            a {
                display: inline-block;
                margin-top: 20px;
                padding: 12px 30px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
            }
            a:hover {
                background: #764ba2;
            }
            .features {
                text-align: left;
                margin: 30px 0;
                padding: 20px;
                background: #f0f4ff;
                border-radius: 10px;
            }
            .features h3 {
                color: #667eea;
                margin-top: 0;
            }
            .features li {
                margin: 8px 0;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎓 महाराष्ट्र बोर्ड SSC AI Tutor</h1>
            <p>Welcome to your personal AI-powered learning platform!</p>
            
            <div class="features">
                <h3>✨ Features:</h3>
                <ul>
                    <li>📚 Complete Maharashtra Board curriculum</li>
                    <li>🤖 AI explanations in simple language</li>
                    <li>📊 Automatic progress tracking</li>
                    <li>✏️ Knowledge testing with board questions</li>
                    <li>🗣️ 3 language support (Marathi, Hindi, English)</li>
                    <li>🚀 Always available (never goes down)</li>
                </ul>
            </div>
            
            <p><strong>⏳ Starting the app...</strong></p>
            <p>If you see this page, it means the frontend is still loading.</p>
            <p style="margin-top: 30px; font-size: 14px; color: #999;">
                The app will be available at http://localhost:3000<br>
                Check back in a moment!
            </p>
            
            <a href="http://localhost:3000">Open Learning App →</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Main server is running",
        "note": "For the full app, visit http://localhost:3000"
    }

@app.get("/api/info")
async def info():
    """API information"""
    return {
        "app": "Maharashtra SSC AI Tutor",
        "version": "2.0 Enhanced",
        "features": [
            "AI-Powered Learning",
            "Progress Tracking",
            "Knowledge Testing",
            "Session Management",
            "High Availability"
        ],
        "backends": {
            "api": "http://localhost:8000",
            "frontend": "http://localhost:3000"
        }
    }

