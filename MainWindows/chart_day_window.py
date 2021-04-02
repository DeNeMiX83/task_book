from PyQt5.QtCore import QTime
from PyQt5.QtWidgets import QMainWindow
from .combitation_window import WorkWithCombination
from .event_window import EventDialog
from MainWindows.window_manager.excel_table import create_excel
from MainWindows.window_manager.load_excel import load_excel_in_week
from MainWindows.window_manager.message_window import create_message_window
from sqlite.sqlite_manager import get_number_day
from MainWindows.template_window.day import Ui_mainWindow
from sqlite import cur, con
from .window_manager.event_time import get_start_and_end


class ChartDayWindow(Ui_mainWindow, WorkWithCombination):
    def __init__(self, mainwindow, day):
        super(ChartDayWindow, self).__init__()
        self.mainwindow = mainwindow
        self.day = day
        # получить номер дня недели
        self.day_n = get_number_day(self.day)
        self.setupUi(self)
        self.initUi()
        # взять данные из бд и заполнить EventView
        self.give_data()
        self.show()

    def initUi(self):
        # Делаю так чтобы инетрвалы времни в списке могли сортироваться
        self.EventView.setSortingEnabled(True)
        # Вставляю название дня недели в поле
        self.lbl_name_day.setText(self.day)
        # кнопка редактирования события
        self.btn_edit_info.clicked.connect(self.edit_event)
        # удаляет выбранный евент
        self.btn_clear_event.clicked.connect(self.clear_event)
        # добавляет новый евент
        self.btn_add_event.clicked.connect(self.add_event)
        # удаляет события из этого дня
        self.btn_clear_day.clicked.connect(self.clear_day)
        # возвражение в окно ChartWeekWindow
        self.btn_back.clicked.connect(self.back_week_window)
        # по клику на ивент показывает его описание
        self.EventView.itemClicked.connect(self.give_event_info)
        # создает по данным событий таблицу excel
        self.btn_create_excel.clicked.connect(self.create_table)
        # востанавливает по данным из excel таблицы события
        self.btn_load_table.clicked.connect(self.load_table)

    def get_description(self, start, end):
        """Возвращает подробное описание ивента"""
        text = cur.execute('''SELECT description FROM events 
                                      WHERE start_hour = ? and start_minute = ? and end_hour = ? and
                                       end_minute = ? and day = ?''',
                           (*start, *end, self.day_n)).fetchone()[0]
        return text

    def add_event(self):
        """Добавляет ивент в EventView"""
        dialog = EventDialog(self)
        dialog.exec()

    def clear_event(self):
        """Удаляет выбранный ивент"""
        try:
            start, end = get_start_and_end(self.EventView.currentItem().text())
        except AttributeError:
            create_message_window(self, 'Событие не выбрано')
            return
        cur.execute('''DELETE FROM events 
                        WHERE start_hour = ? and start_minute = ? and end_hour = ? and 
                        end_minute = ? and day = ?''',
                    (*start, *end, self.day_n))
        con.commit()
        self.EventView.takeItem(self.EventView.currentRow())
        self.event_description.setText('')

    def clear_day(self):
        """Очищает график дня"""
        cur.execute('''DELETE FROM events WHERE day = ?''', (self.day_n,))
        con.commit()
        self.event_description.setText('')
        self.EventView.clear()

    def edit_event(self):
        """Редактирует выбранный ивент"""
        try:
            name = self.EventView.currentItem().text().split('-')[1].strip()
            start, end = get_start_and_end(self.EventView.currentItem().text())
            text = self.get_description(start, end)
        except AttributeError:
            create_message_window(self, 'Событие не выбрано')
            return
        dialog = EventDialog(self, edit=True)
        dialog.event_name.setText(name)
        dialog.event_text.setText(text)
        dialog.event_start.setTime(QTime(*start))
        dialog.event_end.setTime(QTime(*end))
        dialog.exec()

    def back_week_window(self):
        """Показывает окно ChartWeekWindow и закрывает это"""
        self.mainwindow.show()
        self.close()

    def give_data(self):
        """Заполняет события в EventView из БД"""
        events = cur.execute('''SELECT start_hour, start_minute, end_hour, end_minute, name 
                                FROM events WHERE day = ?''',
                             (self.day_n,)).fetchall()
        for items in events:
            time = [str(i).rjust(2, '0') for i in items[:-1]]
            text = 'c {}:{} по {}:{} - {}'.format(*time, items[-1])
            self.EventView.addItem(text)

    def give_event_info(self, state):
        """Показывает побробное описание ивента в event_description"""
        start, end = get_start_and_end(state.text())
        text = self.get_description(start, end)
        self.event_description.setText(text)

    def create_table(self):
        """Создает по данным событий таблицу excel"""
        create_excel(self, [self.day])

    def load_table(self):
        """Востанавливаем события из таблицы excel"""
        load_excel_in_week(self, self.day)
        self.EventView.clear()
        self.give_data()
