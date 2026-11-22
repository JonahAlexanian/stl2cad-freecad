# Security policy

## Supported versions

Security fixes apply to the current release on the `main` branch. Older tags are unsupported unless noted in a release.

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

## Reporting a vulnerability

**Do not** file a public GitHub issue for security-sensitive reports.

Use one of these private channels:

1. **GitHub:** [Private vulnerability report](https://github.com/JonahAlexanian/stl2cad-freecad/security/advisories/new) for this repository.
2. **GitHub issue with confidential note:** open an issue only if you cannot use advisories, and ask a maintainer to restrict visibility.

Include steps to reproduce, affected version (`package.xml` / git tag), and impact if known.

## Scope

| In scope | Out of scope |
|----------|----------------|
| Code in this repo under `freecad/stl2cad/` | The **stl2cad.com** hosted service (report via [RAG Box](https://ragbox.llc/) / site operator) |
| Consent, uploads, and downloads to `https://www.stl2cad.com` as implemented by this add-on | FreeCAD core or third-party add-ons |

## Response expectation

- **Acknowledge** reports within about **7 days**.
- For confirmed issues in this add-on, aim for a fix or documented mitigation within about **30 days**, depending on severity.

Maintainer contact for package metadata: see `package.xml` (`<maintainer>`).