from datetime import time


def get_start_and_end(text):
    """Возращает интервал времени типа int"""
    text = text.split()
    start = list(map(int, text[1].split(':')))
    end = list(map(int, text[3].split(':')))
    return start, end


def get_time_start_and_end(start, end):
    """Возращает интервал времени типа datetime.time"""
    text = f'с {start} по {end}'
    start, end = get_start_and_end(text)
    return time(*start), time(*end)