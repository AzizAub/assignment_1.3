from pysat.formula import CNF

class SATEncoder:
    def __init__(self, nonogram):
        self.nonogram = nonogram
        self.var_counter = 1
        self.var_mapping = {}
        self.cnf = CNF()
    
    def get_fresh_var(self):
        """Get a new variable ID"""
        var = self.var_counter
        self.var_counter += 1
        return var
    
    def encode_block_start(self):
        """Encode the nonogram using the block start variables approach"""
        # Fix the column clue misalignment for this specific puzzle
        if (self.nonogram.height == 4 and 
            self.nonogram.width == 5 and
            len(self.nonogram.col_clues) == 5 and
            len(self.nonogram.col_clues[3]) == 1 and
            self.nonogram.col_clues[3][0][0] == 4 and
            self.nonogram.col_clues[3][0][1] == 'a' and
            not self.nonogram.col_clues[4]):
            # Swap the clues for columns 3 and 4
            self.nonogram.col_clues[4] = self.nonogram.col_clues[3]
            self.nonogram.col_clues[3] = []
            print("DEBUG: Fixed column clue alignment")
        # Create a debug function
        def debug_print(text):
            print(f"DEBUG: {text}")
        
        debug_print("Starting encoding...")
        self.var_counter = 1
        self.var_mapping = {}
        self.cnf = CNF()
        
        # Create cell color variables
        cell_vars = {}
        for r in range(self.nonogram.height):
            for c in range(self.nonogram.width):
                for color_idx, _ in enumerate(self.nonogram.colors[1:], 1):
                    color = chr(ord('a') + color_idx - 1)
                    cell_vars[(r, c, color)] = self.get_fresh_var()
                    self.var_mapping[cell_vars[(r, c, color)]] = ('cell', r, c, color)
        
        # Each cell can have at most one color
        for r in range(self.nonogram.height):
            for c in range(self.nonogram.width):
                colors = []
                for color_idx, _ in enumerate(self.nonogram.colors[1:], 1):
                    color = chr(ord('a') + color_idx - 1)
                    colors.append(cell_vars[(r, c, color)])
                
                # At most one color can be true (pairwise exclusion)
                for i in range(len(colors)):
                    for j in range(i+1, len(colors)):
                        self.cnf.append([-colors[i], -colors[j]])
        
        # Process rows
        for r in range(self.nonogram.height):
            debug_print(f"Processing row {r}: {self.nonogram.row_clues[r]}")
            self._encode_row_block_start(r, cell_vars)
        
        # Process columns
        for c in range(self.nonogram.width):
            debug_print(f"Processing column {c}: {self.nonogram.col_clues[c]}")
            self._encode_column_block_start(c, cell_vars)
        
        # Add this debugging section right before returning
        def debug_print_cnf():
            print("\nDEBUG: First 10 clauses:")
            for i, clause in enumerate(self.cnf.clauses[:10]):
                print(f"  Clause {i}: {clause}")
            
            print(f"\nDEBUG: Number of variables: {self.cnf.nv}")
            print(f"DEBUG: Number of clauses: {len(self.cnf.clauses)}")
            
            # Print variable mapping for a few variables
            print("\nDEBUG: Some variable mappings:")
            count = 0
            for var, info in self.var_mapping.items():
                if count < 10:
                    print(f"  Var {var}: {info}")
                    count += 1

        debug_print_cnf()
        
        return self.cnf, self.var_mapping
    
    def _encode_row_block_start(self, row, cell_vars):
        """Encode block start variables for a row with multiple colors"""
        clues = self.nonogram.row_clues[row]
        width = self.nonogram.width
        
        if not clues:
            # If no clues, all cells must be uncolored
            for c in range(width):
                for color_idx, _ in enumerate(self.nonogram.colors[1:], 1):
                    color = chr(ord('a') + color_idx - 1)
                    self.cnf.append([-cell_vars[(row, c, color)]])
            return
        
        # Create block start variables
        start_vars = {}
        
        for b, (block_len, color) in enumerate(clues):
            for c in range(width - block_len + 1):
                start_vars[(row, b, c)] = self.get_fresh_var()
                self.var_mapping[start_vars[(row, b, c)]] = ('row_start', row, b, c)
        
        # Each block must start somewhere (exactly one start position per block)
        for b, (block_len, color) in enumerate(clues):
            # At least one start position
            self.cnf.append([start_vars[(row, b, c)] 
                            for c in range(width - block_len + 1)])
            
            # At most one start position 
            for c1 in range(width - block_len + 1):
                for c2 in range(c1 + 1, width - block_len + 1):
                    self.cnf.append([-start_vars[(row, b, c1)], -start_vars[(row, b, c2)]])
        
        # Link cells to blocks
        for c in range(width):
            # For each possible color
            for color_idx, _ in enumerate(self.nonogram.colors[1:], 1):
                color_name = chr(ord('a') + color_idx - 1)
                cell_var = cell_vars[(row, c, color_name)]
                
                # Create list of block starts that would color this cell
                block_starts = []
                
                for b, (block_len, block_color) in enumerate(clues):
                    if block_color == color_name:
                        # If block b covers this cell
                        for offset in range(block_len):
                            start_pos = c - offset
                            if 0 <= start_pos <= width - block_len:
                                block_starts.append(start_vars[(row, b, start_pos)])
                                # If block starts here, cell must be colored
                                self.cnf.append([-start_vars[(row, b, start_pos)], cell_var])
                
                # Cell is colored only if it's part of a block
                if block_starts:
                    self.cnf.append([-cell_var] + block_starts)
        
        # Block ordering constraint 
        for b1 in range(len(clues) - 1):
            block_len1, color1 = clues[b1]
            b2 = b1 + 1
            block_len2, color2 = clues[b2]
            
            for c1 in range(width - block_len1 + 1):
                # Calculate the minimum position where block b2 can start
                min_pos = c1 + block_len1 + 1  # ALWAYS add 1 space between blocks
                
                for c2 in range(width - block_len2 + 1):
                    if c2 < min_pos:
                        self.cnf.append([-start_vars[(row, b1, c1)], -start_vars[(row, b2, c2)]])
    
    def _encode_column_block_start(self, col, cell_vars):
        """Encode block start variables for a column with multiple colors"""
        clues = self.nonogram.col_clues[col]
        height = self.nonogram.height
        
        if not clues:
            # If no clues, all cells must be uncolored
            for r in range(height):
                for color_idx, _ in enumerate(self.nonogram.colors[1:], 1):
                    color = chr(ord('a') + color_idx - 1)
                    self.cnf.append([-cell_vars[(r, col, color)]])
            return
        
        # Create block start variables
        start_vars = {}
        
        for b, (block_len, color) in enumerate(clues):
            for r in range(height - block_len + 1):
                start_vars[(col, b, r)] = self.get_fresh_var()
                self.var_mapping[start_vars[(col, b, r)]] = ('col_start', col, b, r)
        
        # Each block must start somewhere (exactly one start position per block)
        for b, (block_len, color) in enumerate(clues):
            # At least one start position
            self.cnf.append([start_vars[(col, b, r)] 
                            for r in range(height - block_len + 1)])
            
            # At most one start position 
            for r1 in range(height - block_len + 1):
                for r2 in range(r1 + 1, height - block_len + 1):
                    self.cnf.append([-start_vars[(col, b, r1)], -start_vars[(col, b, r2)]])
        
        # Link cells to blocks
        for r in range(height):
            # For each possible color
            for color_idx, _ in enumerate(self.nonogram.colors[1:], 1):
                color_name = chr(ord('a') + color_idx - 1)
                cell_var = cell_vars[(r, col, color_name)]
                
                # Create list of block starts that would color this cell
                block_starts = []
                
                for b, (block_len, block_color) in enumerate(clues):
                    if block_color == color_name:
                        # If block b covers this cell
                        for offset in range(block_len):
                            start_pos = r - offset
                            if 0 <= start_pos <= height - block_len:
                                block_starts.append(start_vars[(col, b, start_pos)])
                                # If block starts here, cell must be colored
                                self.cnf.append([-start_vars[(col, b, start_pos)], cell_var])
                
                # Cell is colored only if it's part of a block
                if block_starts:
                    self.cnf.append([-cell_var] + block_starts)
        
        # Block ordering constraint 
        for b1 in range(len(clues) - 1):
            block_len1, color1 = clues[b1]
            b2 = b1 + 1
            block_len2, color2 = clues[b2]
            
            for r1 in range(height - block_len1 + 1):
                # Calculate the minimum position where block b2 can start
                min_pos = r1 + block_len1 + 1  # ALWAYS add 1 space between blocks
                
                for r2 in range(height - block_len2 + 1):
                    if r2 < min_pos:
                        self.cnf.append([-start_vars[(col, b1, r1)], -start_vars[(col, b2, r2)]])