"""Reproduce the official v1.2.1 cx_Freeze Windows build.
Install: python -m pip install -r requirements.txt 'cx_Freeze>=8,<9' pillow
Generate branding/keyswebit.ico from https://keyswebit.com/favicon.ico (may be PNG by URL).
Run: python setup_cxfreeze.py build_exe
"""
from cx_Freeze import setup, Executable
setup(
    name='LabelFix 4x6', version='1.2.1',
    description='Local shipping-label PDF converter',
    options={'build_exe': {
        'build_exe': 'dist/LabelFix4x6',
        'packages': ['pymupdf','tkinter'],
        'includes': ['label_core'],
        'include_files': [('branding/keyswebit.ico', 'branding/keyswebit.ico')],
    }},
    executables=[Executable('label_app.py', base='gui',target_name='LabelFix4x6.exe', icon='branding/keyswebit.ico')],
)
