# PyInstaller build configuration for the Windows desktop package.
from pathlib import Path

from PyInstaller.utils.hooks import collect_all


root = Path(SPECPATH)
datas = [
    (str(path), ".")
    for path in root.glob("*.py")
    if path.name != "desktop_launcher.py"
]
datas.extend(
    (str(root / name), ".")
    for name in (
        "app.js",
        "gradasi.html",
        "logo.svg",
        "specs.json",
        "styles.css",
    )
)
datas.append((str(root / ".streamlit" / "config.toml"), ".streamlit"))

streamlit_datas, streamlit_binaries, streamlit_hiddenimports = collect_all("streamlit")
matplotlib_datas, matplotlib_binaries, matplotlib_hiddenimports = collect_all("matplotlib")
datas += streamlit_datas + matplotlib_datas
binaries = streamlit_binaries + matplotlib_binaries
hiddenimports = streamlit_hiddenimports + matplotlib_hiddenimports + [
    "beranda",
    "cara_kerja",
    "data_tersimpan",
    "kalkulator",
    "laporan_pdf",
    "perbandingan",
    "specs",
    "tentang",
    "theme",
    "ui",
]

a = Analysis(
    [str(root / "desktop_launcher.py")],
    pathex=[str(root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="GradasiAgregat",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
collect = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="GradasiAgregat",
)