from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup
from datetime import datetime
from platformdirs import user_config_dir
from .widgets import Countdown, DateSelector

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
