from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

FASTAPI_URL = "http://localhost:8080/check-grammar"

# -------------------------------------------------
# BASIC HTML TEMPLATE
# -------------------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Monu AI</title>
    <style>
        body {
            font-family: Arial;
            max-width: 800px;
            margin: 40px auto;
        }
        textarea {
            width: 100%;
            height: 120px;
            padding: 10px;
        }
        button {
            padding: 10px 20px;
            margin-top: 10px;
        }
        .result {
            margin-top: 30px;
            padding: 15px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        .red {
            color: red;
            font-weight: bold;
        }
        .green {
            color: green;
            font-weight: bold;
        }
    </style>
</head>
<body>

<h2>Monu AI Grammar Checker</h2>

<form method="POST">
    <textarea name="text" placeholder="Enter your sentence...">{{ user_input or "" }}</textarea>
    <br>
    <button type="submit">Check Grammar</button>
</form>

{% if result %}
<div class="result">
    <h3>Corrected Sentence:</h3>
    <p>{{ result.corrected_text }}</p>

    <h3>Explanation:</h3>
    <p>{{ result.explanation }}</p>

    <h3>Highlighted Errors:</h3>
    <p>{{ highlighted|safe }}</p>
</div>
{% endif %}

</body>
</html>
"""

# -------------------------------------------------
# Convert [r% %r] and [g% %g] to colored HTML
# -------------------------------------------------
def format_highlight(text):
    text = text.replace("[r%", "<span class='red'>")
    text = text.replace("%r]", "</span>")
    text = text.replace("[g%", "<span class='green'>")
    text = text.replace("%g]", "</span>")
    return text


# -------------------------------------------------
# ROUTE
# -------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    highlighted = None
    user_input = None

    if request.method == "POST":
        user_input = request.form.get("text")

        if user_input:
            try:
                response = requests.post(
                    FASTAPI_URL,
                    json={"text": user_input},
                    timeout=120
                )

                if response.status_code == 200:
                    result = response.json()
                    highlighted = format_highlight(
                        result["where_in_user_input_highlight"]
                    )
                else:
                    result = {
                        "corrected_text": "Error from FastAPI",
                        "explanation": response.text
                    }

            except Exception as e:
                result = {
                    "corrected_text": "Connection Error",
                    "explanation": str(e)
                }

    return render_template_string(
        HTML_TEMPLATE,
        result=result,
        highlighted=highlighted,
        user_input=user_input
    )


if __name__ == "__main__":
    app.run(port=5000, debug=True)
