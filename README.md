# Driver's Test Practice

Multi-platform practice quiz app for US state driver's license exams. Supports iOS, Android, and web. All question data is bundled offline — no server required for mobile apps.

## Project Structure

```
drivers/
├── data/                    # Question data (source of truth)
│   ├── states/
│   │   ├── nj/
│   │   │   ├── config.json          # State metadata (name, agency, passing score)
│   │   │   ├── questions_en.yaml    # English questions
│   │   │   ├── questions_es.yaml    # Spanish questions
│   │   │   └── questions_ja.yaml    # Japanese questions
│   │   ├── ny/ ...
│   │   └── ca/ ...
│   └── signs/               # MUTCD road sign images (PNG)
│
├── tools/                   # Build and content scripts
│   ├── bundle.py                # Builds gzipped JSON bundle, copies to apps
│   ├── generate_questions.py    # Generate questions from manual text (Gemini)
│   ├── generate_questions_from_knowledge.py
│   ├── translate.py             # Translate questions to other languages
│   ├── setup_state.py           # Scaffold a new state directory
│   ├── setup_state_from_knowledge.py
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
    ├── ios.yml
    └── android.yml
```

## Data Flow

Questions live in `data/states/*/questions_*.yaml`. When you add or change questions:

```bash
python3 tools/bundle.py
```

This reads all YAML/config files, builds a gzipped JSON bundle (~1.3 MB), and copies it plus sign images to both `ios/.../Resources/` and `android/.../assets/`.

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

```bash
python3 tools/setup_state.py <code> <name> <agency> <pass_pct> <test_count> <manual_url>
python3 tools/generate_questions.py <code> <manual_text_file>
python3 tools/translate.py <code> ja
python3 tools/translate.py <code> es
python3 tools/bundle.py
```
