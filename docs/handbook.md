# SRE Observability Workbench handbook

By Jason Stys.

Compare owner/service/journey SLO bundles over identical windows, with quality, burn and weakened-objective review queues.

Compare owner/service/journey SLO bundles over identical windows, with quality, burn and weakened-objective review queues.

Prevents pooled availability and changed denominators from hiding a failing user journey.

## Read the documentation

| Edition | Audience and contents |
| --- | --- |
| [project-guide.docx](reports/project-guide.docx) | User and developer guide: purpose, current usage, design, boundaries and source references. |

The editable Markdown remains the maintenance source. The Word files are readable editions. See [publication identities and review](reports/publications.json) and the [documentation refresh record](reports/documentation-refresh-2026-11-09.md).

## Current usage and help

[README quick start](../README.md) is the entry point. Use the project-specific guides below before changing inputs, operating modes or deployment assumptions.

### Usage and operations

- [runbook](runbook.md)

### Design and contracts

- [architecture](architecture.md)
- [research](research.md)

### Security and validation

- [testing](testing.md)

## Historical results and reproduction

The reviewed source is [`8027d600ca0f1cb0575e8a23ff0147d3376046cb`](https://github.com/JasonStys/sre-observability-workbench/tree/8027d600ca0f1cb0575e8a23ff0147d3376046cb). The observed functional workflow baseline is `8027d600ca0f1cb0575e8a23ff0147d3376046cb`; those observations are recorded at `2026-11-10T05:25:40.628667+00:00`. They do not certify an unrun later revision.

- [Detailed recorded validation](reports/journeys-2026-11-09.md)
- [Current Actions](https://github.com/JasonStys/sre-observability-workbench/actions) records later integration checks separately.
- Preserve dated measurements and follow the existing testing guide to reproduce them; a test-source inventory alone does not establish execution.

## Practical boundaries

- Synthetic local streams; completeness, ownership and disjointness declarations remain operator assertions.
- Matched-window review does not pool unlike journeys or automatically approve weakened objectives.
- No automatic PromQL/dashboard rewriting or production SLO-policy enforcement is supplied.

## Maintaining these editions

Update the editable usage/design/test documents first. Rebuild and visually review every Word page and workbook tab before replacing an edition; verify the exact binary digests and evidence source in publications.json. Keep account data, logs with secrets, installed-app state and private test stores out of documentation. Source and release assets retain their existing security and licensing boundaries.

## Native graphical application

[First-use controls, supported workflows, profile/retention safety and actual portable acceptance](native-application.md) describe the new real application. [Dated observations](reports/native-application-2026-11-10.md) remain distinct from historical publications and pending release/installation.
