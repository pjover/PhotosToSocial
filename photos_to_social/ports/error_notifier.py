from typing import Protocol


class ErrorNotifier(Protocol):

    def notify(self, title: str, message: str):
        """Notify an error."""
        ...
