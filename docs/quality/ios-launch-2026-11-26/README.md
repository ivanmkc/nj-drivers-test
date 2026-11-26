# iOS launch follow-up — November 26, 2026

The failure in [CI run 45090886906](https://github.com/ivanmkc/nj-drivers-test/actions/runs/45090886906) was a stale test expectation, not a reason to clear NJ’s content-review hold. That c5529f9 run passed all 20 UI tests and Debug/unsigned Release builds, but failed 1 of 17 unit tests at `DriversTestTests.swift:187`.

The metadata test now requires NJ’s pending-review flag and retains a negative check for Kentucky, whose repaired source was byte-identical. Production code and question banks are unchanged by this follow-up. All six holds (AR, NC, NJ, SD, UT, WV) remain active.

## Validation

- Local XCTest: 17 unit tests passed, zero failures, on the iPhone SE / iOS 26 simulator with Xcode 26.0.1. Result bundle: `output/verification-2026-11-26/metadata-unit-confirmed.xcresult` (retained locally).
- Bundle/release-gate regression tests: 10 passed. SwiftLint and `git diff --check` passed.
- The first local invocation used the wrong Python setting and failed before tests at bundling. It is retained as `metadata-unit-fix.xcresult`; it is not a successful test run. The corrected invocation uses the build setting below.
- Fresh [full CI run 45907831941](https://github.com/ivanmkc/nj-drivers-test/actions/runs/45907831941) **passed on ca02898**: 20 UI tests, 17 unit tests, zero failures, including the corrected metadata test. Debug and generic-device unsigned Release builds also passed. This is branch evidence; it is not a signed-device, merged-main or TestFlight result.

From the repository root, use your existing Python environment containing PyYAML:

```sh
xcodebuild test -project ios/DriversTest/DriversTest.xcodeproj -scheme DriversTest -destination 'platform=iOS Simulator,id=SIMULATOR_UUID' -parallel-testing-enabled NO -only-testing:DriversTestTests -resultBundlePath /tmp/DriversTest-metadata-new.xcresult CODE_SIGNING_ALLOWED=NO PYTHON="$PWD/.venv312/bin/python"
```

Choose an installed simulator UUID and a new result path. `PYTHON` is the setting read by the Xcode phase; `PYTHON_EXECUTABLE` is not read. Preserve failed evidence rather than replacing an existing xcresult.

## Pull requests and remaining work

- [PR #78](https://github.com/ivanmkc/nj-drivers-test/pull/78): build/toolchain fixes; remains open.
- [PR #79](https://github.com/ivanmkc/nj-drivers-test/pull/79): source probing/evidence and the original five edition holds; created November 26, stacked on #78.
- iOS quality and store-copy branches remain pushed; their PR submissions are prepared and paused for Chrome coordination. [Prepared titles, bases and descriptions](prepared-prs.json) are saved with this report. Store copy also descends from the build branch: its PR base must be `fix/ios-launch-build`, which isolates its two documentation commits. Quality uses `fix/source-freshness-review`. No merge is authorized by this record.

Main advanced only by the weekly liveness snapshot to `96ecd7f`; that monitoring commit does not regenerate or verify a question bank. Google application-default credentials are still unavailable (`DefaultCredentialsError` on November 26), so content generation/translation remains blocked on the existing project connection. Native browser actions were paused when its active window changed during use; no credential or access scope was broadened.

The remaining comparisons returned HTTP 200 on November 26: [quality against source review](https://github.com/ivanmkc/nj-drivers-test/compare/fix/source-freshness-review...fix/ios-launch-quality?expand=1) and [store copy against build fixes](https://github.com/ivanmkc/nj-drivers-test/compare/fix/ios-launch-build...fix/store-copy-readiness?expand=1). Only PRs #78 and #79 exist; opening a comparison does not submit a PR.

The [November 22 report](../ios-launch-2026-11-22/README.md) retains the complete behavior changes, actual source findings, screenshot manifest, content/sign-content gaps, real-device VoiceOver and signing/store acceptance work. Do not treat branch implementation or a unit pass as a release approval.
