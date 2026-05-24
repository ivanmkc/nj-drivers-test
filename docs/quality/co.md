# Quality Report: Colorado (CO)

- **State:** Colorado
- **Agency:** DMV
- **Manual:** Colorado Driver Handbook (DR 2337, January 2025)
- **Manual URL:** https://dmv.colorado.gov/sites/dmv/files/documents/DR_2337_Jan2025.pdf
- **Manual edition:** 2025-01 (PDF SHA-256 `87869884...b8c866`, 36 pages, 138,051 chars extracted)
- **Question bank:** `data/states/co/questions_en.yaml` (Spanish translation present)
- **Question count:** 255 total (221 text + 34 sign/image questions)
- **Density:** 1.85 questions per 1,000 manual characters
- **Methodology:** per `~/.claude/plans/agile-pondering-truffle.md` (mechanical n-gram precision + Gemini 3 Flash semantic precision + Gemini 3.1 Pro topic-extraction recall + categorical coverage analysis)
- **Verified:** 2026-04-29

## Score

| Axis        | Result                                                  | Grade |
| ----------- | ------------------------------------------------------- | ----- |
| Precision   | 67/67 sampled questions grounded after LLM check (100%) | A     |
| Recall      | 25/25 critical topics covered by >=1 question (100%)    | A     |
| Coverage    | All 10 canonical categories present; mild imbalance     | B+    |
| **Overall** |                                                         | **A** |

CO ships a strong, well-grounded 255-question bank. Every audited claim is traceable to the official handbook, every critical topic is represented, and Colorado-specific mountain-driving content is present (narrow-road right-of-way, runaway truck ramps, downhill gear shifting). Minor issues are listed under Recommended Actions.

## Precision

`tools/audit_questions.py co` returns 0 structural/duplicate/content issues.

Procedure: combined `question + explanation` n-gram lookup against `manual_text.txt`; questions failing mechanical grounding were sent to Gemini 3 Flash with the full handbook as context; a 10-question control sample of mechanically-grounded questions was also LLM-judged to detect false positives.

| Group                                       | Total | Grounded | Partial | Fabricated |
| ------------------------------------------- | ----- | -------- | ------- | ---------- |
| Mechanical n-gram match (no LLM needed)     | 164   | 164      | 0       | 0          |
| LLM-judged: ungrounded by n-gram            | 57    | 57       | 0       | 0          |
| LLM-judged: control sample (mech. grounded) | 10    | 10       | 0       | 0          |
| Sign/image questions (visual, skipped)      | 34    | n/a      | n/a     | n/a        |
| **Total (non-sign)**                        | 221   | 221      | 0       | 0          |

Six questions were initially flagged "fabricated" by the LLM because the handbook context was truncated to 120k chars during the first pass. Re-running with the full 138k-char manual revealed each was grounded:

- **Q192** (aggressive-driver tip "leave early") - manual: _"Leave early for any trip. Too frequently people don't allow enough time..."_
- **Q193** ("three options to avoid a collision") - manual: _"To avoid a collision, drivers have three options: Slow down or stop, Turn, Speed up"_
- **Q206** (power-failure brakes/steering) - manual: _"the steering may be difficult to turn but you can turn it... The brakes will still work but you may have to push very hard on the brake pedal"_
- **Q207** (ask conscious victim permission) - manual: _"Ask a conscious victim for permission before giving care."_
- **Q210** (organ-donor heart-Y symbol) - manual: _"If you say Yes, a heart with a 'Y' will appear on the front of your license, permit or ID."_
- **Q221** (permit test at home) - manual: _"Take your permit test at home!"_

Net precision: **100%** on the sampled subset. No partials, no fabrications.

## Recall

Gemini 3.1 Pro was asked to enumerate the 25 most important specific topics a CO written-test taker must know from the handbook. Each topic was then matched against the question bank using its keyword set (>=2 keyword hits or a multi-word phrase match):

| Topic                                | Matched Qs | Status |
| ------------------------------------ | ---------- | ------ |
| Minor Driver Restrictions            | 2          | OK     |
| Address and Name Changes (30 days)   | 5          | OK     |
| DUI and DWAI Limits                  | 5          | OK     |
| Express Consent Law                  | 4          | OK     |
| Marijuana Impairment Limit (5 ng/ml) | 3          | OK     |
| Child Restraint Laws                 | 5          | OK     |
| Flashing Yellow Arrow                | ~23\*      | OK     |
| Roundabout Right-of-Way              | 7          | OK     |
| Narrow Mountain Roads                | 5          | OK     |
| Emergency Vehicle Right-of-Way       | 11         | OK     |
| School Bus Stopping Rules            | 17         | OK     |
| Default Speed Limits                 | 20         | OK     |
| Turn Signal Distances (100/200 ft)   | 17         | OK     |
| Hill Parking Wheel Direction         | 2          | OK     |
| Passing Bicyclists (3-foot rule)     | 4          | OK     |
| Headlight Usage                      | 10         | OK     |
| Skidding and Hydroplaning            | 2          | OK     |
| Mountain Driving & Runaway Ramps     | 2          | OK     |
| Following Distance (3-second rule)   | 1          | OK     |
| Zipper Merge                         | 2          | OK     |
| Motorcycle Lane Filtering            | 4          | OK     |
| Large Truck No Zones                 | 7          | OK     |
| Bicyclist Stop Sign Law (age 15+)    | 20         | OK     |
| Move It Law                          | 10         | OK     |
| Move Over Law                        | 3          | OK     |

