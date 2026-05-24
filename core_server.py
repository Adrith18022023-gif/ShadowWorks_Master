import os
import sqlite3
import bcrypt
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Your Google Gemini API Key
GEMINI_API_KEY = "YOUR_API_KEY_HERE"

# ----------------- LOCAL DATABASE SETUP -----------------
def init_db():
    # Added timeout=10 and 'with' blocks to prevent database locks!
    with sqlite3.connect("local_database.db", timeout=10) as conn:
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_email TEXT NOT NULL,
                        prompt TEXT NOT NULL,
                        output TEXT NOT NULL)''')
        conn.commit()

init_db()
# --------------------------------------------------------

class AuthRequest(BaseModel):
    email: str
    password: str

class ProcessRequest(BaseModel):
    email: str
    prompt: str
    language: str
    mode: str

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_pwd: str, hashed_pwd: str) -> bool:
    return bcrypt.checkpw(plain_pwd.encode('utf-8'), hashed_pwd.encode('utf-8'))

@app.post("/signup")
def register_user(user: AuthRequest):
    try:
        with sqlite3.connect("local_database.db", timeout=10) as conn:
            cur = conn.cursor()
            hashed = hash_password(user.password)
            cur.execute("INSERT INTO users (email, password) VALUES (?, ?)", (user.email, hashed))
            conn.commit()
        return {"status": "success"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/login")
def login_user(user: AuthRequest):
    try:
        with sqlite3.connect("local_database.db", timeout=10) as conn:
            cur = conn.cursor()
            cur.execute("SELECT password FROM users WHERE email = ?", (user.email,))
            record = cur.fetchone()
        
        if record and verify_password(user.password, record[0]):
            return {"status": "verified"}
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error")

@app.post("/run_ai")
def process_ai_request(req: ProcessRequest):
    mode = req.mode
    lang = req.language
    user_prompt = req.prompt
    
    image_url = ""
    output_text = ""
    
    # 1. Prepare the AI instructions based on mode
    if mode == "Beginner Mode":
        system_instruction = f"You are an expert coding tutor. Write the complete, accurate {lang} code for the following request. Do not include markdown formatting, just the raw code: \n\n"
    elif mode == "Pro Debugger":
        system_instruction = f"You are a strict code debugger for {lang}. Analyze the following code. First, list every error found. Second, provide the complete fixed code. Format the output clearly: \n\n"
    elif mode == "Cinematic Mode":
        system_instruction = "Write a creative 4-line poetic shayari blending programming concepts and the following topic: \n\n"
        clean_prompt = user_prompt.replace(" ", "%20").replace("\n", "")
        image_url = f"https://image.pollinations.ai/prompt/cinematic%20{clean_prompt}%20programming%20digital%20art?width=800&height=400&nologo=true"
    else:
        system_instruction = "You are the inbuilt app assistant for Codemate. Help the user solve this problem regarding the application or general knowledge: \n\n"

    try:
        # 2. DIRECT REST API CALL TO GOOGLE
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": system_instruction + user_prompt}]}]
        }
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        
        # Check if Google gave us a good response
        if response.status_code == 200:
            output_text = response_data['candidates'][0]['content']['parts'][0]['text']
        else:
            error_msg = response_data.get('error', {}).get('message', 'Unknown Error')
            output_text = f"Google API Error: {error_msg}"

        # 3. Save to local database (Auto-unlocks)
        with sqlite3.connect("local_database.db", timeout=10) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO history (user_email, prompt, output) VALUES (?, ?, ?)", 
                        (req.email, user_prompt, output_text))
            conn.commit()

    except Exception as e:
        output_text = f"System Error: {str(e)}"

    return {"reply": output_text, "image": image_url}