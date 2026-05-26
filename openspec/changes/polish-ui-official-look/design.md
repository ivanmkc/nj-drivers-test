## Context

The app ships on three platforms with parallel architecture (model/repository/viewmodel/view/theme). Each platform has a `theme/` module and a shared `view/components/` layer, but the existing theme files are skeletal:

- **iOS** (`Theme.swift`): 9 named asset colors + 2 system-derived surface colors. No type scale. No spacing scale. No elevation.
- **Android** (`Theme.kt`): default Material 3 scheme. No custom palette, typography, or shape system.
- **Web** (`index.css`): bare Tailwind directives + one spinner keyframe. No tokens, no font loading.

Per-screen layouts use platform-native primitives directly (SwiftUI `VStack`, Compose `Column`, JSX `div`) with ad-hoc Tailwind utility classes on the web. There is no shared visual vocabulary, no documented hierarchy rules, no source-attribution component.

This change introduces a real design system without rewriting any business logic. ViewModels, repositories, and the question-bank model are out of scope.

## Goals / Non-Goals

**Goals:**
- A documented design-token vocabulary (palette, type, spacing, elevation, radii) that is identical in semantic meaning across platforms and translated into each platform's native idiom.
- Visual coherence across screens — a user who sees Home, then Quiz, then Results should perceive them as the same app.
- "Official content" legibility — the manual citation is present and visible on every question, every results screen, and the home/state-picker screens.
- Per-platform parity for the 5 user-facing screens (Home, StatePicker, Quiz, Results, Stats).
- Dark mode on all three platforms.

**Non-Goals:**
- New screens, new flows, or new features. No flashcards, no SRS, no new study modes.
- Marketing site or app-store assets.
- Animation/motion system beyond CSS/SwiftUI/Compose transitions that already exist.
- Full accessibility audit (WCAG AAA, screen-reader QA). Color-contrast AA and 44pt/48dp touch targets ARE in scope — they fall out of the token choices and don't require separate work.
- Custom illustration. Sign images stay as-is (MUTCD PNGs in `data/signs/`).
- Server-side / backend changes.

## Decisions

### D1: Palette anchored in navy + slate, not in any state's brand

**Decision:** Primary `#1E3A5F` (navy), surface neutrals on a warm slate (`#F8FAFC` light / `#0F172A` dark), success `#15803D`, error `#B91C1C`, warning `#B45309`, accent `#C5A572` (muted brass for highlights and citation chrome).

**Why:** "Civic / DMV-official" reads through palette and typography more than through layout. Navy + slate + a touch of brass is the visual shorthand for government documents (US passport interior, IRS forms, NHTSA reports) without imitating any single state agency. Avoiding a state-specific palette is important because the app ships 50 jurisdictions — if it looked like California's DMV, NJ users would distrust it.

**Alternatives considered:** (a) Per-state theming where the app adopts the user's jurisdiction's colors. Rejected: massive token surface, inconsistent app feel, would require licensing/IP review per state. (b) Pure neutral monochrome (Linear-style). Rejected: too startup-y for the "official document" goal.

### D2: Type pairing — IBM Plex Serif (display) + Inter (body)

**Decision:** Headings, section titles, and the source-citation chrome use IBM Plex Serif. Body text, button labels, choice text, and UI affordances use Inter.

**Why:** IBM Plex Serif is an open-license slab serif designed for technical/government communication (the "official document" tone). Inter is the de-facto modern UI sans with excellent screen rendering and full weight range. Both are free, self-hostable, well-supported on iOS (system font registration), Android (Compose fontFamily), and web (preloaded woff2). Pairing serif + sans is the conventional "publication" rhythm — newspapers, scientific journals, government reports all use this combination.

**Alternatives considered:** (a) System fonts only (San Francisco / Roboto / system-ui). Rejected: maximally generic; no "official" cue. (b) Single-typeface (Inter or Plex throughout). Rejected: loses the publication-style hierarchy cue. (c) A more decorative serif (e.g., Source Serif, Charter). Rejected: less suited to small UI elements like citation chips.

### D3: Spacing + radii on a 4pt grid with consistent radii

**Decision:** Spacing tokens `xs=4`, `sm=8`, `md=12`, `lg=16`, `xl=24`, `2xl=32`, `3xl=48`. Radii `none=0`, `sm=4`, `md=8`, `lg=12`, `pill=999`. Card elevation as a single `card` shadow per platform (system idiom on each).

