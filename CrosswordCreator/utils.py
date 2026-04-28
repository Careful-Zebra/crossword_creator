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
        self.attempts = 0
        self.max_attempts = 100 # Let it try 50 completely different layouts before giving up

    def generate(self):
        for item in self.word_data:
            word = item['word'].upper()
            clue = item['clue']
            # puzzles/utils.py (inside generate)
            placed = self._place_word(word, clue)
            if not placed:

                self.attempts += 1
                
                # Escape hatch: Crash gracefully with a helpful message
                if self.attempts > self.max_attempts:
                    raise ValueError(f"Could not intersect the word '{word}'. Make sure your words share enough common letters!")
                
                if self.grid_size >= 100:
                    self.grid_size = 12 #reset grid size, make it try and regenerate, hope randomness fixes
                
                # If a word couldn't fit and we are under the limit, expand and regenerate
                self.grid_size += 2
                self.grid = [['' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
                self.placed_words = []
                #Shuffle the word list so the retry builds a completely different shape
                random.shuffle(self.word_data)
                return self.generate()
            
        # After all words are placed, clean up the grid to minimize its size
        self._clean_grid()
        rich_grid = self._assign_numbers()
        
        return {
            "grid": rich_grid,
            "clues": self.placed_words
        }
    
    def _clean_grid(self):
        # 1. Find the bounding box (the edges of the actual crossword)
        min_r = min((r for r in range(self.grid_size) for c in range(self.grid_size) if self.grid[r][c] != ''), default=0)
        max_r = max((r for r in range(self.grid_size) for c in range(self.grid_size) if self.grid[r][c] != ''), default=self.grid_size-1)
        min_c = min((c for r in range(self.grid_size) for c in range(self.grid_size) if self.grid[r][c] != ''), default=0)
        max_c = max((c for r in range(self.grid_size) for c in range(self.grid_size) if self.grid[r][c] != ''), default=self.grid_size-1)

        # 2. Slice the grid to only include the bounding box
        self.grid = [row[min_c:max_c+1] for row in self.grid[min_r:max_r+1]]

        # 3. Shift all the saved coordinates so they match the newly trimmed grid
        for word in self.placed_words:
            word['row'] -= min_r
            word['col'] -= min_c

    def _assign_numbers(self):
        rows = len(self.grid)
        cols = len(self.grid[0]) if rows > 0 else 0
        
        # Create a new "rich" grid where every cell is a dictionary instead of a string
        rich_grid = [[{"char": self.grid[r][c], "num": None} for c in range(cols)] for r in range(rows)]
        
        current_num = 1
        
        # Scan top-to-bottom, left-to-right
        for r in range(rows):
            for c in range(cols):
                if self.grid[r][c] == '': continue
                
                starts_word = False
                # Check if this specific cell is the starting row/col for any word
                for word_data in self.placed_words:
                    if word_data['row'] == r and word_data['col'] == c:
                        word_data['num'] = current_num
                        starts_word = True
                        
                if starts_word:
                    rich_grid[r][c]['num'] = current_num
                    current_num += 1
                    
        return rich_grid

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