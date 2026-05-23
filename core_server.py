from fastapi import FastAPI
from pydantic import BaseModel
import requests
import psycopg2

app = FastAPI()
DB_URL = "postgresql://postgres:ShadowWorks1309206@db.ddvjjvjfpfehyaiuyyaj.supabase.co:5432/postgres"

class UserAuth(BaseModel):
    email: str
    password: str

class AiRequest(BaseModel):
    prompt: str
    language: str
    is_beginner: bool

@app.post("/auth")
def authenticate(user: UserAuth):
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (user.email, user.password))
        data = cursor.fetchone()
        conn.close()
        if data:
            return {"status": "success"}
        return {"status": "failed"}
    except:
        return {"status": "error"}

@app.post("/process")
def process_ai(req: AiRequest):
    if req.is_beginner:
        system_text = f"Write {req.language} code for this and explain every line clearly: "
    else:
        system_text = f"Find the bugs in this {req.language} code, highlight them, and fix them: "
        
    full_prompt = system_text + req.prompt
    
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "phi3",
            "prompt": full_prompt,
            "stream": False
        })
        return {"output": response.json()['response']}
    except:
        return {"output": "System Offline. Local AI Engine not responding!."}