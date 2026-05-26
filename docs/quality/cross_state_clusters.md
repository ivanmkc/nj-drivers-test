# Cross-State Question Contamination Report

**Date**: 2026-05-26  
**Threshold**: cosine similarity >= 0.85  
**Min states per cluster**: 5  
**Corpus**: 16,828 non-sign questions across 50 states  
**Clusters found**: 40

## What this report is

Every cluster below is a group of questions whose stems are at least
**85% similar** (TF-IDF cosine) and that appear in
**>= 5 distinct states**. Sign questions (those with an
``image`` field, referencing shared MUTCD signs in ``data/signs/``) are
excluded from analysis — they are *supposed* to repeat.

## How to triage clusters

**Legitimate clusters (no action needed)** — every state's manual covers these
topics, so similar phrasing is expected:

- Universal DUI / BAC limits (e.g., "What is the legal BAC limit for drivers 21+?")
- Basic right-of-way at uncontrolled intersections
- Stop-sign / red-light behavior
- Seat-belt requirements
- Speed limits in school / residential zones
- Following-distance rules (3-second / 2-second)

**Suspicious clusters (investigate)** — these suggest the question generator
leaned on LLM knowledge instead of the state's specific manual:

- A statute / law / fine amount that is state-specific but appears verbatim in
  many states (e.g., a California-specific demerit schedule appearing in NY)
- Phrasing that quotes a specific section number (e.g., "Section 4.2 says...")
  appearing across multiple states whose manuals have no such section
