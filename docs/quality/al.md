# Alabama (AL) — Quiz Quality Verification

| | |
|---|---|
| State | Alabama (AL) |
| Agency | ALEA |
| Manual | [Alabama Driver Manual (alea.gov)](https://www.alea.gov/sites/default/files/inline-files/driverlicensemanual.pdf) |
| Edition | June 2016 |
| Manual text | 173,549 chars (88 pages) |
| Questions | 292 (EN/ES) |
| Verified | 2026-04-29 |

## Score

| Axis | Grade |
|---|---|
| Precision | A |
| Recall | A |
| Coverage | A |
| **Overall** | **A** |

- **Precision A**: 100% of non-sign questions (274/274) are grounded in the manual.
- **Recall A**: 25/25 (100%) of critical Alabama-specific topics are covered by at least one question.
- **Coverage A**: All 10 canonical categories present, well-balanced (largest category 19%); reasonable question density.

## Precision

Two-pass check per question. Mechanical pass: distinctive 4–6 word phrases from each question's `explanation` were grepped against `manual_text.txt`. Phrases that did not match were sent to Gemini (`gemini-3-flash-preview`) with top-3 keyword-anchored excerpts from the manual for a second opinion. Sign questions (image-based) were excluded — they're MUTCD-derived, not manual-text-derived.

| Bucket | Count | % of non-sign |
|---|---:|---:|
| Total questions | 292 | — |
| Sign questions (image-based, skipped) | 18 | — |
| Non-sign questions | 274 | 100% |
| Grounded by phrase match | 257 | 94% |
| Sent to Gemini judge (17 grep-misses + 10 grounded controls) | 27 | — |
| Confirmed grounded after semantic re-check | 274 | 100% |
| Partial | 0 | 0% |
| Fabricated | 0 | 0% |

**Flagged question IDs**: None. Every non-sign question was verified to be grounded in the Alabama Driver Manual. (All initial grep misses were re-confirmed grounded by Gemini once it was given a correctly-anchored manual excerpt — they only missed because the explanation paraphrases the manual rather than quoting it verbatim, e.g. Q13 cites "Persons under 16 years of age" which IS in the manual at the "Who Cannot Be Licensed" section.)

## Recall

Gemini was asked to enumerate the 25 most important driving topics in the Alabama manual (Alabama-specific where applicable: GDL rules, statutory speed limits, point system, etc.). Each topic was matched against the 292 questions using both keyword overlap and semantic check.

| # | Topic | Covered | Example IDs |
|---:|---|:---:|---|
| 1 | Alabama Graduated Driver License (GDL) Restrictions | ✓ | 27, 28, 31, 32, 249 |
| 2 | Alabama Point System and License Suspension | ✓ | 72, 73, 76, 89 |
| 3 | Legal Blood Alcohol Concentration (BAC) Limits | ✓ | 122, 123 |
| 4 | Alabama Implied Consent Law | ✓ | 125 |
| 5 | Traffic Sign Shapes and Meanings | ✓ | 138, 148, 150, 151, 153 |
| 6 | Alabama Statutory Speed Limits | ✓ | 172, 173, 174 |
| 7 | Stopping for School Buses | ✓ | 178, 248 |
| 8 | Alabama Move Over Law | ✓ | 203 |
| 9 | Right-of-Way at Intersections | ✓ | 181, 210 |
| 10 | Following Distance and the Two-Second Rule | ✓ | 128, 130 |
| 11 | Parking on Hills | ✓ | 105, 106 |
| 12 | Sharing the Road with Bicycles | ✓ | 84, 85, 86, 87, 88, 154 |
| 13 | Large Vehicle No-Zones | ✓ | 97, 98, 104 |
| 14 | Alabama Safety Belt and Child Restraint Laws | ✓ | 109, 110, 111, 246 |
| 15 | Night Driving and Headlight Use | ✓ | 99, 205, 206, 207, 208, 209 |
| 16 | Hydroplaning and Wet Road Safety | ✓ | 91, 131, 212, 218, 219 |
| 17 | Handling Driving Emergencies | ✓ | 224 |
| 18 | Window Tinting Regulations | ✓ | 198 |
| 19 | Mandatory Liability Insurance Law | ✓ | 195 |
| 20 | Pavement Markings and Lane Usage | ✓ | 81, 153, 155, 158, 164, 165 |
| 21 | Railroad Crossing Safety | ✓ | 102, 108, 138, 139, 140, 141 |
| 22 | Proper Turning and Signaling | ✓ | 75, 79, 80, 81, 82, 88 |
| 23 | Documents Required at Traffic Stops | ✓ | 195, 267 |
| 24 | Reporting Traffic Crashes | ✓ | 136 |
| 25 | License Cancellation, Revocation, and Suspension | ✓ | 66 |

**Coverage rate**: 25/25 = 100%.

## Coverage

### Category distribution

All 10 canonical categories are present. The largest single category is `safe_driving_rules` at 19% — well below the 40% over-concentration threshold.

| Category | Count | % |
|---|---:|---:|
| safe_driving_rules | 55 | 19% |
| license_system | 52 | 18% |
| signs_and_signals | 40 | 14% |
| penalties_and_points | 32 | 11% |
| sharing_the_road | 25 | 9% |
| defensive_driving | 22 | 8% |
| vehicle_information | 21 | 7% |
| driver_responsibility | 20 | 7% |
| driver_testing | 16 | 5% |
| alcohol_drugs_health | 9 | 3% |
| **Total** | **292** | **100%** |

### Question density

| Metric | Value |
|---|---|
| Questions | 292 |
| Manual text size | 173,549 chars |
| Density (Qs per 1,000 manual chars) | 1.68 |

The 88-page Alabama manual produces 1.68 Qs per 1,000 chars — comfortably within the typical range across the corpus (most onboarded states are between 1.2 and 2.5).

### Sign-question ratio

| Source | Count | % |
|---|---:|---:|
| Sign questions (image-based, MUTCD-derived) | 18 | 6% |
| Manual-text-derived questions | 274 | 94% |

## Recommended Actions

No precision-flagged questions to fix or remove.

Minor observations (not blocking):

- **`alcohol_drugs_health` is the thinnest category (9 questions, 3%).** The Alabama manual dedicates a meaningful section to Drinking and Driving, Drugs, BAC limits (0.08 / 0.04 CDL / 0.02 under-21), and the Implied Consent Law. Consider adding a handful more DUI-and-drug-policy questions (e.g., per-se BAC for school-bus / daycare drivers, drug-impaired-driving penalties, Implied Consent refusal consequences) to bring this category in line with `defensive_driving` and `vehicle_information`. This would not change the recall grade but would strengthen test-taker exposure to high-stakes content.
- **Manual edition is "June 2016".** `manual_provenance.json` lists `edition: ""`; the PDF cover page in `manual_text.txt` reads "June 2016 Edition". Consider populating `edition` so future verifiers can flag staleness if a newer ALEA edition is released.
