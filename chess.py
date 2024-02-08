import chess_board
import chess_gui
import display_panel
import evalbar_gui
import opening_finder
import tkinter as tk

if __name__ == "__main__":

    # tk window
    top = tk.Tk()
    top.title("Chess")
    top.geometry("1100x600")
    top.configure(background="white")

    # Chess board
    board = chess_board.Board()

    # Opening books
    openings = opening_finder.OpeningFinder()
    openings.load_opening_book_tsv("resources/a.tsv")
    openings.load_opening_book_tsv("resources/b.tsv")
    openings.load_opening_book_tsv("resources/c.tsv")
    openings.load_opening_book_tsv("resources/d.tsv")
    openings.load_opening_book_tsv("resources/e.tsv")

    # Chess GUI (which is a tk.Canvas)
    gui = chess_gui.ChessGUI(top, board)
    gui.pack(side = tk.LEFT)

    # Eval bar (which is a tk.Canvas)
    eval_bar = evalbar_gui.EvalBar(top, gui)
    eval_bar.pack(side = tk.LEFT)

    # Display panel (which is a tk.Frame)
    display = display_panel.DisplayPanel(top, gui)
    display.attach_openings(openings)
    display.pack(side = tk.LEFT)
    
    # Execute main loop
    top.protocol("WM_DELETE_WINDOW", gui.shutdown)
    top.mainloop()