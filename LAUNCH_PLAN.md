# Launch Plan — Driver's Test Prep v1.0

_Repo review date: 2026-09-05. Reviewed `main` (6f03296), the open PR stack #62 → #63, all open issues and PRs, CI history, and the compiled bundle._

## 1. Verdict

**The data layer is launch-quality; no platform is store-submittable yet.** (At review time `main` was three months behind the real trunk; that was resolved the same day, see Phase 0.)

- 50 of 51 US jurisdictions have question banks (18,125 questions, EN + ES everywhere, legacy JA in 17 states). `audit_questions.py` reports 0 issues. On the #63 branch every state's verification report is grade A / PASS under the v2 gates, including the CA, WA, IL, MA and VA banks that were failing on `main`.
- Almost all app-quality work since May lived in draft PR **#63** (`fix/audit-findings`, 38 commits, 244 files, CI fully green), stacked on **#62**. Before the merge, `main` still had the category-stats bug, synchronous 27 MB bundle decode on the main thread, no dark mode on web, no back handling on Android, and no "why trust this" UI. Both PRs are now on `main`; everything below builds on that.
- Neither mobile app can be uploaded to a store today: no app icon on either platform, no iOS privacy manifest, no signing team, placeholder bundle ID, no Android release signing or AAB, Android targets SDK 34 (Play requires 35), and there is no privacy policy or support URL anywhere.
- The web app is live at `ivanmkc.github.io/nj-drivers-test/` but eagerly fetches and parses the 27 MB uncompressed bundle on every load, has no PWA/offline support, no SEO metadata, no error boundary, and no attribution or privacy page.

Recommended shape: **web soft-launch first** (it is already public; fix the load path and add the legal pages), then **Android and iOS through beta tracks in parallel**, then public store release. With one engineer plus review turnaround this is roughly five to six weeks; the critical path is Phase 0 → Phase 1 → beta.

## 2. Review findings

### 2.1 Repo state

| Area | State on `main` | State on #63 (`fix/audit-findings`) |
|---|---|---|
| Question data | 50/51 states, 0 audit issues; CA/WA grade F, IL/MA/VA unverified | 50/50 PASS grade A (v2 gates, 100% judged, ES translation gate, two-judge audit) |
| Bundle | 26.1 MB JSON / 5.4 MB gz, ~43 s build | same size plus ~0.2 MB trust metadata (evidence excerpts, verification summary, official test languages) |
| Python tooling | ruff / pyright clean; pytest exists but never ran in CI | pytest wired into `python-lint.yml`, 100 tests; new `data-validation.yml` |
| Web frontend | React 19 / Vite / Tailwind, 6 screens, localStorage, no router | dark mode, pushState back nav, Exit control, About-this-test, manual excerpts, category stats fixed, full es/ja/fr strings |
| Flask `web/` | legacy; still what the Dockerfile serves | still legacy, patched for XSS escaping and `response.ok` |
| iOS | SwiftUI, 5 screens, iOS 16 target, no unit tests, UI tests pass vacuously | async bundle decode, store-cache pattern, dark-mode fixes, accessibility labels, hermetic UI-test launch |
| Android | Compose, 5 screens, minSdk 26 / target 34, no unit tests | async decode, BackHandler, cache invalidation, 44 px touch targets |
| CI | 7 workflows; Verify Manual Catalog has failed every month since June | 8 workflows, all green on the PR head |

### 2.2 Branch and PR backlog

- At review time: 45 remote branches, 38 open PRs. Only four carried live work: **#62** (verification rigor, base of the stack), **#63** (everything else), **#61** (URL liveness historization), **#57** (app-store copy and imagery). All four are now merged.
- PRs #16–#49 ("Quality report: <state>", CA/VA/WA re-extracts) were superseded by #63, which regenerated or fixed those banks under stricter gates. All 34 are now closed with a pointer to #63; 31 would have merged cleanly (one markdown report each), 3 conflicted.
- Branch `data/dmv-test-languages` holds the 51-jurisdiction test-language matrix referenced by issue #58 and has never been merged. #63 ships a narrower, manual-evidence-only version (23 states) under `official_test_languages` in each `config.json`.

