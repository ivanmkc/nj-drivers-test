# iOS launch recovery — 22 November 2026

Scope: the five priority findings on the iOS App Store launch board. Android/web polish and new countries are separate work. Main remained `a9cb0df`; the build, source-review and copy branches from the interrupted run were preserved.

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

## Validation record

Final device/test totals and the screenshot manifest are recorded after the final runs below. Earlier failing results are retained under this run's `output/verification-2026-11-22/`; they must not be presented as successful tests.

- Python tools: 125 tests passed.
- Structural question audit: 18,072 questions across 51 catalog entries, zero reported issues. This is not a manual-edition or human factual review.
- Ruff check and format, Pyright with the project environment, and SwiftLint: passed before final test execution.
- Local toolchain: Xcode 26.0.1 / iOS 26 SDK. CI selects Xcode 26.3 on macos-15, confirmed in the official runner-images inventory on November 22.

## Release work that is still required

1. **Publish and review the changes.** PR #78 contains the build fixes. The source-review branch is stacked on it; the iOS quality branch is stacked on the source-review branch. Store-copy changes are independent. No merge is implied by a branch or PR existing.
2. **Regenerate and verify AR, NC, SD, UT and WV banks against their current manuals, then regenerate affected translations.** The November 21 recheck reached all eight previously flagged source URLs (six canonical and two recovery). Kentucky was byte-identical to its stored LFS object. The five changed/old-edition banks still have explicit review holds; the release lane refuses to upload while they remain. The generation/translation pipeline's Google application-default credentials are absent on this computer. Do not clear holds solely because a URL is reachable.
3. **Resolve a sign-content inconsistency found during visual review.** `no_passing.png` is a rectangular DO NOT PASS sign, while the shared question explanation describes a pennant. The meaning of the answer is unchanged, but the artwork/shape explanation needs reconciliation and re-verification, including generated translations. The new image description accurately describes the rectangle. This is a content review item, not proof of regenerated banks.
4. **Real-device VoiceOver and release approval.** Automated accessibility audits and largest-text simulator checks supplement, but do not replace, an actual VoiceOver session, device beta and stakeholder sign-off. English sign descriptions and the new UI copy still need locale review.
5. **Apple account/signing and store completion.** No valid code-signing identity exists in this local keychain. Team membership, the final registered bundle ID, App Store Connect credentials, production screenshot slots, final pricing, native Spanish proofreading and owner approvals have not been verified. No TestFlight upload or public submission was performed.

The GitHub connector refuses writes with “Resource not accessible by integration,” and the local gh token is invalid. The independent owner SSH login is valid; it can publish the code. PR #78 was created through the owner's existing GitHub browser session. Native browser actions stopped when Chrome repeatedly changed windows; ready PR descriptions are retained in `output/prs/`.

## Recovery

Keep source holds and legacy records intact if a check fails. Revert the relevant code commit through Git rather than editing generated question bundles or deleting old progress. Restore only the existing required account connection to run content generation; never paste keys into the repository, board, PR or logs. Signing and public-release steps remain separate from an unsigned build pass.
