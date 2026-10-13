/** Negative-boundary and real HTTP client tests. Created by Jason Stys. */
// BEGIN CODE MAP (generated; npm run maps)
// variable: value — line 36
// variable: value — line 37
// variable: args — line 42
// variable: count — line 47
// parameter: incoming — line 48
// parameter: response — line 48
// variable: server — line 48
// parameter: done — line 56
// variable: address — line 57
// variable: origin — line 59
// variable: directory — line 65
// variable: events — line 67
// parameter: line — line 67
// parameter: event — line 68
// parameter: event — line 69
// parameter: done — line 72
// parameter: _incoming — line 76
// parameter: response — line 76
// variable: server — line 76
// parameter: done — line 77
// variable: address — line 78
// parameter: done — line 84
// END CODE MAP
import assert from 'node:assert/strict';
import { readFileSync, mkdtempSync } from 'node:fs';
import { createServer } from 'node:http';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { bounded, optionsFrom, request, run, targetOrigin } from './load.js';

test('literal loopback and bounded integers only', () => {
  assert.equal(targetOrigin('http://127.0.0.1:8000'), 'http://127.0.0.1:8000');
  for (const value of ['https://example.com', 'http://localhost:80', 'http://127.0.0.1:80/a', 'http://127.0.0.1:65536', 'http://user@127.0.0.1:80', 'http://127.0.0.1:80?secret=x']) assert.throws(() => targetOrigin(value));
  for (const value of [0, 1.2, NaN, Infinity, 1001]) assert.throws(() => bounded(value, 1, 1000));
});

test('closed flags and explicit acknowledgement', async () => {
  assert.equal(optionsFrom(['--target', 'http://127.0.0.1:80', '--ack-owned-target']).acknowledged, true);
  for (const args of [['--bad'], ['--target'], ['--attempts', '1', '--attempts', '2'], ['--ack-owned-target', '--ack-owned-target']]) assert.throws(() => optionsFrom(args));
  await assert.rejects(run({target: 'http://127.0.0.1:80', output: 'unused', attempts: 1, concurrency: 1, acknowledged: false}));
});

test('all attempts retained; redirects, response caps and absolute deadlines', async () => {
  let count = 0;
  const server = createServer((incoming, response) => {
    if (incoming.url === '/health') response.end(JSON.stringify({lab: 'sre-observability-workbench'}));
    else if (incoming.url === '/large') response.end('x'.repeat(2048));
    else if (incoming.url === '/hang') return;
    else if (incoming.url === '/slow') { response.write('x'); setTimeout(() => response.end('x'), 60); }
    else if (incoming.url === '/redirect') { response.writeHead(302, {Location: 'https://example.com'}); response.end(); }
    else { response.writeHead(++count % 2 ? 200 : 503); response.end('synthetic'); }
  });
  await new Promise<void>((done) => server.listen(0, '127.0.0.1', done));
  const address = server.address();
  assert(address && typeof address !== 'string');
  const origin = `http://127.0.0.1:${address.port}`;
  try {
    assert.equal((await request(origin + '/large')).status, 0);
    assert.equal((await request(origin + '/hang', undefined, 20)).status, 0);
    assert.equal((await request(origin + '/slow', undefined, 20)).status, 0);
    assert.equal((await request(origin + '/redirect')).status, 302);
    const directory = join(mkdtempSync(join(tmpdir(), 'sre-client-')), 'batch');
    assert.deepEqual(await run({target: origin, output: directory, attempts: 8, concurrency: 2, acknowledged: true}), {attempts: 8, failures: 4});
    const events = readFileSync(join(directory, 'events.jsonl'), 'utf8').trim().split('\n').map((line: string) => JSON.parse(line));
    assert.equal(new Set(events.map((event: {id: number}) => event.id)).size, 8);
    assert.equal(events.filter((event: {status: number}) => event.status === 503).length, 4);
    assert.equal(readFileSync(join(directory, 'client-spans.jsonl'), 'utf8').trim().split('\n').length, 8);
    await assert.rejects(run({target: origin, output: directory, attempts: 1, concurrency: 1, acknowledged: true}));
  } finally { server.closeAllConnections(); await new Promise<void>((done) => server.close(() => done())); }
});

test('target fingerprint mismatch rejects load before creating evidence', async () => {
  const server = createServer((_incoming, response) => response.end(JSON.stringify({lab: 'different-service'})));
  await new Promise<void>((done) => server.listen(0, '127.0.0.1', done));
  const address = server.address();
  assert(address && typeof address !== 'string');
  try {
    await assert.rejects(run({target: `http://127.0.0.1:${address.port}`, output: join(tmpdir(), 'unused-sre-fingerprint'), attempts: 1, concurrency: 1, acknowledged: true}));
    assert.throws(() => request('http://example.com/work'));
    assert.throws(() => request(`http://127.0.0.1:${address.port}/health`, undefined, 0));
  } finally { await new Promise<void>((done) => server.close(() => done())); }
});
