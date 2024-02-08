def loc_to_notation(row, col):
    return "abcdefgh"[col] + str(8-row)

def notation_to_loc(n):
    col = "abcdefgh".index(n[0])
    row = 8-int(n[1])
    return row, col

def algebraic_notation(start_row, start_col, end_row, end_col, all_valid_moves, board):

    piece = board.squares[start_row][start_col]
    piece_upper = piece.upper()
    if piece_upper == "P" and start_col != end_col and board.squares[end_row][end_col] == ".":
        is_en_passant = True
    else:
        is_en_passant = False
    if (board.whites_turn and end_row == 0 and piece == "P"
        or not board.whites_turn and end_row == 7 and piece == "p"):
        is_promotion = True
    else:
        is_promotion = False

    #p = board.squares[start_row][start_col].upper()
    capture = board.squares[end_row][end_col] != "." or is_en_passant

    # Check for short and long castle
    if piece_upper == "K" and start_col - end_col == 2:
        notation = "O-O-O"
    elif piece_upper == "K" and start_col - end_col == -2:
        notation = "O-O"
    else:
        notation = ""
        if piece_upper == "P" and capture:
            notation += loc_to_notation(start_row, start_col)[0]
        elif piece_upper != "P":
            notation += piece_upper
            # Check for ambiguity
            ambiguous = False
            same_file = False
            same_rank = False
            for row in range(8):
                for col in range(8):
                    if (row, col) != (start_row, start_col) and (row, col) in all_valid_moves:
                        moves = all_valid_moves[(row, col)]
                        if (moves and piece_upper == board.squares[row][col].upper() and 
                            ( (end_row, end_col, False, False) in moves or
                              (end_row, end_col, True, False) in moves or
                              (end_row, end_col, False, True) in moves or
                              (end_row, end_col, False, True) in moves) ):
                            # This piece is making the notation ambiguous
                            ambiguous = True
                            if start_col == col:
                                same_file = True
                            if start_row == row:
                                same_rank = True
            if ambiguous:
                if not same_file:
                    notation += loc_to_notation(start_row, start_col)[0]
                elif not same_rank:
                    notation += loc_to_notation(start_row, start_col)[1]
                else:
                    notation += loc_to_notation(start_row, start_col)
        if capture:
            notation += "x"
        notation += loc_to_notation(end_row, end_col)
        if is_promotion:
            notation += "=Q"

    return notation
        
def check_for_terminal_states_and_king_checks(board, any_valid_moves):
    """
    Returns two values:
        1) True if game is over, False otherwise
        2) If above is True:
              -1 for black win
               0 for stalemate
               0.1 for draw by insufficient material
               0.2 for draw by three-fold repetition
               1 for white win
           If above is False:
              -1 for black is checking the white king
              1 for white is checking the black king
              0 otherwise
    """
    
    # Draw by insufficient material
    if is_draw_by_insufficient_material(board):
        return True, 0.1
    
    if is_draw_by_threefold_repeition(board):
        return True, 0.2

    # Compute any checks
    in_check = is_king_in_check(board.whites_turn, board)

    # Stalemate
    if not in_check and not any_valid_moves:
        return True, 0

    # Checks and checkmates
    if board.whites_turn:
        if in_check and not any_valid_moves:
            # Checkmate, black wins
            return True, -1
        if in_check:
            # Black is checking white king
            return False, -1
    else:
        if in_check and not any_valid_moves:
            # Checkmate, white wins
            return True, 1
        if in_check:
            # White is checking black king
            return False, 1
        
    # No special states
    return False, 0


def in_bounds(row, col):
    return row >= 0 and row <= 7 and col >= 0 and col <= 7

