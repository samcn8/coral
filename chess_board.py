import sys
import zobrist

class Board():
    """
    This class contains the entire state of the game board and any past moves.
    This class does not generate or validate any moves; it assumes all moves
    passed through "do_move" have already been validated.
    """

    def __init__(self):

        # Squares represented as an 8x8 list of characters.
        # Character "." indicates an empty square
        self.squares = [ ["."]*8 for i in range(8)]

        # Moves made up to this point.
        # List of tuples which contain the following 10 elements:
        #   0 - Start row
        #   1 - Start col
        #   2 - End row
        #   3 - End col
        #   4 - Character of piece being moved
        #   5 - Character of the piece captured or "."
        #   6 - Boolean of whether this is an en passant capture move
        #   7 - En passant rights prior to this move being made (for undo purposes)
        #   8 - Castling state prior to this move being made (white_castled, black_castled) (for undo purposes)
        #   9 - Castling rights prior to this move being made (WKS, WQS, BKS, WQS) (for undo purposes)
        #  10 - (row, col) of the promotion square if a promotion occured, (-1,-1) otherwise (for undo purposes)
        self.move_history = []

        # Zobrist hash state for all previous moves.  This should correspond
        # to the self.move_history elements.  This is used to quickly check
        # for three-fold repetition
        self.zobrist_history = []


        # Is it white's turn?
        self.whites_turn = True

        # Current castling rights (ks = king side, qs = queen side)
        self.white_ks_castling_rights = True
        self.white_qs_castling_rights = True
        self.black_ks_castling_rights = True
        self.black_qs_castling_rights = True

        # Have white or black castled before
        self.white_castled = False
        self.black_castled = False

        # (row, col) of active en passant square
        # This is the (row, col) of the square the opposing pawn just moved through
        # on a 2-row move, if the current player can capture en passant to that square.
        # Set to (-1, -1) if an en passant capture is not available
        self.en_passant_rights = (-1, -1)

        # Zobrist has of the current state
        self.zobrist_hasher = zobrist.ZobristHasher()
        self.zobrist_hash = 0

        # Initial reset
        self.reset()

    def __str__(self):
        """
        String representation of the board for printing
        """
        board_str = ""
        for row in range(8):
            board_str += str(row) + "  "
            for col in range(8):
                board_str += self.squares[row][col] + " "
            board_str += "\n"
        board_str += "   0 1 2 3 4 5 6 7" + "\n"
        if self.whites_turn:
            board_str += "White's turn\n"
        else:
            board_str += "Black's turn\n"
        if self.white_castled:
            board_str += "White has previously castled\n"
        else:
            board_str += "White has not previously castled\n"
        if self.black_castled:
            board_str += "Black has previously castled\n"
        else:
            board_str += "Black has not previously castled\n"
        board_str += "Castling rights: "
        if self.white_ks_castling_rights:
            board_str += "White KS  "
        if self.white_qs_castling_rights:
            board_str += "White QS  "
        if self.black_ks_castling_rights:
            board_str += "Black KS  "
        if self.black_qs_castling_rights:
            board_str += "Black QS  "
        board_str += "\n"
        board_str += "En passant rights: " + str(self.en_passant_rights) + "\n"
        board_str += "Zobrist hash: " + str(self.zobrist_hash) + "\n"
        board_str += "Move history: " + str(self.move_history) + "\n"
        board_str += "Zobrist history: " + str(self.zobrist_history) + "\n"
        return board_str

    def fatal_error(self, string):
        print("A fatal error has occured!")
        print(string)
        print("Internal board state is: ")
        print(self)
        sys.exit()

    def reset(self):
        """
        Reset the board to its initial state
        """

        self.squares[0] = list("rnbqkbnr")
        self.squares[1] = list("pppppppp")
        self.squares[2] = list("........")
        self.squares[3] = list("........")
        self.squares[4] = list("........")
        self.squares[5] = list("........")
        self.squares[6] = list("PPPPPPPP")
        self.squares[7] = list("RNBQKBNR")
        self.move_history.clear()
        self.zobrist_history.clear()
        self.whites_turn = True
        self.white_ks_castling_rights = True
        self.white_qs_castling_rights = True
        self.white_castled = False
        self.black_ks_castling_rights = True
        self.black_qs_castling_rights = True
        self.black_castled = False
        self.en_passant_rights = (-1, -1)
        self.zobrist_hash = self.zobrist_hasher.full_hash(self)

    def make_move(self, start_row, start_col, end_row, end_col):
        """
        Perform the move and update the game state accordingly.
        This assumes the move is legal and has already been validated.
        """

        piece = self.squares[start_row][start_col]
        if (self.whites_turn and piece not in "KQRBNP" or
            not self.whites_turn and piece not in "kqrbnp"):
            self.fatal_error("Invalid piece passed to Board.do_move")

        # Check for en passant capture
        is_en_passant = (piece.upper() == "P" and (end_row, end_col) == self.en_passant_rights)

        # Get the captured piece, if any
        if is_en_passant and self.whites_turn:
            captured = self.squares[end_row+1][end_col]
        elif is_en_passant and not self.whites_turn:
            captured = self.squares[end_row-1][end_col]
        else:
            captured = self.squares[end_row][end_col]

        # Promotion tuple for accounting
        if (self.whites_turn and end_row == 0 and self.squares[start_row][start_col] == "P" or
            not self.whites_turn and end_row == 7 and self.squares[start_row][start_col] == "p"):
            promotion = (end_row, end_col)
        else:
            promotion = (-1, -1)

        # We now have all the information we need to log the move before updating state
        self.move_history.append((start_row, start_col, end_row, end_col,
                                  piece, captured, is_en_passant, self.en_passant_rights,
                                  (self.white_castled, self.black_castled),
                                  (self.white_ks_castling_rights, self.white_qs_castling_rights, self.black_ks_castling_rights, self.black_qs_castling_rights),
                                   promotion ))

        # If we're a pawn moving two space, check if we have to give the
        # other player en passant rights for next turn
        give_other_player_en_passant_rights = False
        if self.whites_turn and piece == "P":
            if start_row == 6 and end_row == 4: # Pawn moved two spaces
                if (end_col > 0 and self.squares[4][end_col-1] == "p" or # Now pawn left of us
                    end_col < 7 and self.squares[4][end_col+1] == "p"): # Now pawn right of us
                    give_other_player_en_passant_rights = True
                    # Hash - undo old en passant rights, if needed
                    if self.en_passant_rights[1] != -1:
                        self.zobrist_hash ^= self.zobrist_hasher.hash_en_passant[self.en_passant_rights[1]]
                    # Hash - update new en passant rights
                    self.zobrist_hash ^= self.zobrist_hasher.hash_en_passant[end_col]
                    self.en_passant_rights = (5, end_col)

        elif not self.whites_turn and piece == "p":
            if start_row == 1 and end_row == 3: # Pawn moved two spaces
                if (end_col > 0 and self.squares[3][end_col-1] == "P" or # Now pawn left of us
                    end_col < 7 and self.squares[3][end_col+1] == "P"): # Now pawn right of us
                    give_other_player_en_passant_rights = True
                    # Hash - undo old en passant rights, if needed
                    if self.en_passant_rights[1] != -1:
                        self.zobrist_hash ^= self.zobrist_hasher.hash_en_passant[self.en_passant_rights[1]]
                    # Hash - update new en passant rights
                    self.zobrist_hash ^= self.zobrist_hasher.hash_en_passant[end_col]
                    self.en_passant_rights = (2, end_col)     

        if not give_other_player_en_passant_rights:
            # Hash - undo old en passant rights, if needed
            if self.en_passant_rights[1] != -1:
                self.zobrist_hash ^= self.zobrist_hasher.hash_en_passant[self.en_passant_rights[1]]
            self.en_passant_rights = (-1, -1)

        # Move source to dest
        self.squares[end_row][end_col] = self.squares[start_row][start_col]
        self.squares[start_row][start_col] = "."

        # Hash - revert the captured square back to "." if need be
        if captured != "." and not is_en_passant:
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[end_row*8+end_col][self.zobrist_hasher.piece_index[captured]]
        # Hash - place the source on the dest
        self.zobrist_hash ^= self.zobrist_hasher.hash_piece[end_row*8+end_col][self.zobrist_hasher.piece_index[piece]]
        # Hash - revert the source square back to "."
        self.zobrist_hash ^= self.zobrist_hasher.hash_piece[start_row*8+start_col][self.zobrist_hasher.piece_index[piece]]

        # If en passant, remove captured pawn
        if is_en_passant and self.whites_turn:
            self.squares[end_row+1][end_col] = "."
            # Hash - revert the captured pawn square back to "."
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[(end_row+1)*8+end_col][self.zobrist_hasher.piece_index[captured]]
        elif is_en_passant and not self.whites_turn:
            self.squares[end_row-1][end_col] = "."
            # Hash - revert the captured pawn square back to "."
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[(end_row-1)*8+end_col][self.zobrist_hasher.piece_index[captured]]

        # Handle promotion
        # TODO: Allow promotions to pieces other than queen
        if self.whites_turn and end_row == 0 and self.squares[end_row][end_col] == "P":
            self.squares[end_row][end_col] = "Q"
            # Hash - remove pawn from promotion square
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[end_row*8+end_col][self.zobrist_hasher.piece_index["P"]]
            # Hash - apply queen to promotion square
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[end_row*8+end_col][self.zobrist_hasher.piece_index["Q"]]
        elif not self.whites_turn and end_row == 7 and self.squares[end_row][end_col] == "p":
            self.squares[end_row][end_col] = "q"
            # Hash - remove pawn from promotion square
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[end_row*8+end_col][self.zobrist_hasher.piece_index["p"]]
            # Hash - apply queen to promotion square
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[end_row*8+end_col][self.zobrist_hasher.piece_index["q"]]

        # If this was a castling move, also move the rook
        if piece == "K" and start_row == 7 and start_col == 4 and end_row == 7 and end_col == 6:
            # White KS castling
            self.squares[7][5] = self.squares[7][7]
            self.squares[7][7] = "."
            # Hash - apply rook to new square (7*8+5 = 61)
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[61][self.zobrist_hasher.piece_index["R"]]
            # Hash - revert old rook square to "." (7*8+7 = 63)
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[63][self.zobrist_hasher.piece_index["R"]]
            self.white_castled = True
        elif piece == "K" and start_row == 7 and start_col == 4 and end_row == 7 and end_col == 2:
            # White QS castling
            self.squares[7][3] = self.squares[7][0]
            self.squares[7][0] = "."
            # Hash - apply rook to new square (7*8+3 = 59)
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[59][self.zobrist_hasher.piece_index["R"]]
            # Hash - revert old rook square to "." (7*8+0 = 56)
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[56][self.zobrist_hasher.piece_index["R"]]
            self.white_castled = True
        elif piece == "k" and start_row == 0 and start_col == 4 and end_row == 0 and end_col == 6:
            # Black KS castling
            self.squares[0][5] = self.squares[0][7]
            self.squares[0][7] = "."
            # Hash - apply rook to new square (0*8+5 = 5)
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[5][self.zobrist_hasher.piece_index["r"]]
            # Hash - revert old rook square to "." (0*8+7 = 7)
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[7][self.zobrist_hasher.piece_index["r"]]
            self.black_castled = True
        elif piece == "k" and start_row == 0 and start_col == 4 and end_row == 0 and end_col == 2:
            # Black QS castling
            self.squares[0][3] = self.squares[0][0]
            self.squares[0][0] = "."
            # Hash - apply rook to new square (0*8+3 = 3)
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[3][self.zobrist_hasher.piece_index["r"]]
            # Hash - revert old rook square to "." (0*8+0 = 0)
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[0][self.zobrist_hasher.piece_index["r"]]
            self.black_castled = True

        # Update castling rights based on a king being moved
        wqs = True
        wks = True
        bqs = True
        bks = True
        if self.whites_turn and piece == "K" and start_row == 7 and start_col == 4:
            wqs = False
            wks = False
        if not self.whites_turn and piece == "k" and start_row == 0 and start_col == 4:
            bqs = False
            bks = False

        # Update castling rights based on a rook being moved
        if self.whites_turn and piece == "R" and start_row == 7 and start_col == 0:
            wqs = False
        if self.whites_turn and piece == "R" and start_row == 7 and start_col == 7:
            wks = False
        if not self.whites_turn and piece == "r" and start_row == 0 and start_col == 0:
            bqs = False
        if not self.whites_turn and piece == "r" and start_row == 0 and start_col == 7:
            bks = False

        # Update castling rights based on a rook being captured
        if self.whites_turn and captured == "r" and end_row == 0 and end_col == 0:
            bqs = False
        if self.whites_turn and captured == "r" and end_row == 0 and end_col == 7:
            bks = False
        if not self.whites_turn and captured == "R" and end_row == 7 and end_col == 0:
            wqs = False
        if not self.whites_turn and captured == "R" and end_row == 7 and end_col == 7:
            wks = False

        # Hash - remove castling rights if need be
        if self.white_qs_castling_rights and not wqs:
            self.white_qs_castling_rights = False
            # Hash - toggle rights
            self.zobrist_hash ^= self.zobrist_hasher.hash_white_qs_castling_rights
        if self.white_ks_castling_rights and not wks:
            self.white_ks_castling_rights = False
            # Hash - toggle rights
            self.zobrist_hash ^= self.zobrist_hasher.hash_white_ks_castling_rights
        if self.black_qs_castling_rights and not bqs:
            self.black_qs_castling_rights = False
            # Hash - toggle rights
            self.zobrist_hash ^= self.zobrist_hasher.hash_black_qs_castling_rights
        if self.black_ks_castling_rights and not bks:
            self.black_ks_castling_rights = False
            # Hash - toggle rights
            self.zobrist_hash ^= self.zobrist_hasher.hash_black_ks_castling_rights

        # Change turn
        self.whites_turn = not self.whites_turn
        # Hash - change turn
        self.zobrist_hash ^= self.zobrist_hasher.hash_blacks_turn

        # Store zobrist hash in history
        self.zobrist_history.append(self.zobrist_hash)

    def unmake_move(self):
        """
        Unmake the last move.  This restores all state in the class to the
        state prior to the last move made - the zobrist hashes should be the same.
        """

        # Remove the last move from the Zobrist history
        self.zobrist_history.pop()

        # Get the last move from the history
        if not self.move_history:
            self.fatal_error("Trying to undo an empty move history")
        last_move = self.move_history.pop()

        # It was the previous players turn when this move was made
        self.whites_turn = not self.whites_turn
        # Hash - change turn
        self.zobrist_hash ^= self.zobrist_hasher.hash_blacks_turn

        # Restore saved state
        start_row = last_move[0]
        start_col = last_move[1]
        end_row = last_move[2]
        end_col = last_move[3]
        piece = last_move[4]
        capture = last_move[5]
        is_en_passant = last_move[6]
        self.white_castled = last_move[8][0]
        self.black_castled = last_move[8][1]
        promotion = last_move[10]

        # Restore en passant rights if they changed
        epr = last_move[7]
        if epr != self.en_passant_rights:
            # Hash - undo old en passant rights, if needed
            if self.en_passant_rights[1] != -1:
                self.zobrist_hash ^= self.zobrist_hasher.hash_en_passant[self.en_passant_rights[1]]
            # Hash - set en passant rights
            if epr[1] != -1:
                self.zobrist_hash ^= self.zobrist_hasher.hash_en_passant[epr[1]]
            self.en_passant_rights = epr

        # Restore castling rights if they changed
        wks = last_move[9][0]
        if wks != self.white_ks_castling_rights:
            self.white_ks_castling_rights = wks
            # Hash - toggle rights
            self.zobrist_hash ^= self.zobrist_hasher.hash_white_ks_castling_rights
        wqs = last_move[9][1]
        if wqs != self.white_qs_castling_rights:
            self.white_qs_castling_rights = wqs
            # Hash - toggle rights
            self.zobrist_hash ^= self.zobrist_hasher.hash_white_qs_castling_rights
        bks = last_move[9][2]
        if bks != self.black_ks_castling_rights:
            self.black_ks_castling_rights = bks
            # Hash - toggle rights
            self.zobrist_hash ^= self.zobrist_hasher.hash_black_ks_castling_rights
        bqs = last_move[9][3]
        if bqs != self.black_qs_castling_rights:
            self.black_qs_castling_rights = bqs
            # Hash - toggle rights
            self.zobrist_hash ^= self.zobrist_hasher.hash_black_qs_castling_rights

        # If this was a castling move, move the rook back
        if piece == "K" and start_row == 7 and start_col == 4 and end_row == 7 and end_col == 6:
            # White KS castling
            self.squares[7][5] = "."
            self.squares[7][7] = "R"
            # Hash - apply rook to new square (7*8+5 = 61)
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[61][self.zobrist_hasher.piece_index["R"]]
            # Hash - revert old rook square to "." (7*8+7 = 63)
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[63][self.zobrist_hasher.piece_index["R"]]
        elif piece == "K" and start_row == 7 and start_col == 4 and end_row == 7 and end_col == 2:
            # White QS castling
            self.squares[7][3] = "."
            self.squares[7][0] = "R"
            # Hash - apply rook to new square (7*8+3 = 59)
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[59][self.zobrist_hasher.piece_index["R"]]
            # Hash - revert old rook square to "." (7*8+0 = 56)
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[56][self.zobrist_hasher.piece_index["R"]]
        elif piece == "k" and start_row == 0 and start_col == 4 and end_row == 0 and end_col == 6:
            # Black KS castling
            self.squares[0][5] = "."
            self.squares[0][7] = "r"
            # Hash - apply rook to new square (0*8+5 = 5)
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[5][self.zobrist_hasher.piece_index["r"]]
            # Hash - revert old rook square to "." (0*8+7 = 7)
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[7][self.zobrist_hasher.piece_index["r"]]
        elif piece == "k" and start_row == 0 and start_col == 4 and end_row == 0 and end_col == 2:
            # Black QS castling
            self.squares[0][3] = "."
            self.squares[0][0] = "r"
            # Hash - apply rook to new square (0*8+3 = 3)
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[3][self.zobrist_hasher.piece_index["r"]]
            # Hash - revert old rook square to "." (0*8+0 = 0)
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[0][self.zobrist_hasher.piece_index["r"]]

        # Undo any promotion (change it to a pawn)
        if promotion != (-1, -1):
            if promotion[0] != end_row or promotion[1] != end_col:
                self.fatal_error("Promotion move invalid during move unmake")
            if self.whites_turn:
                if promotion[0] != 0:
                    self.fatal_error("Cannot undo white promotion move")
                self.squares[0][promotion[1]] = "P"
                # Hash - remove queen from promotion square
                self.zobrist_hash ^= self.zobrist_hasher.hash_piece[end_row*8+end_col][self.zobrist_hasher.piece_index["Q"]]
                # Hash - apply pawn to promotion square
                self.zobrist_hash ^= self.zobrist_hasher.hash_piece[end_row*8+end_col][self.zobrist_hasher.piece_index["P"]]
            else:
                if promotion[0] != 7:
                    self.fatal_error("Cannot undo black promotion move")
                self.squares[7][promotion[1]] = "p"      
                # Hash - remove queen from promotion square
                self.zobrist_hash ^= self.zobrist_hasher.hash_piece[end_row*8+end_col][self.zobrist_hasher.piece_index["q"]]
                # Hash - apply pawn to promotion square
                self.zobrist_hash ^= self.zobrist_hasher.hash_piece[end_row*8+end_col][self.zobrist_hasher.piece_index["p"]]         

        # If en passant, put the captured pawn back
        if is_en_passant and self.whites_turn:
            self.squares[end_row+1][end_col] = "p"
            # Hash - put the captured pawn back
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[(end_row+1)*8+end_col][self.zobrist_hasher.piece_index["p"]]
        elif is_en_passant and not self.whites_turn:
            self.squares[end_row-1][end_col] = "P"
            # Hash - put the captured pawn back
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[(end_row-1)*8+end_col][self.zobrist_hasher.piece_index["P"]]

        # Put the source back
        self.squares[start_row][start_col] = self.squares[end_row][end_col]
        # Hash - put the source back
        self.zobrist_hash ^= self.zobrist_hasher.hash_piece[start_row*8+start_col][self.zobrist_hasher.piece_index[piece]]

        # Hash - remove source from dest square
        self.zobrist_hash ^= self.zobrist_hasher.hash_piece[end_row*8+end_col][self.zobrist_hasher.piece_index[piece]]
        self.squares[end_row][end_col] = "."

        # Put back the capture if necessary
        if capture != "." and not is_en_passant:
            self.squares[end_row][end_col] = capture
            # Hash - add the captured piece back to the dest
            self.zobrist_hash ^= self.zobrist_hasher.hash_piece[end_row*8+end_col][self.zobrist_hasher.piece_index[capture]]
