import glob
import os
import random
import yaml
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder="static")

# Load all language variants at startup
BASE_DIR = os.path.dirname(__file__)
LANGS = {}  # lang_code -> {"questions": [...], "metadata": {...}}

for path in sorted(glob.glob(os.path.join(BASE_DIR, "nj_drivers_test_questions*.yaml"))):
    fname = os.path.basename(path)
    with open(path) as f:
        data = yaml.safe_load(f)
    # Determine language from filename: _ja.yaml -> "ja", base -> "en"
    if "_ja.yaml" in fname:
        lang = "ja"
    elif "_es.yaml" in fname:
        lang = "es"
    else:
        lang = "en"
    LANGS[lang] = {
        "questions": data["questions"],
        "metadata": data["metadata"],
        "by_id": {q["id"]: q for q in data["questions"]},
    }

CATEGORIES = sorted(set(q["category"] for q in LANGS["en"]["questions"]))


def get_lang():
    return request.args.get("lang", "en") if request.args.get("lang") in LANGS else "en"


def get_questions():
    return LANGS[get_lang()]["questions"]


def get_by_id():
    return LANGS[get_lang()]["by_id"]


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/metadata")
def metadata():
    lang = get_lang()
    data = LANGS[lang]
    return jsonify({
        "total_questions": len(data["questions"]),
        "categories": CATEGORIES,
        "passing_score": data["metadata"]["passing_score"],
        "languages": sorted(LANGS.keys()),
        "language": lang,
    })


@app.route("/api/quiz")
@app.route("/api/quiz/<int:count>")
def quiz(count=50):
    questions = get_questions()
    count = min(count, len(questions))
    selected = random.sample(questions, count)
    quiz_questions = []
    for q in selected:
        quiz_questions.append({
            "id": q["id"],
            "category": q["category"],
            "question": q["question"],
            "choices": q["choices"],
        })
    return jsonify({"questions": quiz_questions, "total": count})


@app.route("/api/answer/<int:question_id>")
def answer(question_id):
    by_id = get_by_id()
    q = by_id.get(question_id)
    if not q:
        return jsonify({"error": "Question not found"}), 404
    return jsonify({
        "id": q["id"],
        "answer": q["answer"],
        "explanation": q["explanation"],
    })


@app.route("/api/answers", methods=["POST"])
def answers():
    by_id = get_by_id()
    ids = request.get_json(force=True).get("ids", [])
    result = {}
    for qid in ids:
        q = by_id.get(qid)
        if q:
            result[str(qid)] = {
                "answer": q["answer"],
                "explanation": q["explanation"],
            }
    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
