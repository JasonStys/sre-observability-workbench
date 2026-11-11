# Installed Windows 1.1.1 validation · 11 November 2026

By Jason Stys. These observations refer to the independently downloaded, published **1.1.1** application built from `9e7f7789a0dd1d93c44dd26088de86812abc6d96`. Historical 1.1.0 documents and release assets remain unchanged.

## Actual installed results

**Actual installed workflows: Passed.** Full original domain, review and export controls passed two normal native launches; all 4 saved bundles retained exact original bytes.

**Old-to-new profile: Passed.** The actual installed 1.1.0 app created a synthetic profile; installed 1.1.1 reopened it and retained all 4 exact bundles without reset.

**Source and distribution: Verified.** Exact-main workflows and processed CodeQL passed with zero open main alerts. Five downloaded assets and installed files matched their verified SHA-256 identities.

**PC and links: Verified.** Existing links were backed up and retargeted with settings retained. Normal profiles and Docker were unchanged; default-profile shortcut activation remains separately untested.

## User workflow and implementation

The [four-page illustrated guide](windows-application-guide-1.1.1.docx) contains two actual installed-app screenshots, a practical user journey, an immutable-source code excerpt and measured validation with operating limits. The [review manifest](windows-application-guide-1.1.1.json) binds the Word, screenshot, code-source and rendered-page hashes. All 40 final page contents across this batch were individually inspected; each Office package passed schema validation. Prepared data stays inside the actual application workflow.

## Installation, private data and limitations

Download the matching Windows EXE and SHA256 sidecar from Releases. This is an unsigned portable app, not an MSI; Python installation and terminal commands are unnecessary. Keep the distribution and runtime notices together.

Open your own new or identified profile outside the installation. History is local plaintext protected by OS-owner access and an exclusive instance lock. Use Help for formats and limits; Exit application closes the owned workbench.

The app runs only a finite owned loopback service. It is not a production monitoring deployment or an external telemetry collector. Local synthetic evidence does not establish an operational SLO.

Reviewer names are assertions, not authenticated identities. These tests used isolated synthetic profiles and did not access existing user data, call external services or change Docker. Back up your complete profile before moving it.

The actual installed 1.1.0 app created the synthetic profile used for the 1.1.1 upgrade test. Saved evidence retained exact bytes after the new app reopened it; no normal user profile was opened or reset. Desktop and Start-menu links were backed up and retargeted, retaining other settings. Target/arguments/read-back verification is distinct from default-profile shortcut activation, which was not independently exercised. Docker was unchanged. This documentation change requires its own full hosted checks; the runtime observations do not certify later source changes.
