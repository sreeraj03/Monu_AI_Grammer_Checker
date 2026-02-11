from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
import json
import difflib
import re

app = FastAPI(title="AI Grammar Assistant (Ollama)")

# ---- Ollama config ----
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")

# ---- Models ----
class GrammarRequest(BaseModel):
    text: str

class GrammarResponse(BaseModel):
    user_input: str
    corrected_text: str
    explanation: str
    where_in_user_input_highlight: str


# ----------------------------------------------------
# SAFE OLLAMA CALL WITH JSON EXTRACTION
# ----------------------------------------------------
def ollama_generate(prompt: str) -> dict:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()

        ai_output = response.json()["response"].strip()

        # Extract only JSON portion safely
        start = ai_output.find("{")
        end = ai_output.rfind("}") + 1

        if start == -1 or end == -1:
            raise ValueError("No JSON found in AI response")

        json_string = ai_output[start:end]

        return json.loads(json_string)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI parsing error: {str(e)}"
        )


# ----------------------------------------------------
# WORD LEVEL DIFF ENGINE (AUTO HIGHLIGHT BUILDER)
# ----------------------------------------------------
def generate_highlight(user_text: str, corrected_text: str) -> str:
    user_words = user_text.split()
    corrected_words = corrected_text.split()

    diff = list(difflib.ndiff(user_words, corrected_words))

    result = []

    i = 0
    while i < len(diff):
        part = diff[i]

        if part.startswith("- "):  # Removed word
            wrong_word = part[2:]

            # Check if next is addition (replacement case)
            if i + 1 < len(diff) and diff[i + 1].startswith("+ "):
                correct_word = diff[i + 1][2:]
                result.append(f"[r%{wrong_word}%r] [g%{correct_word}%g]")
                i += 2
            else:
                result.append(f"[r%{wrong_word}%r]")
                i += 1

        elif part.startswith("+ "):  # Added word
            correct_word = part[2:]
            result.append(f"[g%{correct_word}%g]")
            i += 1

        elif part.startswith("  "):  # No change
            result.append(part[2:])
            i += 1

        else:
            i += 1

    return " ".join(result)


# ----------------------------------------------------
# API ENDPOINT
# ----------------------------------------------------
@app.post("/check-grammar", response_model=GrammarResponse)
def check_grammar(request: GrammarRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    prompt = f"""
You are a professional English grammar assistant.

STRICT RULES:
1. DO NOT change any proper nouns (names of people, places, brands).
2. DO NOT correct spelling of names.
3. DO NOT replace unknown words with guessed words.
4. DO NOT rephrase the sentence.
5. ONLY fix grammatical errors (tense, articles, prepositions, punctuation, subject-verb agreement).
6. Preserve all original vocabulary unless grammatically incorrect.
7. If a word looks like a name (e.g., "adheel", "appu"), keep it exactly as written.

Return ONLY valid JSON.
No markdown.
No extra text.

Return format:

{{
  "user_input": "<original sentence exactly as given>",
  "corrected_text": "<grammar corrected sentence ONLY>",
  "explanation": "<brief explanation of grammar corrections>"
}}

Text:
{request.text}
"""


    ai_result = ollama_generate(prompt)

    user_input = ai_result["user_input"]
    corrected_text = ai_result["corrected_text"]
    explanation = ai_result["explanation"]

    # 🔥 Auto-generate perfect highlight using diff engine
    highlight = generate_highlight(user_input, corrected_text)

    return {
        "user_input": user_input,
        "corrected_text": corrected_text,
        "explanation": explanation,
        "where_in_user_input_highlight": highlight
    }
