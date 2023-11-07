
import curses
import curses.panel


class BSPWindow:
    def __init__(self, window, direction=None):
        self.window = window
        self.direction = direction
        self.subwindows = []
        self.task = None
        self.title = None

    def split(self, direction, percentage):
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
                int(height * percentage), width, int(height * (1 - percentage)), 0)
        else:
            raise ValueError("Invalid direction")
        subwindow1.border(0)
        subwindow2.border(0)
        subwindow1.refresh()
        subwindow2.refresh()
        self.subwindows = [BSPWindow(subwindow1), BSPWindow(subwindow2)]
        for subwindow in self.subwindows:
            subwindow.direction = direction

        return self

    def set_title(self, title: str):
        self.title = title
        return self.subwindows[0]

    def display(self):
        if self.subwindows:
            for subwindow in self.subwindows:
                subwindow.display()
        else:
            self.window.border()
            if self.title:
                self.window.addstr(0, 0, "TEST")

            if self.task:
                # What to do in each Window.
                pass
            else:
                self.window.addstr(1, 1, "Window")
        self.window.refresh()

    def update(self):
        if self.subwindows:
            for subwindow in self.subwindows:
                subwindow.update()
        self.window.refresh()


def main(root_window):
    curses.curs_set(0)
    # root_window = curses.newwin(curses.LINES, curses.COLS, 0, 0)
    root_window.refresh()
    root_bsp_window = BSPWindow(root_window)
    win2 = root_bsp_window.split("down", 0.2)
    win2.set_title("Window 2")
    root_bsp_window.subwindows[0].split("left", 0.3)
    # root_bsp_window.subwindows[1].subwindows[1].split("right", 0.1)
    # root_bsp_window.subwindows[0].subwindows[0].subwindows[0].split("right")
    # root_bsp_window.subwindows[0].subwindows[1].split("down")
    while True:
        root_bsp_window.display()
        # root_bsp_window.update()
        key = root_window.getch()
        if key == ord('q'):
            break


if __name__ == '__main__':
    curses.wrapper(main)