def is_draw_by_insufficient_material(board):
    all_pieces = [board.squares[i][j] for i in range(8) for j in range(8) if board.squares[i][j] != "."]

    # If there are any queens, rooks, or pawns on the board, it's not a draw
    if "Q" in all_pieces or "R" in all_pieces or "P" in all_pieces or "q" in all_pieces or "r" in all_pieces or "p" in all_pieces:
        return False
    
    # If both sides have at most a single knight or bishop left, it's a draw
    if all_pieces.count("b") + all_pieces.count("n") <= 1 and all_pieces.count("B") + all_pieces.count("N") <= 1:
        return True

    # Any other case, it's not a draw
    return False

def is_draw_by_threefold_repeition(board):

    # Check if the current Zobrist hash has been repeated twice before.
    # Note the hash will only be the same if its the same player's turn,
    # so we can skip every other element in the list
    hash = board.zobrist_hash
    appearances = 0
    check = True
    for i in reversed(board.zobrist_history):
        if check and hash == i:
            appearances += 1 # Note the first entry we check will be an "appearance"
        if appearances == 3:
            return True
        check = not check
    return False

def fast_straight_probe(white_king, board, target_row, target_col, row_direction, col_direction):
    a_row = target_row + row_direction
    a_col = target_col + col_direction
    step = 1
    while in_bounds(a_row, a_col):
        piece = board.squares[a_row][a_col]
        if step == 1:
            if (not white_king and piece == "K" or
                white_king and piece == "k"):
                return True
        if row_direction == 0 or col_direction == 0:
            # Non-diagonal
            if (not white_king and piece in "RQ" or
                white_king and piece in "rq"):
                return True
        else:
            # Diagonal
            if (not white_king and piece in "BQ" or
                white_king and piece in "bq"):
                return True
        if piece != ".":
            return False
        a_row += row_direction
        a_col += col_direction
        step += 1
    return False

def is_king_in_check(white_king, board):
    """ If white_king is True, return True if white king is in check; same with black"""

    # Find the king
    king_pos = (-1, -1)
    for row in range(8):
        for col in range(8):
            if white_king and board.squares[row][col] == "K" or not white_king and board.squares[row][col] == "k":
                king_pos = (row, col)
                break
        if king_pos != (-1, -1):
            break
    else:
        print("ERROR: Cannot find king in board " + str(board.squares))
        return False

    # Check for checks with knights first
    for i in [(-1, -2), (-1, 2), (1, -2), (1, 2), (-2, -1), (-2, 1), (2, -1), (2, 1)]:
        a_row = king_pos[0] + i[0]
        a_col = king_pos[1] + i[1]
        if in_bounds(a_row, a_col):
            if (not white_king and board.squares[a_row][a_col] == "N" or
                white_king and board.squares[a_row][a_col] == "n"):
                return True
            
    # Check for checks with pawns next
    if white_king:
        if in_bounds(king_pos[0] - 1, king_pos[1] - 1) and board.squares[king_pos[0] - 1][king_pos[1] - 1] == "p":
            return True
        if in_bounds(king_pos[0] - 1, king_pos[1] + 1) and board.squares[king_pos[0] - 1][king_pos[1] + 1] == "p":
            return True
    else:
        if in_bounds(king_pos[0] + 1, king_pos[1] - 1) and board.squares[king_pos[0] + 1][king_pos[1] - 1] == "P":
            return True
        if in_bounds(king_pos[0] + 1, king_pos[1] + 1) and board.squares[king_pos[0] + 1][king_pos[1] + 1] == "P":
            return True
        
    # Check for checks with bishops, rooks, queens, and kings
    for direction in [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]:
        if fast_straight_probe(white_king, board, king_pos[0], king_pos[1], direction[0], direction[1]):
            return True

    # TODO -- remove this block! Check for checks
    """for row in range(8):
        for col in range(8):
            attacker = board.squares[row][col]
            if attacker in opp_pieces:
                moves = valid_moves(row, col, board, False)
                for m in moves:
                    if king_pos[0] == m[0] and king_pos[1] == m[1]:
                        return True"""

    # If we made it this far, there are no checks
    return False

