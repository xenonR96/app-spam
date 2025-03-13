from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import re
import os

app = Flask(__name__, static_folder="static")
CORS(app)  # Enable CORS for frontend-backend communication


# Load spam words for different languages
def load_spam_words(language):
    try:
        if language == "fr":
            df = pd.read_csv("spam_words_fr.csv", delimiter=",")
        else:  # Default to English
            df = pd.read_csv("spam_words.csv", delimiter=",")

        spam_list = df["Keyword"].dropna().str.lower().tolist()
        spam_list.sort(key=len, reverse=True)  # Sort longest phrases first
        print(f"✅ Loaded {len(spam_list)} spam words for {language}!")
        return spam_list
    except Exception as e:
        print(f"❌ Error loading CSV for {language}: {e}")
        return []


# Dictionary to store both language lists
SPAM_WORDS = {
    "en": load_spam_words("en"),
    "fr": load_spam_words("fr"),
}

# Add a homepage route (Prevents 404 on "/")
@app.route("/")
def home():
    return send_from_directory("static", "index.html")


@app.route('/check_spam', methods=['POST'])
def check_spam():
    print("🔥 Received a request to /check_spam")

    data = request.json
    if not data:
        print("❌ No JSON data received!")
        return jsonify({"error": "No data received"}), 400

    email_text = data.get("text", "").lower().strip()
    language = data.get("language", "en")  # Default to English
    print(f"📝 Checking email text: {email_text} (Language: {language})")

    if language not in SPAM_WORDS:
        return jsonify({"error": "Unsupported language"}), 400

    found_spam_words = []
    checked_phrases = set()

    for phrase in SPAM_WORDS[language]:
        if phrase in email_text and phrase not in checked_phrases:
            found_spam_words.append(phrase)
            checked_phrases.update(phrase.split())

    total_words = len(email_text.split())
    spam_score = round((len(found_spam_words) / total_words) * 100, 2) if total_words > 0 else 0

    print(f"🚨 Found spam words: {found_spam_words} (Score: {spam_score}%)")

    return jsonify({
        "spam_words": found_spam_words,
        "spam_score": spam_score
    })


if __name__ == "__main__":
    # Use Render's port if available, otherwise default to 5000 for local development
    port = int(os.environ.get("PORT", 5001))
    print(f"🚀 Flask server running on port {port}...")
    app.run(host="0.0.0.0", port=port)