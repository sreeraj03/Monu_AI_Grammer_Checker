
# AI Grammar Assistant (FastAPI + Flask + Ollama)

This project is a local AI-powered Grammar Checking System built using:

* **Ollama (gemma3:4b model)** – Local AI model
* **FastAPI** – Backend AI API server
* **Flask** – Web UI server
* **Requests** – API communication

The system allows users to input grammatically incorrect sentences and receive:

* Corrected sentence
* Explanation of errors
* Highlighted grammar mistakes (red = removed, green = added)

---

# 📁 Project Folder Structure

```
1. fastApiServer
   └── AI_grammar_assistant.py

1. webserver
   └── app.py
```

### Hierarchy Explanation

* `1.` represents the top-level folder.
* `fastApiServer` contains the AI backend server.
* `webserver` contains the UI frontend server.

---

# ⚙️ Prerequisites

Make sure you have installed:

* Python 3.9+
* Ollama
* pip

---

# 🚀 Step 1: Install Required Python Packages

Run this in your virtual environment or system Python:

```bash
pip install fastapi uvicorn flask requests pydantic
```

---

# 🤖 Step 2: Install & Run Ollama

### 1️⃣ Install Ollama

Download from:
[https://ollama.com/download](https://ollama.com/download)

After installation, verify:

```bash
ollama --version
```

---

### 2️⃣ Pull the Gemma Model

```bash
ollama pull gemma3:4b
```

This downloads the AI model locally.

---

### 3️⃣ Start Ollama Server

Run:

```bash
ollama run gemma3:4b
```

Or simply ensure Ollama is running in background.

By default, Ollama runs at:

```
http://localhost:11434
```

---

# 🚀 Step 3: Run FastAPI Server

Navigate to:

```
fastApiServer/
```

Run:

```bash
uvicorn AI_grammar_assistant:app --port 8080 --reload
```

FastAPI will start at:

```
http://localhost:8080
```

---

# 🚀 Step 4: Run Flask Web Server

Navigate to:

```
webserver/
```

Run:

```bash
python app.py
```

Flask UI will start at:

```
http://localhost:5000
```

---

# 🔄 Correct Order to Run the System

Always start services in this order:

1️⃣ Start Ollama
2️⃣ Start FastAPI Server (Port 8080)
3️⃣ Start Flask Web Server (Port 5000)

If Ollama is not running, FastAPI will fail.

If FastAPI is not running, Flask will fail to get responses.

---

# 🌐 Application Architecture

```
User (Browser)
      ↓
Flask Web Server (Port 5000)
      ↓
FastAPI Server (Port 8080)
      ↓
Ollama (Port 11434, gemma3:4b)
```

---

# 🔎 How The Request Flow Works

### Step 1: User Input

User enters a sentence in the browser UI.

Example:

```
hello name of me is adheel my appu is friend
```

---

### Step 2: Flask Handles Request

* Flask receives the form input.
* Sends a POST request to:

```
http://localhost:8080/check-grammar
```

With JSON body:

```json
{
  "text": "hello name of me is adheel my appu is friend"
}
```

---

### Step 3: FastAPI Processes Request

FastAPI:

1. Receives JSON request
2. Builds structured AI prompt
3. Sends request to Ollama API:

```
http://localhost:11434/api/generate
```

4. Ollama runs `gemma3:4b`
5. Returns AI-generated JSON response

---

### Step 4: Ollama AI Response

AI returns structured data:

```json
{
  "user_input": "...",
  "corrected_text": "...",
  "explanation": "..."
}
```

FastAPI then:

* Generates word-level difference
* Creates highlight format:

  * `[r%wrong%r]` → red (removed)
  * `[g%correct%g]` → green (added)

---

### Step 5: FastAPI Sends Structured Output

FastAPI returns:

```json
{
  "user_input": "...",
  "corrected_text": "...",
  "explanation": "...",
  "where_in_user_input_highlight": "..."
}
```

---

### Step 6: Flask Displays Result

Flask:

* Converts `[r% %r]` to red HTML span
* Converts `[g% %g]` to green HTML span
* Displays structured output cleanly

---

# 📡 FastAPI Routes

### POST `/check-grammar`

**URL**

```
http://localhost:8080/check-grammar
```

**Request Body**

```json
{
  "text": "Your sentence here"
}
```

**Response Body**

```json
{
  "user_input": "Original sentence",
  "corrected_text": "Corrected sentence",
  "explanation": "Brief grammar explanation",
  "where_in_user_input_highlight": "Highlighted diff"
}
```

---

# 🌐 Flask Web Route

### GET /

Shows the grammar UI form.

### POST /

* Takes user input
* Calls FastAPI
* Displays formatted output

Runs at:

```
http://localhost:5000
```

---

# 🎯 Highlighting System

| Marker       | Meaning                  |
| ------------ | ------------------------ |
| `[r%word%r]` | Incorrect word (removed) |
| `[g%word%g]` | Correct word (added)     |

Example:

```
He [r%go%r] [g%goes%g] to [g%the%g] office.
```

---

# 🛠 Troubleshooting

### ❌ FastAPI Error: Cannot connect to Ollama

Make sure:

```
ollama run gemma3:4b
```

is running.

---

### ❌ Flask Error: Connection refused

Make sure FastAPI is running on port 8080.

---

### ❌ JSON Parsing Error

Ensure model returns clean JSON and safe extraction is implemented.

---

# 🔮 Future Improvements

* Grammar score system
* Error categorization (Tense, Article, Preposition)
* History tracking
* Deployment to cloud (Render / Railway)
* React Frontend
* Authentication system

---

# 🧠 Summary

This system demonstrates:

* Microservice architecture
* AI model integration
* Backend API design
* Frontend server communication
* Structured AI output formatting
* Local LLM deployment using Ollama
