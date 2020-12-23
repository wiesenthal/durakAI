from colorama import Fore, Back, Style, init, deinit

init()


class ColorHandler:
    def __init__(self, initial_color=Fore.WHITE + Style.BRIGHT):
        self.color_stack = []
        self.set(initial_color)
        self.initial_color = initial_color

    @property
    def end(self): # returns color after popped
        self.color_stack.pop()
        col = ''
        for c in self.color_stack:
            col += c
        return Style.RESET_ALL + col

    def clear(self):
        self.color_stack = []
        self.set(initial_color)
        self.initial_color = initial_color

    def start(self, color):
        self.color_stack.append(color)
        return self.top()

    def top(self):
        return self.color_stack[-1]

    def set(self, color):
        print(self.start(color), end='')

    def unset(self):
        print(self.end, end='')

    def colored(self, text, color):
        return self.start(color) + text + self.end

    def __call__(self, color=None):
        if color:
            return self.start(color)
        else:
            return self.end