\*The 23 "Flashing Yellow Arrow" matches are inflated by the keyword "yellow" pulling in unrelated school-bus and signal questions; the topic itself is in fact directly covered.

**Coverage: 25/25 = 100%.** All critical topics have at least one dedicated question.

### Colorado-specific mountain-driving deep-dive

Per task spec, the report pays special attention to mountain-specific content:

| Required CO mountain topic                       | In manual?    | In questions?                                                   |
| ------------------------------------------------ | ------------- | --------------------------------------------------------------- |
| Narrow mountain road right-of-way                | Yes (p. 11)   | Yes (Q84, Q128)                                                 |
| Downhill speed control via lower gears           | Yes (p. 17)   | Yes (Q129)                                                      |
| Runaway truck or bus warning sign (brake smoke)  | Yes (p. 25)   | Yes (Q152)                                                      |
| "Never park/chain up on runaway ramp" safety     | Yes (p. 25)   | **Gap** - the safety rule itself is not asked                   |
| Chain law / traction-device requirement          | Yes (briefly) | **Gap** - 0 questions mention "chain"                           |
| Brake fade                                       | Not mentioned | n/a                                                             |
| Altitude/elevation effects on engine/braking     | Not mentioned | n/a (manual is silent here; not a defect to omit from the quiz) |
| Steep grades / "Grade Ahead" sign interpretation | Yes           | Yes (Q248 - "steep hill or grade ahead" warning sign)           |
| Vehicles going uphill have right-of-way          | Yes (p. 17)   | Yes (Q128)                                                      |

The manual itself defers to the CDOT website for the Colorado Chain Law specifics, so the quiz's omission of explicit chain-law questions mirrors the manual's level of detail. Still, given chain laws are a quintessential CO test-taker concern, adding 1-2 chain-law questions would close the gap.

## Coverage

### Category distribution (10 canonical categories)

| Category               | Count | % of Bank | Notes              |
| ---------------------- | ----- | --------- | ------------------ |
| safe_driving_rules     | 68    | 26.7%     | OK                 |
| signs_and_signals      | 50    | 19.6%     | OK (34 are images) |
| sharing_the_road       | 33    | 12.9%     | OK                 |
| driver_responsibility  | 21    | 8.2%      | OK                 |
| defensive_driving      | 20    | 7.8%      | OK                 |
| vehicle_information    | 16    | 6.3%      | OK                 |
| license_system         | 14    | 5.5%      | OK                 |
| driver_testing         | 13    | 5.1%      | Slightly heavy     |
| penalties_and_points   | 12    | 4.7%      | OK                 |
| alcohol_drugs_health   | 8     | 3.1%      | **Under-covered**  |
| _all 10 cats present_  | -     | -         | OK                 |
| _any cat over 40%?_    | No    | -         | OK                 |

`safe_driving_rules` at 26.7% is the largest bucket but well under the 40% over-concentration threshold. `alcohol_drugs_health` at 3.1% (only 8 questions) is the weakest; the CO manual gives DUI/DWAI/express consent/marijuana significant page space and the topic is heavily tested in practice. This should be expanded.

### Sign-question contribution

- 34 of 50 `signs_and_signals` questions are image-based (MUTCD signs from the shared sign library).
- Sign coverage looks broad: regulatory, warning, guide, work zone, school zone, railroad, wrong way, hill-grade.

### Density vs manual size

- 1.85 questions per 1,000 chars of manual is on the high end for a 36-page handbook. CO's manual is relatively concise; the quiz extracts thoroughly from it without inflation.

## Recommended Actions

Prioritized; none are blockers (audit is clean and grounding is 100%).

1. **Disambiguate Q84 vs Q128** - both ask "who has the right-of-way on a narrow mountain road?" but Q84's answer is "downhill vehicle must yield by backing up" (the specific narrow-road rule, p. 11) while Q128's answer is "vehicle going uphill" (the general mountain-driving heuristic, p. 17). Both are technically grounded but the questions read as contradictory. Recommend either (a) rewording Q128 so the scenario is clearly general mountain driving rather than the same "two vehicles meet, neither can pass" scenario, or (b) collapsing into one canonical question.
2. **Add 1-2 chain-law questions** - the only Colorado-specific topic where the manual touches on it but the quiz omits it (e.g., "Chains, snow tires or alternative traction devices may be required on which Colorado highways in winter?"). The manual's coverage is shallow but a test-taker should know the term exists and that CDOT publishes the chain law.
3. **Expand `alcohol_drugs_health` from 8 to ~15 questions** - this category is under-represented relative to the manual's emphasis (DUI 0.08% BAC, DWAI 0.05%, under-21 0.02%, marijuana 5 ng/ml, express consent revocation lengths, ignition interlock). The 0.02% under-21 BAC ("baby DUI") in particular is not currently in the quiz.
4. **Add 1 explicit `runaway truck ramp` safety question** about the "never chain up, change a tire or park on the ramp" rule. Q152 currently covers how to recognize a runaway truck (brake smoke) but the safety prohibition itself is untested. This is a Colorado-distinctive safety rule.
5. **Optional: convert `driver_testing` over-representation (13 Qs)** - several questions cover examiner-only procedure details (e.g., "where to place your left hand while backing up during the drive test") that arguably belong in `safe_driving_rules`. Re-categorizing would balance the bank slightly.

No factually wrong / fabricated questions were found; no removals required.
