# Changelog

## v1.2.1 — Windows Defender packaging revision
- Replaced PyInstaller with cx_Freeze standalone packaging in the release candidate; a separate Nuitka build is also available for reproducible comparison.
- Eliminated the PowerShell process previously launched when listing installed printers; now uses Winspool EnumPrintersW directly.
- Preserved label conversion, optional auto-printing, and original PDF handling.
- Updated brand icon and transparent release/security documentation.
- **Not a guarantee** against antivirus detection; signing and Microsoft analysis remain recommended for public releases.

## v1.2.0
- Supported Letter/A4 landscape and portrait conversion, one/multiple label pages, Downloads monitoring, and opt-in printing.
