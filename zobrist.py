import random

class ZobristHasher():
    """
    Implements Zobrist hashing for use in transposition tables.
    See https://en.wikipedia.org/wiki/Zobrist_hashing for more information.
    """

    def __init__(self):

        # Unique number for each piece
        self.piece_index = {}
        for id, p in enumerate("PNBRQKpnbrqk"):
            self.piece_index[p] = id

        # Create table of random values
        # 64 (squares) x 12 (pieces) -- hash_piece[square][piece]
        self.hash_piece = []
        for square in range(64):
            self.hash_piece.append([self.random_value() for p in range(12)])
        
        # Random values for black's turn
        self.hash_blacks_turn = self.random_value()

        # Random values for castling rights
        self.hash_white_ks_castling_rights = self.random_value()
        self.hash_white_qs_castling_rights = self.random_value()
        self.hash_black_ks_castling_rights = self.random_value()
        self.hash_black_qs_castling_rights = self.random_value()

        # Random values for en passant file (column)
        self.hash_en_passant = [self.random_value() for e in range(8)]

    def random_value(self):
        return random.randint(0, pow(2, 64))
    
    def full_hash(self, board):
        h = 0
        if not board.whites_turn:
            h ^= self.hash_blacks_turn
        for i in range(64):
            row = i // 8
            col = i % 8
            piece = board.squares[row][col]
            if piece != ".":
                h ^= self.hash_piece[i][self.piece_index[piece]]
        if board.white_ks_castling_rights:
            h ^= self.hash_white_ks_castling_rights
        if board.white_qs_castling_rights:
            h ^= self.hash_white_qs_castling_rights
        if board.black_ks_castling_rights:
            h ^= self.hash_black_ks_castling_rights
        if board.black_qs_castling_rights:
            h ^= self.hash_black_qs_castling_rights
        (e_row, e_col) = board.en_passant_rights
        if e_col != -1:
            h ^= self.hash_en_passant[e_col]
        return h
