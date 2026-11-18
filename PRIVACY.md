# Privacy — LabelFix 4×6 v1.2.0

LabelFix is a **local-only** converter. It does not require an account and has no built-in analytics, telemetry, ad tracking, or cloud processing. It does not access Gmail, Vinted, or other accounts.

**Files processed:** PDF files users select or newly download into a folder they choose to monitor. The original PDF is not modified. Converted copies are saved into the output folder chosen by the user (default: a subfolder under Downloads). The on-screen activity log may include local file names and error messages but is not transmitted by LabelFix.

**Preferences:** The app stores watch/output folder locations, selected printer name and auto-print preference in `%LOCALAPPDATA%\LabelFix4x6\preferences.json`. You can remove this file to reset preferences.

**Printing:** If you enable optional direct printing, LabelFix invokes a separately installed SumatraPDF program to submit converted files to your local Windows printing system. Printers/network print services may have their own data-handling policies.

**Internet:** The app doesn't use the network for converting PDFs. The source-based installer uses pip to download PyMuPDF, and you separately download Python and optionally SumatraPDF from their official sites.

**Sensitive information:** Shipping labels contain recipients' personal information; store and dispose of copies appropriately. Don't attach identifiable labels to public bug reports.
