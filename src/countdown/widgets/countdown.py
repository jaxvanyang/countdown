from math import floor
from textual.widgets import Digits
from datetime import datetime


class Countdown(Digits):
    DEFAULT_VALUE = "00:00:00"

    DEFAULT_CSS = "Countdown { width: auto; }"

    def __init__(self, year: int, month: int, day: int, hour: int, minute: int) -> None:
        super().__init__(self.DEFAULT_VALUE)

        self.date = datetime(year, month, day, hour, minute)

    def on_mount(self) -> None:
        self.update_value()
        self.set_interval(1 / 60, self.update_value)

    def update_value(self) -> None:
        now = datetime.now()
        if self.date < now:
            self.update(self.DEFAULT_VALUE)
            return

        diff = self.date - now
        (hours, rem) = divmod(diff.total_seconds(), 3600)
        (minutes, seconds) = divmod(rem, 60)
        seconds = floor(seconds)

        self.update(f"{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f}")
