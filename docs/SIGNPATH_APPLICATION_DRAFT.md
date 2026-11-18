# SignPath Foundation application — draft (NOT submitted)

**Project:** LabelFix 4×6  
**Project homepage:** https://keyswebit.com/ (replace with actual LabelFix library landing page when published)  
**Public GitHub repository:** https://github.com/GoonieSteve/label-fix-4x6 (create this public repo before submitting)  
**License:** AGPL-3.0-only  
**Category:** Desktop utility, Windows 10/11

## Suggested project description
LabelFix 4×6 is a free and open-source Windows desktop utility that extracts supported carrier shipping labels from Letter/A4 PDF sheets, rotates/crops them to 4×6 pages, preserves barcodes when possible, and offers an optional local Downloads-folder watcher and user-controlled thermal printing. It processes files locally without user accounts, telemetry, uploads or bundled adware.

## Distribution / source provenance
- Public repository contains complete first-party source, build scripts, license, test suite and dependencies.
- GitHub Actions compiles from the checked-out public release tag, tests with synthetic PDFs, packages Windows binary, and supplies build provenance and checksums.
- The public download is already available unsigned before approval, as SignPath requires an already-released project.
- Maintainer(s) enforce MFA, review outside contributions, and manually approve each signing request.
- Code signing policy: `docs/CODE_SIGNING_POLICY.md`; privacy: `PRIVACY.md`; security: `SECURITY.md`.

## Before applying
1. Create the public repo and upload the full contents of this kit (not a zip upload containing private labels).
2. Publish the unsigned downloadable release with clear unsigned status and truthful documentation, and point the library page at it. Do not advertise it as signed or Defender-approved.
3. Add public code-signing-policy link to repo README AND library download page.
4. Confirm GitHub MFA for each maintainer and a human release approver.
5. Review license compatibility of dependencies and bundle content (especially PyMuPDF AGPL obligations).
6. Apply at https://signpath.org/apply.html . Rejection is possible for lack of established public reputation.

**No application was submitted by this file.**
