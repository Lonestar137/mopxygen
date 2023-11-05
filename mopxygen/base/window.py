import curses
import asyncio
from contextlib import AbstractContextManager
from curses.textpad import Textbox, rectangle


class CursesWindow(AbstractContextManager):
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.window = curses.newwin(self.height, self.width, 0, 0)
        self.window.border(0)
        self.window.refresh()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.window.clear()
        self.window.refresh()
        curses.endwin()

    def update(self):
        new_height, new_width = self.stdscr.getmaxyx()
        if new_height != self.height or new_width != self.width:
            self.height, self.width = new_height, new_width
            self.window.resize(self.height, self.width)
            self.window.clear()
            self.window.border(0, 0, 0, 0, 0, 0, 0, curses.ACS_BLOCK)
            self.window.refresh()


class VerticalPane:
    def __init__(self, parent, content):
        self.parent = parent
        self.content = content
        self.height, self.width = parent.getmaxyx()
        self.window = curses.newwin(self.height, self.width // 4, 0, 0)
        self.window.border(0)
        self.window.refresh()

    def display(self):
        self.window.clear()
        self.window.border(0)
        for i, item in enumerate(self.content):
            if i >= self.height - 2:
                break
            if len(item) > self.width // 4 - 2:
                item = item[:self.width // 4 - 5] + "..."
            self.window.addstr(i + 1, 1, item)
        if len(self.content) > self.height - 2:
            self.window.addstr(self.height - 2, 1, "...(more)")
        self.window.refresh()

    def update(self):
        new_height, new_width = self.parent.getmaxyx()
        if new_height != self.height or new_width != self.width:
            self.height, self.width = new_height, new_width
            self.window.resize(self.height, self.width // 4)
            self.window.clear()
            self.window.border(0)
            self.display()


async def check_resize(pane):
    while True:
        await asyncio.sleep(0)  # Allow other tasks to run
        if pane.parent.getch() == curses.KEY_RESIZE:
            pane.update()


async def start(stdscr):
    with CursesWindow(stdscr) as base:
        content = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5",
                   "Item 6", "Item 7", "Item 8", "Item 9", "Item 10"]
        pane = VerticalPane(base.window, content)
        resize_task = asyncio.create_task(check_resize(pane))
        while True:
            pane.display()
            pane.update()

            base.window.refresh()
            base.update()

            key = base.window.getch()
            if key == ord('q'):
                break
        resize_task.cancel()


def main(stdscr):
    curses.curs_set(0)
    return asyncio.run(start(stdscr))


if __name__ == '__main__':
    curses.wrapper(main)

# if __name__ == '__main__':
#     curses.wrapper(asyncio.run, main)
