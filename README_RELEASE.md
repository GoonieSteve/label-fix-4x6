# LabelFix 4×6 — two free distribution routes

This kit contains the source of LabelFix 4×6 v1.2.1 and pinned official Keys Web & IT branding, six synthetic-PDF regression tests, reproducible Windows compilation code, an **unsigned** MSIX packaging workflow, and the documentation needed to apply for SignPath Foundation's open-source code-signing program.

## Work already completed
- v1.2.1 source and previously tested x64 cx_Freeze executable are available.
- SignPath application text and a code-signing policy have been drafted but **not submitted**.
- A GitHub Actions workflow builds the portable EXE **from checked-out repository source** and builds a Store-package MSIX. Source code must be public for a Foundation application.
- The Store MSIX uses preview identity unless you supply exact assigned identity values from Partner Center. A preview MSIX is **not suitable for submission or end-user install**.

## Next actions
1. Create public https://github.com/GoonieSteve/label-fix-4x6 and commit the contents of this directory (not the surrounding zip).
2. Enable GitHub MFA; review project license and security; publish a versioned unsigned release and link your site.
3. Follow `docs/SIGNPATH_APPLICATION_DRAFT.md` to apply at https://signpath.org/apply.html. Foundation approval is discretionary and public reputation is a factor.
4. Register a free Microsoft Store Company developer account and reserve the name; follow `docs/STORE_SUBMISSION_GUIDE.md`. Provide exact Name and Publisher values for a production MSIX build.

No signature, Microsoft Store approval, or Defender guarantee is claimed. See `docs/PUBLIC_LAUNCH_CHECKLIST.md`.
