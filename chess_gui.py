import tkinter as tk
from PIL import Image,ImageTk
import rulebook as rules
import threading
import subprocess
import time
from player_type import PlayerType 

class ChessGUI(tk.Canvas):

    def __init__(self, top, board):

        # Reference to the tkinter main window
        self.top = top

        # Reference to the display panel for notifications
        self.display = None

        # Reference to the eval bar panel
        self.eval_bar = None

        # The chess board we're displaying
        self.board = board

        # Players
        self.player_type = [PlayerType.HUMAN, PlayerType.HUMAN]
        self.external_engine_process = [None, None]

        # Time controls
        self.time_remaining_ms = [0, 0]
        self.time_inc_ms = [0, 0]
        self.start_time_of_current_move = 0
        self.remaining_time_at_start_of_move = 0

        # Variables and locks for thread communication
        self.engine_thread_lock = threading.Lock()
        self.computer_move_finished = False
        self.kill_thread = False

        # Hash size in MB for external engines (-1 means default)
        self.engine_hash_size = -1

        # Contains (best_move, value, moves analyzed, max depth, time took, pv line)
        self.selected_computer_move = None

        # Parameters related to board layout
        self.canvas_height = 600
        self.canvas_width = 600
        self.square_size = 70
        self.board_x_offset = 30
        self.board_y_offset = 5
        self.board_text_distance_from_board = 15

        # Drawable canvas
        tk.Canvas.__init__(self, top, bg = "white", highlightthickness=0, height = self.canvas_height, width = self.canvas_width)

        # Square color palette
        self.light_square_color = "#eeeed2"
        self.dark_square_color = "#769656"
        self.light_highlighted_square_color = "#D9E164"
        self.dark_highlighted_square_color = "#bbcb2b"

        # Fonts
        self.font = "TkDefaultFont"

        self.square_rects = []
        self.squares_imgs = [ [None]*8 for i in range(8)]
        self.sprites = {}
        self.selected_square = (-1, -1)  # (row,col) tuple when active
        self.all_valid_moves = {} # key is (row, col), value is list of valid moves for the current player
        self.game_active = False
        self.show_valid_moves = True
        self.highlight_last_move = True
        self.san_moves = [] # String of moves so far in SAN (algebraic notation) for display

        # Load images from disk
        self.load_sprites()

        # Draw initial board without pieces
        offset_x = self.board_x_offset
        offset_y = self.board_y_offset 
        for row in range(8):
            self.square_rects.append([])
            for col in range(8):
                color = self.square_color(row, col)
                s = self.create_rectangle(offset_x, offset_y, offset_x + self.square_size, offset_y + self.square_size, fill = color)
                self.square_rects[row].append(s)
                offset_x += self.square_size
            offset_x = self.board_x_offset
            offset_y += self.square_size

        # Draw coordinate labels on board
        center_offset = self.square_size / 2
        offset_x = self.board_x_offset - self.board_text_distance_from_board
        offset_y = self.board_y_offset + center_offset
        for i in range(8, 0, -1):
            self.create_text(offset_x, offset_y, text = str(i), font = (self.font, 15, 'bold'))
            offset_y += self.square_size
        offset_x = self.board_x_offset + center_offset
        offset_y = self.board_y_offset + 8 * self.square_size + self.board_text_distance_from_board
        for i in "abcdefgh":
            self.create_text(offset_x, offset_y, text = i, font = (self.font, 15, 'bold'))
            offset_x += self.square_size

        # Bind mouse
        self.bind("<Button-1>", self.mouse_click)

        # Render board
        self.render_board_update()

    def shutdown(self):
        self.game_active = False
        self.kill_thread = True
        for color in [0, 1]:
            if self.player_type[color] == PlayerType.EXTERNAL_ENGINE:
                self.external_engine_process[color].stdin.write("quit\n")
                self.external_engine_process[color].kill()
        self.top.destroy()

    def load_external_engine(self, color, filename):
        if filename == "":
            self.player_type[color] = PlayerType.HUMAN
            return False
        self.player_type[color] = PlayerType.EXTERNAL_ENGINE
        if self.display and color == 0:
            self.display.white_player_name = filename.split("/")[-1]
        elif self.display and color == 1:
            self.display.black_player_name = filename.split("/")[-1]
        if self.display:
            self.display.update_player_text()
        if self.external_engine_process[color] is not None:
            self.external_engine_process[color].kill()
        self.external_engine_process[color] = subprocess.Popen(filename,stdout=subprocess.PIPE, stdin=subprocess.PIPE, universal_newlines=True, bufsize=1)
        output = self.external_engine_process[color].stdout.readline().strip()
        print("From external engine:", output)
        print("To external engine:", "uci")
        self.external_engine_process[color].stdin.write("uci\n")
        output = ""
        while (output != "uciok"):
            output = self.external_engine_process[color].stdout.readline().strip()
            print("From external engine:", output)
        self.update_engine_hash()
        print("To external engine:", "ucinewgame")
        self.external_engine_process[color].stdin.write("ucinewgame\n")
        print("To external engine:", "isready")
        self.external_engine_process[color].stdin.write("isready\n")
        output = self.external_engine_process[color].stdout.readline().strip()
        print("From external engine:", output)
        return True

    def square_color(self, row, col):
        return self.light_square_color if (row + col) % 2 == 0 else self.dark_square_color
    
    def square_highlighted_color(self, row, col):
        return self.light_highlighted_square_color if (row + col) % 2 == 0 else self.dark_highlighted_square_color

    def register_display(self, display):
        self.display = display

    def register_eval_bar(self, eval_bar):
        self.eval_bar = eval_bar

    def load_sprites(self):
        self.sprites.clear()
        filename = "resources/ChessPieces.png"
        with Image.open(filename) as chess_images:
            for pidx, piece in enumerate(list("qkrnbp")):
                self.sprites[piece] = {}
                self.sprites[piece + "small"] = {}
                for cidx, color in enumerate(list("dl")):
                    img = chess_images.crop((pidx * 60, cidx * 60, (pidx + 1) * 60, (cidx + 1) * 60))
                    self.sprites[piece][color] = ImageTk.PhotoImage(img)
                    img = img.resize((25,25))
                    self.sprites[piece + "small"][color] = ImageTk.PhotoImage(img)

    def get_pawn_sprites(self):
        return self.sprites["p"]["l"], self.sprites["p"]["d"]

    def xy_of_piece(self, row, col):
        center_offset = self.square_size / 2
        x = self.board_x_offset + col * self.square_size + center_offset
        y = self.board_y_offset + row * self.square_size + center_offset
        return x, y

    def create_piece_image(self, s, row, col):
        if s == ".":
            return None
        color = "l" if s.isupper() else "d"
        piece = s.lower()
        x, y = self.xy_of_piece(row, col)
        img = self.sprites[piece][color]
        return self.create_image(x, y, image = img)

    def render_board_update(self):

        # Clear pieces
        for row in range(8):
            for col in range(8):
                piece = self.squares_imgs[row][col]
                if piece != None:
                    self.delete(piece)
                    self.squares_imgs[row][col] = None

        # Clear highlights
        for r in range(8):
            for c in range(8):
                self.itemconfig(self.square_rects[r][c], fill=self.square_color(r, c))
        
        # Draw pieces
        for row in range(8):
            for col in range(8):
                self.squares_imgs[row][col] = self.create_piece_image(self.board.squares[row][col], row, col)

        # Draw last move highlights
        if self.highlight_last_move:
            if self.board.move_history:
                last_move = self.board.move_history[-1]
                self.itemconfig(self.square_rects[last_move[0]][last_move[1]], fill=self.square_highlighted_color(last_move[0], last_move[1]))
                self.itemconfig(self.square_rects[last_move[2]][last_move[3]], fill=self.square_highlighted_color(last_move[2], last_move[3]))

    def new_game(self):

        # Reset board
        self.board.reset()

        # Delete any state from old game
        if self.selected_square[0] != -1:
            self.selected_square = (-1, -1)
        self.all_valid_moves.clear()
        self.san_moves.clear()

        # Reset time
        if self.display:
            self.display.time_control_callback("","","")

        # Pre-compute all valid moves for the new player so
        # that we can rapidly look them up in throughout this turn
        self.all_valid_moves = rules.compute_all_valid_moves(self.board)

        # Activate game
        self.game_active = True

        # Render board
        self.render_board_update()

        # Notify display
        if self.display:
            self.display.notify_move(None, None)

        # If external engine, tell it we're starting a new game
        for color in [0, 1]:
            if self.player_type[color] == PlayerType.EXTERNAL_ENGINE:
                print("To external engine:", "ucinewgame")
                self.external_engine_process[color].stdin.write("ucinewgame\n")
                print("To external engine:", "isready")
                self.external_engine_process[color].stdin.write("isready\n")
                output = self.external_engine_process[color].stdout.readline().strip()
                print("From external engine:", output)

        # Start time
        color = 0 if self.board.whites_turn else 1
        self.start_time_of_current_move = round(time.time() * 1000)
        self.remaining_time_at_start_of_move = self.time_remaining_ms[color]

        # If a computer is white, start computer play
        if self.game_active:
            if self.board.whites_turn and self.player_type[0] != PlayerType.HUMAN:
                self.prepare_computer_move()

        # Reset eval bar
        if self.eval_bar:
            self.eval_bar.new_game()

    def end_game(self):

        # If external engine, tell it to stop
        for color in [0, 1]:
            if self.player_type[color] == PlayerType.EXTERNAL_ENGINE:
                print("To external engine:", "stop")
                self.external_engine_process[color].stdin.write("stop\n")

        self.game_active = False

    def update_engine_hash(self):
        if self.engine_hash_size > 0:
            for i in range(2):
                if self.player_type[i] == PlayerType.EXTERNAL_ENGINE and self.external_engine_process[i]:
                    print("To external engine:", "setoption name Hash value", self.engine_hash_size)
                    self.external_engine_process[i].stdin.write("setoption name Hash value " + str(self.engine_hash_size) + "\n")

    def do_move(self, start_row, start_col, end_row, end_col):

        # Get the piece
        piece = self.board.squares[start_row][start_col]

        # Create SAN for move
        san_str = rules.algebraic_notation(start_row, start_col, end_row, end_col, self.all_valid_moves, self.board)
        print("Move is", san_str)

        # Update time remaining for player who just made this move
        color = 0 if self.board.whites_turn else 1
        self.time_remaining_ms[color] = self.remaining_time_at_start_of_move - (round(time.time() * 1000) - self.start_time_of_current_move)
        self.time_remaining_ms[color] += self.time_inc_ms[color]

        # Perform move
        self.board.make_move(start_row, start_col, end_row, end_col)

        # Start deducting time from new players turn
        color = 0 if self.board.whites_turn else 1
        self.start_time_of_current_move = round(time.time() * 1000)
        self.remaining_time_at_start_of_move = self.time_remaining_ms[color]

        # Render board
        self.render_board_update()

        # Pre-compute all valid moves for the new player so
        # that we can rapidly look them up in throughout this turn
        self.all_valid_moves = rules.compute_all_valid_moves(self.board)

        # For SAN, check for check, checkmate, stalemate, and draw by insufficient material
        special_state_black = None
        special_state_white = None
        game_over, status = rules.check_for_terminal_states_and_king_checks(self.board, self.any_valid_moves())
        if game_over:
            if status == 1 or status == -1:
                # Current player is checkmated
                if self.board.whites_turn:
                    san_str += "# 0-1"
                    special_state_white = "Lost by checkmate"
                    special_state_black = "Won by checkmate"
                else:
                    san_str += "# 1-0"
                    special_state_white = "Won by checkmate"
                    special_state_black = "Lost by checkmate"
            elif status == 0:
                # Stalemate
                san_str += " 1/2-1/2"
                special_state_white = "Stalemate"
                special_state_black = "Stalemate"
            elif status == 0.1:
                san_str += " 1/2-1/2"
                special_state_white = "Draw - Insufficient Mat"
                special_state_black = "Draw - Insufficient Mat"
            elif status == 0.2:
                san_str += " 1/2-1/2"
                special_state_white = "Draw - 3x Repetition"
                special_state_black = "Draw - 3x Repetition"                              
            else:
                print("ERROR: Invalid game over code")
            self.game_active = False
        else:
            if status == 1 or status == -1:
                # In check
                san_str += "+"
                if self.board.whites_turn:
                    special_state_white = "In check"
                else:
                    special_state_black = "In check"

        # Log move in SAN
        self.san_moves.append(san_str)

        # Notify on the move
        if self.display:
            self.display.notify_move(special_state_white, special_state_black)

        # If a computer's turn is next, trigger the search
        if self.game_active:
            if (self.board.whites_turn and self.player_type[0] != PlayerType.HUMAN or
                not self.board.whites_turn and self.player_type[1] != PlayerType.HUMAN):
                self.prepare_computer_move()

    def compute_total_piece_values(self, white):
        value = 0
        piece_values = {"P":1, "N":3, "B":3, "R":5, "Q":9}
        for row in range(8):
            for col in range(8):
                piece = self.board.squares[row][col]
                if white and piece in "QRNBP" or not white and piece in "qrnbp":
                    if piece.upper() in piece_values:
                        value += piece_values[piece.upper()]
        return value
    
    def captured_pieces(self, white):
        if white:
            captured = {"q":0, "r":0, "n":0, "b":0, "p":0}
        else:
            captured = {"Q":0, "R":0, "N":0, "B":0, "P":0}
        for m in self.board.move_history:
            if white and m[4] in "KQRNBP" and m[5] != "." or not white and m[4] in "kqrnbp" and m[5] != ".":
                captured[m[5]] += 1
        return captured

    def any_valid_moves(self):
        for moves in self.all_valid_moves.values():
            if moves:
                return True
        return False

    def update_show_valid_moves(self):
        
        # If something is selected, then we may have to update the valid move square displays
        sr = self.selected_square[0]
        sc = self.selected_square[1]
        if sr != -1:
            if self.show_valid_moves:
                for m in self.all_valid_moves[(sr, sc)]:
                    self.itemconfig(self.square_rects[m[0]][m[1]], fill="orange")
            else:
                for r in range(8):
                    for c in range(8):
                        self.itemconfig(self.square_rects[r][c], fill=self.square_color(r, c))
                if self.board.move_history:
                    last_move = self.board.move_history[-1]
                    self.itemconfig(self.square_rects[last_move[0]][last_move[1]], fill=self.square_highlighted_color(last_move[0], last_move[1]))
                    self.itemconfig(self.square_rects[last_move[2]][last_move[3]], fill=self.square_highlighted_color(last_move[2], last_move[3]))
                self.itemconfig(self.square_rects[sr][sc], fill=self.square_highlighted_color(sr, sc))

    def update_highlight_last_move(self):

        sr = self.selected_square[0]
        sc = self.selected_square[1]

        if self.board.move_history:
            last_move = self.board.move_history[-1]
            if self.highlight_last_move:
                self.itemconfig(self.square_rects[last_move[0]][last_move[1]], fill=self.square_highlighted_color(last_move[0], last_move[1]))
                self.itemconfig(self.square_rects[last_move[2]][last_move[3]], fill=self.square_highlighted_color(last_move[2], last_move[3]))
            else:
                self.itemconfig(self.square_rects[last_move[0]][last_move[1]], fill=self.square_color(last_move[0], last_move[1]))
                self.itemconfig(self.square_rects[last_move[2]][last_move[3]], fill=self.square_color(last_move[2], last_move[3]))

    def execute_computer_move_blocking(self):
        """ This is a blocking call and must be run within a Thread """

        # TODO: Handle the case where "new game" is clicked
        depth = 250
        max_time = 0
        if self.display:
            if self.display.engine_depth_clicked.get() == "∞":
                depth = 250
            else:
                depth = int(self.display.engine_depth_clicked.get())
            max_time = int(self.display.engine_time_options[self.display.engine_time_clicked.get()])
        if self.board.whites_turn:
            color = 0
        else:
            color = 1
        if self.player_type[color] == PlayerType.HUMAN:
            print("Error: Trying to execute computer move during human turn")
            return
        else:

            # Get move history in long algebratic notation
            lan_history = ""
            for m in self.board.move_history:
                lan_history += "abcdefgh"[m[1]] 
                lan_history += str(8 - m[0])
                lan_history += "abcdefgh"[m[3]] 
                lan_history += str(8 - m[2])
                lan_history += " "

            uci_pos_str = "position startpos moves " + lan_history + "\n"
            print("To external engine:", uci_pos_str)
            self.external_engine_process[color].stdin.write(uci_pos_str)
            print("To external engine:", "isready")
            self.external_engine_process[color].stdin.write("isready\n")
            output = self.external_engine_process[color].stdout.readline().strip()
            print("From external engine:", output)

            # Send UCI go command
            uci_go_str = "go"
            if depth != 0 and depth != 250:
                uci_go_str += " depth " + str(depth)
            if max_time != 0:
                uci_go_str += " movetime " + str(max_time)
            if self.time_remaining_ms[0] > 0 and self.time_remaining_ms[1] > 0:
                uci_go_str += " wtime " + str(self.time_remaining_ms[0]) + " winc " + str(self.time_inc_ms[0])
                uci_go_str += " btime " + str(self.time_remaining_ms[1]) + " binc " + str(self.time_inc_ms[1])
            uci_go_str += "\n"
            print("To external engine:", uci_go_str)
            self.external_engine_process[color].stdin.write(uci_go_str)
            value = 0
            pv = ""
            moves_searched = 0
            max_depth_searched = 0
            s_time = time.time()
            best_move = None
            while not self.kill_thread:
                from_engine_str = self.external_engine_process[color].stdout.readline().strip()
                if self.kill_thread:
                    break
                print("From external engine:", from_engine_str)
                words = from_engine_str.split()
                if "info" in words and self.display:
                    self.display.append_engine_text_panel(from_engine_str)
                if "info" in words and "depth" in words:
                    pos = words.index("depth") + 1
                    max_depth_searched = int(words[pos])
                if "info" in words and "nodes" in words:
                    pos = words.index("nodes") + 1
                    moves_searched += int(words[pos])
                if "info" in words and "pv" in words:
                    pos = words.index("pv")
                    pv = ""
                    for i in range(pos+1, len(words)):
                        pv += words[i] + " "
                if "info" in words and "cp" in words:
                    pos = words.index("cp") + 1
                    value = int(words[pos])
                    if self.eval_bar:
                        eval = value
                        if not self.board.whites_turn:
                            eval *= -1
                        self.eval_bar.update_winning_chances(eval)
                if len(words) >= 2 and words[0] == "bestmove":
                    e_time = time.time()
                    start_col = "abcdefgh".find(words[1][0])
                    start_row = 8 - int(words[1][1])
                    end_col = "abcdefgh".find(words[1][2])
                    end_row = 8 - int(words[1][3])
                    best_move = ((start_row, start_col, end_row, end_col), value, moves_searched, max_depth_searched, pv, e_time - s_time)
                    break

        # Store the returned move
        with self.engine_thread_lock:
            self.selected_computer_move = best_move
            self.computer_move_finished = True

    def prepare_computer_move(self):
        with self.engine_thread_lock:
            self.computer_move_finished = False
        if self.display:
            e_text = "Engine is currently searching with max depth = " + self.display.engine_depth_clicked.get() + "\n"
            self.display.update_engine_text_panel(e_text)
        search_thread = threading.Thread(target = self.execute_computer_move_blocking)
        search_thread.start()
        self.top.after(500, self.check_if_computer_is_done)

    def check_if_computer_is_done(self):
        if not self.game_active or self.kill_thread:
            self.kill_thread = False
            return
        move = None
        with self.engine_thread_lock:
            if self.computer_move_finished:
                if not self.selected_computer_move:
                    self.board.fatal_error("No computer move selected")
                else:
                    move = self.selected_computer_move
                    self.computer_move_finished = False
            else:
                self.top.after(500, self.check_if_computer_is_done)
        if move:
            if self.eval_bar:
                evaluation = move[1]
                if not self.board.whites_turn:
                    evaluation *= -1
                self.eval_bar.update_winning_chances(evaluation)
            if self.display:
                e_text = "Engine finished searching" + "\n"
                e_text += "Principal variation: " + str(move[4]) + "\n"
                evaluation = move[1]
                if self.board.whites_turn:
                    eval_string = "+" + '{0:.2f}'.format(evaluation / 100)
                else:
                    evaluation *= -1
                    eval_string = '{0:.2f}'.format(evaluation / 100)
                e_text += "Evaluation (white is positive): " + eval_string + "\n"
                e_text += str(move[2]) + " moves searched in " + '{0:.2f}'.format(move[5]) + "s" + "\n"
                e_text += "Max depth reached (excluding captures): " + str(move[3]) + "\n"
                self.display.update_engine_text_panel(e_text)
            self.do_move(move[0][0], move[0][1], move[0][2], move[0][3])

    def shutdown_external_engine(self, color):
        if self.board.whites_turn and color == 0 or not self.board.whites_turn and color ==1:
            self.kill_thread = True
        if self.player_type[color] == PlayerType.EXTERNAL_ENGINE:
            self.external_engine_process[color].stdin.write("quit\n")
            self.external_engine_process[color].kill()

    def mouse_click(self, event):

        # Don't allow user activity if gane over or computer's turn
        if (not self.game_active or
            self.board.whites_turn and self.player_type[0] != PlayerType.HUMAN or
            not self.board.whites_turn and self.player_type[1] != PlayerType.HUMAN):
            return

        # Ensure the mouse click is in-bounds and get square
        col = (event.x - self.board_x_offset) // self.square_size
        row = (event.y - self.board_y_offset) // self.square_size
        if row > 7 or row < 0 or col > 7 or col < 0:
            return
        sr = self.selected_square[0]
        sc = self.selected_square[1]

        # If nothing is yet selected, attempt to select
        if sr == -1:
            if self.board.squares[row][col] in "KQRNBP" and self.board.whites_turn or self.board.squares[row][col] in "kqrnbp" and not self.board.whites_turn:
                self.itemconfig(self.square_rects[row][col], fill=self.square_highlighted_color(row, col))
                self.selected_square = (row, col)
                if self.show_valid_moves:
                    for m in self.all_valid_moves[(row, col)]:
                        self.itemconfig(self.square_rects[m[0]][m[1]], fill="orange")

        # If already selected, attempt to move the piece
        else:
            
            # Unselect, leaving previous move history highlighted
            self.selected_square = (-1,-1)
            for r in range(8):
                for c in range(8):
                    self.itemconfig(self.square_rects[r][c], fill=self.square_color(r, c))
            if self.highlight_last_move and self.board.move_history:
                last_move = self.board.move_history[-1]
                self.itemconfig(self.square_rects[last_move[0]][last_move[1]], fill=self.square_highlighted_color(last_move[0], last_move[1]))
                self.itemconfig(self.square_rects[last_move[2]][last_move[3]], fill=self.square_highlighted_color(last_move[2], last_move[3]))

            # If the move is legal, perform it
            if ( (row, col, True, False) in self.all_valid_moves[(sr, sc)] or (row, col, True, True) in self.all_valid_moves[(sr, sc)] or
                (row, col, False, False) in self.all_valid_moves[(sr, sc)] or (row, col, False, True) in self.all_valid_moves[(sr, sc)] ):
                self.do_move(sr, sc, row, col)
