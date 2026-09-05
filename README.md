# Driver's Test Practice

Multi-platform practice quiz app for US state driver's license exams. Supports iOS, Android, and web. All question data is bundled offline — no server required for mobile apps.

## Project Structure

```
drivers/
├── data/                    # Question data (source of truth)
│   ├── states/              # 51 US jurisdictions (50 states + DC)
│   │   ├── nj/
│   │   │   ├── config.json          # State metadata (name, agency, passing score)
│   │   │   ├── questions_en.yaml    # English questions
│   │   │   └── questions_es.yaml    # Spanish questions
│   │   ├── ny/ ...
│   │   └── wy/ ...
│   └── signs/               # MUTCD road sign images (PNG)
│
├── tools/                   # Build and content scripts
│   ├── bundle.py                # Builds gzipped JSON bundle, copies to apps
│   ├── generate_questions.py    # Generate questions from manual text (Gemini)
│   ├── translate.py             # Translate questions to other languages
│   ├── setup_state.py           # Full pipeline: download PDF, extract, generate
│   ├── add_sign_questions.py    # Add sign-identification questions
│   ├── audit_questions.py       # Quality/accuracy audit
│   └── extract_signs.py
│
├── ios/DriversTest/         # iOS app (SwiftUI)
│   └── DriversTest/
│       ├── model/               # Data models
│       ├── repository/          # ApiClient (bundle loader), LocalStore, Localizer
│       ├── viewmodel/           # QuizViewModel
│       ├── view/                # SwiftUI screens and components
│       ├── theme/               # Colors and styling
│       └── Resources/           # Generated at build time (gitignored)
│
├── android/                 # Android app (Jetpack Compose)
│   └── app/src/main/
│       ├── java/.../            # Kotlin source (same architecture as iOS)
│       └── assets/              # Generated at build time (gitignored)
│
├── web/                     # Web app
│   ├── app.py                   # Flask backend
│   └── static/
│       └── index.html
│
└── .github/workflows/       # CI
    ├── android.yml              # Android build
    ├── android-lint.yml         # ktlint for Kotlin
    ├── data-validation.yml      # Question audit + bundle build
    ├── deploy-pages.yml         # GitHub Pages deployment
    ├── frontend-lint.yml        # ESLint + Prettier for React frontend
    ├── ios.yml                  # iOS build
    ├── python-lint.yml          # Ruff + Pyright for Python tooling
    └── verify-manuals.yml       # Monthly manual URL health check
```

## Data Flow

Questions live in `data/states/*/questions_*.yaml`. When you add or change questions:

```bash
python3 tools/bundle.py
```

This reads all YAML/config files, builds a gzipped JSON bundle (~5.4 MB gzipped, ~27 MB decoded), and copies it plus sign images to both `ios/.../Resources/` and `android/.../assets/`. For the web app it also writes a per-state split (`data/index.json` with metadata only, plus `data/states/<code>/<lang>.json` per bank) and the sign images into `frontend/public/`, so the browser only downloads the state it needs.

The bundle step also runs automatically at build time:
- **iOS**: Xcode "Bundle Questions" run script phase (before compilation)
- **Android**: Gradle `bundleQuestions` task (before asset merging)
- **CI**: Explicit step in both workflow files

Generated files (`Resources/`, `assets/`, `shared/`) are gitignored — they're always rebuilt from `data/`.

## Testing on a Device

### Android

Prerequisites: JDK 17+, Android SDK (or Android Studio)

1. Build the debug APK:
   ```bash
   cd android
   ./gradlew assembleDebug
   ```

2. Install on a connected device via USB:
   ```bash
   adb install app/build/outputs/apk/debug/app-debug.apk
   ```

   Or transfer `app/build/outputs/apk/debug/app-debug.apk` to your phone and open it (enable "Install unknown apps" in your phone's settings).

### iOS

Prerequisites: Xcode 15+, Apple ID

1. Open `ios/DriversTest/DriversTest.xcodeproj` in Xcode
2. Add your Apple ID: Xcode > Settings > Accounts
3. Select your connected iPhone as the build target (top bar)
4. Under Signing & Capabilities, set Team to your "Personal Team"
5. Press **Run** (Cmd+R)

The app installs directly on your phone. Free developer signing expires after 7 days — just re-run from Xcode to refresh.

For TestFlight distribution (requires $99/year Apple Developer Program):
1. Set your paid team in Signing & Capabilities
2. Product > Archive, then Distribute App > TestFlight
3. Invite testers via App Store Connect

### Web

```bash
pip install flask pyyaml
cd web
python3 app.py
```

Open http://localhost:8080 in your browser.

## Adding a New State

Every question set **must** be grounded in a real official driver's manual. Never generate questions from LLM knowledge alone.

### Pipeline

1. **Find the official manual** — locate the state's official driver handbook PDF or online manual.
2. **Set up the state** — downloads the PDF and extracts text:
   ```bash
   python3 tools/setup_state.py <code> <name> <agency> <pass_pct> <test_count> <manual_url>
   ```
3. **Generate questions** — uses extracted manual text as Gemini context:
   ```bash
   python3 tools/generate_questions.py <code> data/states/<code>/manual.txt
   ```
4. **Add sign questions** (optional):
   ```bash
   python3 tools/add_sign_questions.py <code>
   ```
5. **Translate** (English is always required; Spanish is high-value):
   ```bash
   python3 tools/translate.py <code> es
   ```
6. **Bundle** — builds the gzipped JSON and copies to iOS/Android:
   ```bash
   python3 tools/bundle.py
   ```

### Quality checks

```bash
python3 tools/audit_questions.py        # Validate all question data
python3 tools/verify_manuals.py         # HEAD-check every catalog URL
pytest tools/                           # Run unit tests for Python tooling
```

For ongoing catalog maintenance — refreshing a stale URL, adding a state,
handling multi-PDF manuals, and interpreting the monthly tracking issue —
see [`docs/maintaining-state-data.md`](docs/maintaining-state-data.md).

### Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Questions about website CSS, chatbots, or page layout | `manual_url` points to an HTML page, not a PDF | Re-point `manual_url` to the actual PDF and regenerate questions |
| Mass unfaithful/hallucinated questions | Generated from LLM knowledge instead of manual text | Verify `manual_text.txt` contains real manual content, regenerate, and run `quiz_gates` to confirm |
| `audit_questions.py` flags stale `en_source_sha256` | EN questions were edited without re-translating | Re-run `translate.py <code> es` (and `ja` if the file exists); provenance stamps update automatically |
| Extracted manual text is garbage (raw PDF bytes, HTML tags) | Content-sniff or extraction failure | Check the cached extraction under `$TMPDIR/drivers_cache_<uid>/`; re-download the PDF if corrupt |
| 403 or connection-reset when downloading a manual | State site blocks cloud/datacenter IPs (known: ilsos.gov, mass.gov) | Use an Internet Archive PDF snapshot and record it as `recovery_url` in the state's `config.json` |
| Repeated single-batch translation failures | Gemini rejects a batch (usually over-long or malformed) | `translate.py` auto-falls-back to per-question translation; check the rescued/skipped ID summary in its output |
| 1-3 judge flags fluctuate between identical `quiz_gates` runs | Normal LLM variance on borderline questions | Grade-A PASS is the bar, not zero flags; thresholds absorb the wobble |
