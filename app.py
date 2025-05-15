from flask import Flask, request, jsonify, render_template
import os
import json
from dotenv import load_dotenv
import requests
import cohere

app = Flask(__name__)
load_dotenv()

cohere_api_key = os.getenv("COHERE_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
co = cohere.Client(cohere_api_key)

chat_history = []
CHAT_HISTORY_FILE = "chat_history.json"

# Load previous chat history
if os.path.exists(CHAT_HISTORY_FILE):
    with open(CHAT_HISTORY_FILE, "r") as f:
        try:
            chat_history = json.load(f)
        except:
            chat_history = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/clear", methods=["POST"])
def clear_history():
    global chat_history
    chat_history = []
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(chat_history, f)
    return jsonify({"status": "cleared"})

def google_search(query):
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "engine": "google"
    }

    try:
        response = requests.get(url, params=params)
        results = response.json()

        answer_box = results.get("answer_box", {}).get("answer")
        if answer_box:
            return answer_box

        organic = results.get("organic_results", [])
        if organic:
            first = organic[0]
            title = first.get("title", "No title")
            snippet = first.get("snippet", "No snippet available.")
            link = first.get("link", "#")
            return f"🔎 {title}\n{snippet}\n🌐 {link}"

        return "No useful results found on Google."
    except Exception as e:
        print("Google Search error:", e)
        return "Error fetching search results."

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    chat_history.append({"role": "USER", "message": user_input})

    if any(keyword in user_input.lower() for keyword in ["google", "search", "look up"]):
        reply = google_search(user_input)
    else:
        try:
            response = co.chat(
                model="command-r-plus",
                message=user_input,
                chat_history=chat_history,
                temperature=0.7
            )
            reply = response.text.strip()
            chat_history.append({"role": "CHATBOT", "message": reply})
        except Exception as e:
            print("Cohere API error:", e)
            reply = "Sorry, something went wrong with the AI service."

    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(chat_history, f)

    return jsonify({"response": reply})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
