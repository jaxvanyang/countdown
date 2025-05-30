from math import floor, log10
from textual.app import App, ComposeResult, RenderResult
from textual.widget import Widget
from textual.widgets import Digits
from textual.containers import HorizontalGroup
from datetime import datetime

class CountDown(Digits):
    DEFAULT_VALUE = "00:00:00"

    DEFAULT_CSS = "CountDown { width: auto; }"

    def __init__(self, year: int, month: int, day: int) -> None:
        super().__init__(self.DEFAULT_VALUE)

        self.date = datetime(year, month, day)

    def on_mount(self) -> None:
        self.update_value()
        self.set_interval(1, self.update_value)

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

    def __init__(self, year: int, month: int, day: int) -> None:
        super().__init__()

        self.year = year
        self.month = month
        self.day = day

    def compose(self) -> ComposeResult:
        yield NumberSelector(2000, 2050, self.year)
        yield NumberSelector(1, 12, self.month)
        yield NumberSelector(1, 31, self.day)

class NumberSelector(Widget):

    DEFAULT_CSS = """
    NumberSelector {
        width: auto;
        height: auto;
        border: round white;
    }
    """

    def __init__(self, min: int, max: int, default: int | None = None) -> None:
        super().__init__()

        self.min = min
        self.max = max
        self.value = default or min

    def render(self) -> RenderResult:
        width = floor(log10(self.max)) + 1
        return f"{self.value:0{width}}"

class CountDownApp(App):

    TITLE = "Count Down"
    DEFAULT_DATE = (2026, 1, 1)
    BINDINGS = [
        ("q", "quit", "Quit")
    ]
    CSS = """
    Screen {
        align: center middle;
    }

    #countdown {
        align-horizontal: center;

    }

    DateSelector {
        align-horizontal: center;
        margin: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield HorizontalGroup(CountDown(*self.DEFAULT_DATE), id="countdown")
        yield DateSelector(*self.DEFAULT_DATE)

def main():
    app = CountDownApp()
    app.run()


if __name__ == "__main__":
    main()
