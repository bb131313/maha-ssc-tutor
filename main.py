from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import google.generativeai as genai
import os

app = FastAPI()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

HTML='<!DOCTYPE html><html><head><title>MAHA SSC Tutor</title><style>*{box-sizing:border-box;margin:0;padding:0}body{font-family:Segoe UI;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;display:flex;justify-content:center;align-items:center}.c{background:white;padding:2rem;border-radius:20px;max-width:600px;width:90%;box-shadow:0 20px 60px rgba(0,0,0,.3)}.box{height:300px;overflow-y:auto;border:1px solid #ddd;border-radius:10px;padding:1rem;margin-bottom:1rem}.u{color:#667eea;margin-bottom:.5rem}.b{color:#333;margin-bottom:1rem;padding:.5rem;background:#f0f0f0;border-radius:8px}</style></head><body><div class="c"><h1>🤖 MAHA SSC Tutor</h1><div class="box" id="box"></div><input id="in" placeholder="Ask..."><button onclick="s()">Send</button></div><script>async function s(){const i=document.getElementById("in"),b=document.getElementById("box");if(!i.value.trim())return;b.innerHTML+="<div class=u>You: "+i.value+"</div>";b.innerHTML+="<div class=b>Bot:...</div>";const v=i.value;i.value="";const r=await fetch("/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({prompt:v})}).then(r=>r.json());b.innerHTML=b.innerHTML.replace("<div class=b>Bot:...</div>","<div class=b>Bot: "+r.response+"</div>");b.scrollTop=b.scrollHeight}</script></body></html>'

@app.get("/")
async def home(): return HTMLResponse(content=HTML)

@app.post("/chat")
async def chat(req: Request):
    data = await req.json()
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(data.get("prompt",""))
    return {"response": response.text}
