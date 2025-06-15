from .app import CountdownApp

__all__ = [
    "CountdownApp",
]

def main():
    app = CountdownApp()
    app.run()


if __name__ == "__main__":
    main()