### 2.3 Store-submission gaps (present on both `main` and #63)

**iOS** (`ios/DriversTest/DriversTest.xcodeproj/project.pbxproj`)
- `AppIcon.appiconset` declares a 1024×1024 slot with no image file. Hard rejection.
- No `PrivacyInfo.xcprivacy`. `UserDefaults` is a required-reason API; App Store Connect rejects uploads without the manifest.
- `DEVELOPMENT_TEAM = ""` and bundle ID `com.drivers.DriversTest` (placeholder). No archive or upload lane in CI.
- `Info.plist` is empty; no `CFBundleDisplayName`, no `ITSAppUsesNonExemptEncryption`, no `CFBundleLocalizations`, so the store listing will not show ES/JA support.
- iPad and landscape are declared (`TARGETED_DEVICE_FAMILY = "1,2"`) but the layout is portrait-phone only. Either validate on iPad or drop it to iPhone-only for v1.
- Version `1.0 (1)` with no bump automation.

**Android** (`android/app/build.gradle.kts`)
- No launcher icon at all (`res/` contains only `themes.xml`), no adaptive icon, no 512×512 store icon.
- `targetSdk = 34`. Google Play requires 35 for new apps and updates since August 2025.
- No `signingConfigs`, no `bundleRelease`, `isMinifyEnabled = false`. CI uploads only a debug APK.
- Theme is bare `android:Theme.Material.Light.NoActionBar`, no `values-night`, no splash theme; app name hardcoded in the manifest instead of `strings.xml`.
- `bundleQuestions` task uses `isIgnoreExitValue = true`, so a machine without `pyyaml` silently ships an empty app.

**Web** (`frontend/`, `.github/workflows/deploy-pages.yml`)
- `App.tsx` fetches `questions_bundle.json` (27 MB uncompressed, all 51 states × all languages) before rendering the state picker. GitHub Pages gzips on the wire, but the browser still parses 27 MB on every load; on a mid-range phone this is several seconds and a real memory spike.
- No service worker, no web manifest, no icons, no favicon. The "offline" promise does not hold on web.
- No `<meta name="description">`, Open Graph tags, `robots.txt`, `sitemap.xml`, or `404.html`. `user-scalable=no` in `index.html` blocks pinch zoom, an accessibility failure.
- No React error boundary; any render throw is a blank page.
- No frontend tests of any kind (no vitest, no Playwright), despite issue #52 planning a Playwright suite.
- The whole `docs/` directory is the Pages artifact, so internal docs (`style-guides/`, `maintaining-state-data.md`, `quality/TEMPLATE.md`) are published publicly. `docs/index.html` is a stale committed Vite artifact.
- `bundle.py` never copies the bundle to `frontend/public/`, so `npm run dev` has no data unless copied by hand (contradicts `CLAUDE.md`).
- `web/` Flask app and the Dockerfile serve the pre-React UI. Decide to delete or explicitly demote it.

**Cross-platform**
- No privacy policy, support page, terms, or "unofficial, not affiliated with any DMV" disclaimer anywhere in-product or hosted.
- No attribution surface for the 50 manual sources (`SOURCES.md`) or the public-domain MUTCD sign images.
- No decision recorded on app name, pricing, or analytics. Recommendation in PR #57: "Driver's Test Prep — Real Manuals", free, no IAP, no analytics.

### 2.4 Content and compliance gaps

