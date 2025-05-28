import random

class PGNTreeNode():
    def __init__(self, move):
        self.move = move
        self.popularity = 1 # Number of lines going through this node
        self.children = []

class PGNTree():
    
    def __init__(self):
        self.root = PGNTreeNode(".")
    
    def insert(self, move_list, cur_root = None):
        if not move_list:
            return
        if cur_root is None:
            cur_root = self.root
        cur_move = move_list.pop(0)
        for child in cur_root.children:
            if cur_move == child.move:
                child.popularity += 1
                self.insert(move_list, cur_root=child)
                break
        else:
            new_child = PGNTreeNode(cur_move)
            cur_root.children.append(new_child)
            self.insert(move_list, cur_root=new_child)

    def get_children(self, moves_so_far, cur_root = None):
        if cur_root is None:
            cur_root = self.root
        if not moves_so_far:
            return cur_root.children
        cur_move = moves_so_far.pop(0)
        for child in cur_root.children:
            if cur_move == child.move:
                return self.get_children(moves_so_far, cur_root = child)
        return []

    def count_lines(self, cur_root = None):
        if cur_root is None:
            cur_root = self.root
        if not cur_root.children:
            return 1
        count = 0
        for child in cur_root.children:
            count += self.count_lines(cur_root = child)
        return count

    def clear(self):
        self.root = PGNTreeNode(".")

    def __str__(self, cur_root = None, depth = 0):
        if cur_root is None:
            cur_root = self.root
        ret = "\t" * depth + repr(cur_root.move) + "\n"
        for child in cur_root.children:
            ret += self.__str__(cur_root = child, depth = depth + 1)
        return ret


class PGNOpeningBook():

    def __init__(self):
        # This is a tree representing moves in SAN format
        self.opening_tree = PGNTree()

    def load_opening_book_pgn(self, filename):
        self.opening_tree.clear()
        print("Loading opening book for engine use: ", filename)
        with open(filename) as f:
            all_lines = []
            cur_line = ""

            # Pre-process file in case we have line breaks with the same line
            for line in f:
                line = line.strip()
                if not line or line[0] == "[":
                    continue
                # Note that it's likely there is a * at the end if this is an opening
                # book, indicating that the game is not complete.  There might be something
                # like 1/2-1/2 as well.  It's not critical to remove this because even though
                # it adds to the tree, we only compare valid moves.
                if line[-1] == "*":
                    line = line[:-1].strip()
                if line[:2] == "1.":
                    # This is a new line
                    if cur_line != "":
                        all_lines.append(cur_line.strip())
                    cur_line = line
                else:
                    # This is a continuation of a previous line
                    cur_line = cur_line + " " + line
            if cur_line != "":
                all_lines.append(cur_line.strip())

            # Now add all lines
            for line in all_lines:
                moves = line.replace('.', ' ').split(' ')
                moves = [m for m in moves if m != "" and not m.isdigit()]
                self.opening_tree.insert(moves)

        print("Loaded tree with", self.opening_tree.count_lines(), "leaf nodes in engine opening book")
        # TODO: return false and "clear" if something goes wrong
        return True
    
    def get_next_move_random(self, moves_so_far):
        candidate_nodes = self.opening_tree.get_children(moves_so_far)
        candidates = [c.move for c in candidate_nodes]
        candidates_pop = [c.popularity for c in candidate_nodes]
        if candidates:
            # Probability of selection is weighted by the number of lines via a node
            return random.choices(candidates, candidates_pop)[0]
        return None

    def clear(self):
        self.opening_tree.clear()
