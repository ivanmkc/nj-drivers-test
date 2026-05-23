# Driver's Test Practice — Jurisdiction Coverage TODO

## Status Legend
- [x] Complete (questions + translations + sign images)
- [ ] Not started

## US States (50 + DC) — 31 / 51 complete

### Complete (31)
- [x] AL — Alabama (ALEA, 292 Qs, EN/ES)
- [x] AR — Arkansas (ASP, 296 Qs, EN/ES)
- [x] AZ — Arizona (MVD, 295 Qs, EN/ES)
- [x] CA — California (DMV, 284 Qs, EN/ES/JA)
- [x] CO — Colorado (DMV, 255 Qs, EN/ES)
- [x] CT — Connecticut (DMV, 364 Qs, EN/ES)
- [x] FL — Florida (DHSMV, 345 Qs, EN/ES/JA)
- [x] GA — Georgia (DDS, 390 Qs, EN/ES/JA)
- [x] IA — Iowa (DOT, 237 Qs, EN/ES/JA)
- [x] IL — Illinois (SOS, 413 Qs, EN/ES)
- [x] IN — Indiana (BMV, 346 Qs, EN/ES/JA)
- [x] KS — Kansas (DOR, 468 Qs, EN/ES/JA)
- [x] KY — Kentucky (KYTC, 357 Qs, EN/ES)
- [x] MA — Massachusetts (RMV, 456 Qs, EN/ES)
- [x] MD — Maryland (MVA, 202 Qs, EN/ES/JA)
- [x] MI — Michigan (SOS, 350 Qs, EN/ES)
- [x] MN — Minnesota (DVS, 383 Qs, EN/ES)
- [x] MO — Missouri (DOR, 394 Qs, EN/ES/JA)
- [x] NC — North Carolina (DMV, 376 Qs, EN/ES/JA)
- [x] NJ — New Jersey (MVC, 307 Qs, EN/ES/JA)
- [x] NV — Nevada (DMV, 346 Qs, EN/ES)
- [x] NY — New York (DMV, 391 Qs, EN/ES/JA)
- [x] OH — Ohio (BMV, 280 Qs, EN/ES)
- [x] OR — Oregon (DMV, 284 Qs, EN/ES/JA)
- [x] PA — Pennsylvania (PennDOT, 507 Qs, EN/ES/JA)
- [x] SC — South Carolina (DMV, 281 Qs, EN/ES)
- [x] TN — Tennessee (DOS, 874 Qs, EN/ES/JA)
- [x] TX — Texas (DPS, 417 Qs, EN/ES/JA)
- [x] UT — Utah (DLD, 427 Qs, EN/ES)
- [x] VA — Virginia (DMV, 279 Qs, EN/ES/JA)
- [x] WA — Washington (DOL, 376 Qs, EN/ES/JA)
- [x] WI — Wisconsin (DMV, 321 Qs, EN/ES/JA)

### To Do (20)
- [ ] AK — Alaska (DMV)
- [ ] DE — Delaware (DMV)
- [ ] DC — District of Columbia (DMV)
- [ ] HI — Hawaii (CDL)
- [ ] ID — Idaho (ITD)
- [ ] LA — Louisiana (OMV)
- [ ] ME — Maine (BMV)
- [ ] MS — Mississippi (DPS)
- [ ] MT — Montana (MVD)
- [ ] NE — Nebraska (DMV)
- [ ] NH — New Hampshire (DMV)
- [ ] NM — New Mexico (MVD)
- [ ] ND — North Dakota (DOT)
- [ ] OK — Oklahoma (DPS)
- [ ] RI — Rhode Island (DMV)
- [ ] SD — South Dakota (DPS)
- [ ] VT — Vermont (DMV)
- [ ] WV — West Virginia (DMV)
- [ ] WY — Wyoming (DOT)

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
2. Download and extract text (`extract_signs.py` for images, PyMuPDF for text)
3. Create `states/<code>/config.json` with name, agency, passing %, test count
4. Generate questions: `python generate_questions.py <code> <manual_text_file>`
5. Add sign questions: `python add_sign_questions.py <code>`
6. Translate: `python translate.py <code> ja && python translate.py <code> es`
7. Verify with app test client
