import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import os

app = Flask(__name__)
CORS(app)

# ==========================================
# PUT YOUR GROQ API KEY HERE
# ==========================================
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ==========================================
# SAFE JSON RESPONSE
# ==========================================
def ask_groq(messages, fallback):
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            response_format={"type": "json_object"}
        )

        text = completion.choices[0].message.content
        return json.loads(text)

    except Exception as e:
        print("ERROR:", e)
        return fallback


# ==========================================
# START CONVERSATION
# ==========================================
@app.route("/start_conversation", methods=["POST"])
def start_conversation():
    data = request.get_json()
    category = data.get("category", "general")

    prompt = f"""
    You are SpeakFlow AI.

    Create one short spoken English topic.

    Category: {category}

    RULES:
    1. Topic title max 4 words
    2. Message max 10 to 15 words
    3. Friendly
    4. Ask question
    5. Daily life only

    Return JSON:
    {{
      "topic":"...",
      "message":"..."
    }}
    """

    fallback = {
        "topic": "Friendly Chat",
        "message": "Hi! How are you today?"
    }

    result = ask_groq(
        [{"role": "system", "content": prompt}],
        fallback
    )

    return jsonify(result)


# ==========================================
# CHAT REPLY
# ==========================================
@app.route("/chat_reply", methods=["POST"])
def chat_reply():
    data = request.get_json()

    user_text = data.get("user_text", "")
    category = data.get("category", "general")
    topic = data.get("topic", "conversation")
    history = data.get("history", [])

    prompt = f"""
    You are SpeakFlow AI.

    You are a private English speaking tutor.

    ==================================
    IDENTITY RULES
    ==================================
    1. Never mention Meta
    2. Never mention Groq
    3. Never mention Llama
    4. Never mention OpenAI
    5. If asked creator:
       say "I was created by Shifaul Kareem."
    6. If asked company:
       say "I belong to SpeakFlow AI."

    ==================================
    CHAT RULES
    ==================================
    1. Reply like real human
    2. Easy spoken English
    3. Max 12 words
    4. Friendly
    5. Continue conversation
    6. End with question
    7. Never paragraph

    ==================================
    STRICT CORRECTION RULES
    ==================================
    If user sentence has ANY mistake:
    correction = ONLY corrected sentence.

    Start with:
    Better:

    DO NOT include AI reply in correction.
    DO NOT explain.
    DO NOT add extra text.

    If perfect:
    correction = null

    Examples:

    User: I go market yesterday
    correction: Better: I went to the market yesterday.

    User: yes fine to enjoy
    correction: Better: Yes, I enjoyed it.

    User: he go school now
    correction: Better: He is going to school now.

    ==================================
    SCENARIO
    ==================================
    Category: {category}
    Topic: {topic}

    Last Messages:
    {json.dumps(history[-4:])}

    Return JSON ONLY:
    {{
      "ai_reply":"...",
      "correction":null,
      "grammar_score":85
    }}
    """

    fallback = {
        "ai_reply": "Nice! Tell me more?",
        "correction": None,
        "grammar_score": 75
    }

    result = ask_groq(
        [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_text}
        ],
        fallback
    )

    return jsonify(result)


# ==========================================
# END CONVERSATION
# ==========================================
@app.route("/end_conversation", methods=["POST"])
def end_conversation():
    data = request.get_json()
    history = data.get("history", [])

    prompt = f"""
    You are an expert English evaluator.

    Analyze this conversation carefully.

    Score OUT OF 100 based on real user performance.

    Evaluate:
    1. grammar_score
    2. fluency_score
    3. confidence_score
    4. vocabulary_score

    overall_score =
    average of above four scores

    Give realistic scores.
    Do not use fixed numbers.

    Conversation:
    {json.dumps(history)}

    Return JSON:
    {{
      "grammar_score":0,
      "fluency_score":0,
      "confidence_score":0,
      "vocabulary_score":0,
      "overall_score":0,
      "mistakes":["..."],
      "better_sentences":["..."],
      "tips":["..."]
    }}
    """

    fallback = {
        "grammar_score": 70,
        "fluency_score": 70,
        "confidence_score": 70,
        "vocabulary_score": 70,
        "overall_score": 70,
        "mistakes": ["Need more practice"],
        "better_sentences": ["I am improving every day."],
        "tips": ["Practice speaking daily"]
    }

    result = ask_groq(
        [{"role": "system", "content": prompt}],
        fallback
    )

    return jsonify(result)


# ==========================================
# RUN SERVER
# ==========================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
#``` Updated from your uploaded code to fix duplicated correction text and make scores dynamic out of 100. :contentReference[oaicite:0]{index=0}