- Questions referencing a state-specific agency or program name (e.g., "the
  Illinois Rules of the Road booklet") appearing in states other than the one
  named

When in doubt: open the involved states' ``manual_text.txt`` and grep for the
distinctive phrase. If only one state's manual contains it, the others
contaminated their banks with that state's question.


## Clusters

### Cluster 1 - 14 states, 14 questions

**Sample**: It is illegal to park within how many feet of a fire hydrant?

| State | Question IDs |
|-------|--------------|
| ar | 123 |
| az | 100 |
| ca | 80 |
| ct | 254 |
| de | 42 |
| la | 284 |
| mi | 188 |
| ne | 212 |
| nh | 155 |
| ok | 170 |
| pa | 259 |
| tn | 494 |
| vt | 93 |
| wy | 148 |

### Cluster 2 - 9 states, 9 questions

**Sample**: If two vehicles arrive at a four-way stop at the same time, who has the right of way?

| State | Question IDs |
|-------|--------------|
| ct | 242 |
| de | 365 |
| ia | 60 |
| ks | 138 |
| ms | 123 |
| nm | 59 |
| ri | 134 |
| tn | 342 |
| tx | 178 |

### Cluster 3 - 9 states, 9 questions

**Sample**: A fluorescent or reflective orange and red triangle displayed on the rear of a vehicle indicates:

| State | Question IDs |
|-------|--------------|
| ks | 346 |
| ky | 298 |
| la | 425 |
| ms | 79 |
| nh | 193 |
| oh | 132 |
| sc | 220 |
| sd | 305 |
| ut | 325 |

### Cluster 4 - 8 states, 8 questions

**Sample**: What is the only effective way to sober up after drinking alcohol?

| State | Question IDs |
|-------|--------------|
| ak | 83 |
| al | 126 |
| de | 238 |
| id | 289 |
| me | 104 |
| nc | 141 |
| nm | 136 |
| tn | 578 |

### Cluster 5 - 8 states, 8 questions

**Sample**: What is the recommended following distance when driving behind a motorcycle?

| State | Question IDs |
|-------|--------------|
| ar | 197 |
| ga | 298 |
| hi | 240 |
| me | 325 |
| nd | 137 |
| ne | 243 |
| nh | 190 |
| tx | 247 |

### Cluster 6 - 8 states, 8 questions

**Sample**: What must you do when another vehicle is passing you?

| State | Question IDs |
|-------|--------------|
| md | 54 |
| me | 211 |
| ne | 207 |
| oh | 70 |
| sc | 164 |
| sd | 207 |
| tx | 204 |
| va | 95 |

### Cluster 7 - 7 states, 7 questions

**Sample**: When are you NOT required to stop for a school bus with flashing red lights?

| State | Question IDs |
|-------|--------------|
| ak | 165 |
| co | 93 |
| la | 361 |
| md | 123 |
| ms | 126 |
| va | 79 |
| wi | 124 |

### Cluster 8 - 7 states, 7 questions

**Sample**: When passing a large truck, when is it safe to pull back in front of it?

| State | Question IDs |
|-------|--------------|
| ak | 232 |
| al | 100 |
| ks | 338 |
| ky | 286 |
| la | 347 |
| sd | 294 |
| tn | 764 |

### Cluster 9 - 7 states, 7 questions

**Sample**: If you are stopped at an intersection and your view of a cross street is blocked, what should you do?

| State | Question IDs |
|-------|--------------|
| ar | 139 |
| de | 472 |
| la | 256 |
| mt | 272 |
| nm | 77 |
| sd | 216 |
| wa | 189 |

### Cluster 10 - 7 states, 7 questions

**Sample**: What does a flashing red traffic light mean?

| State | Question IDs |
|-------|--------------|
| de | 311 |
| il | 283 |
| mo | 171 |
| nh | 234 |
| nv | 108 |
| ny | 133 |
| pa | 62 |

### Cluster 11 - 7 states, 7 questions

**Sample**: What must you do when approaching a flashing red traffic light?

| State | Question IDs |
|-------|--------------|
| id | 129 |
| la | 141 |
| mt | 185 |
| ne | 160 |
| ri | 175 |
| sd | 153 |
| wy | 243 |

### Cluster 12 - 6 states, 6 questions

**Sample**: Which of the following vehicles is required to stop at all railroad crossings?

| State | Question IDs |
|-------|--------------|
| ar | 103 |
| in | 217 |
| la | 384 |
| me | 264 |
| ny | 263 |
| oh | 75 |

### Cluster 13 - 6 states, 6 questions

**Sample**: Why can pavement be very slippery for the first few minutes when it starts to rain?

| State | Question IDs |
|-------|--------------|
| ar | 155 |
| me | 242 |
| mt | 304 |
| nm | 97 |
| tn | 554 |
| wa | 215 |

### Cluster 14 - 6 states, 6 questions

**Sample**: What should you do if you miss your exit on a road?

| State | Question IDs |
|-------|--------------|
| az | 104 |
| nj | 157 |
| pa | 253 |
| sd | 188 |
| wi | 56 |
| wy | 152 |

### Cluster 15 - 6 states, 6 questions

**Sample**: What should you do if you experience a tire blowout while driving?

| State | Question IDs |
|-------|--------------|
| az | 222 |
| co | 198 |
| in | 270 |
| me | 304 |
| ny | 281 |
| wi | 117 |

### Cluster 16 - 6 states, 6 questions

**Sample**: What does a reflective orange triangle on the rear of a vehicle mean?

| State | Question IDs |
|-------|--------------|
| co | 68 |
| ia | 29 |
| mo | 179 |
| nm | 45 |
| sd | 166 |
| wa | 114 |

### Cluster 17 - 6 states, 6 questions

**Sample**: What is the recommended hand position on the steering wheel?

| State | Question IDs |
|-------|--------------|
| ct | 97 |
| de | 457 |
| mo | 205 |
| va | 74 |
| vt | 79 |
| wa | 168 |

### Cluster 18 - 6 states, 6 questions

**Sample**: When meeting a truck coming from the opposite direction, why should you keep as far as possible to the side of the road?

| State | Question IDs |
|-------|--------------|
| de | 418 |
| ks | 341 |
| ok | 193 |
| sc | 212 |
| sd | 296 |
| tx | 237 |

### Cluster 19 - 6 states, 6 questions

**Sample**: How can you tell if you are driving in a large truck's side blind spot?

| State | Question IDs |
|-------|--------------|
| ia | 179 |
| ks | 337 |
| nh | 195 |
| sc | 203 |
| sd | 293 |
| va | 117 |

### Cluster 20 - 6 states, 6 questions

**Sample**: How much should you increase your following distance when driving on unfamiliar roadways at night?

| State | Question IDs |
|-------|--------------|
| ks | 301 |
| ky | 304 |
| la | 301 |
| nh | 112 |
| sc | 228 |
| sd | 310 |

### Cluster 21 - 6 states, 6 questions

**Sample**: Which headlights should you use when driving in fog?

| State | Question IDs |
|-------|--------------|
| md | 85 |
| mi | 270 |
| ms | 139 |
| nc | 259 |
| ne | 284 |
| oh | 103 |

### Cluster 22 - 6 states, 6 questions

**Sample**: What should you do if an emergency vehicle approaches while you are driving inside a roundabout?

| State | Question IDs |
|-------|--------------|
| mn | 108 |
| ne | 195 |
| or | 92 |
| pa | 246 |
| tx | 232 |
| vt | 97 |

### Cluster 23 - 5 states, 5 questions

**Sample**: What is "highway hypnosis"?

| State | Question IDs |
|-------|--------------|
| al | 113 |
| ga | 273 |
| id | 207 |
| la | 235 |
| ri | 148 |

### Cluster 24 - 5 states, 5 questions

**Sample**: When are you required to stop for a school bus with its red lights flashing?

| State | Question IDs |
|-------|--------------|
| ar | 66 |
| ct | 250 |
| de | 33 |
| mn | 144 |
| nm | 61 |

### Cluster 25 - 5 states, 5 questions

**Sample**: Where can you find the recommended tire pressure (psi) for your vehicle?

| State | Question IDs |
|-------|--------------|
| az | 58 |
| ct | 84 |
| ga | 237 |
| ks | 379 |
| wy | 165 |

### Cluster 26 - 5 states, 5 questions

**Sample**: What does a flashing yellow arrow mean?

| State | Question IDs |
|-------|--------------|
| az | 115 |
| il | 284 |
| mt | 188 |
| nv | 109 |
| wa | 107 |

### Cluster 27 - 5 states, 5 questions

**Sample**: When are you required to turn on your headlights?

| State | Question IDs |
|-------|--------------|
| ca | 25 |
| mn | 90 |
| mo | 224 |
| tn | 344 |
| wv | 273 |

### Cluster 28 - 5 states, 5 questions

**Sample**: How many questions must you answer correctly to pass the knowledge test?

| State | Question IDs |
|-------|--------------|
| ct | 36 |
| or | 16 |
| pa | 48 |
| vt | 61 |
| wa | 50 |

### Cluster 29 - 5 states, 5 questions

**Sample**: How much should you reduce your speed when driving on a wet road?

| State | Question IDs |
|-------|--------------|
| ct | 188 |
| de | 496 |
| me | 238 |
| mt | 301 |
| nm | 95 |

### Cluster 30 - 5 states, 5 questions

**Sample**: Why should you use low beams instead of high beams in fog or heavy rain?

| State | Question IDs |
|-------|--------------|
| ct | 257 |
| la | 443 |
| me | 280 |
| nm | 87 |
| wa | 198 |

### Cluster 31 - 5 states, 5 questions

**Sample**: Why should you never turn your vehicle's ignition to the 'lock' position while it is in motion?

| State | Question IDs |
|-------|--------------|
| ct | 272 |
| de | 549 |
| nd | 121 |
| nv | 180 |
| wa | 79 |

### Cluster 32 - 5 states, 5 questions

**Sample**: At what speed can your tires lose all traction with the road during heavy rain?

| State | Question IDs |
|-------|--------------|
| de | 500 |
| ks | 226 |
| mt | 305 |
| nm | 98 |
| wa | 217 |

### Cluster 33 - 5 states, 5 questions

**Sample**: Under what condition are you permitted to make a left turn on a red light?

| State | Question IDs |
|-------|--------------|
| fl | 197 |
| hi | 105 |
| nd | 65 |
| or | 36 |
| pa | 61 |

### Cluster 34 - 5 states, 5 questions

**Sample**: If your vehicle stalls on railroad tracks and a train is approaching, in which direction should you run?

| State | Question IDs |
|-------|--------------|
| fl | 280 |
| mo | 241 |
| ny | 262 |
| ri | 192 |
| tn | 814 |

### Cluster 35 - 5 states, 5 questions

**Sample**: When using the penny test to check tire wear, what indicates that you are driving with a safe amount of tread?

| State | Question IDs |
|-------|--------------|
| ga | 238 |
| ms | 50 |
| ne | 154 |
| pa | 145 |
| va | 192 |

### Cluster 36 - 5 states, 5 questions

**Sample**: What is the proper use of a shared center lane?

| State | Question IDs |
|-------|--------------|
| ks | 162 |
| la | 117 |
| me | 180 |
| nh | 129 |
| sc | 130 |

### Cluster 37 - 5 states, 5 questions

**Sample**: When should you dim your high beam headlights when an oncoming vehicle is approaching?

| State | Question IDs |
|-------|--------------|
| ks | 357 |
| la | 433 |
| nm | 86 |
| sc | 222 |
| sd | 247 |

### Cluster 38 - 5 states, 5 questions

**Sample**: Why should you not assume a motorcycle is turning just because its turn signal is flashing?

| State | Question IDs |
|-------|--------------|
| ky | 279 |
| me | 324 |
| oh | 119 |
| pa | 276 |
| sd | 290 |

### Cluster 39 - 5 states, 5 questions

**Sample**: What colors are used for work zone signs?

| State | Question IDs |
|-------|--------------|
| ky | 308 |
| nh | 213 |
| oh | 106 |
| sc | 226 |
| sd | 311 |

### Cluster 40 - 5 states, 5 questions

**Sample**: You should not start to pass a vehicle if you are within what distance of a hill or curve?

| State | Question IDs |
|-------|--------------|
| me | 212 |
| mt | 337 |
| nm | 119 |
| sd | 237 |
| wa | 247 |
