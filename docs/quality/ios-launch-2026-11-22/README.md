# iOS launch recovery — 22 November 2026

Scope: the five priority findings on the iOS App Store launch board. Android/web polish and new countries are separate work. Main remained `a9cb0df`; the build, source-review and copy branches from the interrupted run were preserved.

## November 26 CI correction

The subsequent c5529f9 CI run failed one unit test: the metadata assertion still expected NJ to be unheld after the 2026 manual review flag was added. The November 22 all-green app-code suite predates that metadata change; its result does not establish that c5529f9 passed. The assertion is now corrected without clearing the hold, and also checks that unheld KY remains unheld. All 17 unit tests passed locally on November 26; see the [follow-up record](../ios-launch-2026-11-26/README.md) for current CI and PR status.

## Finding-to-fix map

| Board finding | Implemented change | Remaining acceptance work |
| --- | --- | --- |
| Tests do not prove the learning journey | Mandatory-screen assertions; isolated unit target; complete quiz/results/stats/relaunch tests; fatal bundle failures; both targets in CI | Review the PRs and CI evidence before merge |
| Language readiness is blurred | Per-state/language progress, preserved explicit legacy view, study-only consent and English practice, normalized unsupported preferences | Six agency language menus remain uncertain; new copy/sign descriptions need native locale review |
| A quiz offers no way out or back in | Cancel/leave confirmation, immediate answered-question progress, no false completed history, explicit no-resume policy, recoverable missing/empty bank states | Resume is intentionally not implemented; this is disclosed in the exit dialog |
| Accessibility and small-phone fit need proof | 44-point actions, scaled/wrapping layouts, spoken score values, actual sign descriptions, light/dark/largest-text simulator evidence | Real-device VoiceOver and beta review remain required; bounded audit exception is documented below |
| Content quality needs a current release check | Correct source/LFS probes, retained evidence/review flags, identical KY source cleared, six-state release hold, structural audit and six language-source rechecks | Regenerate/review AR, NC, NJ, SD, UT, WV; reconcile DO NOT PASS artwork/explanation; regenerate affected translations |

## Behavior changes

- Required screens now fail UI tests. An XCTest unit target covers exact scoring thresholds, duplicate/invalid taps, weak-question ranking, saved preferences, corrupt data, state/language isolation, legacy progress, empty-bank recovery, missing-answer recovery and abandoned sessions.
- New progress uses `(state, language)` keys. Old `quiz_<state>` records stay available through the explicitly labelled legacy statistics view; they are not guessed to be English or Spanish. Changing language returns to current language statistics. Reset asks for confirmation and clears that state's current/legacy progress and study-language consent.
- Unsupported language selections normalize to English with a visible explanation. Unconfirmed exam languages display study-only labels, consent and persistent quiz/results notices; the learner can choose English practice. Existing Japanese banks remain available, without adding new ones.
- Exit offers **Keep practicing** or **Leave quiz**. Answered-question progress is retained immediately; an unfinished quiz does not create a completed history entry. There is intentionally no resume after exit or relaunch. This policy is explained in the exit dialog.
- Empty banks stay on Home with retry/state/language recovery. Missing answers leave the question unanswered and retryable, without writing progress. The pass result and pass streak compare the raw correct/total fraction; rounding is only for the displayed percentage.
- All five screens use the bundled IBM Plex Serif / Inter fonts, adaptive surfaces and source citations. Count choices reflow in eager rows and grow with Dynamic Type. Text-only controls have real 44-point targets; decorative symbols stay out of the accessibility tree. Chart values are exposed as text to VoiceOver.
- All 36 sign assets have descriptions of the visible artwork in `data/signs/descriptions.json`. These English descriptions describe shape, symbols and printed words, rather than interpreting the correct driving action. They are copied with the actual sign assets. The historically named `speed_limit_25.png` actually displays **50**; its description follows the image, not the filename. The corresponding question asks sign category, not a numeric speed.

## Reproduce the checks

Dependencies: Python 3.12, PyYAML, the repository's development requirements, Xcode 26 with an installed iOS simulator runtime, and SwiftLint. No Apple signing identity is needed for simulator tests or the unsigned device build.

From the repository root, create a local virtual environment if needed:

```sh
python3.12 -m venv .venv
```

```sh
.venv/bin/python -m pip install -r requirements.txt -r requirements-dev.txt
```

```sh
.venv/bin/python -m pytest tools/ -q
```

```sh
.venv/bin/python tools/audit_questions.py
```

```sh
swiftlint lint --config ios/.swiftlint.yml
```

Choose an installed iPhone simulator from this inventory:

```sh
xcrun simctl list devices available
```

Set the destination UUID to that simulator. Use a new result-bundle path for each run; Xcode refuses an existing path, so preserve failures instead of overwriting them.

