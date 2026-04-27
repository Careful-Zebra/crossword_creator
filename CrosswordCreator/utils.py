# puzzles/utils.py
import random

class CrosswordGenerator:
    def __init__(self, words_and_clues, grid_size=15):
        self.grid_size = grid_size
        # Create an empty 2D array (grid_size x grid_size)
        self.grid = [['' for _ in range(grid_size)] for _ in range(grid_size)]
        # Sort words by length descending to place the biggest ones first
        self.word_data = sorted(words_and_clues, key=lambda x: len(x['word']), reverse=True)
        self.placed_words = []

    def generate(self):
        for item in self.word_data:
            word = item['word'].upper()
            clue = item['clue']
            placed = self._place_word(word, clue)
            if not placed:
                # If a word couldn't fit, expand the grid and regenerate everything
                self.grid_size += 2
                self.grid = [['' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
                self.placed_words = []
                return self.generate()  # Recursive call with the larger grid
                
        
        return {
            "grid": self.grid,
            "clues": self.placed_words
        }

    def _place_word(self, word, clue):
        # 1. Place the first word roughly in the middle
        if not self.placed_words:
            start_col = (self.grid_size - len(word)) // 2
            start_row = self.grid_size // 2
            return self._insert(word, clue, start_row, start_col, 'A')

        best_placements = []

        # 2. Look at every cell currently on the board
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                cell_char = self.grid[r][c]
                
                # 3. If the cell has a letter, and that letter is in our new word...
                if cell_char != '' and cell_char in word:
                    
                    # Find exactly where that letter sits in our new word
                    for char_index, char in enumerate(word):
                        if char == cell_char:
                            
                            # Try placing Across (A) by shifting the start column backward
                            start_r_a = r
                            start_c_a = c - char_index
                            if self._can_place(word, start_r_a, start_c_a, 'A'):
                                best_placements.append((start_r_a, start_c_a, 'A'))

                            # Try placing Down (D) by shifting the start row backward
                            start_r_d = r - char_index
                            start_c_d = c
                            if self._can_place(word, start_r_d, start_c_d, 'D'):
                                best_placements.append((start_r_d, start_c_d, 'D'))

        # 4. If we found valid intersections, pick one randomly
        if best_placements:
            r, c, d = random.choice(best_placements)
            return self._insert(word, clue, r, c, d)
        
        # If no intersections work, skip the word
        return False

    def _can_place(self, word, row, col, direction):
        # 1. Check if the word goes out of bounds
        if direction == 'A':
            if col < 0 or col + len(word) > self.grid_size: return False
            if row < 0 or row >= self.grid_size: return False
        elif direction == 'D':
            if row < 0 or row + len(word) > self.grid_size: return False
            if col < 0 or col >= self.grid_size: return False

        # 2. Check for collisions and invalid neighbors
        for i, char in enumerate(word):
            r = row + (i if direction == 'D' else 0)
            c = col + (i if direction == 'A' else 0)
            
            existing_char = self.grid[r][c]
            
            # Direct collision with a different letter
            if existing_char != '' and existing_char != char:
                return False 

            # If the cell is empty, we must ensure it doesn't accidentally 
            # sit adjacent to another word, creating garbage two-letter words.
            if existing_char == '':
                if direction == 'A':
                    if r > 0 and self.grid[r-1][c] != '': return False
                    if r < self.grid_size - 1 and self.grid[r+1][c] != '': return False
                elif direction == 'D':
                    if c > 0 and self.grid[r][c-1] != '': return False
                    if c < self.grid_size - 1 and self.grid[r][c+1] != '': return False

        # 3. Check the tips (prevents words from running tip-to-tail into one long string)
        if direction == 'A':
            if col > 0 and self.grid[row][col-1] != '': return False
            if col + len(word) < self.grid_size and self.grid[row][col+len(word)] != '': return False
        elif direction == 'D':
            if row > 0 and self.grid[row-1][col] != '': return False
            if row + len(word) < self.grid_size and self.grid[row+len(word)][col] != '': return False

        return True
    def _insert(self, word, clue, row, col, direction):
        # 1. Write the letters into the 2D grid array
        for i, char in enumerate(word):
            r = row + (i if direction == 'D' else 0)
            c = col + (i if direction == 'A' else 0)
            self.grid[r][c] = char

        # 2. Save the metadata for the clue list
        self.placed_words.append({
            "word": word, "clue": clue, "row": row, "col": col, "direction": direction
        })
        return True