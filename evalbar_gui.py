import tkinter as tk
import math

class EvalBar(tk.Canvas):

    def __init__(self, top, gui):

        # Reference to the tkinter main window
        self.top = top

        # The chess board that we are connected to
        self.gui = gui

        # Parameters related to the bar layout
        self.canvas_height = 600
        self.canvas_width = 40
        self.bar_x_offset = 5
        self.bar_y_offset = 5
        self.bar_height = 560
        self.bar_width = 20

        # Drawable canvas
        tk.Canvas.__init__(self, top, bg = "white", highlightthickness=0, height = self.canvas_height, width = self.canvas_width)

        # Draw black and white sides of eval bar
        self.black_rect = self.create_rectangle(self.bar_x_offset, self.bar_y_offset, self.bar_x_offset + self. bar_width, self.bar_y_offset + self.bar_height / 2, fill = "black")
        self.white_rect = self.create_rectangle(self.bar_x_offset, self.bar_y_offset + self.bar_height / 2, self.bar_x_offset + self.bar_width, self.bar_y_offset + self.bar_height, fill = "white")

        # Label for evaluation
        self.eval_text = self.create_text((2 * self.bar_x_offset + self. bar_width)/2, 3 * self.bar_y_offset + self.bar_height, text = "+0.0")

        # Register for callbacks
        self.gui.register_eval_bar(self)

    def new_game(self):
        self.update_winning_chances(0)

    def update_winning_chances(self, white_centipawns):
        """
        Computes winning chances for graphing.  This uses the
        formula used by Lichess found here:
        https://github.com/lichess-org/lila/blob/master/ui/ceval/src/winningChances.ts
        """
        multiplier = -0.00368208
        limited_centipawns = min(max(-1000, white_centipawns), 1000)
        white_winning_percentage = 2 / (1 + math.exp(multiplier * limited_centipawns)) - 1;
        self.render_eval_bar(white_winning_percentage, white_centipawns)
    
    def render_eval_bar(self, white_winning_percentage, white_centipawns):
        white_height_mult = (white_winning_percentage + 1) / 2
        white_height = self.bar_height * white_height_mult
        black_height = self.bar_height - white_height
        self.coords(self.black_rect, self.bar_x_offset, self.bar_y_offset, self.bar_x_offset + self.bar_width, self.bar_y_offset + black_height)
        self.coords(self.white_rect, self.bar_x_offset, self.bar_y_offset + black_height, self.bar_x_offset + self.bar_width, self.bar_y_offset + self.bar_height)
        if white_centipawns >= 5000:
            eval_str = "+∞"
        elif white_centipawns <= -5000:
            eval_str = "-∞"
        else:
            eval_str = '{0:.1f}'.format(white_centipawns / 100)
            if white_centipawns >= 0:
                eval_str = "+" + eval_str
        self.itemconfig(self.eval_text, text=eval_str)