**Why:** A 4pt grid is the industry-default that maps cleanly to both Apple HIG (4pt) and Material 3 (4dp). Consistent radii kill the "designed by accident" feel.

### D4: Source-attribution component is its own token-level primitive

**Decision:** A new `SourceCitation` / `<SourceCitation>` component is added to each platform's `Components` layer. It renders the manual edition + agency + page reference in the brass-accented chrome, present on every question detail view and Results screen header. Tokens specify minimum density (font size, padding) so the citation is always visible but never dominant.

**Why:** This is the single highest-value UI change for communicating "this content is grounded in real source material." Currently citations are only in the `explanation` text after answering. Surfacing them up front, in a visually-distinct chrome, makes the trust-claim verifiable in <1s of viewing.

**Alternatives considered:** (a) Citation only in explanation post-answer. Rejected: hides the trust signal until after the user commits an answer. (b) Citation in a dedicated tab. Rejected: extra tap, low discoverability.

### D5: One capability spec, three platform implementations

**Decision:** A single capability `app-visual-theme` owns the design-token vocabulary and per-screen visual requirements. Each platform's spec compliance is verified through manual review against documented mockups in `design.md`, not automated visual regression.

**Why:** A single spec keeps the three platforms semantically aligned (e.g., "the SourceCitation appears in the header of every QuestionDetail screen" applies to all three). Visual regression testing for native + web simultaneously is heavy infrastructure that's not justified for a one-time refresh.

**Alternatives considered:** Three platform-specific specs. Rejected: triplicates the requirement language, creates drift risk.

### D6: Phased rollout, one platform per PR

**Decision:** Implementation lands as three sequential PRs (web first, then iOS, then Android). Tokens are codified before any screen work begins.

**Why:** Web is the fastest to iterate visually (hot-reload, no build cycles), so it serves as the design-validation surface — the user can preview the look in a browser and redirect before native work locks in. iOS and Android then mirror the validated design with platform-idiom adaptations.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| Visual taste is subjective — user dislikes the chosen aesthetic | Web ships first; user previews and can redirect before native work. Each platform is its own PR, independently revertible. |
| Web-font loading regressions (FOUT, layout shift) | Preload critical weights, use `font-display: swap`, declare `size-adjust` to minimize CLS. Limit to 2 typefaces. |
| Self-hosted fonts add ~80KB to web bundle | Acceptable; bundle is already 5.4MB gzipped. Worst case strip to a single typeface. |
| iOS native font registration is platform-specific quirky | Use `Info.plist` UIAppFonts entry; verified working pattern. Fall back to `.system(.serif)` on registration failure. |
| Android Compose font loading from `res/font/` is straightforward but adds APK size | Acceptable trade for visual coherence. Subset the fonts to Latin + ES diacritics. |
| Per-platform implementations drift over time | The spec captures the intent (palette tokens, citation placement, screen hierarchy) so future contributors have a single source of truth for "what the design wants." |
| Sign images may visually clash with the new framing | Frame component has a configurable background; can be tuned per-state if needed. Most signs read fine on a slate background since MUTCD signs are designed for high-contrast outdoor visibility. |

## Migration Plan

No data migration. No code-incompatible breaking change. Each platform's PR can ship and revert independently. Frontend changes are pure CSS/JSX restyle; iOS and Android changes are theme + view layer only.

Rollout sequence:
1. PR #1 — tokens module (all three platforms) + web restyle of all 5 screens. User reviews live in browser.
2. PR #2 — iOS restyle of all 5 screens, mirroring the validated web design.
3. PR #3 — Android restyle of all 5 screens.

## Open Questions

- **Brand mark**: should the app have a wordmark/logo? Currently the home screen reads "Driver's Test Prep" in default type. A simple wordmark in IBM Plex Serif might be enough; a custom mark is out of scope for this change. Default: ship with the wordmark only, defer custom mark.
- **Web/native parity for the citation chip**: Material 3 has its own chip metaphor; should Android use M3's `AssistChip` or a custom `SourceCitation` to match iOS/web exactly? Default: custom component everywhere for visual parity.
- **App icon**: refresh in scope? Currently each platform uses a default. Default: out of scope for this change (asset production is separate work); flag for a follow-up.
