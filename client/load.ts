/** Bounded loopback drill client, SDK spans and complete attempt evidence. Created by Jason Stys. */
// BEGIN CODE MAP (generated; npm run maps)
// definition: Options — line 66
// definition: bounded — line 75
// parameter: maximum — line 75
// parameter: minimum — line 75
// parameter: value — line 75
// definition: targetOrigin — line 81
// parameter: value — line 81
// variable: match — line 82
// definition: request — line 89
// parameter: timeoutMs — line 89
// parameter: traceparent — line 89
// parameter: url — line 89
// parameter: resolveResponse — line 92
// variable: done — line 93
// variable: bytes — line 94
// variable: chunks — line 95
// parameter: body — line 96
// variable: finish — line 96
// parameter: status — line 96
// variable: outgoing — line 102
// parameter: response — line 102
// parameter: chunk — line 103
// variable: timer — line 112
// definition: JsonExporter — line 118
// definition: constructor — line 120
// parameter: descriptor — line 120
// parameter: callback — line 123
// definition: export — line 123
// parameter: spans — line 123
// variable: span — line 124
// definition: shutdown — line 131
// parameter: options — line 135
// definition: run — line 135
// variable: origin — line 136
// variable: health — line 140
// variable: evidence — line 143
// variable: exporter — line 144
// variable: provider — line 145
// variable: tracer — line 146
// variable: cursor — line 147
// variable: failures — line 148
// definition: worker — line 150
// variable: id — line 152
// variable: span — line 153
// variable: correlation — line 154
// variable: started — line 155
// variable: response — line 156
// variable: record — line 157
// parameter: args — line 169
// definition: optionsFrom — line 169
// variable: values — line 170
// variable: acknowledged — line 171
// variable: index — line 172
// variable: flag — line 173
// variable: value — line 176
// END CODE MAP
import { appendFileSync, closeSync, mkdirSync, openSync } from 'node:fs';
import { get } from 'node:http';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { SpanKind, SpanStatusCode } from '@opentelemetry/api';
import { BasicTracerProvider, SimpleSpanProcessor, type ReadableSpan, type SpanExporter } from '@opentelemetry/sdk-trace-base';

export interface Options {
  target: string;
  output: string;
  attempts: number;
  concurrency: number;
  acknowledged: boolean;
}

/** Require a finite bounded integer; value is a count/deadline, not coercible text. */
export function bounded(value: number, minimum: number, maximum: number): number {
  if (!Number.isSafeInteger(value) || value < minimum || value > maximum) throw new Error('invalid bound');
  return value;
}

/** Only a literal loopback origin is accepted; no DNS, credentials, path, query or alternate encoding. */
export function targetOrigin(value: string): string {
  const match = /^http:\/\/127\.0\.0\.1:([1-9][0-9]{0,4})$/.exec(value);
  if (!match?.[1]) throw new Error('only an owned loopback lab is supported');
  bounded(Number(match[1]), 1, 65535);
  return value;
}

/** Read one small local response with an absolute deadline; redirects are returned, never followed. */
export function request(url: string, traceparent?: string, timeoutMs = 1000): Promise<{status: number; body: string}> {
  targetOrigin(new URL(url).origin);
  bounded(timeoutMs, 1, 1000);
  return new Promise((resolveResponse) => {
    let done = false;
    let bytes = 0;
    const chunks: Buffer[] = [];
    const finish = (status: number, body = ''): void => {
      if (done) return;
      done = true;
      clearTimeout(timer);
      resolveResponse({status, body});
    };
    const outgoing = get(url, {agent: false, headers: traceparent ? {traceparent} : {}}, (response) => {
      response.on('data', (chunk: Buffer) => {
        bytes += chunk.length;
        if (bytes > 1024) { finish(0); outgoing.destroy(new Error('response cap')); }
        else chunks.push(chunk);
      });
      response.on('end', () => finish(response.statusCode ?? 0, Buffer.concat(chunks).toString('utf8')));
      response.on('error', () => finish(0));
      response.on('aborted', () => finish(0));
    });
    const timer = setTimeout(() => outgoing.destroy(new Error('request deadline')), timeoutMs);
    outgoing.on('error', () => finish(0));
  });
}

