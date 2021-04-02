import xlsxwriter
from PyQt5.QtWidgets import QInputDialog, QFileDialog
from MainWindows.window_manager.message_window import create_message_window
from sqlite import cur
from sqlite.sqlite_manager import get_number_day


def create_excel(window, days):
    """Создаем таблицу из наших ивентов"""
    # выбор названия файла
    file_name, ok_pressed = QInputDialog.getText(window, "Название файла",
                                                 "Введите желаемое название файла")
    # если название файла не введено то ничего не делаем
    # получаем путь папки куда сохранить файл
    if not ok_pressed or not file_name:
        return
    folder_way = QFileDialog.getExistingDirectory(window)
    if not folder_way:
        return
    # сохраняем сгенерированную таблицу в указанную папку
    try:
        workbook = xlsxwriter.Workbook(f'{folder_way}/{file_name}.xlsx')
    except FileNotFoundError:
        return
    for day in days:
        worksheet = workbook.add_worksheet(day)
        day_n = get_number_day(day)
        # вносим данные в таблицу
        give_info_in_table(worksheet, day_n)
    create_message_window(window, 'Таблица создана')
    workbook.close()


def give_info_in_table(worksheet: xlsxwriter.worksheet.Worksheet, day_n):
    """Заносим информацию в лист таблицы"""
    data = cur.execute('''SELECT * FROM events WHERE day = ? ORDER BY start_hour''',
                       (day_n,)).fetchall()
    row = 0
    for col, item in enumerate(['с', 'по', 'название', 'описание']):
        worksheet.write(row, col, item)
    for row, items in enumerate(data):
        # беру часы и минуты начала и конца события и привожу их к правильному виду
        st_h, st_m, end_h, end_m = [str(i).rjust(2, '0') for i in items[2:-2]]
        start, end = f'{st_h}:{st_m}', f'{end_h}:{end_m}'
        items = [start, end] + list(items[-2:])
        for col, item in enumerate(items):
            worksheet.write(row + 1, col, item)
