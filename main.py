from PyQt5.QtWidgets import QApplication, QMessageBox
from ui_main import SashCartApp
import sys

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        window = SashCartApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as main_err:
        QMessageBox.critical(None, "Critical Error", f"Application crashed:\n{str(main_err)}")
        raise
