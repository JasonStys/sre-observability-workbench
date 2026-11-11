# SRE Observability Workbench native application

Created by Jason Stys · [GitHub](https://github.com/JasonStys) · [Contact](https://www.linkedin.com/in/jason-stys-31b30b351/)

The Windows x64 portable `SreObservabilityWorkbench.exe` bundles the actual project core, SQLite history, Python 3.14.10/Tk 9 runtime, authored examples and runtime notices. End users launch one file, with no separately installed Python, Node, Docker, account or setup commands. This is a portable application, not an MSI/NSIS installer. Publishing and creating its individual desktop shortcut are separate reviewed steps; this source change does not install anything or reset user data.

## Actual project workflows

The **owned fault/recovery drill** starts only its own two numeric-loopback services on OS-assigned ports. Choose 1–50 attempts, finite fault frequency/last fault-eligible call, 0–100ms worker delay and explicit SLO settings. No arbitrary target, hosted collector, notification delivery or exporter is offered. A fixed 15-second request-schedule deadline stops new work; missing attempts remain visible. Actual client failures are retained as status0, not invented success. Real gateway/worker SDK spans and logs are correlated against each attempted client context; gaps remain explicit. The portable Python client does not export a separate client SDK span. The original TypeScript SDK client and actual Prometheus/Grafana verification remain distinct CLI/CI paths.

**Assess request evidence** accepts the original bounded JSONL contract, UTC epoch milliseconds, expected attempt count and exact-unit policy. A blank expected count remains unverified; missing/future/low-volume evidence cannot silently become complete. **Compare objective settings** requires an explicit expected count and compares the same records/window/volume floor. Looser success/latency objectives are flagged for review, never labeled operational recovery. **Review service/journey bundle** opens the original closed manifest contract with distinct local sibling JSONL files and owner queues; unrelated streams are not pooled.

The included checkout/warehouse examples are clearly fictional retail streams ending 2026-11-09T12:00:00Z, with 20 one-second-spaced records per stream, independent trace identities, two slow checkout successes and one warehouse HTTP 503. Prepared cases populate these same controls; they do not run until permission is acknowledged. Change the selected files and settings for your own supported synthetic evidence.

## Inspect, retain, export and exit

Results are actual core outputs, not simulated UI rows. Select an evidence view, use a literal search across the full record and select a row to inspect its complete JSON. The visible table caps 5,000 rows; exact complete bundles remain exportable. No input is interpreted as a command, plugin or Python expression. Unsupported or malformed input is rejected without substituting a prepared sample or clearing prior results.

The **Saved analyses** tab reopens verified original bytes without recalculating old evidence against today's inputs. **Export selected analysis bundle** creates a new private directory and refuses overwrite. **Remove selected local copy** requires confirmation and the selected exact hash manifest; it removes only that retained database copy, leaving input/export files unchanged. Run identities are not reused. **Help**, **Licenses** and **Exit application** remain available. Native close/Exit waits for the captured background operation and SQLite transaction; closing during work does not abandon the writer.

The default Windows workspace is `%LOCALAPPDATA%\JasonStys\SreObservabilityWorkbench`. It is version-independent and outside the executable/source; `--profile PATH` is an advanced explicit alternative, not required for desktop launch. Unknown nonempty profiles, linked/junction paths, install/source-contained profiles and concurrent owners are refused. The profile marker, single-owner lock and bounded `history.sqlite` contain plaintext OS-owner evidence. They do not establish multiuser identity or resist administrators/local malware.

History retains at most 20 runs, 128 MiB of payloads, 64 MiB per bundle, 32 MiB per file and eight files per bundle. Parameters/SQLite/filesystem overhead add space. Capacity failures preserve earlier evidence and require deliberate retention/export choices. Logical removal is not forensic erasure and may not shrink the database file. Back up the entire profile after a clean exit before replacing an executable. Removing the executable leaves saved data intact. Only synthetic profile restart was exercised; a populated real-user migration has not been tested.

## Build and actual package acceptance

Use a separate reviewed Windows CPython **3.14.10** SDK; no global Python/PATH/registry upgrade is needed:

```text
python -m pip install --require-hashes -r requirements-dev.lock -r requirements-native.lock
python scripts/build_native.py
python scripts/test_native_app.py
```

The official reference SDK supplies Tcl/Tk 9.0.4 using DLL zipfs. The builder reads its actual runtime notices, retains the authored/runtime/bootloader licenses, refuses older Python and binds actual bundled `python314.dll` bytes. Startup checks exact source/dirty/resource identities before opening a profile. Checksums are byte-integrity evidence, not Authenticode or publisher authentication. The source GUI remains usable on macOS/Linux with an appropriate Tk runtime; frozen acceptance here targets Windows x64, not mobile or every OS.

Acceptance drives the same real widgets/handlers/mainloop against explicit marked synthetic profiles, checks independent domain oracles, literal filters/detail, exact export, rejection and a second real process reopening identical saved bundle hashes. It captures only its owned window through PrintWindow, with no desktop fallback. Test flags cannot open normal profiles or convert a partial run into success. The child receives no Python/Node/provider environment and uses only the Windows system directory on PATH. No default user workspace or installed application is used.

See [dated native observations](reports/native-application-2026-11-10.md), the existing [testing strategy](testing.md), and [PyInstaller one-file behavior](https://pyinstaller.org/en/stable/operating-mode.html#how-the-one-file-program-works). Tk work stays on the [Tk main thread](https://docs.python.org/3.14/library/tkinter.html#threading-model); analysis runs in one owned worker. Existing source CLI, cross-platform, security, coverage and project-specific external-tool gates remain mandatory.
