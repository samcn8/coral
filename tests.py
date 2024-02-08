import chess_board
import rulebook as rules
import time

def test_move_hashing():
    board = chess_board.Board()
    initial_hash = board.zobrist_hash
    board.make_move(6, 4, 4, 4) # e4
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.make_move(1, 3, 3, 3) # d5
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.make_move(4, 4, 3, 3) # exd5
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.make_move(1, 2, 3, 2) # c5
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.make_move(3, 3, 2, 2) # dxc6
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.make_move(0, 6, 2, 5) # Nf6
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.make_move(2, 2, 1, 2) # c7
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.make_move(1, 4, 3, 4) # e5
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.make_move(6, 0, 4, 0) # a4
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.make_move(0, 5, 5, 0) # Ba3
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.make_move(7, 0, 5, 0) # Rxa3
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.make_move(0, 4, 0, 6) # O-O
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.make_move(1, 2, 0, 1) # cxb8=Q
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.make_move(0, 0, 0, 1) # Rxb8
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.unmake_move() # undo Rxb8
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.unmake_move() # undo cxb8=Q
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.unmake_move() # undo O-O
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.unmake_move() # undo Rxa3
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.unmake_move() # undo Ba3
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.unmake_move() # undo a4
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.unmake_move() # undo e5
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.unmake_move() # undo c7
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.unmake_move() # undo Nf6
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.unmake_move() # undo dxc6
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.unmake_move() # undo c5
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.unmake_move() # undo exd5
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.unmake_move() # undo d5
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    board.unmake_move() # undo e4
    assert board.zobrist_hash == board.zobrist_hasher.full_hash(board)
    assert initial_hash == board.zobrist_hash

def number_of_valid_moves(board, depth):
    if depth == 0:
        return 1
    all_valid_moves = rules.compute_all_valid_moves(board)
    move_count = 0
    for start in all_valid_moves:
        for m in all_valid_moves[start]:
            board.make_move(start[0], start[1], m[0], m[1])
            move_count += number_of_valid_moves(board, depth - 1)
            board.unmake_move()
    return move_count

def test_number_of_captures():
    board = chess_board.Board()
    board.make_move(6, 4, 4, 4) # e4
    board.make_move(1, 3, 3, 3) # d5
    all_valid_moves = rules.compute_all_valid_moves(board)
    move_count = 0
    for start in all_valid_moves:
        for m in all_valid_moves[start]:
            if m[3]:
                move_count += 1
    assert move_count == 1

def test_move_generation():
    truth_moves = {1:20, 2:400, 3:8902, 4:197281}
    board = chess_board.Board()
    all_valid_moves = rules.compute_all_valid_moves(board)
    for i in truth_moves:
        assert number_of_valid_moves(board, i) == truth_moves[i]

if __name__ == '__main__':

    print("test_move_hashing")
    start_time = time.time()
    test_move_hashing()
    end_time = time.time()
    print(" -> passed; time =", '{0:.2f}'.format(end_time - start_time), "seconds")

    print("test_move_generation")
    start_time = time.time()
    test_move_generation()
    end_time = time.time()
    print(" -> passed; time =", '{0:.2f}'.format(end_time - start_time), "seconds")

    print("test_number_of_captures")
    start_time = time.time()
    test_number_of_captures()
    end_time = time.time()
    print(" -> passed; time =", '{0:.2f}'.format(end_time - start_time), "seconds")