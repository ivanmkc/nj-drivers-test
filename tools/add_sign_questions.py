#!/usr/bin/env python3
"""Add road sign image-based questions to a state's question bank.

Usage:
    python add_sign_questions.py nj
    python add_sign_questions.py ny
"""

import os
import sys

import yaml

# Sign questions with real MUTCD sign images (public domain, national standard)
SIGN_QUESTIONS = [
    {
        "image": "stop.png",
        "category": "signs_and_signals",
        "question": "What does this sign mean?",
        "choices": {
            "A": "Slow down and proceed with caution",
            "B": "Come to a complete stop",
            "C": "Yield to oncoming traffic",
            "D": "Stop only if other vehicles are present",
        },
        "answer": "B",
        "explanation": "A red octagonal STOP sign means you must come to a complete stop at the stop line, crosswalk, or before entering the intersection. Check for traffic and pedestrians before proceeding.",
    },
    {
        "image": "yield.png",
        "category": "signs_and_signals",
        "question": "What does this sign require you to do?",
        "choices": {
            "A": "Come to a complete stop",
            "B": "Speed up to merge with traffic",
            "C": "Slow down and give the right-of-way to traffic and pedestrians",
            "D": "Proceed without stopping",
        },
        "answer": "C",
        "explanation": "A red and white triangular YIELD sign means you must slow down and yield the right-of-way to traffic and pedestrians. You must stop if necessary to let others pass safely.",
    },
    {
        "image": "do_not_enter.png",
        "category": "signs_and_signals",
        "question": "What does this sign mean?",
        "choices": {
            "A": "Road closed ahead",
            "B": "No parking allowed",
            "C": "Do not enter this roadway",
            "D": "Dead end ahead",
        },
        "answer": "C",
        "explanation": "A red and white DO NOT ENTER sign means you must not enter the road or ramp where this sign is posted. It is usually seen at freeway off-ramps or one-way streets where entering would put you in the path of oncoming traffic.",
    },
    {
        "image": "wrong_way.png",
        "category": "signs_and_signals",
        "question": "If you see this sign, what should you do?",
        "choices": {
            "A": "Make a U-turn",
            "B": "Continue driving carefully",
            "C": "Stop and back up or turn around — you are going the wrong way",
            "D": "Speed up to exit the area quickly",
        },
        "answer": "C",
        "explanation": "A red and white WRONG WAY sign means you are traveling against traffic on a one-way road or highway ramp. Stop immediately and safely turn around or back up.",
    },
    {
        "image": "one_way_left.png",
        "category": "signs_and_signals",
        "question": "What does this sign indicate?",
        "choices": {
            "A": "Left turn only",
            "B": "Traffic flows in one direction — to the left",
            "C": "Keep left of the median",
            "D": "Highway exit to the left",
        },
        "answer": "B",
        "explanation": "A black and white ONE WAY sign with an arrow indicates that traffic on this street moves in only one direction — the direction the arrow points.",
    },
    {
        "image": "no_u_turn.png",
        "category": "signs_and_signals",
        "question": "What does this sign prohibit?",
        "choices": {
            "A": "Right turns",
            "B": "Left turns",
            "C": "U-turns",
            "D": "Passing other vehicles",
        },
        "answer": "C",
        "explanation": "A white regulatory sign with a U-turn arrow crossed out means U-turns are prohibited at this location.",
    },
    {
        "image": "no_left_turn.png",
        "category": "signs_and_signals",
        "question": "What action is prohibited by this sign?",
        "choices": {
            "A": "Turning right",
            "B": "Turning left",
            "C": "Making a U-turn",
            "D": "Going straight",
        },
        "answer": "B",
        "explanation": "A white regulatory sign showing a left turn arrow crossed out means left turns are not allowed at this intersection.",
    },
    {
        "image": "no_right_turn.png",
        "category": "signs_and_signals",
        "question": "What does this sign mean?",
        "choices": {
            "A": "No U-turn allowed",
            "B": "No left turn allowed",
            "C": "No right turn allowed",
            "D": "No passing allowed",
        },
        "answer": "C",
        "explanation": "A white regulatory sign showing a right turn arrow crossed out means right turns are prohibited at this location.",
    },
    {
        "image": "no_passing.png",
        "category": "signs_and_signals",
        "question": "What does this sign indicate?",
        "choices": {
            "A": "Road narrows ahead",
            "B": "Do not pass other vehicles in this zone",
            "C": "Two-way traffic ahead",
            "D": "Keep right",
        },
        "answer": "B",
        "explanation": "A black and white NO PASSING ZONE pennant-shaped sign means you are not allowed to pass other vehicles in this area. It marks the beginning of a no-passing zone.",
    },
    {
        "image": "keep_right.png",
        "category": "signs_and_signals",
        "question": "What does this sign instruct drivers to do?",
        "choices": {
            "A": "Merge right",
            "B": "Turn right only",
            "C": "Keep to the right of a divider or obstruction",
            "D": "Right lane ends ahead",
        },
        "answer": "C",
        "explanation": "A white regulatory KEEP RIGHT sign with an arrow means you must keep to the right side of a traffic island, median, or obstruction.",
    },
    {
        "image": "speed_limit_25.png",
        "category": "signs_and_signals",
        "question": "What type of sign is this, based on its shape and color?",
        "choices": {
            "A": "A warning sign",
            "B": "A guide sign",
            "C": "A regulatory sign",
            "D": "A construction sign",
        },
        "answer": "C",
        "explanation": "White rectangular signs with black lettering are regulatory signs. Speed limit signs tell you the maximum legal speed for the area under ideal conditions.",
    },
    {
        "image": "deer_crossing.png",
        "category": "signs_and_signals",
        "question": "What does this yellow diamond-shaped sign warn you about?",
        "choices": {
            "A": "A zoo or animal park ahead",
            "B": "Deer frequently cross the road in this area",
            "C": "Hunting area ahead",
            "D": "A wildlife refuge nearby",
        },
        "answer": "B",
        "explanation": "A yellow diamond-shaped sign with a deer silhouette warns that deer frequently cross the road in this area. Slow down and watch for animals, especially at dawn and dusk.",
    },
    {
        "image": "pedestrian_crossing.png",
        "category": "signs_and_signals",
        "question": "What does this sign warn you about?",
        "choices": {
            "A": "School zone ahead",
            "B": "Pedestrian crossing ahead",
            "C": "Hiking trail nearby",
            "D": "Bus stop ahead",
        },
        "answer": "B",
        "explanation": "A yellow diamond-shaped sign with a pedestrian figure warns of a pedestrian crossing ahead. Be prepared to stop for pedestrians crossing the road.",
    },
    {
        "image": "school_zone.png",
        "category": "signs_and_signals",
        "question": "What does the shape of this sign indicate?",
        "choices": {
            "A": "A railroad crossing",
            "B": "A construction zone",
            "C": "A school zone or school crossing",
            "D": "A hospital zone",
        },
        "answer": "C",
        "explanation": "A pentagon-shaped (5-sided) fluorescent yellow-green sign indicates a school zone or school crossing. Slow down and watch for children.",
    },
    {
        "image": "railroad_crossing.png",
        "category": "signs_and_signals",
        "question": "What does this circular yellow sign warn you about?",
        "choices": {
            "A": "A roundabout ahead",
            "B": "A hospital zone",
            "C": "A railroad crossing ahead",
            "D": "A no-passing zone",
        },
        "answer": "C",
        "explanation": "A circular yellow sign with a black X and two R's is the advance warning sign for a railroad crossing ahead. Slow down, look, and listen for trains.",
    },
    {
        "image": "railroad_crossbuck.png",
        "category": "signs_and_signals",
        "question": "Where would you typically see this sign?",
        "choices": {
            "A": "At a school crossing",
            "B": "At a railroad crossing",
            "C": "At a hospital entrance",
            "D": "At a pedestrian bridge",
        },
        "answer": "B",
        "explanation": "The white X-shaped railroad crossbuck sign is placed at railroad crossings. It means you must yield to trains. If a train is approaching, you must stop.",
    },
    {
        "image": "curve_right.png",
        "category": "signs_and_signals",
        "question": "What does this yellow diamond-shaped sign indicate?",
        "choices": {
            "A": "Road ends ahead",
            "B": "Right turn required",
            "C": "A curve to the right ahead",
            "D": "Detour ahead",
        },
        "answer": "C",
        "explanation": "A yellow diamond-shaped sign with a curved arrow warns of a curve in the road ahead. Slow down before entering the curve.",
    },
    {
        "image": "sharp_turn_right.png",
        "category": "signs_and_signals",
        "question": "How does this sign differ from a curve sign?",
        "choices": {
            "A": "It indicates a less severe turn",
            "B": "It warns of a sharp turn requiring a greater speed reduction",
            "C": "It means turn right only",
            "D": "It is only used on highways",
        },
        "answer": "B",
        "explanation": "A sharp turn sign (with a more angled arrow) indicates a sharper turn than a curve sign. You need to reduce your speed more significantly before this turn.",
    },
    {
        "image": "reverse_curve.png",
        "category": "signs_and_signals",
        "question": "What road condition does this sign warn about?",
        "choices": {
            "A": "A winding road",
            "B": "A single curve ahead",
            "C": "A series of two curves in opposite directions",
            "D": "A roundabout ahead",
        },
        "answer": "C",
        "explanation": "A reverse curve sign warns of two curves in opposite directions ahead. Slow down and be prepared for the road to curve first one way, then the other.",
    },
    {
        "image": "winding_road.png",
        "category": "signs_and_signals",
        "question": "What does this sign warn you to expect?",
        "choices": {
            "A": "A single sharp curve",
            "B": "A slippery road surface",
            "C": "A series of curves or turns ahead",
            "D": "A hill ahead",
        },
        "answer": "C",
        "explanation": "A winding road sign warns of a series of curves or turns ahead. Reduce your speed and be alert for changing road conditions.",
    },
    {
        "image": "merge.png",
        "category": "signs_and_signals",
        "question": "What does this sign tell you to prepare for?",
        "choices": {
            "A": "A lane ending",
            "B": "Traffic merging from another road",
            "C": "A divided highway beginning",
            "D": "A road narrowing to one lane",
        },
        "answer": "B",
        "explanation": "A yellow diamond-shaped merge sign warns that traffic from another road will be merging into your lane. Be prepared to adjust your speed and position.",
    },
    {
        "image": "road_narrows.png",
        "category": "signs_and_signals",
        "question": "What does this sign warn about?",
        "choices": {
            "A": "Bridge ahead",
            "B": "Road narrows ahead",
            "C": "Lane ends",
            "D": "Divided highway ends",
        },
        "answer": "B",
        "explanation": "This warning sign indicates the road ahead becomes narrower. Be prepared for reduced road width and adjust your lane position.",
    },
    {
        "image": "divided_highway.png",
        "category": "signs_and_signals",
        "question": "What does this sign indicate is ahead?",
        "choices": {
            "A": "Road ends",
            "B": "Two-way traffic",
            "C": "A divided highway begins",
            "D": "Highway exit",
        },
        "answer": "C",
        "explanation": "This sign warns that the road ahead becomes a divided highway with a median or barrier separating opposing traffic. Keep to the right.",
    },
    {
        "image": "divided_highway_ends.png",
        "category": "signs_and_signals",
        "question": "What does this sign warn you about?",
        "choices": {
            "A": "A divided highway begins",
            "B": "The divided highway ends and two-way traffic resumes",
            "C": "A merge area ahead",
            "D": "Road construction ahead",
        },
        "answer": "B",
        "explanation": "This sign warns that the divided highway is ending. Opposing traffic will no longer be separated by a median. Be prepared for two-way traffic.",
    },
    {
        "image": "two_way_traffic.png",
        "category": "signs_and_signals",
        "question": "What does this sign warn you about?",
        "choices": {
            "A": "A divided highway begins",
            "B": "A passing zone ahead",
            "C": "Two-way traffic ahead — traffic moves in both directions",
            "D": "A lane shift ahead",
        },
        "answer": "C",
        "explanation": "This sign warns of two-way traffic ahead. You may be leaving a one-way road or divided highway and will encounter vehicles traveling in the opposite direction.",
    },
    {
        "image": "slippery_when_wet.png",
        "category": "signs_and_signals",
        "question": "What road condition does this sign warn about?",
        "choices": {
            "A": "Icy road conditions",
            "B": "The road may be slippery when wet",
            "C": "Winding road ahead",
            "D": "Uneven pavement",
        },
        "answer": "B",
        "explanation": "A slippery when wet sign warns that the road surface may become very slippery during rain or wet conditions. Reduce your speed and avoid sudden braking or turning.",
    },
    {
        "image": "hill.png",
        "category": "signs_and_signals",
        "question": "What does this sign warn you about?",
        "choices": {
            "A": "A bump in the road",
            "B": "An uneven road surface",
            "C": "A steep hill or grade ahead",
            "D": "Road construction",
        },
        "answer": "C",
        "explanation": "This sign warns of a steep hill or grade ahead. You may need to adjust your speed and shift to a lower gear, especially in trucks or when towing.",
    },
    {
        "image": "signal_ahead.png",
        "category": "signs_and_signals",
        "question": "What does this sign warn you to prepare for?",
        "choices": {
            "A": "A stop sign ahead",
            "B": "A traffic signal ahead",
            "C": "A school crossing",
            "D": "A police checkpoint",
        },
        "answer": "B",
        "explanation": "This sign warns of a traffic signal ahead. Be prepared to stop if the light is red or yellow. This sign is often placed where the signal may not be visible from a distance.",
    },
    {
        "image": "stop_ahead.png",
        "category": "signs_and_signals",
        "question": "What does this sign tell you to expect ahead?",
        "choices": {
            "A": "A yield sign",
            "B": "A traffic signal",
            "C": "A stop sign where you must stop",
            "D": "A speed bump",
        },
        "answer": "C",
        "explanation": "This sign warns that there is a stop sign ahead. Begin slowing down and prepare to come to a complete stop at the stop sign.",
    },
    {
        "image": "cross_road.png",
        "category": "signs_and_signals",
        "question": "What does this sign warn about?",
        "choices": {
            "A": "A railroad crossing ahead",
            "B": "A crossroad or intersection ahead",
            "C": "A hospital ahead",
            "D": "A pedestrian crossing",
        },
        "answer": "B",
        "explanation": "This sign warns that a crossroad or 4-way intersection is ahead. Watch for traffic entering from side roads.",
    },
    {
        "image": "side_road.png",
        "category": "signs_and_signals",
        "question": "What does this sign warn you about?",
        "choices": {
            "A": "A T-intersection ahead",
            "B": "A side road entering from the right",
            "C": "A curve in the road",
            "D": "A dead end",
        },
        "answer": "B",
        "explanation": "This sign warns of a side road entering from the right. Watch for vehicles entering the highway from the side road.",
    },
    {
        "image": "added_lane.png",
        "category": "signs_and_signals",
        "question": "What does this sign mean?",
        "choices": {
            "A": "Lanes are merging",
            "B": "A lane is ending",
            "C": "A new lane is being added — no merging needed",
            "D": "Right turn required",
        },
        "answer": "C",
        "explanation": "An added lane sign means a new lane is joining the highway without requiring merging. Traffic entering from the ramp has its own new lane.",
    },
    {
        "image": "no_parking.png",
        "category": "signs_and_signals",
        "question": "What does this sign prohibit?",
        "choices": {
            "A": "Stopping at any time",
            "B": "Parking in this area",
            "C": "Standing or idling",
            "D": "Loading or unloading",
        },
        "answer": "B",
        "explanation": "A red and white NO PARKING sign means you cannot park your vehicle in this area. You may briefly stop to load or unload passengers.",
    },
    {
        "image": "handicap_parking.png",
        "category": "signs_and_signals",
        "question": "Who is allowed to park in a space marked with this sign?",
        "choices": {
            "A": "Anyone for less than 15 minutes",
            "B": "Senior citizens only",
            "C": "Only vehicles displaying a valid disability placard or plate",
            "D": "Any driver with a passenger who has a disability",
        },
        "answer": "C",
        "explanation": "A blue sign with the wheelchair symbol marks parking reserved for persons with disabilities. Only vehicles displaying a valid disability parking placard or license plate may park in these spaces. Violations carry heavy fines.",
    },
]


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python add_sign_questions.py <state_code>")
        sys.exit(1)

    state_code = sys.argv[1].lower()
    state_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "states", state_code
    )
    yaml_path = os.path.join(state_dir, "questions_en.yaml")

    if not os.path.exists(yaml_path):
        print(f"Questions file not found: {yaml_path}")
        sys.exit(1)

    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    existing = data["questions"]
    max_id = max(q["id"] for q in existing)

    # Check which sign images actually exist
    signs_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "signs"
    )
    available = set(os.listdir(signs_dir)) if os.path.isdir(signs_dir) else set()

    # Filter to questions whose images exist and aren't already in the bank
    existing_images = {q.get("image") for q in existing if q.get("image")}
    new_questions = []
    for sq in SIGN_QUESTIONS:
        if sq["image"] not in available:
            print(f"  SKIP {sq['image']} (image not found)")
            continue
        if sq["image"] in existing_images:
            print(f"  SKIP {sq['image']} (already exists)")
            continue
        max_id += 1
        q = dict(sq)
        q["id"] = max_id
        new_questions.append(q)

    if not new_questions:
        print("No new sign questions to add.")
        return

    data["questions"].extend(new_questions)
    data["metadata"]["total_questions"] = len(data["questions"])
    cats = sorted(set(q["category"] for q in data["questions"]))
    data["metadata"]["categories"] = cats

    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"\nAdded {len(new_questions)} sign questions to {yaml_path}")
    print(f"Total questions now: {len(data['questions'])}")


if __name__ == "__main__":
    main()
