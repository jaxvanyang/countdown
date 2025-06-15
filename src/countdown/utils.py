def is_leap_year(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def days_of_month(month: int, is_leap: bool = False) -> int:
    assert 1 <= month <= 12

    if month == 2:
        return 29 if is_leap else 28
    elif month in [4, 6, 9, 11]:
        return 30
    else:
        return 31

def cycle_update(min: int, max: int, value: int, delta: int) -> int:
    assert min <= value <= max
    width = max - min + 1
    delta = (delta % width + width) % width
    return min + (value - min + width + delta) % width

