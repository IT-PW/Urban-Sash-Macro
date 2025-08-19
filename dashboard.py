import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QLabel,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QFileDialog,
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5 import QtCore

import resources_rc  # ensure compiled resources are present (pyrcc5)

# --------------------------
# Configuration
# --------------------------
MIN_COLS = 24            # you index up to [23]
ROUND_DENOM = 16         # round to 1/16ths
ROUND_MODE = 'up'        # 'nearest' | 'up' | 'down'
DEFAULT_OUTPUT_DIR = r"\\cor-fs2\CIMPLC\4590\Work"


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
        # font fallback (Haettenschweiler may not exist)
        self.title.setFont(QFont("Haettenschweiler", 36) if QFont("Haettenschweiler").exactMatch()
                           else QFont("", 28))
        self.title.setObjectName("title")

        # Sash image label
        self.sash = QLabel(Dialog)
        self.sash.setGeometry(QtCore.QRect(100, 80, 300, 150))
        self.sash.setFixedSize(300, 150)
        self.sash.setAlignment(QtCore.Qt.AlignCenter)
        self.sash.setObjectName("sash")

        # Input line edit
        self.inputLineEdit = QLineEdit(Dialog)
        self.inputLineEdit.setGeometry(QtCore.QRect(50, 260, 300, 30))
        self.inputLineEdit.setPlaceholderText("Enter filename(s) or browse...")
        self.inputLineEdit.setObjectName("inputLineEdit")

        # Browse button (multiple selection)
        self.browseButton = QPushButton(Dialog)
        self.browseButton.setGeometry(QtCore.QRect(360, 258, 80, 34))
        self.browseButton.setFont(QFont("", 10))
        self.browseButton.setObjectName("browseButton")

        # Generate button
        self.generateButton = QPushButton(Dialog)
        self.generateButton.setGeometry(QtCore.QRect(130, 310, 231, 85))
        font2 = QFont()
        font2.setPointSize(12)
        font2.setBold(True)
        font2.setWeight(75)
        self.generateButton.setFont(font2)
        self.generateButton.setObjectName("generateButton")

        # Output text edit (read-only)
        self.outputTextEdit = QTextEdit(Dialog)
        self.outputTextEdit.setGeometry(QtCore.QRect(50, 420, 390, 130))
        self.outputTextEdit.setReadOnly(True)
        self.outputTextEdit.setObjectName("outputTextEdit")

        # Footer logo/credit label
        self.logo = QLabel(Dialog)
        self.logo.setGeometry(QtCore.QRect(0, 560, 500, 20))
        self.logo.setAlignment(QtCore.Qt.AlignCenter)
        self.logo.setObjectName("logo")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Sash Cart Compiler"))
        self.title.setText(_translate("Dialog", "Sash Cart Compiler"))
        self.browseButton.setText(_translate("Dialog", "Browse..."))
        self.generateButton.setText(_translate("Dialog", "Generate Files"))
        self.logo.setText(
            _translate("Dialog", "Premium Windows, email us at help@premiumwindows.com")
        )


