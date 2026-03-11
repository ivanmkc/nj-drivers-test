import os
import random
import yaml
from flask import Flask, jsonify, send_from_directory

app = Flask(__name__, static_folder="static")

# Load questions once at startup
with open(os.path.join(os.path.dirname(__file__), "nj_drivers_test_questions.yaml")) as f:
    _data = yaml.safe_load(f)
    QUESTIONS = _data["questions"]
    METADATA = _data["metadata"]
    CATEGORIES = sorted(set(q["category"] for q in QUESTIONS))


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/metadata")
def metadata():
    return jsonify({
        "total_questions": len(QUESTIONS),
        "categories": CATEGORIES,
        "passing_score": METADATA["passing_score"],
    })


@app.route("/api/quiz")
@app.route("/api/quiz/<int:count>")
def quiz(count=50):
    count = min(count, len(QUESTIONS))
    selected = random.sample(QUESTIONS, count)
    # Don't send the answer to the client in the quiz payload
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
    q = next((q for q in QUESTIONS if q["id"] == question_id), None)
    if not q:
        return jsonify({"error": "Question not found"}), 404
    return jsonify({
        "id": q["id"],
        "answer": q["answer"],
        "explanation": q["explanation"],
    })


@app.route("/api/answers", methods=["POST"])
def answers():
    """Bulk answer check — accepts JSON body with list of question IDs."""
    from flask import request
    ids = request.get_json(force=True).get("ids", [])
    result = {}
    for qid in ids:
        q = next((q for q in QUESTIONS if q["id"] == qid), None)
        if q:
            result[str(qid)] = {
                "answer": q["answer"],
                "explanation": q["explanation"],
            }
    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
