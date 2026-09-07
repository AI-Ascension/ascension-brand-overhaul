# W03 precommit review — changes required

Reviewer: root, independent of W03 website implementation. Date: 2026-09-07. Website base: `4e2d99c95d89ce3d18981d331faad10c9f1f7376`, with uncommitted implementation. Source file digests and aggregate result digests are in the companion JSON receipt. No website commit, deployment or production mail was performed by this review.

## Observed checks

- Local PHPUnit 11.5.55 on PHP 8.3.6: **24 tests / 55 assertions passed**.
- Static internal file/anchor scan: **11 pages, zero missing destinations**.
- Chromium 153.0.8010.12, five widths (360, 390, 768, 1280, 1440), light/dark, reduced motion: **110 unique states actually loaded, all expected HTTP 200; 10 automated passes, 100 contrast-failing states, eight states with keyboard-inaccessible scroll regions**. The direct `/404.html` route correctly expects 200; Apache unknown-route error handling was not exercised by the PHP development server.
- No source file changed between the recorded snapshot and completion. Opened actual screenshots for every core page, including mobile and desktop examples. This is not manual inspection of every individual viewport or assistive-technology certification.
- Interaction probe confirmed one Linux report after platform filtering, but also reproduced the theme and menu defects below. A 640-pixel reflow probe is not a completed 200% browser-zoom test.
- The first browser attempt could not start because Chromium was absent. It was installed successfully. Two later long-running local processes exited with signal-derived status 143. Connection failures from the terminated server were excluded from product results; missing states were rerun in bounded batches. All four review server ports were confirmed closed afterward.

## Required repairs

1. **Contrast:** `styles.css:428` and `styles.css:1114` apply unsuitable foreground tokens to inverse surfaces. Home evidence cells measured 2.73:1 and the hosting-disclosure footer link 2.28:1 in light mode. Fix all inverse-surface text/link roles in both themes, including faint metadata, then rerun every page.
2. **Scrollable tables:** home and Docs have horizontally scrolling regions inaccessible from the keyboard in small viewport states. Give the scroll container appropriate focus, naming and visible focus treatment, and verify keyboard scrolling without trapping navigation.
3. **Filter empty state:** `runs.html:20` has `hidden`, but `.empty-state` styling at `styles.css:854` overrides its visibility. The screenshot shows two reports and the no-results message simultaneously. Verify initial two rows/no empty state; Linux one row; victory zero rows/visible empty state; reset two rows/no empty state.
4. **Theme toggle:** `script.js` treats system mode as light. On a system-dark page, the first click leaves the dark background unchanged while the label changes. Derive the effective system theme before toggling and keep the control label/state accurate.
5. **Mobile menu:** Escape leaves the opened menu expanded. Close it and restore focus to its toggle; check keyboard navigation and resize behavior.
6. **Visitor-facing implementation placeholders:** `index.html:51` exposes the internal art/model gate as the hero's major visual element. Remove that implementation placeholder from the visitor hero while retaining the unresolved art requirement in delivery evidence. Remove the boxed `AA` fallback mark rather than presenting it as newly authored identity artwork; plain accessible brand text is sufficient pending mandatory generated assets. Press and Build should likewise keep internal worker names and model-routing details out of visitor instructions. The tested quickstart still requires W04 integration.
7. **Privacy accuracy:** `privacy.html:14` says addresses are stored only after a confirmation link is used, but pending addresses are persisted before mail delivery. It also attributes expiry to both token types, while active unsubscribe links deliberately do not expire. Describe pending storage, seven-day confirmation validity, actual pruning behavior and durable unsubscribe links accurately.
8. **Backend evidence and recovery:** `tests/SubscriptionFlowTest.php` runs its lock test sequentially. Add a real multiprocess write-preservation test and storage/write/rename failure checks. The existing mail-failure test proves that pending state survives; it does not prove failed delivery can recover. The endpoint suppresses sends for existing pending records, so implement and test a bounded recovery path without trapping the address until expiration.
9. **Documentation:** `docs/BRAND_IMPLEMENTATION.md` still describes an available reviewed decision/guess-and-reveal route, one staged report and an older token revision. Align it with the actual unavailable decision state, two report records and canonical sync receipt. Do not label planned interactions or pending quickstart integration as implemented.

## Remaining review

After repairs, rerun affected PHP and browser checks against a frozen source snapshot. Complete actual 200% zoom, form-browser states with a synthetic transport, normal-motion checks, keyboard scroll/menu/theme/filter behavior and independent W07 review. Missing artwork, authentic decision publication, W04/W05 integration and production hosting behavior remain separate acceptance gates. This review does not approve a production-ready website.