- **Issue #58 (test-language permissibility)** is marked launch-blocking and is only partly addressed. #63 marks a language as "official" only when the manual says so and labels the rest "practice only", which is honest and does not invent claims. What is still missing: the 51-state matrix from `data/dmv-test-languages` (with sources and confidence levels), the first-time "study aid only" modal, and per-language stats. Decide whether the #63 behaviour is enough for v1 (recommended) or the full #58 UX is required.
- **DC** has only a provenance stub (Issuu flipbook, no PDF). Ship as "coming soon" in the picker; do not block launch.
- **South Dakota** bank comes from the Dec 2023 edition recovered from the Internet Archive; the DPS site no longer serves a PDF. Disclose the edition in About-this-test (already shipped in #63) and re-check quarterly.
- **Verify Manual Catalog** cron has failed five months running because `gh issue create --label "infra,catalog,monthly"` references labels that do not exist. The last run reported 10 stale URLs and 1 error out of 51; nobody has seen the report because the issue step crashes.
- **Japanese banks** exist for 17 states but JA is out of scope going forward. Either keep them as "legacy, practice only" or hide them for v1 so the store listing does not promise a language you will not maintain.
- **Spanish store copy** in PR #57 is machine-drafted and needs a native-speaker pass before submission.

## 3. Phases

### Phase 0 — Consolidate the trunk (week 1)

Exit criterion: `main` equals the #63 head, CI green on `main`, Pages redeployed from it, backlog pruned.

_Status 2026-09-05: items 1, 2, 4 and 5 done on `main` or this branch. #62, #63, #57 and #61 are merged to `main` (head `1b9edaa`), all workflows green, Pages redeployed. PRs #16–#49 closed as superseded with a comment pointing to #63. The `verify-manuals.yml` label fix, README bundle-size fix, UI-test comment fix, and the `data/dmv_test_languages.json` matrix (Phase 2 item 1) are on branch `claude/repo-review-launch-plan-o0cq6n`. Stale branches are NOT deleted: the session's push proxy refuses deletes (HTTP 403), so run the command in item 3 locally._

1. ~~Review and merge **#62**, then **#63** (retarget to `main` after #62 lands).~~ Done.
2. ~~Merge **#61** (URL liveness history) and **#57** (app-store copy) once rebased on the new `main`.~~ Done; #61 validated locally first (ruff, pyright, 115 pytest cases green on the merged tree).
3. ~~Close PRs #16–#49 as superseded with a one-line comment pointing to #63.~~ Done. Still to do locally (needs a token that can delete refs): the 4 merged heads, the 17 `quality-report-*`, `quality-tn`, `verify-ct-quality`, 15 `worktree-agent-*`, and the 4 `add-*-linting` branches (their PRs #12–#15 were closed unmerged; the lint setup landed on `main` by other commits). Keep `docs/polish-ui-mockups` (issue #56 links to its openspec proposal) and `data/dmv-test-languages` until this branch merges.

   ```bash
   git fetch --prune origin
   git push origin --delete docs/app-store-copy feat/verification-rigor fix/audit-findings \
     $(git branch -r | sed 's|origin/||' | grep -E '^(quality-report-|worktree-agent-|quality-tn|verify-ct-quality|add-.*-linting)')
   ```
4. ~~Fix `verify-manuals.yml`: create the `infra`, `catalog`, `monthly` labels.~~ Done on this branch (idempotent `gh label create` step before the issue step). Still to do: re-run it manually after merge and triage the 10 stale URLs it reports. Note #61 added a second weekly `source-liveness.yml` cron that creates its own `stale-source` label; consider folding the monthly job into it.
5. ~~Update `README.md` bundle size and remove the stale "Flask backend required" comment in `DriversTestUITests`.~~ Done on this branch.

### Phase 1 — Store-readiness engineering (weeks 1–3, parallel tracks)

Exit criterion: a signed release build of each mobile app uploads cleanly to TestFlight and the Play internal track; the web app loads a single state in under one second on a mid-range phone.

**Track A: Identity and assets** (blocks everything else, do first)
- Decide app name, bundle ID / package name, and register the App ID in Apple Developer and the package in Play Console. Suggested: `com.<yourdomain>.driverstest` on both.
- Produce the app icon: one 1024×1024 master, exported to `AppIcon.appiconset`, Android adaptive icon (`mipmap-anydpi-v26` foreground/background) plus legacy densities, 512×512 Play icon, web `favicon.ico`, `apple-touch-icon`, and PWA icons (192, 512, maskable).
- Host the legal pages on the existing Pages site: `/privacy/`, `/support/`, `/about/` (sources and MUTCD attribution, unofficial disclaimer). Because the app stores everything locally and makes no network calls, the privacy policy is short; the store forms still require a URL.

**Track B: iOS**
- Add `PrivacyInfo.xcprivacy` declaring `NSPrivacyAccessedAPICategoryUserDefaults` with reason `CA92.1`, no tracking, no collected data types.
- Set `DEVELOPMENT_TEAM`, real bundle ID, `CFBundleDisplayName`, `ITSAppUsesNonExemptEncryption = NO`, `CFBundleLocalizations` (en, es).
- Decide iPad: either add a real iPad layout pass or set `TARGETED_DEVICE_FAMILY = 1` and lock portrait for v1 (recommended).
- Add a Release lane to `ios.yml`: `xcodebuild archive` + `exportArchive` + upload via App Store Connect API key stored in repo secrets (or Fastlane `pilot`). Bump `CURRENT_PROJECT_VERSION` from the CI run number.
- Add a small XCTest unit target for `QuizViewModel` and `LocalStore` so the vacuous UI tests are not the only coverage.

**Track C: Android**
- `compileSdk`/`targetSdk` → 35 (AGP 8.2 needs an upgrade to 8.6+, Kotlin to 2.x, Compose BOM to a 2025 release; do this in one PR and let CI catch API changes).
- Add a release `signingConfig` reading keystore path and passwords from environment variables, `isMinifyEnabled = true` with `isShrinkResources = true`, and confirm the existing Gson keep rules survive.
- Add `bundleRelease` to `android.yml` behind a tag or manual dispatch, with the keystore in repo secrets, uploading the AAB as an artifact (or straight to the internal track via `r0adkll/upload-google-play`).
- Move the app name to `strings.xml`, add `values-es`, `values-night`, a Material 3 theme, and a splash theme (`androidx.core:core-splashscreen`).
- Make `bundleQuestions` fail the build when `bundle.py` fails.
- Add a `src/test` unit suite for `QuizViewModel` and `LocalStore`.

**Track D: Web**
- Split the bundle at build time: `bundle.py` emits `states/index.json` (metadata only, a few KB) plus `states/<code>/<lang>.json` per state and language. The frontend loads the index, then the selected state on demand. This is the single biggest user-facing fix and it also unblocks a PWA that can precache the chosen state.
- Add a web manifest and a service worker (Vite PWA plugin) that precaches the shell and caches state files on first use.
- Add `<meta name="description">`, Open Graph, `robots.txt`, `404.html`, remove `user-scalable=no`, add a React error boundary with a reload button.
- Restrict the Pages artifact to built output only (build into `docs/site/` or move internal docs out of `docs/`).
- Add Playwright smoke tests (load, pick state, answer 3 questions, see results, switch language) and run them in CI on PRs; this is what issue #52 asks for.
- Decide the fate of `web/` and the Dockerfile: recommended to delete both and note the Pages deployment as canonical, or keep the Dockerfile but serve `frontend/dist`.

### Phase 2 — Content and compliance (weeks 2–3, parallel with Phase 1)

Exit criterion: issue #58 has an explicit v1 decision recorded; no state promises a test language the manual does not support; JA policy is decided.

1. ~~Merge `data/dmv-test-languages` as `data/dmv_test_languages.json`.~~ Merged into this branch (51 states: 30 high, 15 medium, 6 low confidence). Nothing reads it yet. Still to do: re-verify the six low-confidence states (MS, MT, OK, SC, SD, WV) and reconcile with the `official_test_languages` fields #63 added to each `config.json`.
2. Choose one: (a) ship #63's "official vs practice-only" chips as v1 and move the modal and per-language stats to v1.1, or (b) build the full #58 UX on all three platforms. Recommendation: (a), because #63 never claims a language is offered without manual evidence.
3. JA: hide by default behind a "show legacy languages" toggle, or drop from the bundle for v1 and shrink the payload. Recommendation: hide, keep data.
4. Edit PR #57 copy to describe the practice-only language labelling and the SD edition caveat, then get a native Spanish proofread.
5. Triage the stale-URL report from the fixed cron; refresh `manual_urls.json` entries and re-run `verify_manuals.py --update-timestamps`.

### Phase 3 — Beta and QA (weeks 3–5)

Exit criterion: one full beta cycle on each mobile platform with no P0/P1 bugs open; accessibility pass done; screenshots regenerated from real builds.

- TestFlight external group and Play internal → closed testing, 10–20 testers, at least five days on each.
- Device matrix: iPhone SE (small), iPhone 15/16, one iPad if shipping iPad; Android API 26 (min), 29 (CI emulator), 35, one small-screen and one large-screen device, one low-RAM device for the bundle decode.
- Scripted test pass per platform: fresh install, pick state, switch language, run 10/25/all-question quizzes, weak-spots mode, stats persistence across restart, reset data, rotation, process death, dark mode, VoiceOver / TalkBack on quiz and results.
- Accessibility audit against WCAG AA: contrast (already fixed in #63), focus order, screen-reader labels, 44 px targets, Dynamic Type / font scale 200%.
- Regenerate the ten store screenshots from production builds (PR #57 currently composes them from mockups) and produce the 6.7" and 6.5" iPhone sets plus Play phone set. iPad set only if shipping iPad.
- Measure and record: cold-start time to state picker on the low-RAM Android device and on web over throttled 4G. Target under 2 s and 1 s respectively.

### Phase 4 — Submission (week 5)

Exit criterion: both apps in review with complete metadata; web launched.

**Apple**
- App Store Connect record with name, subtitle, keywords, description (EN + ES) from PR #57, privacy nutrition label "Data Not Collected", age rating 4+, category Education, support and privacy URLs, review notes explaining the offline design and that state DMV names are attributions, not affiliations.
- Export compliance: no encryption beyond HTTPS (none at all).
- Upload the archive from the CI lane; submit for review. Typical turnaround one to three days.

**Google**
- Play Console app record, store listing (EN + ES), feature graphic from PR #57, 512×512 icon, Data safety form ("no data collected, no data shared"), content rating questionnaire, target audience 13+, category Education, privacy policy URL.
- Promote the closed-testing build to production with a staged rollout at 20% for the first 48 hours.
- Note: new personal developer accounts must run a closed test with 12+ testers for 14 days before production access. If the account is new, start that clock in Phase 3.

**Web**
- Point a custom domain at Pages (add `CNAME`) if you have one; otherwise keep the `github.io` URL and make sure store listings link to it. Consider renaming the repo away from `nj-drivers-test`, which changes the base path.

### Phase 5 — Launch and after

- Launch order: web (already live, announce once Phase 1 track D lands), then Android production, then iOS on approval. Do not gate one store on the other.
- Monitoring: there is no analytics or crash reporting by design. Keep it that way for v1 and rely on store crash reports (Xcode Organizer, Play vitals), both of which need no SDK. Revisit only if the privacy label changes.
- Content cadence: monthly URL verification (cron, now fixed), quarterly re-verification of the 50 manuals with `quiz_gates.py --write-report`, and a re-generation policy: when a manual edition changes, regenerate that state's EN bank, re-translate ES, re-run gates, bump the app.
- Release cadence: data-only updates ship as new app builds (the bundle is compiled in), so budget a monthly mobile release.
- v1.1 backlog: DC via headless-browser capture, full #58 modal and per-language stats, Spanish-by-default from device locale, flashcard mode, iPad layout, Canadian provinces (INTERNATIONAL.md).

## 4. Decisions needed from the owner

1. App name and bundle ID / package name (PR #57 recommends "Driver's Test Prep — Real Manuals").
2. Pricing: free with no IAP (recommended) or otherwise.
3. iPad in v1: yes (needs layout work and screenshots) or no (recommended for v1).
4. Issue #58 scope for v1: #63's evidence-based labelling (recommended) or the full modal + per-language stats.
5. Japanese banks: hide, remove, or ship as legacy.
6. Fate of `web/` Flask app and the Dockerfile.
7. Custom domain and whether to rename the repository.
8. Whether Apple and Google developer accounts already exist and their age (affects the Play 14-day closed-test rule).

## 5. Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| #62/#63 stack is too large to review and rots further | High | Time-box the review to one week; rely on the green CI, the 100 pytest cases, and the fleet-wide gate reports rather than line-by-line review; merge, then fix forward. |
| Apple rejects for "misleading" use of state agency names or DMV-like branding | Medium | Keep the unofficial disclaimer on the state picker and About screen, avoid state seals, mention it in review notes. |
| Android SDK 35 upgrade breaks Compose code | Medium | Do the AGP/Kotlin/Compose bump in an isolated PR; CI builds and UI tests will catch it. |
| 27 MB web bundle causes abandonment on mobile | High if unfixed | Phase 1 track D per-state split; measure before and after. |
| A manual changes between verification and launch | Low per state, high fleet-wide | Fixed cron plus quarterly re-verification; About-this-test already shows the edition and verified date. |
| Play 14-day closed-testing requirement delays Android by two weeks | Medium | Start the closed test the day the first signed AAB exists, in Phase 1, not Phase 3. |
| Spanish copy or UI strings read as machine-translated | Medium | Native proofread of PR #57 and of `docs/i18n.json` before submission. |

## 6. Critical path

```
Week 1   Phase 0: merge #62 → #63 → #61 → #57; prune backlog; fix cron
         Track A: name, IDs, icon, legal pages (blocks B, C, D, Phase 4)
Week 2   Track B iOS + Track C Android + Track D web in parallel
         Phase 2 decisions (#58 scope, JA, web/ fate)
Week 3   First signed builds → TestFlight + Play closed test (start 14-day clock)
         Playwright suite + PWA on web; web soft-launch
Week 4   Beta fixes, accessibility pass, real-build screenshots
Week 5   Store submissions; staged Android rollout
Week 6   iOS approval; announce; switch to monthly cadence
```

## 7. Pre-submission checklist

- [ ] `main` == former #63 head, all 8 workflows green
- [ ] App icon on iOS, Android, web, and store listings
- [ ] `PrivacyInfo.xcprivacy` present; iOS archive uploads without warnings
- [ ] `DEVELOPMENT_TEAM`, bundle ID, display name, localizations set
- [ ] Android `targetSdk 35`, release signing, minified AAB builds in CI
- [ ] Privacy, support, and about/attribution pages live on Pages
- [ ] Unofficial / not-affiliated disclaimer visible in-app
- [ ] Web loads per-state data; PWA installable; error boundary; 404; SEO meta
- [ ] Playwright smoke suite green in CI
- [ ] #58 v1 decision implemented and described in store copy
- [ ] JA policy implemented
- [ ] Store screenshots regenerated from production builds (EN + ES)
- [ ] Spanish copy proofread
- [ ] Data safety form and privacy nutrition label completed ("no data collected")
- [ ] Beta cycle completed on both platforms with no open P0/P1
- [ ] Verify Manual Catalog cron green and stale URLs triaged
