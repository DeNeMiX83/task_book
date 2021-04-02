from datetime import time
from PyQt5.QtWidgets import QDialog
from MainWindows.template_window.event import Ui_Dialog
from MainWindows.window_manager.event_time import get_time_start_and_end
from MainWindows.window_manager.message_window import create_message_window
from sqlite import cur, con


class EventDialog(Ui_Dialog, QDialog):
    def __init__(self, mainwindow, edit=False):
        super(EventDialog, self).__init__()
        self.setupUi(self)
        self.mainwindow = mainwindow
        self.edit = edit
        self.initUi()
        self.show()

    def initUi(self):
        self.buttonBox.accepted.connect(self.save_event)

        self.buttonBox.rejected.connect(self.dialog_close)

    def dialog_close(self):
        self.close()

    def save_event(self):
        """Закрывает окно и передает информацию в EventView"""
        if self.edit:
            self.mainwindow.clear_event()
        start, end = get_time_start_and_end(self.event_start.text(), self.event_end.text())
        name = self.event_name
        text = self.event_text.toPlainText()
        # По собранной информации создает новый ивент
        if self.create_event(start, end, name.text(), text):
            self.close()

    def create_event(self, start, end, name, event_text):
        """Создает ивент в EventView"""
        time = [start.hour, start.minute, end.hour, end.minute]
        t = [str(i).rjust(2, '0') for i in time]
        text = 'c {}:{} по {}:{} - {}'.format(*t, name)
        # проверка что введенный интервал времение не пересекается с временем других ивентов
        if self.is_normal_events(start, end):
            try:
                cur.execute('''INSERT INTO events VALUES(NULL, ?, ?, ?, ?, ?, ?, ?)''',
                            (self.mainwindow.day_n, *time, name, event_text))
                con.commit()
            except Exception as e:
                print(e)
            self.mainwindow.EventView.addItem(text)
            return True
        else:
            create_message_window(self, 'Введите другой инервал времни')

    def is_normal_events(self, start_, end_):
        """Проверка что введено корректное время для добавления в список ивентов"""
        events = list()
        for i in range(self.mainwindow.EventView.count()):
            text = self.mainwindow.EventView.item(i).text().split()
            start, end = get_time_start_and_end(text[1], text[3])
            events.append((start, end))
        if start_ > end_:
            return
        if not events:
            return True
        time_event = events[-1]
        end = time_event[1]
        # проверка что введенное время больше конца времени последнего ивента
        if end < start_:
            return True
        time_event = events[-1]
        start = time_event[0]
        #  роверка что введенное время меньше начало первого ивента
        if end_ < start:
            return True
        x = len(events) - 1
        # если был один ивент то можно дальше не проверять
        if not x:
            return False
        y = x // 2
        # проверяем корректность времени, деля интервал наших поисков
        # каждый раз вдвое пока не узнаем результат
        while True:
            time_event = events[y]
            end1 = time_event[1]
            time_event = events[y + 1]
            start2 = time_event[0]
            left = end1 < start_
            right = end_ < start2
            if left and right:
                return True
            if not left:
                y //= 2
            if not right:
                y += (x - y) // 2
            if y == x - 1 or y == 0:
                return False
