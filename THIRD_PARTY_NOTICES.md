# Third-party software and license notices

## PyMuPDF (PDF processing)

Project: https://pymupdf.io/  
Source: https://github.com/pymupdf/PyMuPDF  
License: **GNU AGPL v3 / Artifex commercial dual-license**. This project uses the AGPL option.  
Full AGPL-3.0 license text is included in this source ZIP as `LICENSE` (the same license applies to LabelFix code).

PyMuPDF is **not** included as a wheel in this source ZIP: first-time setup downloads the installed version selected by `requirements.txt` from PyPI. For proprietary redistribution without AGPL obligations, seek appropriate licensing advice and, where necessary, a commercial license from Artifex.

## SumatraPDF (optional print helper)

Site: https://www.sumatrapdfreader.org/  
Source: https://github.com/sumatrapdfreader/sumatrapdf

SumatraPDF is an **optional, separate install** and is not included in this package. Consult its official repository for license terms and obtain it from its official site.

## Python / Tkinter

Python is provided separately by the Python Software Foundation. Tkinter is part of standard Python distributions where available. Python runtime is **not** included in the source archive. The Windows portable executable, when built with cx_Freeze or Nuitka, bundles the required Python runtime and libraries; the AGPL license and applicable third-party notices must accompany the binary.

## Other organizations

Vinted, JADENS, USPS, FedEx, UPS and Google are third-party trademarks of their respective owners. Mentioning them describes compatible workflows only; the program is not associated with or endorsed by them.

## Additional components present in the Windows portable build

The Windows v1.2.1 cx_Freeze release candidate includes runtime and library binaries. See the corresponding license terms at the upstream projects; this list is provided for transparency and is not a substitute for reviewing every license obligation before wide redistribution.

- **Python 3.12 runtime** — Python Software Foundation License (https://docs.python.org/3/license.html).
- **cx_Freeze** — PSF-derived license (https://cx-freeze.readthedocs.io/en/stable/license.html); the distributable contains `frozen_application_license.txt`.
- **Nuitka** — Apache License 2.0 (alternative build-time compiler; https://nuitka.net/).
- **Pillow** (build-time icon conversion) — HPND-style open-source license (https://github.com/python-pillow/Pillow/blob/main/LICENSE).
- **OpenSSL 3** (bundled Python SSL runtime) — Apache License 2.0 (https://www.openssl.org/source/license.html).
- **Tcl/Tk** (Tkinter GUI runtime) — Tcl/Tk open-source license (https://www.tcl-lang.org/software/tcltk/license.html).

Do not remove license/notice documents when repackaging. Maintain corresponding source and distribution records for every public version.
