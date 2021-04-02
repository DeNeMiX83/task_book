from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow


class WorkWithCombination(QMainWindow):
    def __init__(self):
        super(WorkWithCombination, self).__init__()

    def keyPressEvent(self, event):
        if int(event.modifiers()) == Qt.CTRL:
            if event.key() == Qt.Key_C:
                self.create_table()
            elif event.key() == Qt.Key_V:
                self.load_table()
            elif event.key() == Qt.Key_A:
                self.add_event()
            elif event.key() == Qt.Key_X:
                self.clear_event()