class SashCartCompilerWindow(QMainWindow, Ui_SashCartCompiler):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Load image from Qt resource system, with explicit fallback
        resource_pixmap = QPixmap(":/images/Sash.jpg")
        if not resource_pixmap.isNull():
            scaled = resource_pixmap.scaled(
                self.sash.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation,
            )
            self.sash.setPixmap(scaled)
        else:
            local_path = Path(__file__).resolve().parent / "images" / "Sash.jpg"
            if local_path.is_file():
                local_pixmap = QPixmap(str(local_path))
                scaled = local_pixmap.scaled(
                    self.sash.size(),
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation,
                )
                self.sash.setPixmap(scaled)
            else:
                self.sash.setText("Image not found")

        # Internal list to hold selected file paths
        self.selected_files = []

        # Connect buttons to methods
        self.browseButton.clicked.connect(self.browse_files)
        self.generateButton.clicked.connect(self.execute_process_files)

        # Default UNC output directory
        self.default_output_dir = DEFAULT_OUTPUT_DIR

    # ---------- helpers ----------

    @staticmethod
    def convert_to_fraction(decimal_str, denom=ROUND_DENOM, mode=ROUND_MODE):
        """
        Convert a decimal string into a reduced fraction string using the specified denominator (default 1/16ths).
        mode: 'nearest' (round), 'up' (ceiling), 'down' (floor).
        Examples (denom=16):
          nearest: 12.03 -> 12 1/16,  12.06 -> 12 1/16,  12.09 -> 12 1/8,  12.999 -> 13
          up:      12.01 -> 12 1/16,  12.06 -> 12 2/16 (-> 12 1/8),  12.00 -> 12
          down:    12.09 -> 12 1/16
        Handles negatives and carries at denom/denom -> whole+1.
        """
        import math
        from math import gcd

        try:
            value = float(str(decimal_str).strip())
        except Exception:
            return str(decimal_str)

        sign = "-" if value < 0 else ""
        value = abs(value)

        whole = int(value)
        frac = value - whole

        eps = 1e-12
        if mode == 'up':
            n = math.ceil(frac * denom - eps)
        elif mode == 'down':
            n = math.floor(frac * denom + eps)
        else:  # nearest
            n = int(round(frac * denom))

        if n == denom:  # carry
            whole += 1
            n = 0

        if n == 0:
            return f"{sign}{whole}".strip()

        g = gcd(n, denom)
        n //= g
        d = denom // g

        if whole == 0:
            return f"{sign}{n}/{d}".strip()
        else:
            return f"{sign}{whole} {n}/{d}".strip()

    def _normalize_row(self, row, rownum, issues):
        """Ensure rows have at least MIN_COLS columns; pad and record issues."""
        if len(row) < MIN_COLS:
            pad = MIN_COLS - len(row)
            issues.append(f"Row {rownum}: padded {pad} missing column(s).")
            row = row + [""] * pad
        return row

    # ---------- UI actions ----------

    def browse_files(self):
        initial_dir = Path(__file__).resolve().parent.parent / "Sash"
        if not initial_dir.is_dir():
            initial_dir = Path.home()

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select One or More Sash Files",
            str(initial_dir),
            "Text Files (*.txt *.csv);;All Files (*)",
        )
        if files:
            self.selected_files = files
            basenames = [os.path.basename(f) for f in files]
            self.inputLineEdit.setText("; ".join(basenames))

    # ---------- core ----------

    def process_file(self, absolute_path):
        """
        Reads one sash file (absolute_path), converts dimensions/measurements
        to 1/16ths, applies swap logic, and writes output to the default UNC directory.
        Returns (output_path, row_count, warnings_list).
        """
        p = Path(absolute_path)
        if not p.is_file():
            raise FileNotFoundError(f"Cannot find file: {absolute_path}")

        issues = []
        data = []
        with p.open("r", encoding="utf-8") as f:
            for i, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                parts = [c.strip() for c in line.split(";")]
                parts = self._normalize_row(parts, i, issues)
                data.append(parts)

        if not data:
            raise ValueError(f"Input file '{absolute_path}' is empty or improperly formatted.")

        # Sort by cart number (col 19) safely
        data.sort(key=lambda r: _safe_float(r[19], 0.0))
        alt_car = data[0][19]

        # Convert dimensions and measurements; reset flag column (index 4)
        for row in data:
            # Dimensions "width x height" in column 16
            dim_src = row[16]
            if dim_src:
                # handle 'x' or 'X'
                dims_lower = dim_src.replace("X", "x")
                dims = [s.strip() for s in dims_lower.split("x")]
                if len(dims) == 2:
                    w_frac = self.convert_to_fraction(dims[0])
                    h_frac = self.convert_to_fraction(dims[1])
                    if not w_frac:
                        w_frac = "0"
                    if not h_frac:
                        h_frac = "0"
                    row[16] = f'W {w_frac}" X H {h_frac}"'

            # Convert single measure in column 18 if it doesn't already look fractional
            if row[18] and "/" not in row[18]:
                row[18] = self.convert_to_fraction(row[18])

            # Reset the flag to '0'
            row[4] = "0"

        # ---- Swap logic (fixed & deterministic) ----
        # Build list of "empties" where other[4] == "1" within the same group (col 23), save group key.
        empty_slots = []
        for r in data:
            for other in data:
                if other[23] == r[23] and other[4] == "1" and other[20] != r[20]:
                    # record slot to fill (cart, slot, group)
                    empty_slots.append((other[19], other[20], r[23]))
                    # move r's cart/slot into 'other' and clear flag
                    other[19], other[20], other[7], other[6], other[4] = (
                        r[19],
                        r[20],
                        r[19],
                        r[20],
                        "0",
                    )

        # Now assign recorded empty slots to first available matching group rows
        for cart, slot, group_key in empty_slots:
            for row in data:
                if row[23] == group_key and row[4] == "0" and row[19] != alt_car:
                    row[19], row[20], row[7], row[6] = cart, slot, cart, slot
                    break  # fill each empty once

        # Prepare output
        data.sort(key=lambda r: _safe_float(r[0], 0.0))
        name_wo_ext = p.stem
        out_name = f"{name_wo_ext}-SH.txt"
        out_path = Path(self.default_output_dir) / out_name

        # Ensure the output directory exists and is a directory
        out_dir = Path(self.default_output_dir)
        if not out_dir.exists():
            raise FileNotFoundError(
                f"Output directory does not exist (or is not accessible):\n{self.default_output_dir}"
            )
        if not out_dir.is_dir():
            raise NotADirectoryError(f"Output path is not a directory:\n{self.default_output_dir}")

        # Write
        with out_path.open("w", encoding="utf-8", newline="\n") as f:
            for row in data:
                row[4] = "1"
                f.write(";".join(row) + "\n")

        return str(out_path), len(data), issues

    def execute_process_files(self):
        # Build input paths from selection or textbox
        if self.selected_files:
            input_paths = self.selected_files
        else:
            text = self.inputLineEdit.text().strip()
            if not text:
                self.outputTextEdit.setPlainText("Please provide at least one filename.")
                return
            candidates = [p.strip() for p in text.replace(",", ";").split(";") if p.strip()]
            base_dir = Path(__file__).resolve().parent.parent / "Sash"
            input_paths = [
                p if os.path.isabs(p) else str(base_dir / p)
                for p in candidates
            ]

        output_lines = []
        for file_path in input_paths:
            try:
                out_path, count, issues = self.process_file(file_path)
                line = f"• {os.path.basename(file_path)} → {os.path.basename(out_path)}: {count} rows"
                if issues:
                    line += f"  (warnings: {len(issues)})"
                output_lines.append(line)
                if issues:
                    # show first few warnings; avoids spamming the UI
                    output_lines.extend([f"   - {w}" for w in issues[:5]])
            except Exception as e:
                output_lines.append(f"Error processing '{file_path}': {e}")

        # Clear selected_files after processing
        self.selected_files = []

        # Display results
        self.outputTextEdit.setPlainText("\n".join(output_lines))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SashCartCompilerWindow()
    window.show()
    sys.exit(app.exec_())
