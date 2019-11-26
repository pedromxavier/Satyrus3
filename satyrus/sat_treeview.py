import tkinter as tk
from sat_core import *;

class Window:

    def __init__(self, root, expr, **kwargs):
        self.root = root
        self.expr = expr


        self.size = kwget("size", kwargs, (1200, 500))

        self.root.geometry(f"{self.size[0]}x{self.size[1]}")

        self.title = kwget("title", kwargs, 'tk')

        self.root.title(self.title)

        self.r = kwget('r', kwargs, 16)

        self.dk = 2

        self.show_types = kwget('show_types', kwargs, False)

        self.x, self.y = self.size[0] * 0.5, self.size[1] * 0.05

        self.l = self.size[0] * 0.25
        self.h =self. size[1] * 0.9 / self.expr.height

        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(expand=True, fill='both')

        ############
        self.write_expr()

        self.draw(self.expr, self.x, self.y)

    def write_expr(self):
        args = (self.size[0] * 0.5, self.size[1] * 0.9)

        kwargs = {
            'text' : f"{self.expr}",
            'font' : ("Courier", 14),
        }

        self.canvas.create_text(*args, **kwargs)


    def draw(self, expr, x, y, k=1):
        l = self.l / k
        h = self.h
        dk= self.dk
        if not expr.expr:
            self.draw_node(x, y, expr)
        else:
            n = expr.arity

            if n == 1:
                self.draw_arrow(x, y, x, y + h)
                self.draw(expr.tail[0], x, y + h, k*dk)
            elif n == 2:
                self.draw_arrow(x, y, x-l, y + h)
                self.draw_arrow(x, y, x+l, y + h)
                self.draw(expr.tail[0], x-l, y + h, k*dk)
                self.draw(expr.tail[1], x+l, y + h, k*dk)
            else:
                raise ValueError

            self.draw_node(x, y, expr.token)

    def draw_node(self, x, y, label):
        r = self.r;

        oval_args = (x-r, y-r, x+r, y+r);

        oval_kwargs = {
            'fill' : 'light gray',
            'outline' : 'black',
            };

        text_args = (x, y);

        text_kwargs = {
            'text' : f"{label}",
            'font' : ("Courier", 14),
            };

        type_args = (x, y + 8)

        type_kwargs = {
            'text' : f"{type(label)}",
            'font' : ("Courier", 8),
        }

        self.canvas.create_oval(*oval_args, **oval_kwargs);
        self.canvas.create_text(*text_args, **text_kwargs);
        if self.show_types:
            self.canvas.create_text(*type_args, **type_kwargs);

    def draw_arrow(self, x, y, z, w):

        arrow_args = (x, y, z, w);

        arrow_kwargs = {
                'fill' : 'black',
                'arrow': 'last',
            };

        self.canvas.create_line(*arrow_args, **arrow_kwargs)


def tree_view(expr, **kw):
    root = tk.Tk()
    self = Window(root, expr, **kw)
    root.mainloop()
