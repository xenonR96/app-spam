from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Load spam words (including phrases)
def load_spam_words():
    try:
        df = pd.read_csv("spam_words.csv", delimiter=",")  # Ensure correct delimiter
        spam_list = df["Keyword"].dropna().str.lower().tolist()
        spam_list.sort(key=len, reverse=True)  # Sort by length (longer phrases first)
        print(f"✅ Loaded {len(spam_list)} spam words!")
        return spam_list  # Keep as a sorted list
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return []

SPAM_WORDS = load_spam_words()

@app.route('/check_spam', methods=['POST'])
def check_spam():
    print("🔥 Received a request to /check_spam")

    data = request.json
    if not data:
        print("❌ No JSON data received!")
        return jsonify({"error": "No data received"}), 400

    email_text = data.get("text", "").lower().strip()
    print(f"📝 Checking email text: {email_text}")

    found_spam_words = []
    checked_phrases = set()

    for phrase in SPAM_WORDS:
        if phrase in email_text and phrase not in checked_phrases:
            found_spam_words.append(phrase)
            checked_phrases.update(phrase.split())  # Mark individual words to prevent duplicates

    # Compute spam score as a percentage
    total_words = len(email_text.split())  # Count total words in email
    spam_score = round((len(found_spam_words) / total_words) * 100, 2) if total_words > 0 else 0

    print(f"🚨 Found spam words: {found_spam_words} (Score: {spam_score}%)")

    return jsonify({
        "spam_words": found_spam_words,
        "spam_score": spam_score
    })

if __name__ == "__main__":
    print("🚀 Flask server is running on http://127.0.0.1:5000/")
    app.run(debug=True)