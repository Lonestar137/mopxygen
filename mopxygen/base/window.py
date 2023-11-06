from dataclasses import dataclass
import os
import abc
import time
import subprocess
import curses
import asyncio
from typing import Union, List
from contextlib import AbstractContextManager
from curses.textpad import Textbox, rectangle


class CursesWindow(AbstractContextManager):
    def __init__(self, stdscr, bottom_gap: int = 10):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.window = curses.newwin(
            self.height-bottom_gap, self.width, 0, 0)
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


def open_files(content, display_height, display_width):
    file_contents = {}

    width = display_width - 2
    for filename in content:
        try:
            with open(filename, 'r') as f:
                file_rows = f.read().splitlines()
                lines = [l[:width] for l in file_rows]
                trimmed_lines = []
                if len(lines) > display_height - 2:
                    trimmed_lines = lines[:display_height - 2]
                else:
                    trimmed_lines = lines

                file_contents[filename] = {
                    "display_str": trimmed_lines, "original": file_rows}
        except FileNotFoundError:
            file_contents[filename] = {
                "display_str": [f"File not found: {filename}"], "original": [""]}
    return file_contents


def find_default_editor() -> str:
    editor = None
    try:
        editor = os.environ["EDITOR"]
    except KeyError:
        editor = "nano"
    return editor


