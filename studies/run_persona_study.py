"""Persona-driven UX comprehension study runner.

Each persona sees their own flow's screenshots (in order) and answers a fixed
question list in character. Answers are saved as JSON for scoring against
ground truth (see studies/2026-08-09-persona-ux-study.md).
"""

import json
import os

from google import genai
from google.genai import types

MODEL = "gemini-3.1-pro-preview"
CLIENT = genai.Client(vertexai=True, project="adk-coding-agents", location="global")
HERE = os.path.dirname(__file__)
SHOTS = os.path.join(HERE, "screenshots")
OUT = os.path.join(HERE, "answers")
os.makedirs(OUT, exist_ok=True)

PERSONAS = {
    "jordan": {
        "framing": (
            "You are Jordan, a 17-year-old in New Jersey preparing for your first "
            "learner's permit test. You are tech-savvy but know nothing about DMV "
            "rules. You just opened this practice app on your phone. The screenshots "
            "show, in order: the state list, the NJ home screen, the 'About this "
            "test' section expanded, a quiz question, and the same question after "
            "you tapped an answer."
        ),
        "shots": [
            "jordan-01-statepicker",
            "jordan-02-home",
            "jordan-03-about-expanded",
            "jordan-04-quiz",
            "jordan-05-quiz-answered",
        ],
        "questions": [
            "How many questions are on the real NJ test, and how many must you get right to pass?",
            "You keep getting road-sign questions wrong. How would you practice only your weak areas?",
            "After you tap an answer, how does the app show whether you were right or wrong?",
            "Where does the app say its questions come from? How could you check that source yourself?",
            "You realize you actually need the Pennsylvania test. How do you switch states?",
            "Some language buttons at the top have a small check mark. What does it mean?",
            "As a first-time user, what confused you or felt missing in this flow?",
        ],
    },
    "maria": {
        "framing": (
            "You are Maria, 34, a native Spanish speaker in Nevada with limited "
            "English, preparing for the Nevada knowledge test. You switched the app "
            "to Spanish. Screenshots in order: the Nevada home screen after switching "
            "to Spanish, the 'About' section expanded, and a quiz question after "
            "answering. Answer in English (for the researchers) but from Maria's "
            "perspective."
        ),
        "shots": ["maria-01-home-es", "maria-02-about-es", "maria-03-quiz-answered-es"],
        "questions": [
            "Can Maria take the REAL Nevada DMV test in Spanish, according to this app? How is that shown?",
            "Could she take the real test in Japanese? How does the app communicate that?",
            "Is the app interface actually in Spanish after switching? Any parts still in English?",
            "Where can Maria verify the questions come from the official Nevada manual?",
            "After answering, there is a quoted block from the manual. What language is it in, and is that a problem for Maria?",
            "What is the biggest friction point for a Spanish speaker in this flow?",
        ],
    },
    "ken": {
        "framing": (
            "You are Ken, 68, in Wyoming, renewing after decades. You prefer dark "
            "mode and larger text; small gray text is hard for you. Screenshots in "
            "order: the Wyoming home screen (dark mode), the About section expanded, "
            "the results screen after a 10-question quiz, and the statistics screen."
        ),
        "shots": [
            "ken-01-home-dark",
            "ken-02-about-dark",
            "ken-03-results-dark",
            "ken-04-stats-dark",
        ],
        "questions": [
            "How many questions are on the real Wyoming test and how many correct answers pass?",
            "Which languages can the REAL Wyoming test be taken in, per this app?",
            "What proof does the app offer that its content is trustworthy? List everything you can see.",
            "On the results screen: what score did Ken get, and did he pass? How is pass/fail communicated?",
            "On the statistics screen: how many quizzes has Ken taken, and why is there no score chart?",
            "Which specific pieces of text were hardest for you to read (size or contrast), if any?",
        ],
    },
    "aisha": {
        "framing": (
            "You are Aisha, 29, a data journalist evaluating whether this practice "
            "app can be trusted for California. You are professionally skeptical. "
            "Screenshots in order: the California About section expanded (dark "
            "desktop), and a quiz question after answering."
        ),
        "shots": ["aisha-01-about-ca", "aisha-02-quiz-evidence"],
        "questions": [
            "Does the app claim you can take California's official test in any specific language? What exactly does it say?",
            "What evidence backs the correct answer on the quiz screen? Quote what you see.",
            "What verification claims does the About section make? Are they specific enough to check?",
            "Could you locate the actual official manual from this app to fact-check it? How?",
            "As a skeptic: what increases your trust here, and what would you still challenge?",
        ],
    },
}


def run_persona(name: str, spec: dict) -> None:
    questions = "\n".join(f"{i + 1}. {q}" for i, q in enumerate(spec["questions"]))
    prompt = f"""{spec["framing"]}

Answer each question IN ORDER, staying in character, but be concrete and specific:
name actual buttons, numbers, and text you can see. If something is not visible
or not stated in the screenshots, say so explicitly — that is a finding, not a
failure. Do not invent UI that is not shown.

Questions:
{questions}

Return JSON: {{"answers": ["..."], "confidence": ["high|medium|low", ...]}} with one
entry per question."""
    parts = [types.Part(text=prompt)]
    for shot in spec["shots"]:
        with open(os.path.join(SHOTS, f"{shot}.png"), "rb") as f:
            parts.append(types.Part(inline_data=types.Blob(mime_type="image/png", data=f.read())))
    resp = CLIENT.models.generate_content(
        model=MODEL,
        contents=[types.Content(role="user", parts=parts)],
        config=types.GenerateContentConfig(temperature=0.1, response_mime_type="application/json"),
    )
    if resp.text is None:
        raise RuntimeError(f"empty response for {name}")
    with open(os.path.join(OUT, f"{name}.json"), "w") as f:
        f.write(resp.text)
    print(f"{name}: saved {len(json.loads(resp.text).get('answers', []))} answers")


if __name__ == "__main__":
    for persona_name, persona_spec in PERSONAS.items():
        run_persona(persona_name, persona_spec)
