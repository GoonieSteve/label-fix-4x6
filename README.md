# LabelFix 4×6

**Free Windows shipping-label PDF converter by Keys Web & IT**  
Version **1.2.1** · November 2026 · Free / open source (AGPL-3.0-only)

Turn many shipping labels supplied on **US Letter (8.5 × 11 or 11 × 8.5 in)** and **A4** PDF sheets into true **4 × 6-inch (100 × 150 mm nominal)** PDF pages for thermal label printers. Designed around the everyday task of downloading emailed Vinted shipping labels, but also recognizes a number of common carrier label layouts.

**What it does**: Recognizes a shipping label, trims excess page area, straightens common rotated layouts, and preserves original PDF vector content—including sharp barcode lines—where possible. Save a corrected copy or optionally send it to a selected Windows printer.

## Quick start for Windows users

**Recommended: Windows portable download (no Python needed)**

1. Download the `LabelFix4x6-Windows-portable-v1.2.1.zip` file from Keys Web & IT.
2. Right-click the ZIP and choose **Extract All**.
3. Open the extracted `LabelFix4x6` folder and double-click **`LabelFix4x6.exe`**. Keep the accompanying DLLs and support files in the same folder. Do not move or email just the EXE.
4. Select a PDF to convert, or start watching Downloads. Set up optional auto-printing only after confirming manual conversion works.

**Alternative: Source code ZIP** (requires Python for local setup):

1. Extract the ZIP to a permanent folder (for example, `Documents\LabelFix4x6`). Do **not** run the BAT files inside the compressed ZIP.
2. Install **Python 3** from https://www.python.org/downloads/windows/ if not already installed. Use Python 3.11–3.13 for the published source-based setup. The installation needs `pip` and `venv`.
3. Double-click **`SETUP_FIRST.bat`** once. This creates a private environment and installs the PDF dependency from PyPI. Internet access is needed for initial setup.
4. Double-click **`START_CONVERTER.bat`** to open LabelFix.
5. Click **Choose PDF(s) to convert** to convert one or more downloaded labels; then click **Open converted labels** to find the finished PDFs.

> This source ZIP includes the full build instructions, not a precompiled EXE. If the Windows portable download is unavailable, the source setup remains supported. Do not download an unsigned EXE from an untrusted mirror.

## Automatic Downloads folder monitoring

1. Leave the app open and click **Start watching Downloads**.
2. Download a new shipping-label PDF from Gmail, your browser, or another source. Use **Download**, not your browser's Print button.
3. LabelFix recognizes supported labels and saves converted copies in `Downloads\LabelFix_4x6_Labels` by default.
4. PDFs that cannot be confidently recognized as shipping labels are skipped, not force-converted.
5. Files already present before monitoring starts are **not** automatically printed. Use **Retry newest downloaded PDF** or manually select a PDF if you need to process an earlier download.

You can choose a different watch folder and a separate output folder. Keep those folders distinct to avoid repeatedly processing your own outputs. Monitoring runs only while the application is open.

## Optional automatic printing

Auto-print is **off by default**. To enable it:

1. Install the separately distributed free **SumatraPDF** application from https://www.sumatrapdfreader.org/ .
2. Open your printer's Windows **Printing preferences** and select **4 × 6-inch** labels, portrait, 1 page per sheet, with the correct gap label media. For JADENS JD-268BT users, a speed of **4** and density of **8** solved one real-world barcode stop problem; your printer may need different values.
3. Restart LabelFix and select the correct printer from its list.
4. Check **Print automatically after conversion**.
5. Click **Start watching Downloads** and download a **new** recognized shipping-label PDF.

LabelFix submits the finished PDF to your selected printer through SumatraPDF, using `noscale` (actual-size printing). A “submitted” message only confirms the print command was accepted; it cannot confirm paper and ink/thermal output. Check the full barcode on the first physical label and scan it if possible. Don't ship cropped or unreadable labels.

**Don't want auto-print?** Leave the checkbox off. Converted PDFs are always saved locally and can be printed manually.

## Supported documents & limitations

- Windows desktop GUI (Tkinter); source-based installation requires Python.
- Designed for PDF shipping labels on portrait/landscape US Letter or A4, plus already correctly sized 4 × 6 PDFs; 1–20 PDF pages and up to 70 MB.
- Recognizes some USPS, FedEx, UPS, Vinted, Evri, InPost and other label patterns; **not** every carrier/template is supported.
- Works best with sharp original PDF artwork. Some scans/image-only PDFs may be skipped if they cannot be confidently identified.
- Rejects unrelated reports/invoices rather than cropping them automatically.
- The program does **not** fetch emails, log into Gmail/Vinted, or access any carrier account. You download the PDFs yourself.
- Conversion takes place **locally**. There is no telemetry, no built-in upload feature, and no automatic updates.
- Requires SumatraPDF installed separately for silent/direct printing. The converter does not install it or include it.
- The app can't guarantee barcode readability, thermal printer calibration, carrier acceptance, or physical print completion.
- Compatibility with other printers is not guaranteed; test one label before relying on auto-print.

