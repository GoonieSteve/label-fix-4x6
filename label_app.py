"""LabelFix 4x6 by Keys Web & IT: local Windows PDF label converter."""
from __future__ import annotations

import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from label_core import UnrecognizedLabel, convert_document, safe_output_name


def config_path() -> Path:
    base = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'LabelFix4x6'
    base.mkdir(parents=True, exist_ok=True)
    return base / 'preferences.json'


def actual_downloads() -> Path:
    home = Path.home()
    # Windows allows Downloads to be redirected to OneDrive or other locations.
    if os.name == 'nt':
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r'Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders')
            value, _ = winreg.QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')
            path = Path(os.path.expandvars(value))
            if path.is_dir():
                return path
        except (OSError, ValueError):
            pass
    return home / 'Downloads'


def find_sumatra() -> Optional[str]:
    paths = [shutil.which('SumatraPDF.exe')]
    for env in ('PROGRAMFILES', 'PROGRAMFILES(X86)', 'LOCALAPPDATA'):
        root = os.environ.get(env)
        if root:
            paths.extend([str(Path(root) / 'SumatraPDF' / 'SumatraPDF.exe'),
                          str(Path(root) / 'SumatraPDF.exe')])
    for p in paths:
        if p and Path(p).is_file():
            return p
    return None


def list_printers() -> list[str]:
    """Enumerate installed Windows printers through Winspool, without shelling out.

    No PowerShell, command prompt, network connection, elevation or installation
    is involved. This is the documented local Windows EnumPrintersW API.
    """
    if os.name != 'nt':
        return []
    try:
        import ctypes
        from ctypes import wintypes

        class PRINTER_INFO_4W(ctypes.Structure):
            _fields_ = [('pPrinterName', wintypes.LPWSTR),
                        ('pServerName', wintypes.LPWSTR),
                        ('Attributes', wintypes.DWORD)]

        enum = ctypes.WinDLL('winspool.drv', use_last_error=True).EnumPrintersW
        enum.argtypes = [wintypes.DWORD, wintypes.LPWSTR, wintypes.DWORD,
                         ctypes.c_void_p, wintypes.DWORD,
                         ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(wintypes.DWORD)]
        enum.restype = wintypes.BOOL
        flags = 0x2 | 0x4  # PRINTER_ENUM_LOCAL | PRINTER_ENUM_CONNECTIONS
        needed, returned = wintypes.DWORD(0), wintypes.DWORD(0)
        enum(flags, None, 4, None, 0, ctypes.byref(needed), ctypes.byref(returned))
        if not needed.value:
            return []
        buffer = ctypes.create_string_buffer(needed.value)
        if not enum(flags, None, 4, buffer, len(buffer),
                    ctypes.byref(needed), ctypes.byref(returned)):
            return []
        entries = ctypes.cast(buffer, ctypes.POINTER(PRINTER_INFO_4W))
        return sorted({entries[i].pPrinterName for i in range(returned.value)
                       if entries[i].pPrinterName}, key=str.casefold)
    except (OSError, AttributeError, ValueError):
        return []


