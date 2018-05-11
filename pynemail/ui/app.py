import asyncio
import curses


class App:

    def __init__(self):
        self.screen = None
        self.loop = asyncio.get_event_loop()
        self.stopped = False

    def __enter__(self):
        self.screen = curses.initscr()
        self.screen.nodelay(True)
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(1)

        try:
            curses.start_color()
        except:
            pass
        return self

    def __exit__(self, *args):
        self.screen.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    def render(self):
        self.page.render()

    def refresh(self):
        self.page.refresh()

    async def get_input(self):
        if self.stopped:
            return
        key = self.screen.getch()
        if key == -1:
            await asyncio.sleep(0.02)
        else:
            if key == ord('q') or key == ord('Q'):
                self.stopped = True
                self.loop.stop()
            elif key == curses.KEY_RESIZE:
                pass  # TODO: Something!
            else:
                self.page.keypress(key)
            self.loop.call_soon(self.render)
            self.loop.call_soon(self.refresh)
        self.loop.create_task(self.get_input())

    # TODO: Don't pass page in!!!
    def run(self, page):
        self.page = page
        self.loop.call_soon(self.render)
        self.loop.call_soon(self.refresh)
        self.loop.create_task(self.get_input())
        try:
            self.loop.run_forever()
        finally:
            self.loop.run_until_complete(asyncio.gather(*asyncio.Task.all_tasks()))
            self.loop.close()

    # TODO: Use functools.partial to allow **kwargs
    def schedule(self, delay, func, *args):
        self.loop.call_later(delay, func, *args)

    def repeat(self, interval, func, *args, **kwargs):
        def schedule():
            self.schedule(interval, _repeater)
        def _repeater():
            if not self.stopped:
                schedule()
            func(*args, **kwargs)
        schedule()