class VerticalPane:
    def __init__(self, parent, content, title=None):
        self.parent = parent
        self.content = content
        self.title = title
        self.height, self.width = parent.getmaxyx()
        self.preview_width = self.width // 4 * 3
        self.content_dict = open_files(
            content, self.height, self.preview_width)
        self.selected = None
        self.window = curses.newwin(self.height, self.width // 4, 0, 0)
        self.window.border(0)
        self.window.refresh()
        self.scroll_pos = 0
        self.selected_index = 0
        self.focused = True

    def display(self):
        self.window.clear()
        self.window.border(0)
        if self.title:
            self.window.addstr(0, 1, self.title, curses.A_BOLD)
        middle_index = self.height // 2
        for i in range(self.height - 2):
            index = self.scroll_pos + i
            if index >= len(self.content):
                index -= len(self.content)
            item = self.content[index]
            if len(item) > self.width // 4 - 2:
                item = item[:self.width // 4 - 5] + "..."
            # if i == middle_index:
            if item == self.get_selected_item():
                if self.focused:
                    self.window.addstr(i + 1, 1, item, curses.A_REVERSE)
                else:
                    self.window.addstr(i + 1, 1, item, curses.A_BOLD)
            else:
                self.window.addstr(i + 1, 1, item)
        if len(self.content) > self.height - 2:
            self.window.addstr(self.height - 2, 1, "...(more)")
        if self.focused:
            selected_item = self.get_selected_item()
            preview_window = curses.newwin(
                self.height, self.width // 4 * 3, 0, self.width // 4)
            preview_window.border(0)
            preview_window.refresh()
            for i, line in enumerate(self.content_dict[selected_item]["display_str"]):
                preview_window.addstr(1+i, 1, line)
            preview_window.refresh()

        self.window.refresh()

    def update(self):
        new_height, new_width = self.parent.getmaxyx()
        if new_height != self.height or new_width != self.width:
            self.height, self.width = new_height, new_width
            self.window.resize(self.height, self.width // 4)
            self.window.clear()
            self.window.border(0)
            self.display()

    def scroll_down(self):
        self.scroll_pos += 1
        if self.scroll_pos >= len(self.content):
            self.scroll_pos = 0
        self.selected_index += 1
        if self.selected_index >= len(self.content):
            self.selected_index = 0

    def scroll_up(self):
        self.scroll_pos -= 1
        if self.scroll_pos < 0:
            self.scroll_pos = len(self.content) - 1
        self.selected_index -= 1
        if self.selected_index < 0:
            self.selected_index = len(self.content) - 1

    def handle_key(self, key, process=None):
        if key == curses.KEY_DOWN or key == ord('j'):
            self.scroll_down()
        elif key == curses.KEY_UP or key == ord('k'):
            self.scroll_up()
        elif key == curses.KEY_ENTER or key == ord('\n') and type(process) == LessPane:
            selected_item = self.get_selected_item()
            process.spawn_less(selected_item)
        elif key in [ord('l'), ord('\n'), curses.KEY_ENTER]:
            selected_item = self.get_selected_item()
            subprocess.run(["less", selected_item])
        elif key == ord('e'):
            editor = find_default_editor()
            selected_item = self.get_selected_item()
            subprocess.run([editor, selected_item])

    def get_selected_item(self):
        return self.content[self.selected_index]

    def focus(self):
        self.focused = True

    def search(self):
        # TODO: SEARCH
        # in VerticalPane, create textpad, clone original, and set update content
        pass


class LessPane:
    def __init__(self, parent):
        self.parent = parent
        self.height, self.width = parent.getmaxyx()
        self.window = curses.newwin(
            self.height, self.width // 4 * 3, 0, self.width // 4)
        self.window.border(0)
        self.window.refresh()
        self.process = None

    def display(self):
        self.window.clear()
        self.window.border(0)
        self.window.refresh()

    def update(self):
        new_height, new_width = self.parent.getmaxyx()
        if new_height != self.height or new_width != self.width:
            self.height, self.width = new_height, new_width
            self.window.resize(self.height, self.width // 4 * 3)
            self.window.clear()
            self.window.border(0)
            self.display()

    def spawn_less(self, filename):
        self.process = subprocess.Popen(
            ["less", filename], stdout=subprocess.PIPE)
        output = self.process.communicate()[0]
        self.window.addstr(1, 1, output.decode())
        self.window.refresh()

    def kill_less(self):
        if self.process is not None:
            self.process.kill()
            self.process = None
            self.window.clear()
            self.window.border(0)
            self.window.refresh()

    def focus(self):
        self.focused = True


@dataclass
class Indicator:
    """ 
        value:    
            bool, will be check box
            %str, Will show a bar.
            str%, Will show as string.
            str, Will show as string.
    """
    name: str
    value: Union[str, bool]
    prompt_color: str = None
    value_color: str = None

    def display_indicator(self, parent, y, x):
        parent.addstr(y, x + 1, self.name, curses.A_BOLD)


class StatusLineWidget:
    def __init__(self, parent, indicators: List[Indicator]):
        self.parent = parent
        self.height, self.width = parent.getmaxyx()
        self.pane_height = int(self.height * 0.17)
        self.window = curses.newwin(
            self.pane_height, self.width, self.height, 0)
        self.window.border(0)
        self.window.refresh()
        self.indicators: List[Indicator] = indicators

    def display(self):
        self.window.clear()
        self.window.border(0)

        row_width = 20
        row_height = 3
        base_x = 1
        y = 1

        for indicator in self.indicators:
            if base_x > self.width and not y > self.pane_height - 1:
                y += row_height
                base_x = 1
            if y > self.pane_height - 1:
                self.window.addstr(self.pane_height-1, 1,
                                   "more hidden indicators . . .", curses.A_BOLD)

            try:
                indicator.display_indicator(self.window, y, base_x)
                base_x += row_width
            except:
                pass

        self.window.refresh()

    def update(self):
        new_height, new_width = self.parent.getmaxyx()
        if new_height != self.height or new_width != self.width:
            self.height, self.width = new_height, new_width
            self.window.resize(self.height, self.width // 4 * 3)
            self.window.clear()
            self.window.border(0)
            self.display()


async def check_resize(pane):
    while True:
        await asyncio.sleep(0)  # Allow other tasks to run
        if pane.parent.getch() == curses.KEY_RESIZE:
            pane.update()


async def start_fileview(stdscr, content):

    indicators = [
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world"),
        Indicator(name="Test:", value="world")
    ]
    with CursesWindow(stdscr, bottom_gap=10) as base:
        pane = VerticalPane(base.window, content, title="Files")
        status_line = StatusLineWidget(base.window, indicators)
        resize_task = asyncio.create_task(check_resize(pane))
        # less_pane = LessPane(base.window)
        while True:
            pane.display()
            pane.update()
            # less_pane.display()
            # less_pane.update()

            status_line.display()
            status_line.update()

            base.window.refresh()
            base.update()

            key = base.window.getch()
            if key == ord('q'):
                break
            else:
                pane.handle_key(key)
        resize_task.cancel()


def main(stdscr):
    curses.curs_set(0)
    content = ["Item " + ("-" * i) for i in range(100)]
    content.append("/tmp/gameoverlayui.log")
    content.append("/tmp/tree.log")
    content.append("/home/jonesgc/.bashrc")
    return asyncio.run(start_fileview(stdscr, content))


if __name__ == '__main__':
    curses.wrapper(main)

# if __name__ == '__main__':
#     curses.wrapper(asyncio.run, main)
