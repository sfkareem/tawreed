import importlib.util
import os
import subprocess
import sys


def check_and_install_pillow() -> None:
    """Check whether Pillow is importable; if not, install it via pip.

    The presence-check uses importlib.util.find_spec rather than a
    bare ``import PIL`` so the linter doesn't flag the import itself
    as unused. (F401 guard.)
    """
    if importlib.util.find_spec("PIL") is not None:
        print("Pillow is already installed.")
        return

    print("Pillow not found, installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    print("Pillow installed successfully.")


def generate_logo():
    logo_path = "tawreed_logo_transparent.png"
    if os.path.exists(logo_path):
        print(f"{logo_path} already exists, skipping generation.")
        return

    print("Generating logo PNG using PySide6...")
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPen

    img = QImage(256, 256, QImage.Format_ARGB32)
    img.fill(QColor(0, 0, 0, 0))

    painter = QPainter(img)
    painter.setRenderHint(QPainter.Antialiasing)

    painter.setBrush(QColor(30, 30, 46))
    pen = QPen(QColor(137, 180, 250))
    pen.setWidth(12)
    painter.setPen(pen)

    painter.drawEllipse(12, 12, 232, 232)

    painter.setPen(QColor(205, 214, 244))
    font = QFont("Segoe UI", 120, QFont.Bold)
    painter.setFont(font)
    painter.drawText(img.rect(), Qt.AlignCenter, "T")

    painter.end()
    img.save(logo_path, "PNG")
    print("Logo PNG generated successfully.")


def convert_to_ico():
    png_path = "tawreed_logo_transparent.png"
    ico_path = "tawreed_logo.ico"

    from PIL import Image

    img = Image.open(png_path)
    img.save(
        ico_path,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    print(f"Converted {png_path} to {ico_path}")


def run_pyinstaller():
    print("Running PyInstaller...")
    python_dir = os.path.dirname(sys.executable)
    pyinstaller_exe = os.path.join(python_dir, "Scripts", "pyinstaller.exe")
    if not os.path.exists(pyinstaller_exe):
        pyinstaller_exe = os.path.join(python_dir, "pyinstaller.exe")
    if not os.path.exists(pyinstaller_exe):
        pyinstaller_exe = "pyinstaller"

    cmd = [pyinstaller_exe, "--clean", "tawreed.spec"]
    print(f"Executing: {' '.join(cmd)}")
    subprocess.check_call(cmd)
    print("Packaging complete.")


if __name__ == "__main__":
    generate_logo()
    check_and_install_pillow()
    convert_to_ico()
    run_pyinstaller()
