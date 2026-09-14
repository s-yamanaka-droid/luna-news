# Now on AIr × Lakkan — 2026-09-14 update

## Implemented
- Newspaper layout retained. Added Lakkan's Luna / recruitment / CRM / FDE service links from the existing Lakkan source.
- Added 6 source-backed news reports and 2 clearly labeled editorial columns to the September 14 issue.
- Source publication dates and issue update dates are separate. Original analysis and service introductions are labeled.
- Generator prompt now requests body sections, analysis, actions and source dates for future issues.
- Added read-only freshness check and build-time health.json. These checks do not schedule updates by themselves.

## Verified
- python3 scripts/rebuild_all.py: success, 127 dated issues plus homepage.
- python3 scripts/check_newspaper.py: 128 pages, local links / image files / anchors / article counts pass.
- python3 -m unittest discover -s tests: 6 tests pass.
- python3 scripts/check_freshness.py: latest_issue 2026-09-14, age_days 0, 8 articles.
- node --check docs/assets/newspaper.js: pass.
- Browser: desktop service panel, 390px article view, no horizontal overflow; 8 article bodies and 8 analysis sections.

## Update outage
- Both this checkout and /Users/yamanakashuto/apps/luna-news originally ended at 2026-09-07.
- The latter has done markers through September 7 and a delivery receipt from that day.
- No com.luna.news launchd registration or matching active plist found on this Mac.
- No daily run logs after September 7 found here. This establishes an absent local schedule; it does not establish whether a different host has a scheduler.
- The original daily script targets /Users/yamanakashuto/apps/luna-news and also pushes, publishes, posts to Slack/Threads, and syncs Obsidian. It was not executed as a recovery shortcut.
- The original checkout's existing user modifications were preserved.

## Remaining
- Production publish and restart of unattended daily updates are not performed.
- Before re-enabling automation, choose one canonical checkout containing this design; restarting the old script unchanged would use the old templates.
- Weekly and cases pages retain their earlier designs/content.
- health.json records the build-time observation; scripts/check_freshness.py recalculates age when invoked.
