# CLAUDE.md

Multi-platform offline driver's test practice app (iOS, Android, Web). Questions are generated from official state driver manuals using Gemini, compiled into a single gzipped JSON bundle, and shipped to all platforms.

## Architecture

```
data/states/<code>/          # Source of truth (YAML + config.json)
    -> tools/bundle.py       # Compiles to gzipped JSON
    -> shared/               # Bundle artifact (gitignored)
    -> ios/Resources/         # Copied to each platform (gitignored)
    -> android/assets/
    -> frontend/public/
```

All generated/compiled files are gitignored and rebuilt from `data/` on every build. Never commit bundle artifacts or sign images under app directories.

## Key Commands

```bash
# Python tooling
pip install -r requirements.txt -r requirements-dev.txt
ruff check . && ruff format --check . && pyright   # Lint + type check
python3 tools/bundle.py                             # Rebuild bundle for all platforms
python3 tools/audit_questions.py                    # Validate all question data

# Add a new state (full pipeline)
python3 tools/setup_state.py <code> <name> <agency> <pass_pct> <test_count> <manual_url>
python3 tools/generate_questions.py <code> data/states/<code>/manual.txt
python3 tools/add_sign_questions.py <code>
python3 tools/translate.py <code> es
python3 tools/translate.py <code> ja

# Web (Flask)
cd web && python3 app.py                            # localhost:8080

# Frontend (React/Vite)
cd frontend && npm install && npm run dev
npm run lint && npm run format:check                # ESLint + Prettier

# iOS
open ios/DriversTest/DriversTest.xcodeproj          # Build in Xcode (Cmd+R)
cd ios && swiftlint                                 # Lint Swift code

# Android
cd android && ./gradlew assembleDebug               # Build APK
cd android && ./gradlew ktlintCheck                 # Lint Kotlin code
```

## Critical Rules

- **All questions must be grounded in official state driver manuals.** Never generate questions from LLM knowledge alone. Every state's `config.json` must include a real `manual_url`.
- **YAML is the source format; JSON/gzip is compiled.** Edit questions in `data/states/<code>/questions_<lang>.yaml`, then run `bundle.py`. Never edit bundle files directly.
- **English (en) is always required.** Spanish (es) and Japanese (ja) translations are optional. Translations are generated via Gemini, not hand-written.
- **Bundle rebuilds on every app build.** iOS (Xcode run script phase), Android (Gradle `bundleQuestions` task), and CI all run `bundle.py` automatically.
- **Python scripts run from the repo root.** Always `python3 tools/<script>.py`, not `cd tools && python3 script.py`.

## Code Style

### Python (ruff + pyright)
- Python 3.10+, line length 99
- Rules: E, F, W, I (isort), UP (pyupgrade), B (bugbear)
- Pyright basic mode — fix real type errors, don't over-annotate
- Use `if x is None: raise ValueError(...)` for null checks, not `assert`
- Shared utilities go in `tools/_util.py`

### Frontend (ESLint + Prettier)
- React 19, TypeScript strict, Vite, Tailwind CSS
- Single quotes, semicolons, trailing commas, 100-char width
- Derive state when possible — don't store values computable from other state
- Check `response.ok` before parsing fetch responses
- Wrap custom hook returns in `useMemo` for reference stability

### iOS (SwiftLint)
- SwiftUI, MVVM, iOS 15+
- Use `@StateObject` for objects created inline, `@ObservedObject` only for injected objects
- Cache expensive computed properties (especially UserDefaults/disk reads) — don't deserialize in SwiftUI `body`
- `private` by default for ViewModel internals not needed by views

### Android (ktlint)
- Jetpack Compose, Kotlin 1.9+, Material 3
- Use `LaunchedEffect` for fire-and-forget effects, `DisposableEffect` only when cleanup is needed
- Compose functions use PascalCase (ktlint `function-naming` rule disabled)
- Wildcard imports are allowed for Compose (`no-wildcard-imports` disabled)
- Cache store reads — don't deserialize from SharedPreferences in composition

## Data Format

```yaml
# data/states/<code>/questions_en.yaml
metadata:
  source: "Official Manual Name"
  total_questions: 307
  categories: [license_system, safe_driving_rules, ...]
questions:
  - id: 1
    category: "safe_driving_rules"
    question: "What should you do at a red light?"
    choices:
      A: "Speed up"
      B: "Stop"
      C: "Honk"
      D: "Reverse"
    answer: "B"
    explanation: "You must stop at a red light. (Ch. 4, p. 32)"
    image: "stop_sign.png"  # Optional, for sign questions
```

Valid categories: `license_system`, `driver_testing`, `driver_responsibility`, `safe_driving_rules`, `defensive_driving`, `alcohol_drugs_health`, `penalties_and_points`, `sharing_the_road`, `vehicle_information`, `signs_and_signals`

## Environment

- **Gemini API**: Scripts use Vertex AI (`genai.Client(vertexai=True, project="adk-coding-agents", location="global")`). Requires Google Cloud auth (application default credentials).
- **Docker**: `docker build . && docker run -p 8080:8080` — bundles data at build time, serves via Gunicorn.
- **GitHub Pages**: Frontend deploys to `docs/` with base path `/nj-drivers-test/`.

## Gotchas

- `shared/`, `ios/.../Resources/`, `android/.../assets/`, `frontend/public/questions_bundle.json` are all gitignored build artifacts. If they're missing, run `bundle.py`.
- iOS and Android apps have identical architecture (model/repository/viewmodel/view/theme). Changes to one platform usually need mirroring on the other.
- Sign images live in `data/signs/` (shared MUTCD signs) and are copied to each platform by `bundle.py`.
- The web Flask app (`web/app.py`) loads the bundle into memory once at import time. If the bundle file doesn't exist, the import crashes.
- `tools/translate.py` skips failed batches rather than inserting untranslated English. Check output for skip warnings.
