from math import floor, log10
from pathlib import Path
from textual.app import App, ComposeResult, RenderResult
from textual.widget import Widget
from textual.widgets import Digits
from textual.containers import HorizontalGroup
from datetime import datetime
from platformdirs import user_config_dir

class CountDown(Digits):
    DEFAULT_VALUE = "00:00:00"

    DEFAULT_CSS = "CountDown { width: auto; }"

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

        diff = self.date - now
        (hours, rem) = divmod(diff.total_seconds(), 3600)
        (minutes, seconds) = divmod(rem, 60)
        seconds = floor(seconds)

        self.update(f"{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f}")

class DateSelector(HorizontalGroup):

    DEFAULT_CSS = ".hour { margin-left: 1; }"

    def __init__(self, year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> None:
        super().__init__()

        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute

    def compose(self) -> ComposeResult:
        yield NumberSelector(2000, 2050, self.year)
        yield NumberSelector(1, 12, self.month)
        yield NumberSelector(1, 31, self.day)
        yield NumberSelector(0, 23, self.hour, classes="hour")
        yield NumberSelector(0, 59, self.minute)

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

    def render(self) -> RenderResult:
        width = floor(log10(self.max)) + 1
        return f"{self.value:0{width}}"

class CountDownApp(App):

    TITLE = "Count Down"
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

        date = date or self.DEFAULT_DATE
        date.extend(self.DEFAULT_DATE[len(date):len(self.DEFAULT_DATE)])

        if self.CONFIG_PATH.is_file():
            with open(self.CONFIG_PATH) as f:
                content = ",".join(f.readlines())
                values = content.split(",")

            for i in range(0, 5):
                if len(values) > i:
                    date[i] = int(values[i])
                else:
                    break

        self.date = date

    def compose(self) -> ComposeResult:
        yield HorizontalGroup(CountDown(*self.date), id="countdown")
        yield DateSelector(*self.date)

def main():
    app = CountDownApp()
    app.run()


if __name__ == "__main__":
    main()
