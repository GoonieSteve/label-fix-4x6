# Microsoft Store submission — preparation, not yet submitted

Microsoft offers free registration for both Individual and Company developer accounts. For business software offered under Keys Web & IT, choose **Company** and verify the legal LLC/organization identity. An Individual account displays the individual publisher instead; Microsoft does not support converting an Individual account into a Company account.

1. Go to https://storedeveloper.microsoft.com/ and register a Company developer account (free). Microsoft requires official business documents or D-U-N-S details, plus domain/work-email verification as applicable. The account owner must do the identity verification and accept agreements.
2. In Microsoft Partner Center, reserve an app name (e.g., **LabelFix 4×6**).
3. In the reserved app's Product identity page, copy the **exact Package/Identity Name** and **Publisher** distinguished name. Never guess; placeholders will not pass certification.
4. Run `.github/workflows/windows-portable-and-msix.yml` with those exact values (or use `scripts/build_msix.ps1` on Windows with the Windows SDK). The package is an MSIX full-trust desktop package with an x64 exe and conch images.
5. Review the unsigned package with the Windows App Certification Kit; test installing via a temporary self-signed development certificate on a separate Windows test system before Store submission. **Do not distribute developer-signed or unsigned preview MSIX to end users.**
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
