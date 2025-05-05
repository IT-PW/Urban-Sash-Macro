import os
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit,
    QFileDialog, QHBoxLayout, QListWidget, QMessageBox, QCheckBox, QApplication
)

from processor import process_file
from utils import categorize_files

class SashCartApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("P.W. - Sash Cart Compiler")
        self.setFixedSize(540, 260)

        self.processed_outputs = {}
        self.file_locations = {}
        self.timestamps = {}
        self.init_ui()
        self.load_stylesheet()

    def load_stylesheet(self):
        if os.path.exists("style.qss"):
            with open("style.qss", "r") as f:
                self.setStyleSheet(f.read())

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # Header (Logo only)
        logo = QSvgWidget("images/logo.svg")
        logo.setFixedSize(240, 50)
        root.addWidget(logo, alignment=Qt.AlignLeft)

        # Controls
        self.process_button = QPushButton("Process File(s)")
        self.process_button.clicked.connect(self.select_and_process_files)

        self.overwrite_checkbox = QCheckBox("Overwrite existing -SH files without confirmation")

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)

        root.addWidget(self.process_button)
        root.addWidget(self.overwrite_checkbox)
        root.addWidget(self.status_label)

        # Output section (hidden by default)
        self.output_section = QWidget()
        output_layout = QVBoxLayout(self.output_section)

        self.file_list_widget = QListWidget()
        self.file_list_widget.setFixedHeight(140)
        self.file_list_widget.itemClicked.connect(self.display_output_for_selected)

        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)

        output_layout.addWidget(self.file_list_widget)
        output_layout.addWidget(self.output_display)

        self.output_section.setVisible(False)
        root.addWidget(self.output_section)

        # Footer
        self.footer = QLabel("Premium Windows, email us at help@premiumwindows.com")
        self.footer.setAlignment(Qt.AlignCenter)
        root.addWidget(self.footer)

    def select_and_process_files(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "All Files (*)", options=options)
        if not files:
            return

        reply = QMessageBox.question(self, "Confirm", "Are you sure?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        frame_skipped, invalid_files, existing_sh, valid_files = categorize_files(files)

        if frame_skipped:
            QMessageBox.information(self, "Notice", f"Frame files detected for: {', '.join(frame_skipped)}. Skipped them.")

        if invalid_files:
            QMessageBox.information(self, "Notice", f"Non-raw sash files skipped: {', '.join(invalid_files)}")

        if existing_sh and not self.overwrite_checkbox.isChecked():
            reply = QMessageBox.question(self, "Warning",
                "There are already sash files made for the selected files. Overwrite?",
                QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                return

        self.status_label.setText("Processing...")
        QApplication.processEvents()

        self.file_list_widget.clear()
        self.processed_outputs.clear()
        self.file_locations.clear()
        self.timestamps.clear()

        for file_path in valid_files:
            base_name = os.path.basename(file_path)
            job_name = os.path.splitext(base_name)[0]
            try:
                output_data, output_file_path = process_file(file_path)
                output_text = "\n".join([";".join(map(str, row)) for row in output_data])
                timestamp = datetime.now().strftime("%I:%M:%S %p")
                job_display = f"{timestamp} : {job_name}-SH.txt"

                self.processed_outputs[job_display] = output_text
                self.file_locations[job_display] = output_file_path
                self.timestamps[job_display] = timestamp
                self.file_list_widget.addItem(job_display)
            except Exception as e:
                QMessageBox.critical(self, "Processing Error", f"Failed to process {base_name}:\n{str(e)}")

        self.status_label.setText("Done.")
        self.setFixedSize(540, 510)
        self.output_section.setVisible(True)

    def display_output_for_selected(self, item):
        file_name = item.text()
        self.output_display.setPlainText(self.processed_outputs.get(file_name, "No output found."))
