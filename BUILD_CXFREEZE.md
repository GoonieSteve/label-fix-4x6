# Reproducible cx_Freeze build for Windows

The 1.2.1 **release candidate** distributed with the rebuilt ZIP uses **cx_Freeze** (PSF-derived license) instead of PyInstaller. The same Python source and tests are used for the alternative Nuitka build. The Windows release remains unsigned and **has not been certified free from antivirus detections**.

On Windows 10/11 x64 with Python 3.12 installed:

1. `py -3.12 -m pip install -r requirements.txt "cx_Freeze>=8,<9" pillow`
2. `py -3.12 -m unittest discover -s tests -v`
3. Download official branded artwork from `https://keyswebit.com/favicon.ico`, then use Pillow `Image.open(...).save('branding/keyswebit.ico',format='ICO',sizes=[(16,16),(32,32),(48,48),(256,256)])` to create a real Windows icon. The site sometimes serves PNG data at an `.ico` URL.
4. `py -3.12 setup_cxfreeze.py build_exe`
5. Test `dist\LabelFix4x6\LabelFix4x6.exe`. Keep all DLLs and subfolders when packaging.
6. Include `LICENSE`, `README.md`, `THIRD_PARTY_NOTICES.md`, and all other release docs. Test the actual executable with Windows Defender and a real printer before publishing it publicly.

The CI workflow used to produce the binary was tested with a Windows startup smoke test and PDF conversion regression tests. Windows CI did **not** have Defender real-time protection enabled, so no clean-antivirus verdict can be inferred.

Report actual suspicious Defender detections to Microsoft with the detection name and binary: https://www.microsoft.com/en-us/wdsi/filesubmission . Do not instruct customers to disable Defender.
