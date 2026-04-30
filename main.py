from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import google.generativeai as genai
import os

app = FastAPI()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

HTML = """
<!DOCTYPE html>
<html><head><title>MAHA SSC Tutor</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Segoe UI,sans-serif;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;display:flex;justify-content:center;align-items:center}
.c{background:white;padding:2rem;border-radius:20px;box-shadow:0 20px 60px rgba(0,0,0,.3);max-width:600px;width:90%}
h1{color:#333;margin-bottom:1.5rem;text-align:center}
.box{height:300px;overflow-y:auto;border:1px solid #ddd;border-radius:10px;padding:1rem;margin-bottom:1rem}
.u{color:#667eea;margin-bottom:.5rem}
.b{color:#333;margin-bottom:1rem;padding:.5rem;background:#f0f0f0;border-radius:8px}
.g{display:flex;gap:.5rem}
input{flex:1;padding:12px;border:1px solid #ddd;border-radius:8px;font-size:16px}
button{padding:12px 24px;background:#667eea;color:white;border:none;border-radius:8px;cursor:pointer;font-size:16px}
button:hover{background:#5a6fd6}
</style></head>
<body>
<div class="c">
<h1>🤖 MAHA SSC Tutor</h1>
<div class="box" id="box"></div>
<div class="g">
<input id="in" placeholder="Ask a question..." onkeypress="e.key==='Enter'&&s()">
<button onclick="s()">Send</button>
</div>
</div>
<script>
async function s(){
const i=document.getElementById("in"),b=document.getElementById("box"),m=i.value.trim();
if(!m)return;
b.innerHTML+=`<div class="u">👤 You: ${m}</div>`;
b.innerHTML+=`<div class="b">🤖 Thinking...</div>`;
i.value="";
try{
const r=await fetch("/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({prompt:m})});
const d=await r.json();
b.innerHTML=b.innerHTML.replace(/🤖 Thinking...<\/div>/,`<div class="b">🤖 Bot: ${d.response}</div>`);
}catch(e){b.innerHTML+=`<div class="b">❌ Error</div>`}
b.scrollTop=b.scrollHeight
}
</script>
</body></html>
"""

@app.get("/")
async def home(): return HTMLResponse(content=HTML)

@app.post("/chat")
async def chat(req: Request):
    d=await req.json()
    m=genai.GenerativeModel("gemini-1.5-flash")
    r=m.generate_content(d.get("prompt",""))
    return {"response":r.text}
