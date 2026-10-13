# Security boundary and reporting

Created by Jason Stys. [Contact through LinkedIn](https://www.linkedin.com/in/jason-stys-31b30b351/) or [GitHub](https://github.com/JasonStys). Do not put credentials, real customer data or exploit payloads into a public issue. This is an author-reviewed educational lab, not an independent security audit or production certification.

## In scope

Synthetic operations on the exact owned 127.0.0.1 listeners. No arbitrary DNS targets, account credentials, remote exporter, network fault-control endpoint, ads, scripts in reports, code execution from input, production scanning, paid cloud account or local Docker changes. The bounded client checks its lab marker and requires an ownership acknowledgement, but that marker is **not authentication** against another local process.

Services intentionally have no user accounts or TLS and must not be exposed publicly. Another process/user on this PC can reach loopback; local administrators can inspect files/process memory. 0700 directories/0600 client files are best-effort platform permissions; Windows ACLs are inherited, and evidence is not encrypted. Do not feed personal/production data into this lab or claim account privacy beyond these constraints.

## Controls

- Closed evidence schema, bounded parsing, explicit integer units, exclusive outputs and no shell eval.
- Literal local targets, finite load/concurrency, absolute client deadline, response cap, worker upstream timeout, fixed paths and no redirect following.
- Logs/spans never serialize raw HTTP URLs, query strings, headers, baggage, payloads, arbitrary span attributes, exceptions or provider keys. Fixed service/status labels avoid personal identifiers and high cardinality.
- Structured request correlation accepts validated W3C IDs but does not use IDs as identity/authentication.
- Escaped inert HTML with restrictive CSP, no JavaScript/CSS/assets/network fetches. SQLite inserts use bound parameters; schema is trusted checked-in source, not user SQL.
- Full hashed Python/npm graphs; official tool digests before one-member regular-file extraction, pinned GitHub actions, read-only checkout credentials and least-scoped CodeQL upload permission.
- Digest-pinned transient CI Grafana with generated password, no anonymous signup, disabled provider telemetry, capability restrictions and explicit loopback listener. No password or generated evidence is committed.

Availability is bounded, not DDoS-proof. OS/framework request parsing still has finite standard-library limits; repeated local requests can fill limited evidence retention or consume resources. Native libraries/vendor images can have future vulnerabilities. No vulnerability suppressions or automatic destructive cleanup are used. Report counts/trace IDs are synthetic; provenance completeness is asserted, not signed.
