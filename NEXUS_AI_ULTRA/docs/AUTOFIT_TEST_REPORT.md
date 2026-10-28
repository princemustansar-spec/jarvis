# Dashboard auto-fit — 28 October 2026

The existing navy/cyan dashboard now sizes itself from the **usable window viewport**, including changes caused by window resizing, title/taskbar space or Windows display scaling. Physical screen resolution is not used as a fixed canvas. No rebuild, new frontend, JavaScript resize polling, transform/zoom scaling or backend changes were introduced.

## Changes

- Desktop shell fills the viewport with a bounded header, sidebar and main content area. Sidebar navigation scrolls independently when necessary.
- Width- and height-aware CSS grid tracks, clamped typography, buttons and spacing keep the full dashboard visible at the requested desktop viewport sizes.
- AI rings and core use their actual panel's container dimensions, with space reserved for outlines/glow. They shrink or grow when the window changes size.
- Chat history and activity lists retain their own scrolling. All dashboard action buttons remain inside their panels at both target sizes.
- Settings and other module pages have an independent vertical scroll area on desktop. Their bottom save buttons remain reachable. Smaller windows use normal vertical document flow rather than clipping or shrinking controls indefinitely.
- Existing colors, gradients, borders, icons, animations, HTML markup, JavaScript actions, providers, APIs and native pywebview host are preserved. Only responsive CSS and its tests/documentation changed.

## Executed checks

Headless system Chromium with Playwright against the actual running FastAPI app:

| Usable viewport | Result |
| --- | --- |
| 1366 × 768 | Full dashboard fits; no horizontal overflow; dashboard action buttons inside panels; AI ring diameter 183.5 CSS px |
| 1920 × 1080 | Full dashboard fits; no horizontal overflow; dashboard action buttons inside panels; AI ring diameter about 321 CSS px |
| 1366 × 650 | Reduced laptop client-height fallback; vertical dashboard scroll available |
| 1093 × 614 | Scaled/smaller client-area layout; normal vertical flow, no horizontal overflow |
| 800 × 600 | Native minimum-window fallback; normal vertical flow, no horizontal overflow |
| 390 × 844 | Existing mobile layout retained without horizontal overflow |

At every size: opened Settings, scrolled to the bottom Save all providers button, verified it was within the viewport, resized the same page and confirmed unsaved input remained intact. Desktop Settings uses overflow-y:auto. The navy #030d18 and cyan #00dbf6 palette tokens were asserted. No JavaScript page errors occurred.

`tests/autofit.cjs` contains these assertions. `docs/autofit-results.json` records outcomes. `autofit-*.png` and `autofit-settings-*.png` are real screenshots, visually inspected at the two requested resolutions.

Also passed: **33 Python tests**, including all existing API and desktop-host integration tests. The frontend preservation test now checks unchanged HTML and action JavaScript; stylesheet changes are intentional and covered by the new layout/appearance checks. The existing `tests/browser.cjs` suite passed all 17 navigation sections, persisted memory, real system-tool results, Stop/Resume and approval-gated file creation.

Reproduction, with the app running in explicit headless mode:

```
NODE_PATH=/tmp/nexus-browser/node_modules node tests/autofit.cjs
NODE_PATH=/tmp/nexus-browser/node_modules node tests/browser.cjs
.venv/bin/python -m pytest -q
```

Install Playwright into that disposable tooling directory as described in TEST_REPORT.md; use CHROMIUM_PATH for a different installed Chromium executable. No browser or screenshot dependency was added to the application.

These are actual Chromium viewport tests, not a claim that a physical Windows laptop or native WebView2 window was tested in this Linux cloud. On Windows, close/reopen the updated app; rebuild an existing portable EXE with BUILD_WINDOWS.bat to include the updated stylesheet. No manual screen-size configuration is needed.