## Updating from the original JADENS/Vinted converter

LabelFix can load printer and folder preferences from the prior `JADENS4x6Converter` configuration if it finds them and no new LabelFix preferences exist. **Copying the new source files directly over an older app is not recommended.** Extract LabelFix in its own separate folder, run setup once, and test conversion and manual printing before enabling auto-print.

## Troubleshooting

| Symptom | What to do |
| --- | --- |
| PDF skipped as unsupported | Check it really contains a shipping label. Use **Choose PDF(s)** to retry a particular file. Unsupported templates may require a converter update. |
| 11 × 8.5-inch PDF still skipped | Confirm you are using LabelFix **1.2.1** and not the original 1.0 converter. Download the PDF, not the web viewer page. |
| App opens but does not print | Install SumatraPDF, restart LabelFix, select a printer, and explicitly enable auto-print. |
| Paper cuts off halfway through the barcode | Check printer feed calibration, 4×6 paper selection, printing density/darkness, speed, and driver preferences. |
| Printed label is too small | Use 4×6 media and actual-size output, not Letter or Fit-to-page. |
| Nothing happens after running START_CONVERTER | Run `DEBUG_LAUNCH.bat` and read the error; verify setup completed. |
| Already-downloaded file isn't processed | Click **Retry newest downloaded PDF** or **Choose PDF(s)**; the watcher intentionally only detects new files. |

## Privacy & safety

Shipping labels often contain names, addresses and tracking numbers. This software leaves the original PDFs untouched and stores converted copies on your PC. Avoid uploading real shipping labels to public bug reports or sharing screenshots that expose customer information. See `PRIVACY.md` and `SECURITY.md` for details.

## License & dependencies

LabelFix source is distributed under the **GNU Affero General Public License, version 3 only (AGPL-3.0-only)**. See `LICENSE` for the full license. This project uses **PyMuPDF**, which offers an open-source AGPL or commercial license; see `THIRD_PARTY_NOTICES.md` and https://pymupdf.io/licensing . SumatraPDF, if you choose it, is downloaded and installed separately from its own official site. The source package does not redistribute PyMuPDF wheels or SumatraPDF binaries.

**Unofficial product.** LabelFix is an independent utility made available by Keys Web & IT. It is not affiliated with or endorsed by Vinted, JADENS, USPS, FedEx, UPS, Google or SumatraPDF.

**No warranty.** Provided “as is,” without warranty of fitness for shipment, printer compatibility or carrier acceptance. Verify labels before mailing.

## For developers

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe label_app.py
```

To build a portable Windows EXE on a **Windows** machine, run `BUILD_WINDOWS_EXE.bat` or trigger the included GitHub Actions workflow. See `BUILDING.md`. Python build environments cannot cross-compile Windows executables from Linux.

## Antivirus reports and software trust

This release is currently **unsigned**. Windows Defender or SmartScreen may flag new unsigned software, especially if the file has not yet established a download reputation. Treat an actual malware quarantine seriously: do not disable antivirus or add exclusions to use LabelFix. Open **Windows Security → Virus & threat protection → Protection history** and record the detection name, quarantined file path, and version. Report a suspected false positive to Microsoft at https://www.microsoft.com/en-us/wdsi/filesubmission and share the precise alert with Keys Web & IT. The owner must verify the alert before calling it a false positive. Source code is provided for audit under AGPL-3.0-only.

## Build provenance

The v1.2.1 release candidate portable EXE uses cx_Freeze, with its full PSF-style license included as `frozen_application_license.txt`. `BUILD_CXFREEZE.md` and `setup_cxfreeze.py` reproduce the build; `BUILDING.md` describes the alternative Nuitka method. Both methods bundle Python for end users. Neither method is a substitute for Defender review or code signing.


## Code signing policy and public release preparation

See [Code signing policy](docs/CODE_SIGNING_POLICY.md), [SignPath application preparation](docs/SIGNPATH_APPLICATION_DRAFT.md), and [Microsoft Store packaging](docs/STORE_SUBMISSION_GUIDE.md). Signing is **not currently approved or active**.
