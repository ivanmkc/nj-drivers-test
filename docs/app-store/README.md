# App Store assets · v1.0

Drafted launch assets for the iOS App Store and Google Play Store.

```
docs/app-store/
├── COPY.md                          Full drafted copy (EN + ES, iOS + Play)
├── README.md                        This file
├── _compose.py                      Regenerates the marketing images below
├── marketing/
│   └── feature-graphic-play.png     Google Play feature graphic (1024x500)
└── screenshots/
    ├── source/                      Untreated mock screenshots (from #51)
    │   ├── 01-home-light.png        ── reused as source material
    │   ├── 02-state-picker-light.png
    │   ├── 03-quiz-light.png
    │   ├── 04-quiz-dark.png
    │   ├── 05-results-light.png
    │   └── 06-stats-light.png
    ├── ios-6.7/                     Composed for iPhone 6.7" slot (1290x2796)
    │   ├── 01-home.png
    │   ├── 02-state-picker.png
    │   ├── 03-quiz.png
    │   ├── 05-results.png
    │   └── 06-stats.png
    └── play-phone/                  Composed for Play phone slot (1080x1920)
        └── ...
```

## What's launch-ready, what isn't

**Ready as v1 drafts** (sufficient for stakeholder review and store-listing preview):
- All copy in [`COPY.md`](./COPY.md)
- Play feature graphic
- Phone screenshots (composed from the approved design mocks #51)

**Needs production work before public submission** (tracked in issue #55):
- Screenshots from the actual built apps (not the mock previews) — depends on #52 (web), #53 (iOS), #54 (android) landing UI polish
- Production fonts (current images use DejaVu Serif as a stand-in for IBM Plex Serif; production assets should embed the real fonts)
- Native-Spanish-speaker proofreading of all ES copy
- App icon (1024×1024 iOS, 512×512 Play) — currently default
- iPad screenshots if shipping for iPad
- Privacy Policy + Support URL (must be hosted before App Store accepts the submission)
- Optional: 15–30s preview video for both stores

## Regenerating images

The marketing images are deterministic — `_compose.py` produces them from the source mocks plus drawn copy. After any edit to copy or design tokens:

```bash
python3 docs/app-store/_compose.py
```

Outputs are checked in so reviewers can see them on GitHub without running anything.

## Acceptance criteria for this asset set

See issue #55 for the full launch checklist. At minimum before public store submission:

- [ ] Copy reviewed and signed off
- [ ] Screenshots regenerated from production builds, not mocks
- [ ] Native-speaker pass on ES copy
- [ ] App icon designed and rendered at every required size
- [ ] Privacy Policy + Support URLs live
- [ ] Both stores' Privacy / Data Safety forms completed (all "no data collected")
