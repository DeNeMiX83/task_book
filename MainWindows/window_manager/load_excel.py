import xlrd
from PyQt5.QtWidgets import QFileDialog

from MainWindows.window_manager.message_window import create_message_window
from sqlite import cur, con
from sqlite.sqlite_manager import get_number_day


def load_excel_in_week(window, day=None):
    """Загружает информацию из таблицы excel в таблицу events из БД"""
    file_name = QFileDialog.getOpenFileName(window, 'Выберите таблицу', '', '(*.xlsx)')[0]
    try:
        workbook = xlrd.open_workbook(file_name)
    except FileNotFoundError:
        return
    days = workbook.sheet_names()
    if day:
        days = [day]
    for day in days:
        try:
            day_n = get_number_day(day)
            worksheet = workbook.sheet_by_name(day)
            data = get_data_from_worksheet(worksheet)
            cur.execute('''DELETE FROM events WHERE day = ?''', (day_n,))
            load_data_in_list_widget(data, day_n)
        except xlrd.biffh.XLRDError:
            pass
        except TypeError as e:
            print(e)
            create_message_window(window, 'Ошибка чтения таблицы')
    create_message_window(window, 'Таблица загружена')


def get_data_from_worksheet(worksheet: xlrd.sheet.Sheet):
    """берем матрицу данных из листа таблицы"""
    num_rows = worksheet.nrows - 1
    num_cells = worksheet.ncols - 1
    curr_row = -1
    data = []
    while curr_row < num_rows:
        row = []
        curr_row += 1
        curr_cell = -1
        while curr_cell < num_cells:
            curr_cell += 1
            cell_value = worksheet.cell_value(curr_row, curr_cell)
            row.append(cell_value)
        data.append(row)
    # если в таблице нет этих элементов значит пользователь пытается использовать другую таблицу
    if data[0] != ['с', 'по', 'название', 'описание']:
        return []
    return data[1:]


def load_data_in_list_widget(data, day_n):
    """Заносим данные в таблицу events"""
    for line in data:
        time = line[0].split(':') + line[1].split(':')
        name = line[2]
        event_text = line[-1].replace('\n\n', '\n')
        cur.execute('''INSERT INTO events VALUES(NULL, ?, ?, ?, ?, ?, ?, ?)''',
                    (day_n, *time, name, event_text))
    con.commit()
