class Page:

    def __init__(self):
        self.child_pages = []

    def _keypress(self, key):
        raise NotImplementedError('Page._keypress')

    def _render(self):
        raise NotImplementedError('Page._render')

    def _resize(self):
        raise NotImplementedError('Page._resize')

    def _refresh(self):
        raise NotImplementedError('Page._refresh')

    def keypress(self, key):
        for page in self.child_pages[::-1]:
            if not page._keypress(key):
                break
        else:
            self._keypress(key)

    def render(self):
        self._render()
        for page in self.child_pages:
            page.render()

    def resize(self, h, w):
        self._resize(h, w)
        for page in self.child_pages:
            page.resize(h, w)

    def refresh(self):
        self._refresh()
        for page in self.child_pages:
            page.refresh()
