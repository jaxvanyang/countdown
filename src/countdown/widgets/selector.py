from math import floor, log10
from textual.app import ComposeResult, RenderResult
from textual.message import Message
from textual.widget import Widget
from textual.containers import HorizontalGroup
from countdown.utils import days_of_month, is_leap_year, cycle_update

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
        ("left,h,a", "select_left", "Select left"),
        ("right,l,d", "select_right", "Select right"),
        ("up,k,w", "increase", "Increase"),
        ("down,j,s", "decrease", "Decrease"),
    ]
    MIN_YEAR = 1
    MAX_YEAR = 9999

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
