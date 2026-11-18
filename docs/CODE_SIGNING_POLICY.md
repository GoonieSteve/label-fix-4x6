# Code signing policy — LabelFix 4×6

**Current status: NOT YET APPROVED by SignPath Foundation. The publicly distributed EXE is currently unsigned.**

Upon acceptance, the release page will state: **“Free code signing provided by SignPath.io, certificate by SignPath Foundation”**. Signatures are not claimed before approval.

## Roles
- **Authors / source maintainers:** the owner of the public LabelFix repository (initial project maintainer: [@GoonieSteve](https://github.com/GoonieSteve)).
- **Reviewers:** trusted repository owner(s) review external pull requests prior to merge; authors cannot self-approve changes proposed by other contributors.
- **Signing approver:** repository owner, who must explicitly approve **each** production signing request after source diff, tests, source provenance, and release assets have been reviewed.
- **Authentication:** all authors, reviewers and approvers must enable MFA on GitHub and SignPath.

## Build provenance and permissions
- Only approved release tags from the **public** project repository are eligible for signing.
- A clean Windows GitHub Actions runner checks out the source at the release commit; builds and tests happen in CI.
- Dependencies and official Keys Web & IT artwork are pinned in the public repository and must be verified; never submit third-party upstream DLLs for *our* signing unless permitted by SignPath rules.
- No binary downloaded from an unverified external server may replace artifacts built from the public repository in the signing path.
- Signing is manual and will only be enabled after Foundation approval and configuration.
- The release includes checksum, license, documentation and a link to source/tag.

## Privacy
The application processes user-selected shipping PDFs locally; it never transfers names, addresses or tracking data to the publisher or a service. Optional auto-printing deliberately sends the converted PDF to a user-selected **local installed printer** through a separately installed SumatraPDF executable. See [PRIVACY.md](../PRIVACY.md).

## Eligibility caveat
SignPath Foundation requires an established project reputation, prior public release and strict governance. A new project may be declined. Do not claim certification or publisher identity until a signature is issued and verified.
