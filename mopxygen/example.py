
import curses
import curses.panel


class BSPWindow:
    def __init__(self, window, direction=None, behavior=None, title=None):
        self.window = window
        self.direction = direction
        self.subwindows = []
        self.behavior = behavior
        self.title = title

    def split(self, direction, percentage, behavior=None, title=None):
        if self.subwindows:
            raise ValueError("Window already split")
        height, width = self.window.getmaxyx()
        if direction == "left":
            subwindow1 = curses.newwin(height, int(width * percentage), 0, 0)
            subwindow2 = curses.newwin(height, int(
                width * (1 - percentage)), 0, int(width * percentage))
        elif direction == "right":
            subwindow1 = curses.newwin(
                height, int(width * (1 - percentage)), 0, 0)
            subwindow2 = curses.newwin(height, int(
                width * percentage), 0, int(width * (1 - percentage)))
        elif direction == "up":
            subwindow1 = curses.newwin(int(height * percentage), width, 0, 0)
            subwindow2 = curses.newwin(
                int(height * (1 - percentage)), width, int(height * percentage), 0)
        elif direction == "down":
            subwindow1 = curses.newwin(
                int(height * (1 - percentage)), width, 0, 0)
            subwindow2 = curses.newwin(
                int(height * percentage) + 1, width, int(height * (1 - percentage)), 0)

        else:
            raise ValueError("Invalid direction")
        self.window.clear()
        self.subwindows = [BSPWindow(subwindow1, self.direction, self.behavior, self.title), BSPWindow(
            subwindow2, direction, behavior, title)]
        for subwindow in self.subwindows:
            subwindow.display()
        # subwindow.direction = direction

    def display(self):
        # self.window.clear()
        if self.subwindows:
            for subwindow in self.subwindows:
                subwindow.display()
        else:
            self.window.border()
            self.window.addstr(1, 1, "Window")
            if self.behavior:
                self.behavior(self.window)
            if self.title:
                self.window.addstr(0, 2, self.title)
        self.window.refresh()

    def update(self):
        if self.subwindows:
            for subwindow in self.subwindows:
                subwindow.update()
        self.window.refresh()


def behavior1(window):
    window.addstr(2, 2, "Behavior 1")


def behavior2(window):
    window.addstr(2, 2, "Behavior 2")


def main(stdscr):
    curses.curs_set(0)
    root_window = curses.newwin(curses.LINES, curses.COLS, 0, 0)
    root_window.border()
    root_window.refresh()
    root_bsp_window = BSPWindow(
        root_window, behavior=behavior1, title="Root Window")
    root_bsp_window.split("right", 0.3, behavior=behavior2,
                          title="Left Subwindow")
    root_bsp_window.subwindows[0].split("down", 0.5, title="Bottom Subwindow")
    # root_bsp_window.subwindows[0].subwindows[0].split(
    #     "down", 0.5, title="Bottom Subwindow2")

    while True:
        root_bsp_window.display()
        root_bsp_window.update()

        key = stdscr.getch()
        if key == ord('q'):
            break


if __name__ == '__main__':
    curses.wrapper(main)
