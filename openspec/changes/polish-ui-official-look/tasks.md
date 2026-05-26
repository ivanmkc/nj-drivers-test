## 1. Design tokens — establish vocabulary first

- [ ] 1.1 Document the canonical token table (palette, type pairing, spacing, radii, elevation) in `design.md` (already drafted) — confirm hex values, contrast ratios pass WCAG AA.
- [ ] 1.2 Author IBM Plex Serif + Inter font subsets (Latin + ES diacritics) and check into `frontend/public/fonts/`, `ios/DriversTest/DriversTest/Resources/Fonts/`, `android/app/src/main/res/font/`. Verify total per-platform footprint is under ~120KB.
- [ ] 1.3 Web: extend `tailwind.config.js` (or `tailwind.config.ts`) with the documented token names — `colors.primary`, `spacing.xs..3xl`, `borderRadius.sm..pill`, `fontFamily.display/body`, `boxShadow.card`.
- [ ] 1.4 Web: register `@font-face` rules in `index.css` with `font-display: swap`; add `<link rel="preload">` for Inter 400/600 in `index.html`.
- [ ] 1.5 iOS: expand `theme/Theme.swift` with the full token set (color, font, spacing, radius, shadow). Add asset-catalog color sets for every named color with light/dark variants. Register fonts via `Info.plist` `UIAppFonts`.
- [ ] 1.6 Android: rewrite `theme/Theme.kt` to define a complete Material 3 `ColorScheme` (light + dark), a `Typography` referencing the bundled fonts via `FontFamily`, a custom `Shapes` set, and an extension `LocalAppSpacing` for spacing tokens. Wire into `MaterialTheme { ... }` in `AppRoot.kt`.

## 2. SourceCitation component — implement once per platform, reused everywhere

- [ ] 2.1 Web: add `frontend/src/components/SourceCitation.tsx` rendering `{state, agency, edition, page?}` in the brass-chrome chip variant. Snapshot test the dark + light variants.
- [ ] 2.2 iOS: add a `SourceCitation` view to `view/components/Components.swift` with the same props/contract.
- [ ] 2.3 Android: add a `SourceCitation` composable to `view/components/Components.kt`.
- [ ] 2.4 All three: write the component to accept missing fields gracefully (no page → omit the page chip; no agency → fall back to "Official Manual").

## 3. Component library polish (buttons, cards, inputs)

- [ ] 3.1 Web: rebuild primary/secondary/ghost button variants, card, chip, answer-choice control against the new tokens. Update every existing usage in `components/*.tsx`.
- [ ] 3.2 iOS: extend `Components.swift` with the same variants. Update screen call sites.
- [ ] 3.3 Android: same in `Components.kt`. Update screen call sites.

## 4. Per-screen restyle — Web first (acts as design preview)

- [ ] 4.1 `StartScreen.tsx` → hero block with serif wordmark + civic tagline + state-picker CTA. SourceCitation shown beneath state preview.
- [ ] 4.2 `StatePicker.tsx` → restyled search field, alphabetically grouped state cards with agency badge.
- [ ] 4.3 `QuizScreen.tsx` → header with progress + SourceCitation chip, question in display serif, choices as touch-target-sized cards.
- [ ] 4.4 `ResultsScreen.tsx` → score hero block with serif numerals, citation-grouped review list, primary CTA "Study weak topics" (links back into a filtered Quiz).
- [ ] 4.5 `StatsScreen.tsx` → cards for streak / accuracy / sessions, with type hierarchy aligned to the new scale.
- [ ] 4.6 `LoadingScreen.tsx` → skeleton matching StartScreen layout, NOT a centered spinner.
- [ ] 4.7 `LangBar.tsx` → toggle styled as a pill with selected-state chrome.

## 5. Web — empty / error states

- [ ] 5.1 Add an `EmptyState` component (icon + copy + action). Use on QuizScreen when language has zero questions for the selected state.
- [ ] 5.2 Add an `ErrorState` component (icon + message + retry button). Wire into bundle-load failures and sign-image failures.

## 6. Web — dark mode

- [ ] 6.1 Wire `prefers-color-scheme: dark` defaulting in tailwind config + an explicit `data-theme` attribute on `<html>` for user override.
- [ ] 6.2 Add a small dark-mode toggle to `LangBar` (or app header), persist choice to `localStorage`, apply pre-paint via inline script in `index.html` to avoid FOUC.

## 7. Web — review checkpoint

- [ ] 7.1 Open PR, deploy to GitHub Pages preview, screenshot all 5 screens light + dark. User reviews; redirect or proceed.
- [ ] 7.2 Run `npm run lint && npm run format:check`. Confirm no console errors in dev or built bundle.

## 8. iOS — restyle, mirroring validated web design

- [ ] 8.1 `HomeScreen.swift` → hero block + state CTA pattern.
- [ ] 8.2 `StatePickerScreen.swift` → searchable list + agency badge.
- [ ] 8.3 `QuizScreen.swift` → header progress + SourceCitation + display-serif question + card choices.
- [ ] 8.4 `ResultsScreen.swift` → hero score block + citation-grouped review.
- [ ] 8.5 `StatsScreen.swift` → metric cards on new type scale.
- [ ] 8.6 `Components.swift` → primary/secondary buttons, cards, chips applied. Skeleton loading view added.
- [ ] 8.7 Verify dark mode renders correctly (System → Settings → Appearance → Dark).
- [ ] 8.8 Run `swiftlint` clean. Build + run in Xcode simulator (iPhone 15 and iPhone SE) — screenshot all 5 screens light + dark.

## 9. Android — restyle, mirroring validated web design

- [ ] 9.1 `HomeScreen.kt` → hero block + CTA.
- [ ] 9.2 `StatePickerScreen.kt` → searchable list + agency badge.
- [ ] 9.3 `QuizScreen.kt` → header progress + SourceCitation + display-serif question + card choices.
- [ ] 9.4 `ResultsScreen.kt` → hero score block + citation-grouped review.
- [ ] 9.5 `StatsScreen.kt` → metric cards on new type scale.
- [ ] 9.6 `Components.kt` → variants applied. Skeleton loading composable added.
- [ ] 9.7 Verify dark mode (system toggle).
- [ ] 9.8 Run `./gradlew ktlintCheck` clean. Build + run in emulator (Pixel 7 + Pixel 4a for size variety) — screenshot all 5 screens light + dark.

## 10. Cross-platform parity check

- [ ] 10.1 Side-by-side screenshot grid (web/iOS/Android × 5 screens × light/dark = 30 screenshots) attached to the third PR's description.
- [ ] 10.2 Reviewer spot-checks: SourceCitation present on every QuizScreen and ResultsScreen review row; primary CTA visually identical across platforms; type hierarchy consistent.
- [ ] 10.3 Confirm no behavior regressions: select a state, run a full quiz, hit submit, view results — on each platform.

## 11. Docs + release notes

- [ ] 11.1 Add a `docs/design-system.md` (or extend `CLAUDE.md`) with the token table, font usage rules, and component-variant cheat sheet so future contributors don't reintroduce ad-hoc styles.
- [ ] 11.2 PR descriptions reference this change and link to the design.md decisions for context.
