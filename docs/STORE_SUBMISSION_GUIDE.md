# Microsoft Store submission — preparation, not yet submitted

Microsoft offers free registration for both Individual and Company developer accounts. A personal Microsoft account can successfully enter Partner Center, but that is not evidence that a business-branded application is eligible for publication from an Individual developer account. Current Store Policy 10.14 says a Company account is required if a reasonable consumer would interpret an app or publisher name as a business entity, or the software is being published as part of a trade or profession. LabelFix currently uses Keys Web & IT branding. Review this before submission: publish as an individual only if the listing genuinely qualifies as an individual project, under the individual's verified publisher identity, with metadata and in-app branding that comply with the policy. Otherwise wait for appropriate business registration and Company account. Microsoft does not support converting Individual to Company developer account. Source: https://learn.microsoft.com/en-us/windows/apps/publish/store-policies#1014-account-type .

1. Use the verified Microsoft Store developer account. An Individual account is only appropriate for a genuinely individual project meeting Store Policy 10.14. For a Keys Web & IT business-branded launch, a Company account is required. Account owners must complete identity verification and accept agreements.
2. In Partner Center > Apps & games > New product > MSIX or PWA app, reserve an app name (e.g., **LabelFix 4×6**).
3. In the reserved app's Product identity page, copy the **exact Package/Identity Name** and **Publisher** distinguished name. Never guess; placeholders will not pass certification.
4. Run `.github/workflows/windows-portable-and-msix.yml` with those exact values (or use `scripts/build_msix.ps1` on Windows with the Windows SDK). The package is an MSIX full-trust desktop package with an x64 exe and conch images.
5. Ensure the package's PublisherDisplayName exactly matches the real Partner Center Product identity (not the Keys Web & IT brand by default). Review the unsigned package with the Windows App Certification Kit; test installing via a temporary self-signed development certificate on a separate Windows test system before Store submission. **Do not distribute developer-signed or unsigned preview MSIX to end users.**
6. Upload the MSIX package in Partner Center, add descriptions/screenshots, pricing = Free, privacy URL (public link), support contact, and obtain Microsoft certification. The Store signs the package and hosts it after approval.
7. On keyswebit.com, link to the final published Store listing. A Store-issued signature only covers the Store package; it does not sign the separate portable zip or executable on your website.

## Functional review before certification
- The current app uses a user-selected output folder and optionally watches Downloads. Verify packaged file-system access on a physical Windows PC, including OneDrive/redirected Downloads.
- Auto-printing uses an **external separately installed SumatraPDF**. Check that packaged full-trust execution can locate and launch it. The app should still function for conversion without Sumatra.
- Test printer selection, changes of settings, manual print, auto print, all PDF layouts, and clean uninstall.
- Keep releases reproducible, ensure the license is included, and never incorporate live customer labels into screenshots or test samples.

## Official sources
- https://learn.microsoft.com/en-us/windows/apps/publish/get-started
- https://learn.microsoft.com/en-us/windows/msix/desktop/desktop-to-uwp-manual-conversion
- https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/code-signing-options
