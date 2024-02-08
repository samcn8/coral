import csv

class OpeningFinder():
    def __init__(self):
        self.total_openings_loaded = 0
        self.openings = {} # Fen position string -> Opening name

    def load_opening_book_tsv(self, filename):
        """ This method loads a tsv file containing a list of openings with lines
        in the form ECO reference, name, move in SAN."""
        with open(filename) as f:
            csv_reader = csv.reader(f, delimiter="\t")
            next(csv_reader)
            count = 0
            for line in csv_reader:
                opening_name = line[1]
                fen_string = line[4].split()[0]
                self.openings[fen_string] = opening_name
                count += 1
        print("Opening book", filename, "containing", count, "openings has been loaded.")
        self.total_openings_loaded += count

    def find_opening(self, board):
        fen_string = ""
        for row in range(0, 8):
            skip = 0
            for col in range(0, 8):
                c = board.squares[row][col]
                if c == ".":
                    skip += 1
                else:
                    if skip > 0:
                        fen_string += str(skip)
                        skip = 0
                    fen_string += c
            if skip > 0:
                fen_string += str(skip)
            if row != 7:
                fen_string += "/"
        return self.openings.get(fen_string)
        