#!/usr/bin/env node
// Browser verification captures are test evidence, not new brand artwork.
import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';

const argumentsByName = new Map();
for (let index = 2; index < process.argv.length; index += 2) {
  if (!process.argv[index]?.startsWith('--') || !process.argv[index + 1]) {
    throw new Error('Use --base-url URL --routes FILE --output DIRECTORY.');
  }
  argumentsByName.set(process.argv[index], process.argv[index + 1]);
}
const base = new URL(argumentsByName.get('--base-url'));
if (!['http:', 'https:'].includes(base.protocol) || !['localhost', '127.0.0.1', '[::1]'].includes(base.hostname) || base.username || base.password) {
  throw new Error('This offline review runner accepts a loopback origin only.');
}
const manifest = JSON.parse(await readFile(argumentsByName.get('--routes'), 'utf8'));
const routes = Array.isArray(manifest) ? manifest : manifest.routes;
if (!Array.isArray(routes) || routes.length < 1 || routes.length > 40) throw new Error('Invalid bounded route list.');
const seen = new Set();
for (const route of routes) {
  if (!/^[a-z0-9-]{1,60}$/.test(route.id) || seen.has(route.id)) throw new Error('Invalid or duplicate route ID.');
  seen.add(route.id);
  if (typeof route.path !== 'string' || !route.path.startsWith('/') || new URL(route.path, base).origin !== base.origin) throw new Error('Route escaped the reviewed origin.');
  if (![200, 404].includes(route.status)) throw new Error('Route must declare expected HTTP 200 or 404.');
}
const output = path.resolve(argumentsByName.get('--output'));
await mkdir(output, { recursive: false });
const browser = await chromium.launch({ headless: true });
const results = [];
const viewports = [360, 390, 768, 1280, 1440];
const modes = ['light', 'dark'];
let browserVersion;
try {
  browserVersion = await browser.version();
  for (const route of routes) {
    for (const width of viewports) {
      for (const colorScheme of modes) {
        const context = await browser.newContext({ viewport: { width, height: 900 }, colorScheme, reducedMotion: 'reduce' });
        const externalRequests = [];
        const failures = [];
        const consoleErrors = [];
        await context.route('**/*', async intercept => {
          const url = new URL(intercept.request().url());
          if (url.origin !== base.origin && !['data:', 'blob:'].includes(url.protocol)) {
            externalRequests.push(url.origin + url.pathname);
            await intercept.abort();
          } else await intercept.continue();
        });
        const page = await context.newPage();
        page.on('pageerror', error => consoleErrors.push(error.message));
        page.on('requestfailed', request => failures.push({ url: request.url(), failure: request.failure()?.errorText }));
        const id = `${route.id}-${width}-${colorScheme}`;
        let result;
        try {
          const response = await page.goto(new URL(route.path, base).href, { waitUntil: 'networkidle', timeout: 20000 });
          await page.evaluate(() => document.fonts.ready);
          const accessibility = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze();
          const layout = await page.evaluate(() => ({
            title: document.title,
            htmlLanguage: document.documentElement.lang,
            mainCount: document.querySelectorAll('main').length,
            h1Count: document.querySelectorAll('h1').length,
            viewportWidth: window.innerWidth,
            scrollWidth: document.documentElement.scrollWidth,
            reducedMotion: matchMedia('(prefers-reduced-motion: reduce)').matches,
            brokenImages: Array.from(document.images).filter(image => !image.complete || image.naturalWidth === 0).map(image => image.getAttribute('src')),
            placeholderLinks: Array.from(document.querySelectorAll('a[href]')).filter(link => ['#', ''].includes(link.getAttribute('href'))).map(link => link.textContent.trim()),
          }));
          const keyboard = [];
          for (let index = 0; index < 10; index++) {
            await page.keyboard.press('Tab');
            keyboard.push(await page.evaluate(() => {
              const element = document.activeElement;
              const rect = element.getBoundingClientRect();
              const style = getComputedStyle(element);
              return { tag: element.tagName, text: (element.getAttribute('aria-label') || element.textContent || '').trim().slice(0, 100),
                visible: rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden',
                focusVisible: element.matches(':focus-visible'), outlineStyle: style.outlineStyle, outlineWidth: style.outlineWidth };
            }));
          }
          await page.evaluate(() => { document.activeElement.blur(); scrollTo(0, 0); });
          const screenshot = await page.screenshot({ path: path.join(output, id + '.png'), fullPage: true, animations: 'disabled' });
          result = { id, path: route.path, expectedStatus: route.status, status: response?.status(), width, colorScheme,
            screenshot: id + '.png', screenshotSha256: createHash('sha256').update(screenshot).digest('hex'),
            layout, keyboard, externalRequests, requestFailures: failures, consoleErrors,
            accessibilityViolations: accessibility.violations.map(violation => ({ id: violation.id, impact: violation.impact, description: violation.description, helpUrl: violation.helpUrl,
              nodes: violation.nodes.map(node => ({ target: node.target, summary: node.failureSummary })) })),
            accessibilityIncomplete: accessibility.incomplete.map(check => ({ id: check.id, targets: check.nodes.map(node => node.target) })),
            manualReview: 'not_yet_inspected',
          };
          result.automatedPass = result.status === route.status && layout.scrollWidth <= layout.viewportWidth + 1 && layout.brokenImages.length === 0 && layout.placeholderLinks.length === 0 && result.accessibilityViolations.length === 0 && failures.length === 0 && consoleErrors.length === 0 && externalRequests.length === 0;
        } catch (error) {
          result = { id, path: route.path, width, colorScheme, automatedPass: false, error: error.message, externalRequests, requestFailures: failures, consoleErrors };
        } finally {
          await context.close();
        }
        results.push(result);
        await writeFile(path.join(output, id + '.json'), JSON.stringify(result, null, 2) + '\n');
        console.log(`${result.automatedPass ? 'PASS' : 'FAIL'} ${id}`);
      }
    }
  }
} finally {
  await browser.close();
  await writeFile(path.join(output, 'report.json'), JSON.stringify({
    observedAt: new Date().toISOString(), contentClass: 'browser_verification_capture', browserVersion, baseUrl: base.href,
    completedStates: results.length, expectedStates: routes.length * viewports.length * modes.length,
    automatedPass: results.length === routes.length * viewports.length * modes.length && results.every(result => result.automatedPass),
    limitations: ['Automated checks supplement manual screenshot, keyboard, zoom and assistive-technology inspection.', 'This run uses reduced motion; normal motion and explicit theme controls require separate interaction checks.', 'Loopback review blocks external requests and does not establish a deployed result.'], results,
  }, null, 2) + '\n');
}
if (results.some(result => !result.automatedPass)) process.exitCode = 1;
