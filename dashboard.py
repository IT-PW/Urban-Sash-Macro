import sys
import os
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
from PyQt5 import QtCore, QtGui, QtWidgets

import resources_rc  # Make sure your Qt resource file is available


class Ui_SashCartCompiler(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowTitle("Sash Cart Compiler")
        Dialog.resize(500, 600)

        # Title label
        self.title = QLabel(Dialog)
        self.title.setGeometry(QtCore.QRect(0, 10, 500, 60))
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setFont(QFont("Haettenschweiler", 36))
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
        font2 = QtGui.QFont()
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

        # Load image from Qt resource system
        resource_pixmap = QPixmap(":/images/Sash.jpg")
        if not resource_pixmap.isNull():
            scaled = resource_pixmap.scaled(
                self.sash.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation,
            )
            self.sash.setPixmap(scaled)
        else:
            # Fallback: load from local 'images' folder if resource not found
            local_path = os.path.join(os.path.dirname(__file__), "images", "Sash.jpg")
            if os.path.isfile(local_path):
                local_pixmap = QPixmap(local_path)
                scaled = local_pixmap.scaled(
                    self.sash.size(),
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation,
                )
                self.sash.setPixmap(scaled)

        # Internal list to hold selected file paths
        self.selected_files = []

        # Connect buttons to methods
        self.browseButton.clicked.connect(self.browse_files)
        self.generateButton.clicked.connect(self.execute_process_files)

        # Default UNC output directory
        self.default_output_dir = r"\\cor-fs2\CIMPLC\4590\Work"

    def browse_files(self):
        """
        Open file dialog to select multiple sash input files.
        Selected paths are stored in self.selected_files.
        """
        initial_dir = os.path.join(os.path.dirname(__file__), "..", "Sash")
        if not os.path.isdir(initial_dir):
            initial_dir = os.path.expanduser("~")

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select One or More Sash Files",
            initial_dir,
            "Text Files (*.txt *.csv);;All Files (*)",
        )
        if files:
            self.selected_files = files
            # Display just the basenames in the line edit
            basenames = [os.path.basename(f) for f in files]
            self.inputLineEdit.setText("; ".join(basenames))

    def convert_to_fraction(self, decimal_str):
        """
        Convert a decimal string into a fraction string (nearest 1/32).
        Returns strings like "12 5/32" or "7/16" if less than 1.
        """
        try:
            value = float(decimal_str)
        except ValueError:
            return decimal_str  # Return original if not a valid float

        whole = int(value)
        frac = round((value - whole) * 32)
        lookup = {
            0: "",
            1: "1/32",
            2: "1/16",
            3: "3/32",
            4: "1/8",
            5: "5/32",
            6: "3/16",
            7: "7/32",
            8: "1/4",
            9: "9/32",
            10: "5/16",
            11: "11/32",
            12: "3/8",
            13: "13/32",
            14: "7/16",
            15: "15/32",
            16: "1/2",
            17: "17/32",
            18: "9/16",
            19: "19/32",
            20: "5/8",
            21: "21/32",
            22: "11/16",
            23: "23/32",
            24: "3/4",
            25: "25/32",
            26: "13/16",
            27: "27/32",
            28: "7/8",
            29: "29/32",
            30: "15/16",
            31: "31/32",
        }
        frac_str = lookup.get(frac, f"{frac}/32")
        if whole == 0:
            return frac_str
        return f"{whole} {frac_str}".strip()

    def process_file(self, absolute_path):
        """
        Reads one sash file (absolute_path), converts dimensions/measurements
        to fractions, applies swap logic, and writes output to the default UNC directory.
        Returns (output_path, row_count).
        """
        if not os.path.isfile(absolute_path):
            raise FileNotFoundError(f"Cannot find file: {absolute_path}")

        # Read and parse semicolon-delimited data
        with open(absolute_path, "r", encoding="utf-8") as f:
            data = [line.strip().split(";") for line in f if line.strip()]

        if not data:
            raise ValueError(f"Input file '{absolute_path}' is empty or improperly formatted.")

        # Sort by cart number (column index 19)
        data.sort(key=lambda r: float(r[19] or 0))
        alt_car = data[0][19]

        # Convert dimensions and measurements; reset flag column (index 4)
        for row in data:
            # Dimensions "width x height" in column 16
            dims = row[16].split("x")
            if len(dims) == 2:
                w_str, h_str = dims[0].strip(), dims[1].strip()
                w_frac = self.convert_to_fraction(w_str)
                h_frac = self.convert_to_fraction(h_str)
                row[16] = f'W {w_frac}" X H {h_frac}"'

            # Convert single measure in column 18 if not already a fraction
            if "/" not in row[18]:
                row[18] = self.convert_to_fraction(row[18])

            # Reset the flag to '0'
            row[4] = "0"

        # Swap logic: find matching slots and swap cart info
        empty_slots = []
        for r in data:
            for other in data:
                if (
                        other[23] == r[23]
                        and other[4] == "1"
                        and other[20] != r[20]
                ):
                    empty_slots.append((other[19], other[20]))
                    other[19], other[20], other[7], other[6], other[4] = (
                        r[19],
                        r[20],
                        r[19],
                        r[20],
                        "0",
                    )

        for idx, (cart, slot) in enumerate(empty_slots):
            for row in data:
                if (
                        row[23] == data[idx][23]
                        and row[4] == "0"
                        and row[19] != alt_car
                ):
                    row[19], row[20], row[7], row[6] = cart, slot, cart, slot

        # Prepare output filename and path
        data.sort(key=lambda r: float(r[0] or 0))
        base_name = os.path.basename(absolute_path)
        name_wo_ext = os.path.splitext(base_name)[0]
        out_name = f"{name_wo_ext}-SH.txt"
        out_path = os.path.join(self.default_output_dir, out_name)

        # Ensure the output directory exists
        if not os.path.isdir(self.default_output_dir):
            raise FileNotFoundError(f"Output directory does not exist:\n{self.default_output_dir}")

        # Write to the UNC output directory
        with open(out_path, "w", encoding="utf-8") as f:
            for row in data:
                row[4] = "1"
                f.write(";".join(row) + "\n")

        return out_path, len(data)

    def execute_process_files(self):
        """
        Triggered when "Generate Files" button is clicked.
        Processes each selected file (absolute path) and writes
        output to the default UNC share. Displays status or errors.
        """
        # If the user used Browse to select files, self.selected_files holds them
        if self.selected_files:
            input_paths = self.selected_files
        else:
            # Otherwise, try to interpret the line edit as a single absolute or relative path
            text = self.inputLineEdit.text().strip()
            if not text:
                self.outputTextEdit.setPlainText("Please provide at least one filename.")
                return
            # Split on semicolon or comma if user pasted multiple basenames
            candidates = [p.strip() for p in text.replace(",", ";").split(";") if p.strip()]
            input_paths = []
            for cand in candidates:
                if os.path.isabs(cand):
                    input_paths.append(cand)
                else:
                    # Assume relative to ../Sash folder
                    base_dir = os.path.dirname(__file__)
                    rel_path = os.path.join(base_dir, "..", "Sash", cand)
                    input_paths.append(rel_path)

        output_messages = []
        for file_path in input_paths:
            try:
                out_path, count = self.process_file(file_path)
                output_messages.append(f"• {os.path.basename(file_path)} → {os.path.basename(out_path)}: {count} rows")
            except Exception as e:
                output_messages.append(f"Error processing '{file_path}': {e}")

        # Clear selected_files after processing
        self.selected_files = []

        # Display results
        self.outputTextEdit.setPlainText("\n".join(output_messages))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SashCartCompilerWindow()
    window.show()
    sys.exit(app.exec_())
