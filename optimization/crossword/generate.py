import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            var_domain = self.domains[var]
            var_domain_copy = var_domain.copy()
            for word in var_domain_copy:
                if len(word) != var.length:
                    var_domain.remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        x_domain = self.domains[x]
        x_domain_copy = x_domain.copy()
        y_domain = self.domains[y]
        revised = False
        for x_val in x_domain_copy:
            x_idx, y_idx = self.crossword.overlaps[x, y]
            if all([x_val[x_idx] != y_val[y_idx] 
                    for y_val in y_domain]):
                x_domain.remove(x_val)
                revised = True
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = {pair for pair in self.crossword.overlaps 
                    if self.crossword.overlaps[pair] is not None}
            
        while len(arcs) > 0:
            arc = arcs.pop()
            x, y = arc
            revised = self.revise(x, y)
            if revised:
                if len(self.domains[x]) == 0:
                    return False
                arcs_to_recheck = {(z, x) for z in self.crossword.neighbors(x)}
                arcs = arcs.union(arcs_to_recheck)

        return True
    
    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return len(assignment) == len(self.crossword.variables)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        distinct_words = len(assignment) == len({assignment[v] for v in assignment})

        node_consistent = all([len(assignment[var]) == var.length 
                               for var in assignment])
        
        arcs = [pair for pair in self.crossword.overlaps 
                if self.crossword.overlaps[pair] is not None]
        arc_consistent = True
        for arc in arcs:
            x, y = arc
            if x in assignment and y in assignment:
                x_word = assignment[x]
                y_word = assignment[y]
                x_idx, y_idx = self.crossword.overlaps[x, y]
                if x_word[x_idx] != y_word[y_idx]:
                    arc_consistent = False
                    break
        return distinct_words and node_consistent and arc_consistent
        
    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        x_domain = self.domains[var]
        neighbours = self.crossword.neighbors(var)
        unassigned_neighbours = {n for n in neighbours if n not in assignment}
        word_elim_num_map = {word: 0 for word in x_domain}
        for x_word in x_domain:
            for y in unassigned_neighbours:
                y_domain = self.domains[y]
                overlap = self.crossword.overlaps[var, y]
                x_idx, y_idx = overlap
                eliminated_y_words = [y_word for y_word in y_domain 
                                      if x_word[x_idx] != y_word[y_idx]]
                word_elim_num_map[x_word] += len(eliminated_y_words)
        x_domain_sorted = sorted(x_domain, key=lambda x_word: word_elim_num_map[x_word])
        return x_domain_sorted

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_vars = self.crossword.variables - set(dict.keys(assignment))
        
        def min_remaining_val_lambda(var):
            return len(self.domains[var])
        
        def degree_lambda(var):
            return -len(self.crossword.neighbors(var))
        
        def sort_key(var):
            return (min_remaining_val_lambda(var), degree_lambda(var))
        
        unassigned_vars_sorted = sorted(unassigned_vars, key=sort_key)
        return unassigned_vars_sorted[0]        

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for val in self.order_domain_values(var, assignment):
            assignment[var] = val
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            assignment.pop(var)
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