def prune_moves_to_avoid_checks(row, col, moves, board):
    """ Get rid of moves that have us in check after they are made """
    pruned_moves = []
    if board.squares[row][col] in "KQRNBP":
        white = True
    else:
        white = False
    for m in moves:
        board.make_move(row, col, m[0], m[1])
        if not is_king_in_check(white, board):
            pruned_moves.append(m)
        board.unmake_move()
    return pruned_moves

def are_there_any_valid_moves(board):
    for row in range(8):
        for col in range(8):
            piece = board.squares[row][col]
            if board.whites_turn and piece in "KQRNBP" or not board.whites_turn and piece in "kqrnbp":
                if len(valid_moves(row, col, board, True)) > 0:
                    return True
    return False

def compute_all_valid_moves(board):
    all_moves = {} # key is (row, col), value is list of valid moves (new row, new col, is en passant?, is capture?) for the piece
    for row in range(8):
        for col in range(8):
            piece = board.squares[row][col]
            if board.whites_turn and piece in "KQRNBP" or not board.whites_turn and piece in "kqrnbp":
                all_moves[(row, col)] = valid_moves(row, col, board, True)
    return all_moves

def valid_moves(row, col, board, check_for_checks):

    # Moves is a list of (new row, new col, is en passant?, is capture?) - all moves for the piece on row, col
    moves = []
    piece = board.squares[row][col]

    # White pawn
    if piece == "P":
        # Move "up" to an empty space
        if row >= 1 and board.squares[row-1][col] == ".":
            moves.append((row-1, col, False, False))
        # If first move, allow two "up" moves
        if row == 6 and board.squares[row-1][col] == "." and board.squares[row-2][col] == ".":
            moves.append((row-2, col, False, False))
        # Capture diagonally
        if row >= 1 and col >= 1 and board.squares[row-1][col-1] in "kqrnbp":
            moves.append((row-1, col-1, False, True))
        if row >= 1 and col <= 6 and board.squares[row-1][col+1] in "kqrnbp":
            moves.append((row-1, col+1, False, True))
        # En passant
        if board.move_history:
            last_move = board.move_history[-1]
            if (row == 3 and col >= 1 and board.squares[2][col-1] == "." and
                last_move[4] == "p" and last_move[0] == 1 and last_move[1] == col-1 and
                last_move[2] == 3 and last_move[3] == col-1):
                moves.append((row-1, col-1, True, True))
            if (row == 3 and col <= 6 and board.squares[2][col+1] == "." and
                last_move[4] == "p" and last_move[0] == 1 and last_move[1] == col+1 and
                last_move[2] == 3 and last_move[3] == col+1):
                moves.append((row-1, col+1, True, True))

    # Black pawn
    elif piece == "p":
        # Move "up" to an empty space
        if row <= 6 and board.squares[row+1][col] == ".":
            moves.append((row+1, col, False, False))
        # If first move, allow two "up" moves
        if row == 1 and board.squares[row+1][col] == "." and board.squares[row+2][col] == ".":
            moves.append((row+2, col, False, False))
        # Capture diagonally
        if row <= 6 and col <= 6 and board.squares[row+1][col+1] in "KQRNBP":
            moves.append((row+1, col+1, False, True))
        if row <= 6 and col >= 1 and board.squares[row+1][col-1] in "KQRNBP":
            moves.append((row+1, col-1, False, True))
        # En passant
        if board.move_history:
            last_move = board.move_history[-1]
            if (row == 4 and col >= 1 and board.squares[5][col-1] == "." and
                last_move[4] == "P" and last_move[0] == 6 and last_move[1] == col-1 and
                last_move[2] == 4 and last_move[3] == col-1):
                moves.append((row+1, col-1, True, True))
            if (row == 4 and col <= 6 and board.squares[5][col+1] == "." and
                last_move[4] == "P" and last_move[0] == 6 and last_move[1] == col+1 and
                last_move[2] == 4 and last_move[3] == col+1):
                moves.append((row+1, col+1, True, True))

    # White king
    elif piece == "K":
        for r in [row-1, row, row+1]:
            for c in [col-1, col, col+1]:
                if r == row and c == col:
                    continue
                if in_bounds(r, c) and board.squares[r][c] == ".":
                    moves.append((r, c, False, False))
                elif in_bounds(r, c) and board.squares[r][c] in "kqrnbp":
                    moves.append((r, c, False, True))
        # Only check for castling if we're "checking for checks", since the
        # act of castling cannot capture an opposing king.
        if check_for_checks:
            # Check short castle then long castle
            for rook_col in [7, 0]:
                # Ensure king and rook have never moved, and the rook has not been captured
                for m in board.move_history:
                    if ((m[0] == 7 and m[1] == 4 or m[0] == 7 and m[1] == rook_col) or # king or rook moved
                        m[2] == 7 and m[3] == rook_col): # rook was captured
                        break
                else:
                    # Ensure squares between them are empty
                    for space_col in range(min(rook_col, 4) + 1, max(rook_col, 4)):
                        if board.squares[7][space_col] != ".":
                            break
                    else:
                        # Ensure king is not in check
                        if not is_king_in_check(True, board):
                            # Ensure king will not go through check
                            if rook_col == 7:
                                for c in [5, 6]:
                                    board.make_move(7, 4, 7, c)
                                    is_in_check = is_king_in_check(True, board)
                                    board.unmake_move()
                                    if is_in_check:
                                        break
                                else:
                                    # We can castle
                                    moves.append((7, 6, False, False))
                            elif rook_col == 0:
                                for c in [3, 2]:
                                    board.make_move(7, 4, 7, c)
                                    is_in_check = is_king_in_check(True, board)
                                    board.unmake_move()
                                    if is_in_check:
                                        break
                                else:
                                    # We can castle
                                    moves.append((7, 2, False, False))                             

    # Black king
    elif piece == "k":
        for r in [row-1, row, row+1]:
            for c in [col-1, col, col+1]:
                if r == row and c == col:
                    continue
                if in_bounds(r, c) and board.squares[r][c] == ".":
                    moves.append((r, c, False, False))
                elif in_bounds(r, c) and board.squares[r][c] in "KQRNBP":
                    moves.append((r, c, False, True))
        # Only check for castling if we're "checking for checks", since the
        # act of castling cannot capture an opposing king.
        if check_for_checks:
            # Check short castle then long castle
            for rook_col in [7, 0]:
                # Ensure king and rook have never moved, and the rook has not been captured
                for m in board.move_history:
                    if ((m[0] == 0 and m[1] == 4 or m[0] == 0 and m[1] == rook_col) or # king or rook moved
                        m[2] == 0 and m[3] == rook_col): # rook was captured
                        break
                else:
                    # Ensure squares between them are empty
                    for space_col in range(min(rook_col, 4) + 1, max(rook_col, 4)):
                        if board.squares[0][space_col] != ".":
                            break
                    else:
                        # Ensure king is not in check
                        if not is_king_in_check(False, board):
                            # Ensure king will not go through check
                            if rook_col == 7:
                                for c in [5, 6]:
                                    board.make_move(0, 4, 0, c)
                                    is_in_check = is_king_in_check(False, board)
                                    board.unmake_move()
                                    if is_in_check:
                                        break
                                else:
                                    # We can castle
                                    moves.append((0, 6, False, False))
                            elif rook_col == 0:
                                for c in [3, 2]:
                                    board.make_move(0, 4, 0, c)
                                    is_in_check = is_king_in_check(False, board)
                                    board.unmake_move()
                                    if is_in_check:
                                        break
                                else:
                                    # We can castle
                                    moves.append((0, 2, False, False))

    # White knight
    elif piece == "N":
        for r, c in [(row - 2, col - 1),
                     (row - 1, col - 2),
                     (row - 2, col + 1),
                     (row - 1, col + 2),
                     (row + 2, col - 1),
                     (row + 1, col - 2),
                     (row + 2, col + 1),
                     (row + 1, col + 2)]:
            if in_bounds(r, c) and board.squares[r][c] == ".":
                moves.append((r, c, False, False))
            elif in_bounds(r, c) and board.squares[r][c] in "kqrnbp":
                moves.append((r, c, False, True))

    # Black knight
    elif piece == "n":
        for r, c in [(row - 2, col - 1),
                     (row - 1, col - 2),
                     (row - 2, col + 1),
                     (row - 1, col + 2),
                     (row + 2, col - 1),
                     (row + 1, col - 2),
                     (row + 2, col + 1),
                     (row + 1, col + 2)]:
            if in_bounds(r, c) and board.squares[r][c] == ".":
                moves.append((r, c, False, False))
            elif in_bounds(r, c) and board.squares[r][c] in "KQRNBP":
                moves.append((r, c, False, True))

    # White rook
    elif piece == "R":
        moves.extend(straight_probe(row, col, True, -1, 0, board))
        moves.extend(straight_probe(row, col, True, 1, 0, board))
        moves.extend(straight_probe(row, col, True, 0, -1, board))
        moves.extend(straight_probe(row, col, True, 0, 1, board))

    # Black rook
    elif piece == "r":
        moves.extend(straight_probe(row, col, False, -1, 0, board))
        moves.extend(straight_probe(row, col, False, 1, 0, board))
        moves.extend(straight_probe(row, col, False, 0, -1, board))
        moves.extend(straight_probe(row, col, False, 0, 1, board))

    # White bishop
    elif piece == "B":
        moves.extend(straight_probe(row, col, True, -1, -1, board))
        moves.extend(straight_probe(row, col, True, -1, 1, board))
        moves.extend(straight_probe(row, col, True, 1, -1, board))
        moves.extend(straight_probe(row, col, True, 1, 1, board))

    # Black bishop
    elif piece == "b":
        moves.extend(straight_probe(row, col, False, -1, -1, board))
        moves.extend(straight_probe(row, col, False, -1, 1, board))
        moves.extend(straight_probe(row, col, False, 1, -1, board))
        moves.extend(straight_probe(row, col, False, 1, 1, board))

    # White queen
    elif piece == "Q":
        moves.extend(straight_probe(row, col, True, -1, 0, board))
        moves.extend(straight_probe(row, col, True, 1, 0, board))
        moves.extend(straight_probe(row, col, True, 0, -1, board))
        moves.extend(straight_probe(row, col, True, 0, 1, board))
        moves.extend(straight_probe(row, col, True, -1, -1, board))
        moves.extend(straight_probe(row, col, True, -1, 1, board))
        moves.extend(straight_probe(row, col, True, 1, -1, board))
        moves.extend(straight_probe(row, col, True, 1, 1, board))

    # Black queen
    elif piece == "q":
        moves.extend(straight_probe(row, col, False, -1, 0, board))
        moves.extend(straight_probe(row, col, False, 1, 0, board))
        moves.extend(straight_probe(row, col, False, 0, -1, board))
        moves.extend(straight_probe(row, col, False, 0, 1, board))
        moves.extend(straight_probe(row, col, False, -1, -1, board))
        moves.extend(straight_probe(row, col, False, -1, 1, board))
        moves.extend(straight_probe(row, col, False, 1, -1, board))
        moves.extend(straight_probe(row, col, False, 1, 1, board))

    # Are we pruning moves that result in checks?
    if check_for_checks:
        moves = prune_moves_to_avoid_checks(row, col, moves, board)

    return moves

def straight_probe(row, col, white, direction_row, direction_col, board):
    moves = []
    if white:
        valid_squares = ".kqrnbp"
    else:
        valid_squares = ".KQRNBP"
    r = row + direction_row
    c = col + direction_col
    while in_bounds(r, c) and board.squares[r][c] in valid_squares:
        if board.squares[r][c] == ".":
            moves.append((r, c, False, False))
            r += direction_row
            c += direction_col
        else:
            # This is a capture
            moves.append((r, c, False, True))
            break
    return moves
