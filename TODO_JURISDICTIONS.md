# Driver's Test Practice — Jurisdiction Coverage TODO

## Status Legend
- [x] Complete (questions + translations + sign images)
- [ ] Not started

## US States (50 + DC) — 49 / 51 complete

### Complete (49)
- [x] AK — Alaska (DMV, 292 Qs, EN/ES)
- [x] AL — Alabama (ALEA, 292 Qs, EN/ES)
- [x] AR — Arkansas (ASP, 296 Qs, EN/ES)
- [x] AZ — Arizona (MVD, 295 Qs, EN/ES)
- [x] CA — California (DMV, 284 Qs, EN/ES/JA)
- [x] CO — Colorado (DMV, 255 Qs, EN/ES)
- [x] CT — Connecticut (DMV, 364 Qs, EN/ES)
- [x] DE — Delaware (DMV, 649 Qs, EN/ES)
- [x] FL — Florida (DHSMV, 345 Qs, EN/ES/JA)
- [x] GA — Georgia (DDS, 390 Qs, EN/ES/JA)
- [x] HI — Hawaii (DOT, 376 Qs, EN/ES)
- [x] IA — Iowa (DOT, 237 Qs, EN/ES/JA)
- [x] ID — Idaho (ITD, 349 Qs, EN/ES)
- [x] IL — Illinois (SOS, 413 Qs, EN/ES)
- [x] IN — Indiana (BMV, 346 Qs, EN/ES/JA)
- [x] KS — Kansas (DOR, 468 Qs, EN/ES/JA)
- [x] KY — Kentucky (KYTC, 357 Qs, EN/ES)
- [x] LA — Louisiana (OMV, 588 Qs, EN/ES)
- [x] MA — Massachusetts (RMV, 456 Qs, EN/ES)
- [x] MD — Maryland (MVA, 202 Qs, EN/ES/JA)
- [x] ME — Maine (BMV, 435 Qs, EN/ES)
- [x] MI — Michigan (SOS, 350 Qs, EN/ES)
- [x] MN — Minnesota (DVS, 383 Qs, EN/ES)
- [x] MO — Missouri (DOR, 394 Qs, EN/ES/JA)
- [x] MS — Mississippi (DPS, 252 Qs, EN/ES)
- [x] MT — Montana (DOJ, 460 Qs, EN/ES)
- [x] NC — North Carolina (DMV, 376 Qs, EN/ES/JA)
- [x] ND — North Dakota (DOT, 263 Qs, EN/ES)
- [x] NE — Nebraska (DMV, 332 Qs, EN/ES)
- [x] NH — New Hampshire (DMV, 268 Qs, EN/ES)
- [x] NJ — New Jersey (MVC, 307 Qs, EN/ES/JA)
- [x] NM — New Mexico (MVD, 222 Qs, EN/ES)
- [x] NV — Nevada (DMV, 346 Qs, EN/ES)
- [x] NY — New York (DMV, 391 Qs, EN/ES/JA)
- [x] OH — Ohio (BMV, 280 Qs, EN/ES)
- [x] OK — Oklahoma (DPS, 307 Qs, EN/ES)
- [x] OR — Oregon (DMV, 284 Qs, EN/ES/JA)
- [x] PA — Pennsylvania (PennDOT, 507 Qs, EN/ES/JA)
- [x] RI — Rhode Island (DMV, 374 Qs, EN/ES)
- [x] SC — South Carolina (DMV, 281 Qs, EN/ES)
- [x] TN — Tennessee (DOS, 874 Qs, EN/ES/JA)
- [x] TX — Texas (DPS, 417 Qs, EN/ES/JA)
- [x] UT — Utah (DLD, 427 Qs, EN/ES)
- [x] VA — Virginia (DMV, 279 Qs, EN/ES/JA)
- [x] VT — Vermont (DMV, 305 Qs, EN/ES)
- [x] WA — Washington (DOL, 376 Qs, EN/ES/JA)
- [x] WI — Wisconsin (DMV, 321 Qs, EN/ES/JA)
- [x] WV — West Virginia (DMV, 407 Qs, EN/ES)
- [x] WY — Wyoming (DOT, 281 Qs, EN/ES)

### Not Yet Sourced (2)
- [ ] DC — District of Columbia (DMV, recovered:false stub)
- [ ] SD — South Dakota (DPS, recovered:false stub)

## Canadian Provinces & Territories (13)

- [ ] AB — Alberta (Registry)
- [ ] BC — British Columbia (ICBC)
- [ ] MB — Manitoba (MPI)
- [ ] NB — New Brunswick (SNB)
- [ ] NL — Newfoundland & Labrador (DMV)
- [ ] NS — Nova Scotia (Access NS)
- [ ] NT — Northwest Territories (DOT)
- [ ] NU — Nunavut (DOT)
- [ ] ON — Ontario (MTO)
- [ ] PE — Prince Edward Island (HPE)
- [ ] QC — Quebec (SAAQ)
- [ ] SK — Saskatchewan (SGI)
- [ ] YT — Yukon (DOT)

## Pipeline per Jurisdiction
1. Find official driver manual PDF URL
2. Download and extract text via `tools/setup_state.py` (PyMuPDF)
3. Create `data/states/<code>/config.json` with name, agency, passing %, test count
4. Generate questions: `python3 tools/generate_questions.py <code> data/states/<code>/manual_text.txt`
5. Add sign questions: `python3 tools/add_sign_questions.py <code>`
6. Translate: `python3 tools/translate.py <code> es` (EN required, JA out of scope)
7. Run gates: `python3 tools/quiz_gates.py <code> --block-on-fail`
8. Audit + bundle: `python3 tools/audit_questions.py && python3 tools/bundle.py`