/** Export only fixed SDK correlation/status/timing fields; the destination was created exclusively. */
class JsonExporter implements SpanExporter {
  /** Own the exclusively created span descriptor; no credentials or remote endpoints are stored. */
  constructor(private readonly descriptor: number) {}

  /** Serialize completed spans without arbitrary attributes, request headers or remote exporter calls. */
  export(spans: ReadableSpan[], callback: Parameters<SpanExporter['export']>[1]): void {
    for (const span of spans) {
      appendFileSync(this.descriptor, JSON.stringify({service: 'client', name: span.name, trace_id: span.spanContext().traceId, span_id: span.spanContext().spanId, status: span.status.code}) + '\n');
    }
    callback({code: 0});
  }

  /** Close only the file descriptor owned by this provider. */
  async shutdown(): Promise<void> { closeSync(this.descriptor); }
}

/** Generate every requested attempt once, retain failures/timeouts and stop after the bounded batch. */
export async function run(options: Options): Promise<{attempts: number; failures: number}> {
  const origin = targetOrigin(options.target);
  bounded(options.attempts, 1, 1000);
  bounded(options.concurrency, 1, 8);
  if (!options.acknowledged) throw new Error('owned target acknowledgement required');
  const health = await request(origin + '/health');
  if (health.status !== 200 || JSON.parse(health.body).lab !== 'sre-observability-workbench') throw new Error('not a workbench lab');
  mkdirSync(options.output, {mode: 0o700});
  const evidence = openSync(resolve(options.output, 'events.jsonl'), 'wx', 0o600);
  const exporter = new JsonExporter(openSync(resolve(options.output, 'client-spans.jsonl'), 'wx', 0o600));
  const provider = new BasicTracerProvider({spanProcessors: [new SimpleSpanProcessor(exporter)]});
  const tracer = provider.getTracer('sre.workbench.client', '1.0.0');
  let cursor = 0;
  let failures = 0;
  /** Claim an attempt before awaiting I/O; event-loop scheduling prevents duplicate IDs between workers. */
  async function worker(): Promise<void> {
    while (cursor < options.attempts) {
      const id = ++cursor;
      const span = tracer.startSpan('work', {kind: SpanKind.CLIENT});
      const correlation = span.spanContext();
      const started = performance.now();
      const response = await request(origin + '/work', `00-${correlation.traceId}-${correlation.spanId}-01`);
      const record = {schema: 1, id, at_ms: Date.now(), duration_us: Math.max(0, Math.round((performance.now() - started) * 1000)), status: response.status, trace_id: correlation.traceId, span_id: correlation.spanId};
      if (response.status < 200 || response.status >= 300) { failures++; span.setStatus({code: SpanStatusCode.ERROR}); }
      span.end();
      appendFileSync(evidence, JSON.stringify(record) + '\n');
    }
  }
  try { await Promise.all(Array.from({length: options.concurrency}, () => worker())); }
  finally { closeSync(evidence); await provider.shutdown(); }
  return {attempts: cursor, failures};
}

/** Parse a closed CLI flag set; numeric settings are validated by run before any load is sent. */
export function optionsFrom(args: string[]): Options {
  const values = new Map<string, string>();
  let acknowledged = false;
  for (let index = 0; index < args.length; index++) {
    const flag = args[index];
    if (flag === '--ack-owned-target') { if (acknowledged) throw new Error('duplicate flag'); acknowledged = true; continue; }
    if (!flag || !['--target', '--output', '--attempts', '--concurrency'].includes(flag) || values.has(flag)) throw new Error('unknown/duplicate flag');
    const value = args[++index];
    if (!value) throw new Error('missing value');
    values.set(flag, value);
  }
  return {target: values.get('--target') ?? '', output: values.get('--output') ?? '', attempts: Number(values.get('--attempts') ?? '40'), concurrency: Number(values.get('--concurrency') ?? '1'), acknowledged};
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try { console.log(JSON.stringify(await run(optionsFrom(process.argv.slice(2))))); }
  catch { console.error('Drill rejected or failed; check owned target, bounds and new output directory.'); process.exitCode = 1; }
}
