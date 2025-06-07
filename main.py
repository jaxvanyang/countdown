from math import floor, log10
from pathlib import Path
from textual.app import App, ComposeResult, RenderResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Digits
from textual.containers import HorizontalGroup
from datetime import datetime
from platformdirs import user_config_dir

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

class DateSelector(HorizontalGroup, can_focus=True):
    """A widget to select date."""

    class Updated(Message):
        """Date updated message."""

    DEFAULT_CSS = """
    .selected {
        text-style: $button-focus-text-style;
        background-tint: $foreground 5%;
    }

    #hour {
        margin-left: 1;
    }
    """
    BINDINGS = [
        ("h", "select_left", "Select left"),
        ("j", "decrease", "Decrease"),
        ("k", "increase", "Increase"),
        ("l", "select_right", "Select right"),
    ]
    MIN_YEAR = 2000
    MAX_YEAR = 2050

    def __init__(self, year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> None:
        super().__init__()

        self.selected = 0
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute

    def compose(self) -> ComposeResult:
        yield NumberSelector(self.MIN_YEAR, self.MAX_YEAR, self.year, classes="selected", id="year")
        yield NumberSelector(1, 12, self.month, id="month")
        yield NumberSelector(1, days_of_month(self.month, is_leap_year(self.year)), self.day, id="day")
        yield NumberSelector(0, 23, self.hour, id="hour")
        yield NumberSelector(0, 59, self.minute, id="minute")

    def action_select_left(self) -> None:
        if self.selected > 0:
            self.selected -= 1

        self.query_one(".selected", NumberSelector).remove_class("selected")
        self.query(NumberSelector)[self.selected].add_class("selected")

    def action_select_right(self) -> None:
        if self.selected < 4:
            self.selected += 1

        self.query_one(".selected", NumberSelector).remove_class("selected")
        self.query(NumberSelector)[self.selected].add_class("selected")

    def action_decrease(self) -> None:
        match self.selected:
            case 0:
                self.update_year(-1)
            case 1:
                self.update_month(-1)
            case 2:
                self.update_day(-1)
            case 3:
                self.update_hour(-1)
            case 4:
                self.update_minute(-1)
            case _:
                return

        self.post_message(self.Updated())

    def action_increase(self) -> None:
        match self.selected:
            case 0:
                self.update_year(1)
            case 1:
                self.update_month(1)
            case 2:
                self.update_day(1)
            case 3:
                self.update_hour(1)
            case 4:
                self.update_minute(1)
            case _:
                return

        self.post_message(self.Updated())

    def update_year(self, delta: int) -> None:
        self.year = cycle_update(self.MIN_YEAR, self.MAX_YEAR, self.year, delta)
        self.query_one("#year", NumberSelector).value = self.year
        self.query_one("#year", NumberSelector).refresh()

    def update_month(self, delta: int) -> None:
        self.month = cycle_update(1, 12, self.month, delta)
        self.query_one("#month", NumberSelector).value = self.month
        self.query_one("#month", NumberSelector).refresh()

    def update_day(self, delta: int) -> None:
        days = days_of_month(self.month, is_leap_year(self.year))
        self.day = cycle_update(1, days, self.day, delta)
        self.query_one("#day", NumberSelector).max = days
        self.query_one("#day", NumberSelector).value = self.day
        self.query_one("#day", NumberSelector).refresh()

    def update_hour(self, delta: int) -> None:
        self.hour = cycle_update(0, 23, self.hour, delta)
        self.query_one("#hour", NumberSelector).value = self.hour
        self.query_one("#hour", NumberSelector).refresh()

    def update_minute(self, delta: int) -> None:
        self.minute = cycle_update(0, 59, self.minute, delta)
        self.query_one("#minute", NumberSelector).value = self.minute
        self.query_one("#minute", NumberSelector).refresh()

class NumberSelector(Widget):

    DEFAULT_CSS = """
    NumberSelector {
        width: auto;
        height: auto;
        border: round white;
    }
    """

    def __init__(self, min: int, max: int, default: int | None = None, **kwargs) -> None:
        super().__init__(**kwargs)

        self.min = min
        self.max = max
        self.value = default or min
        assert min <= self.value <= max

    def render(self) -> RenderResult:
        width = floor(log10(self.max)) + 1
        return f"{self.value:0{width}}"

class CountdownApp(App):

    TITLE = "Countdown"
    DEFAULT_DATE = [2026, 1, 1, 0, 0]
    CONFIG_PATH = Path(user_config_dir("countdown")) / "date.csv"
    BINDINGS = [
        ("q", "quit", "Quit")
    ]
    CSS = """
    Screen {
        align: center middle;
    }

    #countdown {
        align-horizontal: center;
        margin: 1;
    }

    DateSelector {
        align-horizontal: center;
        margin: 1;
    }
    """

    def __init__(self, date: list[int] | None = None):
        super().__init__()

        date = date or self.load_date()
        date.extend(self.DEFAULT_DATE[len(date):len(self.DEFAULT_DATE)])
        self.date = date

    def compose(self) -> ComposeResult:
        yield HorizontalGroup(Countdown(*self.date), id="countdown")
        yield DateSelector(*self.date)

    def on_date_selector_updated(self, message: DateSelector.Updated) -> None:
        self.sync_date()
        self.refresh_countdown()

    def load_date(self) -> list[int]:
        """Read date from the config file."""

        date = self.DEFAULT_DATE
        if self.CONFIG_PATH.is_file():
            with open(self.CONFIG_PATH) as f:
                content = ",".join(f.readlines())
                values = content.split(",")

            for i in range(0, 5):
                if len(values) > i:
                    date[i] = int(values[i])
                else:
                    break

        return date

    def sync_date(self) -> None:
        """Sync date and write to the config file."""

        d = self.query_one(DateSelector)
        self.date = [d.year, d.month, d.day, d.hour, d.minute]

        if not self.CONFIG_PATH.is_file():
            self.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

        with open(self.CONFIG_PATH, "w") as f:
            f.write(",".join(str(value) for value in self.date))

    def refresh_countdown(self) -> None:
        """Sync the date with the countdown widget."""

        self.query_one(Countdown).date = datetime(*self.date)

def main():
    app = CountdownApp()
    app.run()


if __name__ == "__main__":
    main()
