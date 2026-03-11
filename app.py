import json
import os
import random
import re
import yaml
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder="static")

BASE_DIR = os.path.dirname(__file__)
STATES_DIR = os.path.join(BASE_DIR, "states")

# Auto-discover states and their question files at startup
# Structure: STATES[state_code][lang_code] = {"questions": [...], "by_id": {...}}
# CONFIG[state_code] = {...config.json...}
STATES = {}
CONFIG = {}

for state_code in sorted(os.listdir(STATES_DIR)):
    state_dir = os.path.join(STATES_DIR, state_code)
    if not os.path.isdir(state_dir):
        continue

    config_path = os.path.join(state_dir, "config.json")
    if not os.path.exists(config_path):
        continue

    with open(config_path) as f:
        CONFIG[state_code] = json.load(f)

    STATES[state_code] = {}

    for fname in sorted(os.listdir(state_dir)):
        match = re.match(r"questions_(\w+)\.yaml$", fname)
        if not match:
            continue
        lang = match.group(1)
        with open(os.path.join(state_dir, fname)) as f:
            data = yaml.safe_load(f)
        STATES[state_code][lang] = {
            "questions": data["questions"],
            "by_id": {q["id"]: q for q in data["questions"]},
        }


def get_state():
    state = request.args.get("state", "").lower()
    return state if state in STATES else None


def get_lang(state):
    lang = request.args.get("lang", "en")
    return lang if lang in STATES.get(state, {}) else "en"


def get_state_lang():
    state = get_state()
    if not state:
        return None, None, None
    lang = get_lang(state)
    return state, lang, STATES[state].get(lang) or STATES[state].get("en")


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/signs/<state>/<path:filename>")
def serve_sign(state, filename):
    state = state.lower()
    if state not in CONFIG:
        return jsonify({"error": "Invalid state"}), 404
    signs_dir = os.path.join(STATES_DIR, state, "signs")
    if not os.path.isdir(signs_dir):
        signs_dir = os.path.join(BASE_DIR, "signs")
    return send_from_directory(signs_dir, filename)


@app.route("/api/states")
def states():
    result = []
    for code in sorted(CONFIG.keys()):
        cfg = CONFIG[code]
        langs = sorted(STATES.get(code, {}).keys())
        total = len(STATES.get(code, {}).get("en", {}).get("questions", []))
        has_questions = total > 0
        result.append({
            "code": code,
            "name": cfg["name"],
            "agency": cfg["agency"],
            "passing_score_pct": cfg["passing_score_pct"],
            "test_question_count": cfg["test_question_count"],
            "languages": langs,
            "total_questions": total,
            "has_questions": has_questions,
        })
    return jsonify({"states": result})


@app.route("/api/metadata")
def metadata():
    state, lang, data = get_state_lang()
    if not state:
        return jsonify({"error": "Missing or invalid state parameter"}), 400
    cfg = CONFIG[state]
    categories = sorted(set(q["category"] for q in data["questions"])) if data else []
    return jsonify({
        "state": state,
        "state_name": cfg["name"],
        "agency": cfg["agency"],
        "total_questions": len(data["questions"]) if data else 0,
        "categories": categories,
        "passing_score_pct": cfg["passing_score_pct"],
        "test_question_count": cfg["test_question_count"],
        "languages": sorted(STATES.get(state, {}).keys()),
        "language": lang,
    })


@app.route("/api/quiz")
@app.route("/api/quiz/<int:count>")
def quiz(count=50):
    state, lang, data = get_state_lang()
    if not state or not data:
        return jsonify({"error": "Missing or invalid state parameter"}), 400
    questions = data["questions"]
    count = min(count, len(questions))
    selected = random.sample(questions, count)
    quiz_questions = []
    for q in selected:
        item = {"id": q["id"], "category": q["category"], "question": q["question"], "choices": q["choices"]}
        if q.get("image"):
            item["image"] = q["image"]
        quiz_questions.append(item)
    return jsonify({"questions": quiz_questions, "total": count})


@app.route("/api/answer/<int:question_id>")
def answer(question_id):
    state, lang, data = get_state_lang()
    if not state or not data:
        return jsonify({"error": "Missing or invalid state parameter"}), 400
    q = data["by_id"].get(question_id)
    if not q:
        return jsonify({"error": "Question not found"}), 404
    return jsonify({"id": q["id"], "answer": q["answer"], "explanation": q["explanation"]})


@app.route("/api/answers", methods=["POST"])
def answers():
    state, lang, data = get_state_lang()
    if not state or not data:
        return jsonify({"error": "Missing or invalid state parameter"}), 400
    by_id = data["by_id"]
    ids = request.get_json(force=True).get("ids", [])
    result = {}
    for qid in ids:
        q = by_id.get(qid)
        if q:
            result[str(qid)] = {"answer": q["answer"], "explanation": q["explanation"]}
    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
