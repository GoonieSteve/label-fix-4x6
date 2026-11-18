# Security notes

- **Never enable automatic printing until a test label looks correct.** Unfamiliar shipping label templates can be skipped or interpreted incorrectly; watch the first print and check the tracking barcode.
- The app does not execute PDF JavaScript or scripts, but relies on PyMuPDF to parse PDF structure. Only open PDFs from sources you trust and keep Python/PyMuPDF up to date.
- PDFs larger than 70 MB, encrypted PDFs, and documents over 20 pages are not converted.
- The source ZIP contains readable BAT scripts and Python files. The Windows portable build bundles a Python interpreter and PDF libraries, so only obtain EXE builds from a source you trust. The EXE has no installation wizard and requires no administrative privileges.
- If you build a Windows portable executable using PyInstaller, it will be unsigned unless you code-sign it. Windows SmartScreen may warn about an unsigned app. **Do not tell users to disable antivirus or SmartScreen.** Code signing and Windows hardware testing are recommended before broad public distribution.
- The application never modifies or deletes original shipping labels and intentionally skips ambiguous documents. The watcher does not process existing downloads automatically when started.
- This is an independent utility and not an official postal or shipping-provider application.
