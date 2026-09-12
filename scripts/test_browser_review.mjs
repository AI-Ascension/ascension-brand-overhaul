// Exercise the real locked browser audit against a disposable loopback server.
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { mkdtemp, readFile, rm, stat } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const temporaryRoot = await mkdtemp(path.join(tmpdir(), 'brand-browser-audit-'));
const output = path.join(temporaryRoot, 'capture');
const run = (args) => new Promise((resolve) => {
  const child = spawn(process.execPath, args, { cwd: root, stdio: 'inherit' });
  child.once('exit', code => resolve(code));
});
const contentType = (file) => file.endsWith('.html') ? 'text/html; charset=utf-8' : file.endsWith('.png') ? 'image/png' : 'application/octet-stream';
const server = createServer(async (request, response) => {
  const requestPath = new URL(request.url, 'http://127.0.0.1').pathname;
  const relative = requestPath === '/' ? 'art/asset-board.html' : requestPath.slice(1);
  const target = path.resolve(root, relative);
  if (!target.startsWith(root + path.sep)) { response.writeHead(400).end(); return; }
  try {
    const body = await readFile(target);
    response.writeHead(200, {'content-type': contentType(target)}).end(body);
  } catch { response.writeHead(404).end('not found'); }
});

try {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const address = server.address();
  assert.equal(typeof address, 'object');
  const base = `http://127.0.0.1:${address.port}`;
  assert.equal(await run(['scripts/browser_review.mjs', '--base-url', base, '--routes', 'tests/browser-routes.json', '--output', output]), 0, 'browser audit must pass for the reviewed catalog');
  const report = JSON.parse(await readFile(path.join(output, 'report.json')));
  assert.equal(report.automatedPass, true);
  assert.equal(report.completedStates, 10);
  assert.equal(await run(['scripts/browser_review.mjs', '--base-url', 'https://example.test', '--routes', 'tests/browser-routes.json', '--output', `${output}-negative`]), 1, 'non-loopback origins must fail closed');
  console.log('browser audit positive and non-loopback negative cases passed');
} finally {
  await new Promise(resolve => server.close(resolve));
  await rm(temporaryRoot, { recursive: true, force: true });
}
