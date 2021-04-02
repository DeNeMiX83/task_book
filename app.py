import sys
from PyQt5.QtWidgets import QApplication
from MainWindows import ChartWeekWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ChartWeekWindow()
    sys.exit(app.exec())
