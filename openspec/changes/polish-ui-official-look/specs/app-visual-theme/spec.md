## ADDED Requirements

### Requirement: Design tokens are codified per platform and semantically identical across platforms

Each platform SHALL define a tokens module that encodes the documented palette (primary navy, surface neutrals on slate, success, error, warning, brass accent), typography pairing (IBM Plex Serif for display, Inter for body, with weights 400/500/600/700), spacing on a 4pt grid (`xs/sm/md/lg/xl/2xl/3xl` = `4/8/12/16/24/32/48`), radii (`none/sm/md/lg/pill` = `0/4/8/12/999`), and elevation (one `card` shadow per platform). Token names and semantic meanings SHALL be identical across iOS, Android, and web; only the platform-native implementation differs.

#### Scenario: Tokens exist in all three platform theme modules
- **WHEN** a reviewer inspects `ios/DriversTest/DriversTest/theme/`, `android/app/src/main/java/com/drivers/test/theme/`, and `frontend/src/`
- **THEN** each platform exposes the same set of named tokens (e.g., `color.primary`, `spacing.md`, `font.display`, `radius.lg`) with matching semantic values

#### Scenario: A renamed token cascades across platforms
- **WHEN** a future maintainer renames or repurposes a token
- **THEN** the change SHALL be applied to all three platforms in the same PR; partial application across platforms is a regression

### Requirement: Color palette satisfies WCAG AA contrast for body text on surface backgrounds

For every defined text-on-surface color pair in light and dark mode, the contrast ratio SHALL be at least 4.5:1 for body text (14pt+ regular) and 3:1 for large text (18pt+ or 14pt+ bold), as measured by WCAG 2.1 contrast formula.

#### Scenario: Body text on light surface
- **WHEN** the reviewer measures `color.text.primary` against `color.surface.light` with a contrast tool
- **THEN** the ratio is ≥ 4.5:1

#### Scenario: Body text on dark surface
- **WHEN** the reviewer measures `color.text.primary` against `color.surface.dark`
- **THEN** the ratio is ≥ 4.5:1

### Requirement: Typography uses IBM Plex Serif for display and Inter for body, self-hosted on each platform

The display typeface SHALL be IBM Plex Serif (weights 500, 600). The body/UI typeface SHALL be Inter (weights 400, 500, 600, 700). Fonts SHALL be self-hosted on each platform — bundled into the app for iOS/Android, served from `frontend/public/fonts/` (preloaded) for web. No reliance on remote CDNs at runtime.

#### Scenario: Web preloads critical fonts and uses font-display: swap
- **WHEN** a reviewer inspects the rendered `index.html` and the `@font-face` declarations
- **THEN** Inter 400/600 are preloaded via `<link rel="preload">`, every `@font-face` uses `font-display: swap`, and no Google Fonts URL is referenced

#### Scenario: iOS registers fonts via Info.plist
- **WHEN** a reviewer inspects `Info.plist` for the iOS app
- **THEN** `UIAppFonts` lists the IBM Plex Serif and Inter font files, and the Theme module references them with stable names

#### Scenario: Android loads fonts from res/font/
- **WHEN** a reviewer inspects `android/app/src/main/res/font/` and the Theme module
- **THEN** the IBM Plex Serif and Inter weights are present as `.ttf` files and the Compose `Typography` exposes them via a `FontFamily`

### Requirement: Every question-detail surface shows the source citation in dedicated chrome

Whenever a user views a question (during a quiz, or in a results review), the surface SHALL display a `SourceCitation` component containing at minimum: the state agency name, the manual edition, and the page/section reference if available. The citation SHALL be rendered in the brass-accented chrome distinct from body text, and SHALL be visible without scrolling on a 375pt-wide screen.

#### Scenario: Citation visible on quiz question
- **WHEN** a user is on the QuizScreen viewing a question on any platform
- **THEN** the SourceCitation is rendered in the screen header or immediately below the question text, visible above the fold on iPhone SE (375pt) without scrolling

#### Scenario: Citation visible on results review
- **WHEN** a user opens a question's detail from the ResultsScreen
- **THEN** the same SourceCitation component is rendered with the same content fields

#### Scenario: Citation distinct from body text
- **WHEN** a reviewer inspects the SourceCitation rendering against the body text of the question
- **THEN** the citation uses the brass accent token, a smaller type size, and is visually grouped (e.g., framed chip, underlined block, or sidebar) — clearly not part of the question prose

### Requirement: All 5 user-facing screens follow the same visual hierarchy convention

Home, StatePicker, Quiz, Results, and Stats screens SHALL each present content in a three-tier hierarchy: a hero block (page identity + key context), supporting content (the screen's main interaction or data), and a primary action affordance. Tier 1 uses display typography; tier 2 uses body typography with section headers; tier 3 uses the primary button variant.

#### Scenario: A user navigates between screens and perceives a consistent layout language
- **WHEN** the user flows Home → StatePicker → Quiz → Results → Stats
- **THEN** each screen's hero/supporting/action structure is visually parseable in the same regions; the user does not need to relearn the layout

#### Scenario: Primary action uses the documented button variant
- **WHEN** a reviewer inspects the primary CTA on each of the 5 screens on each of the 3 platforms
- **THEN** all CTAs render using the same `Button(variant: .primary)` / equivalent — same color, radius, padding, and label typography

### Requirement: Loading, empty, and error states have first-class visual treatments

Every screen SHALL render distinct visual treatments for loading (skeleton placeholders matching the eventual content shape, NOT a bare spinner), empty (illustration or muted icon + explanatory copy + remediation action), and error (clear error message + retry affordance + support path). The bare full-screen spinner currently in `LoadingScreen.tsx` SHALL be replaced.

#### Scenario: Bundle still loading
- **WHEN** the app starts and the question bundle has not yet loaded
- **THEN** the user sees a skeleton mimicking the Home screen layout, NOT a centered spinner alone

#### Scenario: User selects a state with no questions in their language
- **WHEN** the user lands on QuizScreen for a state/language combo with zero questions
- **THEN** the user sees the empty-state treatment (icon + copy explaining the gap + action to switch language or state), not a blank screen

#### Scenario: API/asset fetch fails
- **WHEN** an asset (sign image, bundle) fails to load
- **THEN** the user sees a labeled error UI with a retry button, not a silent failure or a JS console error

### Requirement: Dark mode is supported on all three platforms

The theme module SHALL define light and dark variants for every color token. iOS and Android SHALL follow the system appearance setting automatically. Web SHALL expose a `prefers-color-scheme` media query default plus a user-toggleable override stored in `localStorage`.

#### Scenario: System dark mode applied to native apps
- **WHEN** the user sets their device to dark mode and opens the iOS or Android app
- **THEN** the app renders in dark variant without any in-app toggle being touched

#### Scenario: Web respects system preference
- **WHEN** a user with `prefers-color-scheme: dark` loads the web app for the first time
- **THEN** the dark variant is applied on first paint, no flash of light theme

#### Scenario: Web toggle persists across sessions
- **WHEN** a user toggles the web app to dark mode and reloads
- **THEN** the dark variant is applied on reload, before the first paint of content