```sh
xcodebuild test -project ios/DriversTest/DriversTest.xcodeproj -scheme DriversTest -destination 'platform=iOS Simulator,id=SIMULATOR_UUID' -parallel-testing-enabled NO -resultBundlePath /tmp/DriversTest-new-run.xcresult CODE_SIGNING_ALLOWED=NO PYTHON="$PWD/.venv/bin/python"
```

```sh
xcodebuild build -project ios/DriversTest/DriversTest.xcodeproj -scheme DriversTest -configuration Release -sdk iphoneos -destination 'generic/platform=iOS' CODE_SIGNING_ALLOWED=NO PYTHON="$PWD/.venv/bin/python"
```

The explicit `PYTHON` build setting matters: Xcode can choose a different Python than a shell's PATH. A missing PyYAML dependency now stops bundling instead of quietly using stale data. A deliberately failing Python stub propagated exit 42 in the actual project phase.

## Accessibility audit scope

Native iOS audits found and drove fixes for a selected-language contrast problem, an undersized missed-answer label and a fixed-height statistics message that clipped at enlarged text. Statistics now use eager layouts, stack from xxxLarge, scale their minimum height and merge label/value for assistive technology. The quiz counter and answer tally also stack from xxxLarge rather than squeezing the tally into a half-width column.

iOS 26 also intermittently flags the native black/white quiz tally as low contrast. The test handles only a contrast finding whose element ID is `quiz-tally`, and only when that exact element’s current screenshot independently measures at least 4.5:1 from its two dominant opaque colors (each at least 1% of pixels). The calculation uses sRGB luminance and saves both measurement and screenshot as test attachments. Any other finding, low ratio or unmeasurable image still fails. A fixture checks black/white, low-contrast gray/white and a flat unmeasurable image. This bounded flat-label check is not a general image or full-screen accessibility validator.

## Validation record

Earlier failing results are retained under this run's `output/verification-2026-11-22/`; they must not be presented as successful tests. The following rows distinguish the full app-code suite from the later checks after adding the NJ content-review flag and extending the largest-text case to Spanish. Production Swift code was unchanged after the full suite; the later changes are the NJ data flag and the stronger UI test.

| Run | Result and scope |
| --- | --- |
| `pro-complete-final` | **20 UI tests + 17 unit tests passed.** All final Swift code, including stacked largest-text quiz header; no tally contrast exception was used. This run preceded the later NJ review flag and Spanish extension of the dark-mode test. |
| `se-layout-verified` | Both complete Spanish flow and largest-text dark-mode flow passed (100.296 s / 165.919 s), before the NJ flag. |
| `pro-content-verified` | Final six-hold bundle: Spanish quiz/results/statistics/relaunch and largest-text English dark-mode flows passed (86.319 s / 191.511 s). |
| `se-content-verified` | Final six-hold bundle: both flows passed (95.491 s / 190.336 s). |
| `pro-spanish-accessibility` | Final six-hold bundle: largest-text dark-mode flow switches to Spanish on Home and verifies Spanish statistics; passed (189.906 s). |
| `se-spanish-accessibility` | Same Spanish flow on iPhone SE passed (238.935 s). |
| `pro-final-verified` | 17 unit tests and 2 UI tests passed: complete Spanish quiz → results → statistics → relaunch; rendered-contrast safeguard fixture. The live flow audits unanswered/answered quiz, results and statistics. |
| `se-ready-flow` | Complete Spanish quiz → results → statistics → relaunch and its audits passed (87.776 s). This is the final visual layout before the test-only tally identifier and audit safeguard were added. |
| `pro-release-candidate` | 17 unit tests passed; 18 of 19 UI tests passed. This earlier full run covered picker/home audit, exit/cancel, language consent/English switch and content-review notice. Its statistics contrast failure was repaired and the affected journey rechecked above. This row is a partial pass, not a green full suite. |
| `final-content-device-release` | Final unsigned Release build for generic iOS device succeeded. No archive signing or upload. |

Named screen captures and their originating tests are listed in [screenshots.json](screenshots.json). Light-mode and largest-accessibility-text dark-mode captures show all five screens on iPhone 17 Pro and iPhone SE; these are test evidence, not approved App Store screenshot assets. The dark test captures the initial English picker, then switches to Spanish for Home, quiz, results and statistics. The actual light and dark compositions were reviewed on both phone sizes. Screenshots capture a viewport, not all scrollable content or a VoiceOver session.

- Release gate: exit 1 with exactly AR, NC, NJ, SD, UT and WV, as required until edition review/regeneration is complete. No hold was cleared to force a green release.
- Python tools: 126 tests passed, including rejection of unsafe YAML object construction.
- Structural question audit: 18,072 English questions across 51 catalog entries, zero reported issues. The generated bundle has 42,851 question entries when translations are included. This is not a manual-edition or human factual review.
- Ruff check and format, Pyright with the project environment, and SwiftLint: passed before final test execution.
- Bundling uses PyYAML’s C safe loader when available, with the Python safe loader as fallback. Before the subsequent NJ metadata hold, a full generated uncompressed bundle compared byte-for-byte identical before/after the loader change; generation took 6.26 seconds locally. This does not change or regenerate question content.
- Local toolchain: Xcode 26.0.1 / iOS 26 SDK. CI selects Xcode 26.3 on macos-15, confirmed in the official runner-images inventory on November 22.

