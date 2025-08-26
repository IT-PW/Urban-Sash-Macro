import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QLabel, QPushButton,
    QLineEdit, QTextEdit, QFileDialog,
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5 import QtCore

import resources_rc  # ensure pyrcc5 compiled resources exist (resources_rc.py)

# --------------------------
# Configuration
# --------------------------
MIN_COLS = 24              # you index up to [23]
ROUND_DENOM = 16           # 1/16ths
ROUND_MODE = 'nearest'     # 'nearest' (half-up), 'up', 'down'
DEFAULT_OUTPUT_DIR = r"\\cor-fs2\CIMPLC\4590\Work"

# Newline policy:
#   'preserve' -> sniff input file and match its EOLs
#   'windows'  -> CRLF
#   'unix'     -> LF
#   'mac'      -> CR (classic)
NEWLINE_POLICY = 'preserve'


def _safe_float(val, default=0.0):
    try:
        return float(val)
    except Exception:
        return default


class Ui_SashCartCompiler(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowTitle("Sash Cart Compiler")
        Dialog.resize(500, 600)

        # Title label
        self.title = QLabel(Dialog)
        self.title.setGeometry(QtCore.QRect(0, 10, 500, 60))
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setFont(QFont("Haettenschweiler", 36) if QFont("Haettenschweiler").exactMatch()
                           else QFont("", 28))

        # Sash image
        self.sash = QLabel(Dialog)
        self.sash.setGeometry(QtCore.QRect(100, 80, 300, 150))
        self.sash.setFixedSize(300, 150)
        self.sash.setAlignment(QtCore.Qt.AlignCenter)

        # Input
        self.inputLineEdit = QLineEdit(Dialog)
        self.inputLineEdit.setGeometry(QtCore.QRect(50, 260, 300, 30))
        self.inputLineEdit.setPlaceholderText("Enter filename(s) or browse...")

        # Browse
        self.browseButton = QPushButton(Dialog)
        self.browseButton.setGeometry(QtCore.QRect(360, 258, 80, 34))
        self.browseButton.setText("Browse...")

        # Generate
        self.generateButton = QPushButton(Dialog)
        self.generateButton.setGeometry(QtCore.QRect(130, 310, 231, 85))
        f = QFont(); f.setPointSize(12); f.setBold(True)
        self.generateButton.setFont(f)
        self.generateButton.setText("Generate Files")

        # Output
        self.outputTextEdit = QTextEdit(Dialog)
        self.outputTextEdit.setGeometry(QtCore.QRect(50, 420, 390, 130))
        self.outputTextEdit.setReadOnly(True)

        # Footer
        self.logo = QLabel(Dialog)
        self.logo.setGeometry(QtCore.QRect(0, 560, 500, 20))
        self.logo.setAlignment(QtCore.Qt.AlignCenter)
        self.logo.setText("Premium Windows, email us at help@premiumwindows.com")


class SashCartCompilerWindow(QMainWindow, Ui_SashCartCompiler):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Load image from resources; fallback to local file
        pix = QPixmap(":/images/Sash.jpg")
        if not pix.isNull():
            self.sash.setPixmap(pix.scaled(self.sash.size(), QtCore.Qt.KeepAspectRatio,
                                           QtCore.Qt.SmoothTransformation))
        else:
            local = Path(__file__).resolve().parent / "images" / "Sash.jpg"
            if local.is_file():
                self.sash.setPixmap(QPixmap(str(local)).scaled(
                    self.sash.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
            else:
                self.sash.setText("Image not found")

        self.selected_files = []
        self.browseButton.clicked.connect(self.browse_files)
        self.generateButton.clicked.connect(self.execute_process_files)

        self.default_output_dir = DEFAULT_OUTPUT_DIR

    # ---------- Newline handling ----------

    @staticmethod
    def _sniff_newline(path: Path) -> str:
        """Return the predominant newline in a file: '\r\n', '\n', or '\r' (fallback to os.linesep)."""
        try:
            with path.open('rb') as f:
                data = f.read(1_000_000)  # first MB is plenty
            crlf = data.count(b'\r\n')
            # subtract CRLF from raw counts to avoid double-counting
            cr = data.count(b'\r') - crlf
            lf = data.count(b'\n') - crlf
            if crlf >= cr and crlf >= lf and crlf > 0:
                return '\r\n'
            if lf >= cr and lf > 0:
                return '\n'
            if cr > 0:
                return '\r'
        except Exception:
            pass
        # No line endings found (single-line file) or error: default to system
        return os.linesep

    def _resolve_newline(self, src_path: Path) -> str:
        if NEWLINE_POLICY == 'windows':
            return '\r\n'
        if NEWLINE_POLICY == 'unix':
            return '\n'
        if NEWLINE_POLICY == 'mac':
            return '\r'
        # preserve
        return self._sniff_newline(src_path)

    # ---------- Conversion helpers ----------

    @staticmethod
    def convert_to_fraction(value_str, denom=ROUND_DENOM, mode=ROUND_MODE):
        """
        Convert decimals or fractions (e.g. '33 19/32') to reduced 1/16ths.
        mode: 'nearest' (half-up), 'up', 'down'. Handles negatives & carry.
        """
        import math
        from math import gcd

        s = str(value_str).strip()
        if not s:
            return s

        # normalize sign
        s = s.replace("−", "-")
        sign_mult = -1 if s.startswith("-") else 1
        s = s.lstrip("+- ").strip()

        # Parse input -> float value
        if "/" in s:
            parts = s.split()
            frac_tok = next((t for t in reversed(parts) if "/" in t), None)
            whole = 0
            if len(parts) >= 2:
                try:
                    whole = int(parts[0])
                except Exception:
                    whole = 0
            try:
                n_s, d_s = frac_tok.split("/")
                num, den = int(n_s), int(d_s)
                if den == 0:
                    return value_str
                value = (whole + num / den) * sign_mult
            except Exception:
                return value_str
        else:
            try:
                value = float(s) * sign_mult
            except Exception:
                return value_str

        # Round to target denominator
        sign = "-" if value < 0 else ""
        value = abs(value)
        whole = int(value)
        frac = value - whole

        if mode == 'up':
            n = math.ceil(frac * denom - 1e-12)
        elif mode == 'down':
            n = math.floor(frac * denom + 1e-12)
        else:  # nearest (half-up)
            n = math.floor(frac * denom + 0.5 - 1e-12)

        if n == denom:  # carry
            whole += 1
            n = 0

        if n == 0:
            return f"{sign}{whole}"

        g = gcd(n, denom)
        n //= g
        d = denom // g
        return f"{sign}{whole} {n}/{d}" if whole else f"{sign}{n}/{d}"

    def _normalize_row(self, row, rownum, issues):
        """Ensure minimum columns per row; pad and record."""
        if len(row) < MIN_COLS:
            issues.append(f"Row {rownum}: padded {MIN_COLS - len(row)} missing column(s).")
            row += [""] * (MIN_COLS - len(row))
        return row

    # ---------- File dialog ----------

    def browse_files(self):
        initial_dir = Path(__file__).resolve().parent.parent / "Sash"
        if not initial_dir.is_dir():
            initial_dir = Path.home()
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select One or More Sash Files", str(initial_dir),
            "Text Files (*.txt *.csv);;All Files (*)",
        )
        if files:
            self.selected_files = files
            self.inputLineEdit.setText("; ".join(Path(f).name for f in files))

    # ---------- Core processing ----------

    def process_file(self, absolute_path):
        """
        Read one file, convert dimensions & measures to nearest 1/16 (including /32 inputs),
        apply swap logic, and write output to UNC with original newline style (or policy).
        Returns (output_path, row_count, warnings).
        """
        p = Path(absolute_path)
        if not p.is_file():
            raise FileNotFoundError(f"Cannot find file: {absolute_path}")

        issues, data = [], []

        # We don't need exact input EOLs for parsing; universal newlines is fine here.
        with p.open("r", encoding="utf-8") as f:
            for i, raw in enumerate(f, start=1):
                line = raw.strip()
                if not line:
                    continue
                row = self._normalize_row([c.strip() for c in line.split(";")], i, issues)
                data.append(row)

        if not data:
            raise ValueError(f"Input file '{absolute_path}' is empty or improperly formatted.")

        # Sort by cart number (col 19)
        data.sort(key=lambda r: _safe_float(r[19], 0.0))
        alt_car = data[0][19]

        # Convert values; reset flag col 4
        for row in data:
            # col 16: "W x H" (could be decimals or fractions)
            dim = row[16]
            if dim:
                dims = dim.replace("X", "x").split("x")
                if len(dims) == 2:
                    w = self.convert_to_fraction(dims[0].strip())
                    h = self.convert_to_fraction(dims[1].strip())
                    row[16] = f'W {w}" X H {h}"'
            # col 18: single measurement (decimal or fractional)
            if row[18]:
                row[18] = self.convert_to_fraction(row[18])
            # reset flag
            row[4] = "0"

        # Swap logic (kept deterministic)
        empty_slots = []
        for r in data:
            for other in data:
                if other[23] == r[23] and other[4] == "1" and other[20] != r[20]:
                    empty_slots.append((other[19], other[20], r[23]))
                    other[19], other[20], other[7], other[6], other[4] = (
                        r[19], r[20], r[19], r[20], "0"
                    )

        for cart, slot, group in empty_slots:
            for row in data:
                if row[23] == group and row[4] == "0" and row[19] != alt_car:
                    row[19], row[20], row[7], row[6] = cart, slot, cart, slot
                    break

        # Output path
        data.sort(key=lambda r: _safe_float(r[0], 0.0))
        out_dir = Path(self.default_output_dir)
        if not out_dir.is_dir():
            raise FileNotFoundError(f"Output directory not found or inaccessible: {self.default_output_dir}")
        out_path = out_dir / f"{p.stem}-SH.txt"

        # Resolve newline string to use
        newline_str = self._resolve_newline(p)

        # Write EXACT newline (no translation) by using newline=''
        with out_path.open("w", encoding="utf-8", newline="") as f:
            for row in data:
                row[4] = "1"
                f.write(";".join(row) + newline_str)

        return str(out_path), len(data), issues

    def execute_process_files(self):
        if self.selected_files:
            input_paths = self.selected_files
        else:
            text = self.inputLineEdit.text().strip()
            if not text:
                self.outputTextEdit.setPlainText("Please provide at least one filename.")
                return
            base_dir = Path(__file__).resolve().parent.parent / "Sash"
            input_paths = [
                p.strip() if os.path.isabs(p.strip()) else str(base_dir / p.strip())
                for p in text.replace(",", ";").split(";") if p.strip()
            ]

        lines = []
        for file_path in input_paths:
            try:
                out_path, count, issues = self.process_file(file_path)
                msg = f"• {os.path.basename(file_path)} → {os.path.basename(out_path)}: {count} rows"
                if issues:
                    msg += f" (warnings: {len(issues)})"
                lines.append(msg)
                if issues:
                    lines.extend([f"   - {w}" for w in issues[:5]])
            except Exception as e:
                lines.append(f"Error processing '{file_path}': {e}")

        self.selected_files = []
        self.outputTextEdit.setPlainText("\n".join(lines))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SashCartCompilerWindow()
    window.show()
    sys.exit(app.exec_())
