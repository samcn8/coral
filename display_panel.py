import tkinter as tk
import tkinter.scrolledtext as st
from tkinter import filedialog as fd 
import math
import time
from player_type import PlayerType 

class DisplayPanel(tk.Frame):

    def __init__(self, top, gui):

        # Parameters related to display panel layout
        self.height = 600
        self.width = 400

        tk.Frame.__init__(self, top, bg = "white", height = self.height, width = self.width)
        self.pack_propagate(False)
        self.top = top

        # The chess board that we are connected to
        self.gui = gui

        # Register for callbacks
        self.gui.register_display(self)

        # Opening tree, which will be loaded seperately if we have one
        self.openings = None

        # Captured pieces images
        self.whites_captured_images = {"q":[], "r":[], "n":[], "b":[], "p":[]}
        self.blacks_captured_images = {"Q":[], "R":[], "N":[], "B":[], "P":[]}

        # Heading
        heading1 = tk.Label(self, background="White", text="Coral Chess GUI by Sam Nelson", font = (gui.font, 20, 'bold'))
        heading1.pack(side = tk.TOP)
        heading2 = tk.Label(self, background="White", text="https://www.github.com/samcn8/coral", font = (gui.font, 10, 'bold'))
        heading2.pack(side = tk.TOP)

        # Player names
        self.white_player_name = "Human"
        self.black_player_name = "Human"

        # Players info canvas
        pawn_light, pawn_dark = self.gui.get_pawn_sprites()
        box_width = 390
        box_height = 70
        box_side_buffer = 4
        canvas_added_top_buffer = 5
        box_space_between = 10
        self.black_captured_y = 3 + canvas_added_top_buffer + box_side_buffer + 2 * box_height // 3
        self.white_captured_y = 6 + canvas_added_top_buffer + box_side_buffer + 2 * box_height // 3 + box_height + box_space_between
        self.player_info_canvas = tk.Canvas(self, bg = "white", highlightthickness=0, height = canvas_added_top_buffer + 2 * box_side_buffer + 2 * box_height + box_space_between, width = 2 * box_side_buffer + box_width)
        self.player_info_canvas.pack(side = tk.TOP, pady = 5)
        self.player2_box = self.player_info_canvas.create_rectangle(box_side_buffer, canvas_added_top_buffer + box_side_buffer, box_side_buffer + box_width, canvas_added_top_buffer + box_side_buffer + box_height, outline="Black", width = 4)
        self.player1_box = self.player_info_canvas.create_rectangle(box_side_buffer, canvas_added_top_buffer + box_side_buffer + box_height + box_space_between, box_side_buffer + box_width, canvas_added_top_buffer + box_side_buffer + 2 * box_height + box_space_between, outline="Black", width = 4)
        
        self.selection_box_side = box_height / 2 - 6
        self.selection_box_x = box_side_buffer + 4
        self.player2_human_selection_box_y = canvas_added_top_buffer + box_side_buffer + 4
        self.player2_computer_selection_box_y = canvas_added_top_buffer + box_side_buffer + self.selection_box_side + 8
        self.player1_human_selection_box_y = canvas_added_top_buffer + box_side_buffer + 4 + box_height + box_space_between
        self.player1_computer_selection_box_y = canvas_added_top_buffer + box_side_buffer + self.selection_box_side + 8 + box_height + box_space_between

        self.player2_human_box = self.player_info_canvas.create_rectangle(self.selection_box_x, self.player2_human_selection_box_y, self.selection_box_x + self.selection_box_side, self.player2_human_selection_box_y + self.selection_box_side, outline="Black", width = 1)
        self.player_info_canvas.create_text(self.selection_box_x + self.selection_box_side/2, self.player2_human_selection_box_y + self.selection_box_side/2, text = "H")
        self.player2_computer_box = self.player_info_canvas.create_rectangle(self.selection_box_x, self.player2_computer_selection_box_y, self.selection_box_x + self.selection_box_side, self.player2_computer_selection_box_y + self.selection_box_side, outline="Black", width = 1)
        self.player_info_canvas.create_text(self.selection_box_x + self.selection_box_side/2, self.player2_computer_selection_box_y + self.selection_box_side/2, text = "C")
        self.player1_human_box = self.player_info_canvas.create_rectangle(self.selection_box_x, self.player1_human_selection_box_y, self.selection_box_x + self.selection_box_side, self.player1_human_selection_box_y + self.selection_box_side, outline="Black", width = 1)
        self.player_info_canvas.create_text(self.selection_box_x + self.selection_box_side/2, self.player1_human_selection_box_y + self.selection_box_side/2, text = "H")
        self.player1_computer_box = self.player_info_canvas.create_rectangle(self.selection_box_x, self.player1_computer_selection_box_y, self.selection_box_x + self.selection_box_side, self.player1_computer_selection_box_y + self.selection_box_side, outline="Black", width = 1)
        self.player_info_canvas.create_text(self.selection_box_x + self.selection_box_side/2, self.player1_computer_selection_box_y + self.selection_box_side/2, text = "C")       

        self.player2_name = self.player_info_canvas.create_text(80, canvas_added_top_buffer + box_side_buffer + box_height // 3, text = self.black_player_name, anchor = tk.W)
        self.player1_name = self.player_info_canvas.create_text(80, canvas_added_top_buffer + box_side_buffer + box_height // 3 + box_height + box_space_between, text = self.white_player_name, anchor = tk.W)
        self.player2_score = self.player_info_canvas.create_text(100, self.black_captured_y, text = "")
        self.player1_score = self.player_info_canvas.create_text(100, self.white_captured_y, text = "")
        self.player_info_canvas.create_image(60, canvas_added_top_buffer + box_side_buffer + box_height // 2, image = pawn_dark)
        self.player_info_canvas.create_image(60, canvas_added_top_buffer + box_side_buffer + box_space_between + math.floor(box_height * (1.5)), image = pawn_light)

        self.special_state_white = None
        self.special_state_black = None

        # Bind mouse
        self.player_info_canvas.bind("<Button-1>", self.mouse_click)

        # Game options frame
        game_options_frame = tk.Frame(self, bg="white")
        game_options_frame.pack(side = tk.TOP, pady=5)
        ng_button = tk.Button(game_options_frame, highlightbackground = "white", text="New Game", command = self.new_game)
        ng_button.pack(side = tk.LEFT)
        rs_button = tk.Button(game_options_frame, highlightbackground = "white", text="Resign", command = self.end_game)
        rs_button.pack(side = tk.LEFT)
        tk.Label(game_options_frame, background="White", text="  Time Controls: ").pack(side=tk.LEFT)
        self.time_control_options = {
            "1 min bullet": (60000, 0),
            "2+1 bullet": (120000, 1000),
            "3 min blitz": (180000, 0),
            "3+2 blitz": (180000, 2000),
            "5 min blitz": (300000, 0),
            "5+3 blitz": (300000, 3000),
            "10 min rapid": (600000, 0),
            "10+5 rapid": (600000, 5000),
            "15+10 rapid": (900000, 10000),
            "30 min classical": (1800000, 0),
            "30+20 classical": (1800000, 20000),
            "None": (-1, -1)
        }
        self.time_control_clicked = tk.StringVar()
        self.time_control_clicked.set(list(self.time_control_options.keys())[11])
        time_controls_dropdown = tk.OptionMenu(game_options_frame, self.time_control_clicked, *self.time_control_options.keys())
        time_controls_dropdown.config(background="white", highlightbackground = "white")
        time_controls_dropdown.pack(side = tk.LEFT)
        self.time_control_clicked.trace_add("write", self.time_control_callback)
        self.time_control_callback(None, None, None)

        # Engine limit frame
        engine_limit_frame = tk.Frame(self, bg="white")
        engine_limit_frame.pack(side = tk.TOP, pady=5)
        tk.Label(engine_limit_frame, background="White", text="   Max engine depth: ").pack(side=tk.LEFT)
        engine_depth_options = [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
            "∞",
        ]
        self.engine_depth_clicked = tk.StringVar()
        self.engine_depth_clicked.set(engine_depth_options[15])
        engine_depth_dropdown = tk.OptionMenu(engine_limit_frame, self.engine_depth_clicked, *engine_depth_options)
        engine_depth_dropdown.config(background="white", highlightbackground = "white")
        engine_depth_dropdown.pack(side = tk.LEFT)
        tk.Label(engine_limit_frame, background="White", text="  Max engine time: ").pack(side=tk.LEFT)
        self.engine_time_options = {
            "None": 0,
            "1s": 1000,
            "2s": 2000,
            "5s": 5000,
            "10s": 10000,
            "15s": 15000,
            "20s": 20000,
            "30s": 30000,
            "45s": 45000,
            "60s": 60000,
            "90s": 90000,
            "120s": 120000,
            "300s": 300000,
        }
        self.engine_time_clicked = tk.StringVar()
        self.engine_time_clicked.set(list(self.engine_time_options.keys())[3])
        engine_time_dropdown = tk.OptionMenu(engine_limit_frame, self.engine_time_clicked, *self.engine_time_options.keys())
        engine_time_dropdown.config(background="white", highlightbackground = "white")
        engine_time_dropdown.pack(side = tk.LEFT)

        # Engine hash size frame
        engine_hash_frame = tk.Frame(self, bg="white")
        engine_hash_frame.pack(side = tk.TOP, pady=5)
        tk.Label(engine_hash_frame, background="White", text="  Engine hash table size in MB: ").pack(side = tk.LEFT)
        self.hash_size_entry = tk.Entry(engine_hash_frame, width = 5)
        self.hash_size_entry.pack(side = tk.LEFT)
        hash_button = tk.Button(engine_hash_frame, highlightbackground = "white", text="Apply", command = self.update_engine_hash)
        hash_button.pack(side = tk.LEFT)

        # Set initial player text
        self.update_player_text()

        # Highlight moves
        self.highlight_last_move = tk.BooleanVar()
        self.highlight_last_move.set(True)
        highlight_last_move_checkbox = tk.Checkbutton(self, bg = "white", text='Highlight previous move',variable=self.highlight_last_move, onvalue=1, offvalue=0, command=self.update_highlight_last_move)
        highlight_last_move_checkbox.pack(side = tk.TOP, anchor = tk.W)

        # Show legal moves
        self.show_valid_moves = tk.BooleanVar()
        self.show_valid_moves.set(True)
        valid_moves_checkbox = tk.Checkbutton(self, bg = "white", text='Show legal moves',variable=self.show_valid_moves, onvalue=1, offvalue=0, command=self.update_show_valid_moves)
        valid_moves_checkbox.pack(side = tk.TOP, anchor = tk.W)

        # Game moves
        self.move_text_panel = st.ScrolledText(self, width = 60, height = 6, background="white", highlightbackground="black", highlightthickness=1, borderwidth = 0)
        self.move_text_panel.pack(side = tk.TOP, pady = 5)
        self.opening_text = "Game Moves"
        self.move_text = ""
        self.move_number = 1
        self.move_text_panel.insert(tk.INSERT, self.opening_text + "\n" + self.move_text)
        self.move_text_panel.configure(state ='disabled') 

        # Engine stats
        self.engine_stats_panel = st.ScrolledText(self, width = 60, height = 6, background="white", highlightbackground="black", highlightthickness=1, borderwidth = 0)
        self.engine_stats_panel.pack(side = tk.TOP, pady = 5)
        self.update_engine_text_panel("Engine Information")

    def new_game(self):
        for imgs in self.whites_captured_images.values():
            for i in imgs:
                self.player_info_canvas.delete(i)
            imgs.clear()
        for imgs in self.blacks_captured_images.values():
            for i in imgs:
                self.player_info_canvas.delete(i)
            imgs.clear()
        self.opening_text = "Game Moves"
        self.move_text = ""
        self.move_number = 1
        self.move_text_panel.configure(state ='normal') 
        self.move_text_panel.delete(1.0, tk.END)
        self.move_text_panel.insert(tk.INSERT, self.opening_text + "\n" + self.move_text)
        self.move_text_panel.configure(state ='disabled') 
        self.update_engine_text_panel("Engine Information")
        self.gui.new_game()
        self.update_time_display()

    def end_game(self):
        if self.gui.game_active:
            if self.gui.board.whites_turn:
                self.special_state_white = "Lost by resignation"
                self.special_state_black = "Won by resignation"
            else:
                self.special_state_white = "Won by resignation"
                self.special_state_black = "Lost by resignation"
            self.gui.end_game()
            self.update_player_text()

    def update_engine_hash(self):
        # TODO: Ensure engine(s) support this hash size
        try:
            hash_int = int(self.hash_size_entry.get())
        except ValueError:
            return
        if hash_int > 0 and hash_int < 20000:
            self.gui.engine_hash_size = hash_int
            self.gui.update_engine_hash()

    def time_control_callback(self, var, index, mode):
        vals = self.time_control_options[self.time_control_clicked.get()]
        self.gui.time_remaining_ms = [vals[0], vals[0]]
        self.gui.time_inc_ms = [vals[1], vals[1]]

    def attach_openings(self, openings):
        self.openings = openings

    def update_show_valid_moves(self):
        self.gui.show_valid_moves = self.show_valid_moves.get()
        self.gui.update_show_valid_moves()

    def update_highlight_last_move(self):
        self.gui.highlight_last_move = self.highlight_last_move.get()
        self.gui.update_highlight_last_move()

    def append_engine_text_panel(self, append_text):
        self.engine_stats_panel.configure(state ='normal') 
        self.engine_stats_panel.insert(tk.INSERT, "\n" + append_text)
        self.engine_stats_panel.see("end")
        self.engine_stats_panel.configure(state ='disabled') 

    def update_engine_text_panel(self, new_text):
        self.engine_stats_panel.configure(state ='normal') 
        self.engine_stats_panel.delete(1.0, tk.END)
        self.engine_stats_panel.insert(tk.INSERT, new_text)
        self.engine_stats_panel.configure(state ='disabled') 

    def create_player_text(self):
        wtext = self.white_player_name
        btext = self.black_player_name
        if self.gui.time_remaining_ms[0] >= 0 or self.gui.time_remaining_ms[1] >= 0:
            w_min = str(math.floor(self.gui.time_remaining_ms[0] / 1000 / 60))
            w_sec = math.floor((self.gui.time_remaining_ms[0] / 1000) % 60)
            if w_sec < 10:
                w_sec = "0" + str(w_sec)
            else:
                w_sec = str(w_sec)
            wtext += " (" + w_min + ":" + w_sec + ")"
            b_min = str(math.floor(self.gui.time_remaining_ms[1] / 1000 / 60))
            b_sec = math.floor((self.gui.time_remaining_ms[1] / 1000) % 60)
            if b_sec < 10:
                b_sec = "0" + str(b_sec)
            else:
                b_sec = str(b_sec)
            btext += " (" + b_min + ":" + b_sec + ")"
        if self.special_state_white:
            wtext = wtext + " - " + self.special_state_white
        if self.special_state_black:
            btext = btext + " - " + self.special_state_black
        return wtext, btext

    def create_piece_image(self, s):
         color = "l" if s.isupper() else "d"
         piece = s.lower() + "small"
         img = self.gui.sprites[piece][color]
         return self.player_info_canvas.create_image(0, 0, image = img)

    def update_player_text(self):
        wt, bt = self.create_player_text()
        white_width = 1
        black_width = 1
        white_font = "normal"
        black_font = "normal"
        if self.gui.game_active and self.gui.board.whites_turn:
            white_width = 4
            white_font = "bold"
        elif self.gui.game_active and not self.gui.board.whites_turn:
            black_width = 4
            black_font = "bold"
        self.player_info_canvas.itemconfig(self.player1_box, width = white_width)
        self.player_info_canvas.itemconfig(self.player1_name, text = wt, font = (self.gui.font, 15, white_font))
        self.player_info_canvas.itemconfig(self.player2_box, width = black_width)
        self.player_info_canvas.itemconfig(self.player2_name, text = bt, font = (self.gui.font, 15, black_font))

    def update_time_display(self):
        color = 0 if self.gui.board.whites_turn else 1
        if self.time_control_clicked.get() != "None":
            self.gui.time_remaining_ms[color] = self.gui.remaining_time_at_start_of_move - (round(time.time() * 1000) - self.gui.start_time_of_current_move)
            if self.gui.time_remaining_ms[color] <= 0:
                self.gui.time_remaining_ms[color] = 0
                if color == 0:
                    self.special_state_white = "Lost on time"
                    self.special_state_black = "Won on time"
                else:
                    self.special_state_white = "Won on time"
                    self.special_state_black = "Lost on time"
                self.gui.game_active = False
            self.update_player_text()
        if self.gui.game_active:
            self.top.after(250, self.update_time_display)

    def notify_move(self, special_state_white, special_state_black):

        # Update player text
        self.special_state_white = special_state_white
        self.special_state_black = special_state_black
        self.update_player_text()
        
        # Update move panel
        if self.gui.san_moves:
            m = self.gui.san_moves[-1]
            if self.gui.board.whites_turn:
                # Record the move that black just made
                m_str = m
            else:
                # Record the move that white just made
                m_str = str(self.move_number) + ". " + m
                self.move_number += 1
            self.move_text += m_str + " "
            if self.openings:
                opening_text_result = self.openings.find_opening(self.gui.board)
                if opening_text_result:
                    self.opening_text = opening_text_result
            else:
                self.opening_text = ""
            self.move_text_panel.configure(state ='normal') 
            self.move_text_panel.delete(1.0, tk.END)
            self.move_text_panel.insert(tk.INSERT, self.opening_text + "\n" + self.move_text)
            self.move_text_panel.see(tk.END)
            self.move_text_panel.configure(state ='disabled') 

        # Edit white's captured pieces and score
        white_captured = self.gui.captured_pieces(True)
        new_x = 100
        new_y = self.white_captured_y
        white_score = self.gui.compute_total_piece_values(True)
        for i in "pnbrq":
            c_new = white_captured[i]
            c_old = len(self.whites_captured_images[i])
            if c_old > c_new:
                print("ERROR: white capture mismatch")
            if c_old < c_new:
                for j in range(c_new - c_old):
                    self.whites_captured_images[i].append(self.create_piece_image(i))
            # Re-place all of them on the screen
            for img in self.whites_captured_images[i]:
                coords = self.player_info_canvas.coords(img)
                xdiff = new_x - coords[0]
                ydiff = new_y - coords[1]
                if xdiff != 0 or ydiff != 0:
                    self.player_info_canvas.move(img, xdiff, ydiff)
                new_x += 10
            if c_new > 0:
                new_x += 15
        white_ending_x = new_x

        # Edit black's captured pieces and score
        black_captured = self.gui.captured_pieces(False)
        new_x = 100
        new_y = self.black_captured_y
        black_score = self.gui.compute_total_piece_values(False)
        for i in "PNBRQ":
            c_new = black_captured[i]
            c_old = len(self.blacks_captured_images[i])
            if c_old > c_new:
                print("ERROR: black capture mismatch")
            if c_old < c_new:
                for j in range(c_new - c_old):
                    self.blacks_captured_images[i].append(self.create_piece_image(i))
            # Re-place all of them on the screen
            for img in self.blacks_captured_images[i]:
                coords = self.player_info_canvas.coords(img)
                xdiff = new_x - coords[0]
                ydiff = new_y - coords[1]
                if xdiff != 0 or ydiff != 0:
                    self.player_info_canvas.move(img, xdiff, ydiff)
                new_x += 10
            if c_new > 0:
                new_x += 15
        black_ending_x = new_x

        # Compute and display material score
        if white_score > black_score:
            score = white_score - black_score
            coords = self.player_info_canvas.coords(self.player1_score)
            xdiff = white_ending_x - coords[0]
            self.player_info_canvas.move(self.player1_score, xdiff, 0)
            self.player_info_canvas.itemconfig(self.player1_score, text = "+" + str(score))
            self.player_info_canvas.itemconfig(self.player2_score, text = "")
        elif black_score > white_score:
            score = black_score - white_score
            coords = self.player_info_canvas.coords(self.player2_score)
            xdiff = black_ending_x - coords[0]
            self.player_info_canvas.move(self.player2_score, xdiff, 0)
            self.player_info_canvas.itemconfig(self.player1_score, text = "")
            self.player_info_canvas.itemconfig(self.player2_score, text = "+" + str(score))
        else:
            self.player_info_canvas.itemconfig(self.player1_score, text = "")
            self.player_info_canvas.itemconfig(self.player2_score, text = "")

    def mouse_click(self, event):
        
        if event.x > self.selection_box_x and event.x < self.selection_box_x + self.selection_box_side:
            if event.y > self.player2_human_selection_box_y and event.y < self.player2_human_selection_box_y + self.selection_box_side:
                if self.gui.player_type[1] == PlayerType.EXTERNAL_ENGINE:
                    self.gui.shutdown_external_engine(1)
                self.gui.player_type[1] = PlayerType.HUMAN
                self.black_player_name = "Human"
            elif event.y > self.player2_computer_selection_box_y and event.y < self.player2_computer_selection_box_y + self.selection_box_side:
                name= fd.askopenfilename()
                if not self.gui.load_external_engine(1, name):
                    self.black_player_name = "Human"
            elif event.y > self.player1_human_selection_box_y and event.y < self.player1_human_selection_box_y + self.selection_box_side:
                if self.gui.player_type[0] == PlayerType.EXTERNAL_ENGINE:
                    self.gui.shutdown_external_engine(0)
                self.gui.player_type[0] = PlayerType.HUMAN
                self.white_player_name = "Human"
            elif event.y > self.player1_computer_selection_box_y and event.y < self.player1_computer_selection_box_y + self.selection_box_side:
                name= fd.askopenfilename()
                if not self.gui.load_external_engine(0, name):
                    self.white_player_name = "Human"
            self.update_player_text()
