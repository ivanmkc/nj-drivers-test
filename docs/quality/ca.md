# California (CA) — Quiz Quality Report

- **State:** California (CA)
- **Manual edition:** 2025 California Driver Handbook (dmv.ca.gov)
- **Manual size:** 137,033 chars across 92 PDF pages
- **Question count:** 284 (11 sign questions, 273 text questions)
- **Languages:** EN, ES, JA
- **Report generated:** 2026-05-24

## Score

**Overall grade: C**

| Axis | Grade | Metric |
|---|---|---|
| Precision | **F** | ~59.0% grounded (est. 112 fabricated/partial of 273 text questions, including 72 confirmed HTML/CSS-derived) |
| Recall | **B** | 22/25 (88%) of critical topics have ≥1 question |
| Coverage | **A** | 10/10 canonical categories present; max share 20.4% |

## Precision

Two-stage check: every non-sign question first gets a mechanical 3-6-gram match against the
PyMuPDF-extracted manual text. A random sample of mechanically-ungrounded questions plus a
control sample of mechanically-grounded questions go to a Gemini judge (`gemini-3-flash-preview`)
with the manual excerpt as context.

| Stage | Grounded | Ungrounded | Sign (skipped) |
|---|---|---|---|
| Mechanical (3-6-gram match) | 81 | 192 | 11 |

**Deterministic web-artifact detector** flagged **72** questions whose text contains CSS/HTML
tokens (e.g. `--wp--preset-…`, `z-index`, `rgb(…)`, `linear-gradient`, `iframe`, `Google Tag Manager`).
These appear to have been generated from the DMV website's HTML/CSS source code rather than the
driver handbook PDF. Spot-checks in the LLM judge confirm: e.g. Q225 asks about a CSS aspect-ratio preset,
Q229 about gradient color stops, Q237 about a button z-index — none of which are driving-test content.

Affected ID ranges (compressed):

`Q121-123, 125-143, 204, 206-250, 252, 254-256`

LLM judge verdict on the precision sample:

| Verdict | Count |
|---|---|
| grounded | 14 |
| partial | 0 |
| fabricated | 6 |
| unknown | 7 |

- Bad-rate in ungrounded sample: **33%** (6/18)
- Bad-rate in grounded-control sample: **0%** (0/9)
- Extrapolated to the full 273-question text bank: ~**112** estimated fabricated/partial questions.

### Flagged as `fabricated` by LLM judge

| ID | Note |
|---|---|
| Q225 | The manual does not contain CSS or WordPress preset definitions. |
| Q229 | The manual does not contain CSS or gradient preset definitions. |
| Q237 | The manual does not contain CSS or z-index information. |
| Q240 | The manual does not contain CSS or gradient preset definitions. |
| Q252 | The manual does not contain HTML source code or Google Tag Manager details. |
| Q260 | The manual does not mention IBC Case Status or specific checkable statuses. |

## Recall

`gemini-3.1-pro-preview` was given the manual (split into two overlapping halves to avoid
output truncation) and asked for the most important topics a CA written-test taker must know.
For each topic, we substring-match the topic keywords against every question's text, choices,
and explanation.

**Coverage rate: 22/25 (88%).**

| Topic | # Qs | Sample IDs |
|---|---|---|
| Provisional Driver License Restrictions | 4 | Q82, Q90, Q104, Q190 |
| Hand and Arm Turn Signals (uncovered) | 0 | _none_ |
| Headlight Usage and Dimming Distances | 4 | Q1, Q25, Q59, Q115 |
| Roadway Lane Line Markings | 3 | Q21, Q64, Q76 |
| High-Occupancy Vehicle Carpool Lanes | 2 | Q21, Q79 |
| Center Left Turn Lane Rules | 4 | Q81, Q107, Q109, Q115 |
| Legal and Illegal U-Turns | 9 | Q21, Q64, Q69, Q70, Q76 |
| Parking on Uphill and Downhill Grades | 2 | Q19, Q78 |
| Colored Curb Parking Regulations | 72 | Q4, Q5, Q6, Q8, Q9 |
| Traffic Signal Lights and Arrows | 5 | Q4, Q5, Q8, Q20, Q117 |
| Right-of-Way at Intersections | 3 | Q22, Q57, Q103 |
| Sharing the Road with Large Trucks | 4 | Q14, Q60, Q110, Q188 |
| Yielding to Emergency Vehicles | 3 | Q5, Q26, Q115 |
| School Zones and School Buses (uncovered) | 0 | _none_ |
| Special Speed Limit Zones | 8 | Q1, Q4, Q6, Q17, Q64 |
| Pedestrian Right-of-Way and Crosswalks | 18 | Q5, Q8, Q12, Q20, Q22 |
| Navigating Roundabouts and Intersections | 3 | Q20, Q111, Q189 |
| Sharing the Road with Motorcycles | 2 | Q110, Q192 |
| Sharing the Road with Bicycles | 8 | Q48, Q54, Q62, Q63, Q81 |
| Reacting to Emergency Vehicles | 3 | Q5, Q26, Q115 |
| Special Speed Limits and Blind Intersections | 8 | Q1, Q4, Q6, Q17, Q64 |
| Driver Record Points and Suspensions | 3 | Q4, Q108, Q198 |
| Visual Scanning and Following Distance | 7 | Q10, Q14, Q23, Q58, Q60 |
| Driving in Fog and Bad Weather | 2 | Q85, Q92 |
| Seat Belts and Child Restraints (uncovered) | 0 | _none_ |

## Coverage

- **Question density:** 2.07 questions per 1,000 manual chars (284 Qs / 137,033 chars).
- **Sign-image questions:** 11 (3.9% of bank).
- **Categories present:** 10/10 canonical.
- **Missing categories:** none.
- **Max category share:** 20.4% (threshold: 40%).

| Category | Count | Share |
|---|---|---|
| driver_responsibility | 58 | 20.4% |
| safe_driving_rules | 42 | 14.8% |
| signs_and_signals | 42 | 14.8% |
| license_system | 33 | 11.6% |
| sharing_the_road | 27 | 9.5% |
| driver_testing | 22 | 7.7% |
| vehicle_information | 19 | 6.7% |
| penalties_and_points | 16 | 5.6% |
| defensive_driving | 15 | 5.3% |
| alcohol_drugs_health | 10 | 3.5% |

## Recommended Actions

- **CRITICAL — Remove or regenerate 72 HTML/CSS-derived questions** (IDs `Q121-123, 125-143, 204, 206-250, 252, 254-256`). These were generated from the DMV website's page source instead of the handbook PDF. Re-extract `manual_text.txt` (PyMuPDF should ignore the HTML chrome; if the manual was scraped from the web page it needs to be re-downloaded as PDF), then re-run `tools/generate_questions.py ca` for the affected range.
- Review and rewrite/remove `fabricated`-flagged questions outside the web-artifact range — notably **Q260** (claims "IBC Case Status" is a checkable DMV online status; the manual does not list this). The other 5 LLM-flagged IDs (Q225, Q229, Q237, Q240, Q252) are already covered by the bulk action above.
- Add questions for uncovered critical topics: Hand and Arm Turn Signals; School Zones and School Buses; Seat Belts and Child Restraints.

---

_Auto-generated by per-state verification agent on 2026-05-24._
_Manual SHA-256: `63c96b38efd7cf7d139e98f12dad5f4a412d336451740cd1506208ee13cf3b82`._
