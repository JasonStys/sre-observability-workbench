/** Generate/check exact TypeScript and JavaScript AST symbol headers. Created by Jason Stys. */
// BEGIN CODE MAP (generated; npm run maps)
// variable: root — line 36
// variable: begin — line 37
// variable: end — line 38
// definition: mapped — line 41
// parameter: name — line 41
// parameter: original — line 41
// variable: source — line 42
// variable: insertion — line 43
// variable: file — line 44
// variable: records — line 45
// parameter: node — line 47
// definition: visit — line 47
// variable: label — line 49
// variable: kind — line 50
// variable: line — line 51
// variable: count — line 57
// variable: header — line 58
// parameter: left — line 58
// parameter: record — line 58
// parameter: right — line 58
// variable: check — line 62
// variable: stale — line 63
// variable: folder — line 64
// parameter: entry — line 65
// variable: name — line 65
// variable: path — line 66
// variable: original — line 67
// variable: expected — line 68
// END CODE MAP
import ts from 'typescript';
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
const begin = '// BEGIN CODE MAP (generated; npm run maps)';
const end = '// END CODE MAP';

/** Remove the old header, walk compiler syntax nodes, then offset every recorded definition to its final line. */
function mapped(original, name) {
  const source = original.replace(/\n\/\/ BEGIN CODE MAP[^\n]*\n[\s\S]*?\/\/ END CODE MAP\n/, '\n');
  const insertion = source.indexOf('\n') + 1;
  const file = ts.createSourceFile(name, source, ts.ScriptTarget.Latest, true, name.endsWith('.ts') ? ts.ScriptKind.TS : ts.ScriptKind.JS);
  const records = new Map();
  /** Record declarations/parameters/variables with compiler-provided source positions; no execution/eval. */
  function visit(node) {
    if (ts.isFunctionDeclaration(node) || ts.isClassDeclaration(node) || ts.isInterfaceDeclaration(node) || ts.isMethodDeclaration(node) || ts.isVariableDeclaration(node) || ts.isParameter(node) || ts.isConstructorDeclaration(node)) {
      const label = node.name?.getText(file) ?? 'constructor';
      const kind = ts.isParameter(node) ? 'parameter' : ts.isVariableDeclaration(node) ? 'variable' : 'definition';
      const line = file.getLineAndCharacterOfPosition(node.getStart(file)).line + 1;
      records.set(`${kind}:${label}:${line}`, {kind, label, line});
    }
    ts.forEachChild(node, visit);
  }
  visit(file);
  const count = records.size + 2;
  const header = [begin, ...Array.from(records.values()).sort((left, right) => left.line - right.line || left.label.localeCompare(right.label)).map((record) => `// ${record.kind}: ${record.label} — line ${record.line > 1 ? record.line + count : record.line}`), end].join('\n') + '\n';
  return source.slice(0, insertion) + header + source.slice(insertion);
}

const check = process.argv.includes('--check');
const stale = [];
for (const folder of ['client', 'scripts']) {
  for (const name of readdirSync(resolve(root, folder)).filter((entry) => /\.(ts|mjs)$/.test(entry)).sort()) {
    const path = resolve(root, folder, name);
    const original = readFileSync(path, 'utf8');
    const expected = mapped(original, name);
    if (original !== expected) { stale.push(`${folder}/${name}`); if (!check) writeFileSync(path, expected, 'utf8'); }
  }
}
console.log(stale.length ? `Code maps: ${stale.join(', ')}` : 'TypeScript/JavaScript code maps current');
if (check && stale.length) process.exitCode = 1;
