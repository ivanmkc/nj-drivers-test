# Driver's Test Practice — Jurisdiction Coverage TODO

## Status Legend
- [x] Complete (questions + translations + sign images)
- [ ] Not started

## US States (50 + DC)

### Complete
- [x] GA — Georgia (DDS, 390 Qs, EN/JA/ES)
- [x] NJ — New Jersey (MVC, 332 Qs, EN/JA/ES)
- [x] NY — New York (DMV, 407 Qs, EN/JA/ES)

### To Do
- [ ] AL — Alabama (DPS)
- [ ] AK — Alaska (DMV)
- [ ] AZ — Arizona (MVD)
- [ ] AR — Arkansas (DFA)
- [ ] CA — California (DMV)
- [ ] CO — Colorado (DMV)
- [ ] CT — Connecticut (DMV)
- [ ] DE — Delaware (DMV)
- [ ] DC — District of Columbia (DMV)
- [ ] FL — Florida (DHSMV)
- [ ] HI — Hawaii (CDL)
- [ ] ID — Idaho (ITD)
- [ ] IL — Illinois (SOS)
- [ ] IN — Indiana (BMV)
- [ ] IA — Iowa (DOT)
- [ ] KS — Kansas (DOR)
- [ ] KY — Kentucky (KYTC)
- [ ] LA — Louisiana (OMV)
- [ ] ME — Maine (BMV)
- [ ] MD — Maryland (MVA)
- [ ] MA — Massachusetts (RMV)
- [ ] MI — Michigan (SOS)
- [ ] MN — Minnesota (DVS)
- [ ] MS — Mississippi (DPS)
- [ ] MO — Missouri (DOR)
- [ ] MT — Montana (MVD)
- [ ] NE — Nebraska (DMV)
- [ ] NV — Nevada (DMV)
- [ ] NH — New Hampshire (DMV)
- [ ] NM — New Mexico (MVD)
- [ ] NC — North Carolina (DMV)
- [ ] ND — North Dakota (DOT)
- [ ] OH — Ohio (BMV)
- [ ] OK — Oklahoma (DPS)
- [ ] OR — Oregon (DMV)
- [ ] PA — Pennsylvania (PennDOT)
- [ ] RI — Rhode Island (DMV)
- [ ] SC — South Carolina (DMV)
- [ ] SD — South Dakota (DPS)
- [ ] TN — Tennessee (DOS)
- [ ] TX — Texas (DPS)
- [ ] UT — Utah (DLD)
- [ ] VT — Vermont (DMV)
- [ ] VA — Virginia (DMV)
- [ ] WA — Washington (DOL)
- [ ] WV — West Virginia (DMV)
- [ ] WI — Wisconsin (DMV)
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
