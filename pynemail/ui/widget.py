from typing import List


class Widget:

    def __init__(self) -> None:
        self.child_pages = []  # type: List[Page]

    def _keypress(self, key: int) -> bool:
        raise NotImplementedError('Page._keypress')

    def _render(self) -> None:
        raise NotImplementedError('Page._render')

    def _resize(self, h: int, w: int) -> None:
        raise NotImplementedError('Page._resize')

    def _refresh(self) -> None:
        raise NotImplementedError('Page._refresh')

    def keypress(self, key: int) -> bool:
        for page in self.child_pages[::-1]:
            if not page._keypress(key):
                return False
        else:
            return self._keypress(key)

    def render(self) -> None:
        self._render()
        for page in self.child_pages:
            page.render()

    def resize(self, h: int, w: int) -> None:
        self._resize(h, w)
        for page in self.child_pages:
            page.resize(h, w)

    def refresh(self) -> None:
        self._refresh()
        for page in self.child_pages:
            page.refresh()
