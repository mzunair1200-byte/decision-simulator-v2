from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Groq client (SAFE FOR DEPLOYMENT)
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise Exception("GROQ_API_KEY not found")

client = Groq(api_key=api_key)

# AI System Prompt
SYSTEM_PROMPT = """
You are an AI Decision Simulator.

Return ONLY valid JSON.

Format:
{
  "decision": "",
  "options": [
    {
      "option": "",
      "risk_level": "",
      "success_probability": "",
      "pros": [],
      "cons": [],
      "outcome": ""
    }
  ],
  "final_suggestion": "",
  "confidence": ""
}
"""

# Root route
@app.get("/")
def home():
    return {"message": "AI Decision Simulator API running"}

# Health check (important for deployment)
@app.get("/health")
def health():
    return {"status": "ok"}

# Main AI endpoint
@app.post("/generate")
def generate(data: dict):
    try:
        user_input = data.get("input")

        if not user_input:
            return {"error": "No input provided"}

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ]
        )

        raw_output = response.choices[0].message.content

        # Clean markdown if any
        raw_output = raw_output.replace("```json", "").replace("```", "").strip()

        # Convert to JSON safely
        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            return {
                "error": "Model returned invalid JSON",
                "raw": raw_output
            }

    except Exception as e:
        return {
            "error": "Server error",
            "details": str(e)
        }
   