## Release work that is still required

1. **Publish and review the changes.** [PR #78](https://github.com/ivanmkc/nj-drivers-test/pull/78) contains the build fixes. The source-review branch is stacked on it; the iOS quality branch is stacked on the source-review branch. Store-copy changes are independent. No merge is implied by a branch or PR existing.
2. **Regenerate and verify AR, NC, NJ, SD, UT and WV banks against their current manuals, then regenerate affected translations.** The November 21 recheck reached all eight previously flagged source URLs (six canonical and two recovery). Kentucky was byte-identical to its stored LFS object. The five previously identified banks plus newly found NJ still have explicit review holds; the release lane refuses to upload while they remain. The generation/translation pipeline's Google application-default credentials are absent on this computer. Do not clear holds solely because a URL is reachable.
The official NJ URL now serves 2026 while its stored bank cites 2025; the new NJ hold is included in this quality branch. See the [eight-question source spot-check](nj-source-spot-check.json) for bounded English/Spanish findings and source page numbers.

The six low-confidence language rows (MS, MT, OK, SC, SD, WV) were also checked against primary agency pages; see [language-source findings](language-recheck.json). Oklahoma explicitly limits its online test to English, and an SD agency document provides historical evidence of Spanish testing. The full current menus remain unresolved. All six app configs lack official-language evidence, so the app keeps its conservative study-only warning; handbook translations and interpreter forms are not treated as proof of exam availability.

3. **Resolve a sign-content inconsistency found during visual review.** `no_passing.png` is a rectangular DO NOT PASS sign, while the shared question explanation describes a pennant. The meaning of the answer is unchanged, but the artwork/shape explanation needs reconciliation and re-verification, including generated translations. The new image description accurately describes the rectangle. This is a content review item, not proof of regenerated banks.
4. **Real-device VoiceOver and release approval.** Xcode’s physical-device inventory returned zero devices on November 22. Automated accessibility audits and largest-text simulator checks supplement, but do not replace, an actual VoiceOver session, device beta and stakeholder sign-off. English sign descriptions and the new UI copy still need locale review.
5. **Apple account/signing and store completion.** No valid code-signing identity exists in this local keychain. Team membership, the final registered bundle ID, App Store Connect credentials, production screenshot slots, final pricing, native Spanish proofreading and owner approvals have not been verified. No TestFlight upload or public submission was performed.

### PR handoff

Only #78 is submitted. These pushed branch comparisons are prepared for the remaining PRs; opening a comparison does not itself create a PR. Links returned HTTP 200 on November 22.

| Change | Base ← head | Action |
| --- | --- | --- |
| Build/CI | `main` ← `fix/ios-launch-build` | [Review PR #78](https://github.com/ivanmkc/nj-drivers-test/pull/78); its iOS CI run 129 succeeded |
| Source review (original five holds) | `fix/ios-launch-build` ← `fix/source-freshness-review` | [Open prepared comparison](https://github.com/ivanmkc/nj-drivers-test/compare/fix/ios-launch-build...fix/source-freshness-review?expand=1) |
| iOS quality + new NJ hold | `fix/source-freshness-review` ← `fix/ios-launch-quality` | [Open prepared comparison](https://github.com/ivanmkc/nj-drivers-test/compare/fix/source-freshness-review...fix/ios-launch-quality?expand=1) |
| Store copy | `main` ← `fix/store-copy-readiness` | [Open prepared comparison](https://github.com/ivanmkc/nj-drivers-test/compare/main...fix/store-copy-readiness?expand=1) |

Review the stack from build → source → quality, or retarget dependent PRs after each base lands. Do not merge a dependency that is still under review merely to make a comparison shorter. The independent store-copy branch can be reviewed separately.

The GitHub connector refuses writes with “Resource not accessible by integration,” and the local gh token is invalid. The independent owner SSH login is valid; it can publish the code. PR #78 was created through the owner's existing GitHub browser session. Native browser actions stopped when Chrome repeatedly changed windows; ready PR descriptions are retained in `output/prs/`. Agent Bridge later refused the next board status save with “Tool access unavailable; renew the application run grant.” The last accepted board status therefore predates the final push/test record; the repository report is the newer evidence.

## Recovery

Keep source holds and legacy records intact if a check fails. Revert the relevant code commit through Git rather than editing generated question bundles or deleting old progress. Restore only the existing required account connection to run content generation; never paste keys into the repository, board, PR or logs. Signing and public-release steps remain separate from an unsigned build pass.
