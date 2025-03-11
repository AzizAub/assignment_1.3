class Nonogram:
    def __init__(self):
        self.grid_type = None  # 'rect' or 'tri'
        self.height = 0
        self.width = 0
        self.colors = []
        self.row_clues = []
        self.col_clues = []
    
    @staticmethod
    def parse_file(filename):
        """Parse a nonogram file and return a Nonogram object"""
        nonogram = Nonogram()
        
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f.readlines()]
            
            # Parse grid type
            grid_info = lines[0].split()
            if grid_info[0] == 'rect':
                nonogram.grid_type = 'rect'
                nonogram.height = int(grid_info[1])
                nonogram.width = int(grid_info[2])
            
            # Parse colors
            colors = lines[1].split()
            nonogram.colors = colors
            
            # Parse clues
            clue_lines = [line for line in lines[2:] if line.strip()]
            
            # Row clues come first
            nonogram.row_clues = []
            for i in range(min(nonogram.height, len(clue_lines))):
                clue = parse_clue(clue_lines[i])
                nonogram.row_clues.append(clue)
            
            # Then column clues
            nonogram.col_clues = []
            for i in range(nonogram.height, min(nonogram.height + nonogram.width, len(clue_lines))):
                clue = parse_clue(clue_lines[i])
                nonogram.col_clues.append(clue)
            
            # Fill in empty clues if necessary
            while len(nonogram.row_clues) < nonogram.height:
                nonogram.row_clues.append([])
            
            while len(nonogram.col_clues) < nonogram.width:
                nonogram.col_clues.append([])
        
        return nonogram

def parse_clue(clue_line):
    """Parse a clue string into a list of (count, color) tuples"""
    clues = []
    parts = clue_line.split()
    
    for part in parts:
        i = 0
        while i < len(part) and part[i].isdigit():
            i += 1
        
        count = int(part[:i]) if i > 0 else 0
        color = part[i:] if i < len(part) else ''
        
        if count > 0 and color:
            clues.append((count, color))
    
    return clues