def send_to_printer(path: Path, sumatra: str, printer: str) -> None:
    # SumatraPDF documents -print-to and -print-settings; 'noscale' uses the
    # true 4x6 PDF page size and existing JADENS Windows printer defaults.
    proc = subprocess.run([sumatra, '-print-to', printer,
                           '-print-settings', 'noscale', str(path)],
                          capture_output=True, text=True, timeout=65,
                          creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    if proc.returncode != 0:
        raise RuntimeError(f'Printer command returned code {proc.returncode}. {proc.stderr.strip()}')


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('LabelFix 4x6 - Keys Web & IT - v1.2.1')
        self.geometry('805x670')
        self.minsize(700, 575)
        self.configure(bg='#f1f5f9')
        self.load_brand_icon()
        self.events: queue.Queue = queue.Queue()
        self.busy: set[Path] = set()
        self.last_output: Optional[Path] = None
        self.watching = False
        self.known: dict[Path, tuple[int,int]] = {}
        self.pending: dict[Path, tuple[tuple[int,int],int]] = {}
        self.sumatra = find_sumatra()
        self.preferences = self.load_preferences()
        self.downloads = Path(self.preferences.get('downloads', str(actual_downloads())))
        self.output = Path(self.preferences.get('output', str(self.downloads / 'LabelFix_4x6_Labels')))

        self.auto_print = tk.BooleanVar(value=bool(self.preferences.get('auto_print', False)))
        self.printer = tk.StringVar(value=self.preferences.get('printer', ''))
        self.watch_folder = tk.StringVar(value=str(self.downloads))
        self.out_folder = tk.StringVar(value=str(self.output))
        self.message = tk.StringVar(value='Ready. Select a PDF or start watching Downloads.')
        self.watch_label = tk.StringVar(value='Start watching Downloads')
        self._build_ui()
        self.after(250, self.process_events)
        self.after(2200, self.poll)
        self.after(350, self.refresh_printers_async)

    def load_brand_icon(self) -> None:
        """Load Keys Web & IT's exact site favicon when bundled for Windows.

        Resource lives inside the executable bundle, so no network request
        or separate icon installation is needed for end users.
        """
        try:
            bundle_dir = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
            icon_file = bundle_dir / 'branding' / 'keyswebit.ico'
            if icon_file.is_file():
                self.iconbitmap(str(icon_file))
        except (OSError, tk.TclError):
            # Icon is branding only; a damaged image must not block printing.
            pass

    def load_preferences(self) -> dict:
        # Seamless migration for owners of the original JADENS/Vinted utility.
        new_file = config_path()
        old_file = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'JADENS4x6Converter' / 'preferences.json'
        for candidate in (new_file, old_file):
            try:
                settings = json.loads(candidate.read_text(encoding='utf-8'))
                if isinstance(settings, dict):
                    return settings
            except (OSError, ValueError):
                pass
        return {}

    def save_preferences(self):
        try:
            data = {'downloads': self.watch_folder.get(), 'output': self.out_folder.get(),
                    'auto_print': self.auto_print.get(), 'printer': self.printer.get()}
            config_path().write_text(json.dumps(data, indent=2), encoding='utf-8')
        except OSError as exc:
            self.write_log('Cannot save settings: ' + str(exc))

    def _build_ui(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TFrame', background='#f1f5f9')
        style.configure('TLabel', background='#f1f5f9', foreground='#0f172a', font=('Segoe UI', 10))
        style.configure('Header.TLabel', font=('Segoe UI Semibold', 21), foreground='#112a44')
        style.configure('Muted.TLabel', font=('Segoe UI', 9), foreground='#475569')
        style.configure('TButton', font=('Segoe UI', 10), padding=8)
        style.configure('Accent.TButton', background='#176b82', foreground='white')
        style.map('Accent.TButton', background=[('active', '#0e5265')])

        root = ttk.Frame(self, padding=20)
        root.pack(fill='both', expand=True)
        ttk.Label(root, text='LabelFix 4x6   v1.2.1', style='Header.TLabel').pack(anchor='w')
        ttk.Label(root, text='Convert shipping labels from Letter/A4 PDFs | Windows | Private, local processing',
                  style='Muted.TLabel').pack(anchor='w', pady=(0, 14))

        tools = ttk.Frame(root)
        tools.pack(fill='x', pady=4)
        ttk.Button(tools, text='Choose PDF(s) to convert', style='Accent.TButton',
                   command=self.pick_files).pack(side='left', padx=(0, 10))
        ttk.Button(tools, text='Open converted labels', command=self.open_output).pack(side='left', padx=(0, 10))
        ttk.Button(tools, text='Print last label', command=self.print_last).pack(side='left')

        folder_frame = ttk.LabelFrame(root, text='Folders', padding=10)
        folder_frame.pack(fill='x', pady=(12, 4))
        folder_frame.columnconfigure(1, weight=1)
        ttk.Label(folder_frame, text='Watch:').grid(row=0, column=0, sticky='w', padx=(0, 8), pady=4)
        ttk.Entry(folder_frame, textvariable=self.watch_folder).grid(row=0, column=1, sticky='ew', pady=4)
        ttk.Button(folder_frame, text='Browse', command=self.pick_downloads).grid(row=0, column=2, padx=(6, 0))
        ttk.Label(folder_frame, text='Save to:').grid(row=1, column=0, sticky='w', padx=(0, 8), pady=4)
        ttk.Entry(folder_frame, textvariable=self.out_folder).grid(row=1, column=1, sticky='ew', pady=4)
        ttk.Button(folder_frame, text='Browse', command=self.pick_output).grid(row=1, column=2, padx=(6, 0))

        watchrow = ttk.Frame(root)
        watchrow.pack(fill='x', pady=(10, 4))
        self.watch_btn = ttk.Button(watchrow, textvariable=self.watch_label,
                                    style='Accent.TButton', command=self.toggle_watch)
        self.watch_btn.pack(side='left', padx=(0, 10))
        ttk.Button(watchrow, text='Convert PDFs already in folder (no print)',
                   command=self.process_existing).pack(side='left')
        ttk.Button(root, text='Retry newest downloaded PDF (prints if auto-print enabled)',
                   command=self.retry_latest).pack(anchor='w', pady=(4, 0))

        printerbox = ttk.LabelFrame(root, text='Optional: direct printing', padding=10)
        printerbox.pack(fill='x', pady=(12, 5))
        ttk.Label(printerbox, text='Installed printer:').grid(row=0, column=0, sticky='w', padx=(0, 8), pady=4)
        self.printer_menu = ttk.Combobox(printerbox, textvariable=self.printer, width=42)
        self.printer_menu.grid(row=0, column=1, sticky='ew')
        ttk.Button(printerbox, text='Refresh', command=self.refresh_printers_async).grid(row=0, column=2, padx=6)
        printerbox.columnconfigure(1, weight=1)
        chk = ttk.Checkbutton(printerbox, text='Print automatically after conversion (only if explicitly enabled)',
                              variable=self.auto_print, command=self.on_print_toggle)
        chk.grid(row=1, column=0, columnspan=3, sticky='w', pady=5)
        if not self.sumatra:
            ttk.Label(printerbox, text='Auto-print requires SumatraPDF. Install it, then restart the converter.',
                      style='Muted.TLabel').grid(row=2, column=0, columnspan=3, sticky='w')
            self.auto_print.set(False)
        else:
            ttk.Label(printerbox, text='Uses your printer settings: 4x6 paper, actual size, and your preferred darkness.',
                      style='Muted.TLabel').grid(row=2, column=0, columnspan=3, sticky='w')

        ttk.Label(root, textvariable=self.message, style='Muted.TLabel', wraplength=680).pack(anchor='w', pady=(10, 4))
        logs = ttk.Frame(root)
        logs.pack(fill='both', expand=True)
        self.log = tk.Text(logs, height=9, state='disabled', wrap='word', relief='flat',
                           font=('Consolas', 9), bg='#ffffff', fg='#334155', padx=10, pady=8)
        self.log.pack(side='left', fill='both', expand=True)
        sb = ttk.Scrollbar(logs, command=self.log.yview)
        sb.pack(side='right', fill='y')
        self.log.configure(yscrollcommand=sb.set)
        self.write_log('Original downloaded PDFs are never changed or deleted.')
        self.write_log('Supports portrait/landscape Letter and A4 sheets, including rotated labels.')
        self.write_log('Only recognized shipping labels are converted; other PDFs are skipped.')
        self.protocol('WM_DELETE_WINDOW', self.exit_app)

    def write_log(self, message: str):
        self.log.configure(state='normal')
        self.log.insert('end', message + '\n')
        self.log.see('end')
        self.log.configure(state='disabled')

    def pick_files(self):
        paths = filedialog.askopenfilenames(title='Select shipping label PDF(s)',
                                            filetypes=[('PDF files', '*.pdf')])
        for p in paths:
            self.queue_convert(Path(p))

    def pick_downloads(self):
        p = filedialog.askdirectory(title='Choose folder to monitor')
        if p:
            if self.watching:
                self.toggle_watch()
            self.watch_folder.set(p)
            self.save_preferences()

    def pick_output(self):
        p = filedialog.askdirectory(title='Choose folder for converted 4x6 labels')
        if p:
            self.out_folder.set(p)
            self.save_preferences()

    def open_output(self):
        out = Path(self.out_folder.get()).expanduser()
        out.mkdir(parents=True, exist_ok=True)
        if os.name == 'nt':
            os.startfile(str(out))
        else:
            self.write_log('Output folder: ' + str(out))

    def on_print_toggle(self):
        if self.auto_print.get() and not self.sumatra:
            self.auto_print.set(False)
            messagebox.showinfo('SumatraPDF required',
                                'Install free SumatraPDF first, then restart this app.\n'
                                'https://www.sumatrapdfreader.org/download-free-pdf-viewer')
        elif self.auto_print.get() and not self.printer.get().strip():
            self.auto_print.set(False)
            messagebox.showwarning('Choose printer', 'Select your thermal label printer first.')
        self.save_preferences()

    def refresh_printers_async(self):
        def worker():
            self.events.put(('printers', list_printers()))
        threading.Thread(target=worker, daemon=True).start()

    def toggle_watch(self):
        if self.watching:
            self.watching = False
            self.watch_label.set('Start watching Downloads')
            self.write_log('Stopped watching Downloads.')
            return
        folder = Path(self.watch_folder.get()).expanduser()
        if not folder.is_dir():
            messagebox.showerror('Folder not found', f'This folder does not exist:\n{folder}')
            return
        if folder.resolve() == Path(self.out_folder.get()).expanduser().resolve():
            messagebox.showerror('Choose separate folders',
                'The watch and output folders must be different to avoid reprocessing labels.')
            return
        self.known = {}
        self.pending = {}
        for f in folder.glob('*'):
            if f.is_file() and f.suffix.lower() == '.pdf':
                try:
                    s = f.stat()
                    self.known[f] = (s.st_size, s.st_mtime_ns)
                except OSError:
                    pass
        self.watching = True
        self.watch_label.set('Stop watching Downloads')
        self.write_log(f'Watching {folder} for NEW PDFs. Existing files are not automatically printed. To retry an earlier download, use the Retry newest button.')
        self.message.set('Watching for new PDFs downloaded from Gmail...')
        self.save_preferences()

    def process_existing(self):
        folder = Path(self.watch_folder.get()).expanduser()
        if not folder.is_dir():
            messagebox.showerror('Folder not found', str(folder))
            return
        files = sorted([p for p in folder.glob('*.pdf') if p.is_file()],
                       key=lambda p: p.stat().st_mtime, reverse=True)
        if not files:
            self.write_log('No PDFs in selected folder.')
            return
        if len(files) > 25:
            if not messagebox.askyesno('Convert existing PDFs',
                                       f'Found {len(files)} PDFs. Try converting the most recent 25?'):
                return
            files = files[:25]
        for p in files:
            self.queue_convert(p, allow_print=False)
        self.write_log(f'Checking {len(files)} existing PDF(s); auto-print disabled for this batch.')

    def retry_latest(self):
        """Retry the most recent saved PDF, including one skipped by the old version."""
        folder = Path(self.watch_folder.get()).expanduser()
        if not folder.is_dir():
            messagebox.showerror('Folder not found', str(folder))
            return
        pdfs = [p for p in folder.glob('*.pdf') if p.is_file()]
        if not pdfs:
            messagebox.showinfo('No downloaded PDFs', 'Download the PDF from Gmail, then retry.')
            return
        latest = max(pdfs, key=lambda p: p.stat().st_mtime_ns)
        may_print = self.auto_print.get() and bool(self.sumatra) and bool(self.printer.get().strip())
        action = 'convert it and SEND IT TO YOUR PRINTER' if may_print else 'convert it (without printing)'
        if not messagebox.askyesno('Retry latest PDF',
                                   f'Most recent download:\n{latest.name}\n\n{action}?'):
            return
        self.write_log('Retry requested: ' + latest.name)
        self.queue_convert(latest, allow_print=True, reprint_existing=True)

    def poll(self):
        if self.watching:
            folder = Path(self.watch_folder.get()).expanduser()
            try:
                if folder.resolve() == Path(self.out_folder.get()).expanduser().resolve():
                    self.watching = False
                    self.watch_label.set('Start watching Downloads')
                    self.write_log('Watcher stopped: output folder matches watched folder.')
                    self.after(2000, self.poll)
                    return
                for f in folder.iterdir():
                    if not f.is_file() or f.suffix.lower() != '.pdf' or f.name.endswith('.partial.pdf'):
                        continue
                    s = f.stat()
                    current = (s.st_size, s.st_mtime_ns)
                    if f in self.known:
                        continue
                    if f not in self.pending:
                        self.pending[f] = (current, 0)
                        continue
                    prev, repeats = self.pending[f]
                    if current != prev:
                        self.pending[f] = (current, 0)
                    elif repeats >= 1 and s.st_size > 0:
                        self.known[f] = current
                        del self.pending[f]
                        self.queue_convert(f)
                    else:
                        self.pending[f] = (current, repeats + 1)
            except (OSError, PermissionError) as exc:
                self.write_log('Watch error: ' + str(exc))
        self.after(2000, self.poll)

    def queue_convert(self, source: Path, allow_print: bool = True,
                      reprint_existing: bool = False):
        source = source.resolve()
        if source in self.busy:
            return
        self.busy.add(source)
        output_folder = Path(self.out_folder.get()).expanduser().resolve()
        can_print = (allow_print and self.auto_print.get() and bool(self.sumatra)
                     and bool(self.printer.get().strip()))
        printer = self.printer.get().strip()
        sumatra = self.sumatra

        def worker():
            try:
                destination = safe_output_name(source, output_folder)
                if destination.exists():
                    self.events.put(('message', 'Already converted: ' + source.name))
                    if reprint_existing and can_print and sumatra:
                        try:
                            send_to_printer(destination, sumatra, printer)
                            self.events.put(('message', 'Submitted existing 4x6 PDF to printer: ' + destination.name))
                        except Exception as exc:
                            self.events.put(('error', f'Existing label saved; printing failed: {exc}'))
                    return
                result = convert_document(source, destination)
                self.events.put(('success', result))
                if can_print and sumatra:
                    try:
                        send_to_printer(destination, sumatra, printer)
                        self.events.put(('message', 'Submitted to printer: ' + destination.name))
                    except Exception as exc:
                        self.events.put(('error', f'Label saved, but auto-print failed: {exc}'))
            except UnrecognizedLabel as exc:
                self.events.put(('message', f'Skipped {source.name}: {exc}'))
            except Exception as exc:
                self.events.put(('error', f'Could not convert {source.name}: {exc}'))
            finally:
                self.events.put(('done', source))

        threading.Thread(target=worker, daemon=True).start()

    def print_last(self):
        if not self.last_output or not self.last_output.is_file():
            messagebox.showinfo('No label yet', 'Convert a PDF first.')
            return
        if not self.sumatra:
            if os.name == 'nt':
                os.startfile(str(self.last_output))
            messagebox.showinfo('Open label',
                                'The converted label has been opened. Print at Actual Size, 4x6.\n'
                                'For one-click printing, install SumatraPDF and restart this utility.')
            return
        if not self.printer.get().strip():
            messagebox.showwarning('Choose printer', 'Select your thermal label printer first.')
            return
        label, printer, sumatra = self.last_output, self.printer.get().strip(), self.sumatra
        self.write_log('Sending ' + label.name + ' to ' + printer + '...')
        def worker():
            try:
                send_to_printer(label, sumatra, printer)
                self.events.put(('message', 'Submitted to printer: ' + label.name))
            except Exception as exc:
                self.events.put(('error', f'Printing failed: {exc}'))
        threading.Thread(target=worker, daemon=True).start()

    def process_events(self):
        try:
            while True:
                op, data = self.events.get_nowait()
                if op == 'printers':
                    self.printer_menu['values'] = data
                    # Printer selection is explicit, never guess between devices.
                elif op == 'success':
                    self.last_output = data.output
                    self.write_log(f'Converted {data.source.name} -> {data.output.name} ({data.pages} page(s), {data.source_type})')
                    self.message.set('Ready: ' + str(data.output))
                elif op == 'message':
                    self.write_log(data)
                elif op == 'error':
                    self.write_log('ERROR: ' + data)
                    self.message.set(data)
                elif op == 'done':
                    self.busy.discard(data)
        except queue.Empty:
            pass
        self.after(300, self.process_events)

    def exit_app(self):
        self.save_preferences()
        self.destroy()


if __name__ == '__main__':
    App().mainloop()
