from PyQt5.QtWidgets import QDialog

from MainWindows.template_window.combo_info import Ui_Dialog


class CombinationInfo(Ui_Dialog, QDialog):
    def __init__(self):
        super(CombinationInfo, self).__init__()
        self.setupUi(self)
        self.show()