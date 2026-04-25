from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
import json
from dotenv import load_dotenv
import os
load_dotenv(dotenv_path="apikey.env")

app = FastAPI()

# CORS (so frontend can connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Groq client
print("API KEY:", os.getenv("GROQ_API_KEY"))
import os
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# System prompt (STRICT STRUCTURE)
SYSTEM_PROMPT = """
You are an AI Decision Simulator.

Your job is to help users make decisions by analyzing options, risks, benefits, and outcomes.

IMPORTANT RULES:
- Respond ONLY in valid JSON
- No markdown
- No explanations
- No extra text

Use this structure:

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

@app.get("/")
def home():
    return {"message": "AI Decision Simulator API is running"}
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/generate")
def generate(data: dict):
    user_input = data.get("input")

    if not user_input:
        return {"error": "No input provided"}

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ]
        )

        raw_output = response.choices[0].message.content

        # Clean possible markdown artifacts
        raw_output = raw_output.replace("```json", "").replace("```", "").strip()

        # Convert to JSON
        try:
            json_output = json.loads(raw_output)
            return json_output
        except json.JSONDecodeError:
            return {
                "error": "Invalid AI response format",
        "raw": raw_output
            }
        return parsed_output
    except Exception as e:
        return {
            "error": "Something went wrong",
            "details": str(e)
        }
   