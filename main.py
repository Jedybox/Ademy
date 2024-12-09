from PyQt6.QtWidgets import QApplication
import sys

from MainWindow import MainWindow

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    sys.exit(app.exec())

print('We Done!')