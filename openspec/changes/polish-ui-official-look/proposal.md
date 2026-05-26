## Why

The app now ships authoritative, source-grounded content for 50 jurisdictions — but the UI doesn't yet communicate that authority. The frontend has zero custom styling (bare Tailwind, no theme tokens, no typographic system), iOS uses named asset colors without a coherent design language, and Android leans on Material-3 defaults. A first-time user can't tell at a glance whether this is a polished study tool grounded in real DMV manuals or a hobbyist quiz app. Coordinated visual polish across iOS, Android, and web will close that gap and make the "official content from real state manuals" story legible the moment the app loads.

## What Changes

- **Design tokens** (palette, typography scale, spacing scale, elevation, radii) defined once per platform and applied consistently. Palette anchored in a civic-trustworthy navy/slate with a warm accent for affordances — readable as DMV-adjacent without copying any specific agency's branding.
- **Typography pass** — switch from system defaults to a paired serif (headings, branding) + humanist sans (body, UI). Establishes the "official document" tone without sacrificing legibility on small screens.
- **Per-screen layout refresh** for all 5 screens (Home, StatePicker, Quiz, Results, Stats) on all 3 platforms. Each screen gets a clearer hierarchy (hero block, supporting content, primary action), generous whitespace, and consistent component variants.
- **Component library polish** — buttons, cards, chips, progress indicators, and the answer-choice control restyled against the new tokens. Sign-image questions get a dedicated, framed presentation so the image reads as authoritative source content rather than inline clip art.
- **Source attribution surface** — every screen that shows a question makes the manual citation visible (state, agency, edition) so the "this comes from the real manual" claim is verifiable from the UI, not buried in metadata.
- **Dark mode** parity (iOS/Android already inherit system; web gets explicit dark tokens).
- **Empty/loading/error states** — replace bare spinners and blank screens with state-aware skeletons and reassuring copy.

Out of scope: marketing site, app-store assets, motion/animation system beyond basic transitions, accessibility audit beyond color-contrast and touch-target minimums (those are correct-by-construction in the tokens).

## Capabilities

### New Capabilities
- `app-visual-theme`: Codifies the design system (palette, type, spacing, elevation, radii) and the per-screen visual requirements (hierarchy, source attribution placement, state handling). One capability, applied consistently to iOS, Android, and web — platform-specific implementations live in `ios/.../theme/`, `android/.../theme/`, `frontend/src/`.

### Modified Capabilities
<!-- None — no existing spec captures UI behavior today. -->

## Impact

- **Frontend (web)**: `frontend/src/{index.css,App.tsx,components/*.tsx}` — Tailwind config gains design tokens; every component gets restyled. Adds 2 web fonts (self-hosted, ~80KB woff2 total). No new JS dependencies.
- **iOS**: `ios/DriversTest/DriversTest/theme/Theme.swift` (expanded), `view/components/Components.swift` (variants), `view/screen/*.swift` (layout polish). Asset catalog gains new color sets and an updated app icon. No new SwiftPM dependencies.
- **Android**: `android/app/src/main/java/com/drivers/test/theme/Theme.kt` (expanded with full Material 3 color scheme + typography), `view/components/Components.kt`, `view/screen/*.kt`. Adds Material 3 typography artifact (already on classpath). No new Gradle dependencies.
- **No data/bundle changes** — `data/states/` and the bundle compilation are untouched. State count, question count, audit results: all unchanged.
- **CI**: existing lint/test/build pipelines unchanged; visual diffs will be human-reviewed.
- **Risk**: visual taste is subjective. Mitigation: document the design rationale in `design.md` and check in low-fi mockups so the user can redirect before per-screen implementation. Per-platform PRs can be reverted independently if one lands poorly.
