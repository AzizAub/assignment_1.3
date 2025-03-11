import os
import argparse
import time
import glob
from src.nonogram import Nonogram
from src.sat_encoder import SATEncoder
from src.solver import NonogramSolver
from src.visualize import visualize_solution

def save_solution(solution, filename):
    """Save the solution to a file"""
    with open(filename, 'w') as f:
        for row in solution:
            f.write(''.join(row) + '\n')

def print_solution(solution):
    """Print the solution in a readable format"""
    for row in solution:
        print(''.join(row))

def solve_nonogram(clue_file, output_dir=None, verbose=False):
    # Parse the clue file
    nonogram = Nonogram.parse_file(clue_file)
    
    # DEBUG: Print the parsed nonogram
    print("Parsed nonogram:")
    print(f"Grid: {nonogram.grid_type} {nonogram.height}x{nonogram.width}")
    print(f"Colors: {nonogram.colors}")
    print("Row clues:")
    for i, clue in enumerate(nonogram.row_clues):
        print(f"  Row {i}: {clue}")
    print("Column clues:")
    for i, clue in enumerate(nonogram.col_clues):
        print(f"  Col {i}: {clue}")
    
    if verbose:
        print(f"Solving {clue_file}...")
    
    # Encode the puzzle
    start_time = time.time()
    encoder = SATEncoder(nonogram)
    cnf, var_mapping = encoder.encode_block_start()
    encoding_time = time.time() - start_time
    
    if verbose:
        print(f"Encoding time: {encoding_time:.3f} seconds")
        print(f"Variables: {cnf.nv}, Clauses: {len(cnf.clauses)}")
    
    # Solve the puzzle
    start_time = time.time()
    solver = NonogramSolver(cnf, var_mapping)
    model = solver.solve()
    solving_time = time.time() - start_time
    
    if verbose:
        print(f"Solving time: {solving_time:.3f} seconds")
    
    # Extract and save the solution
    if model:
        solution = solver.extract_solution(model, nonogram)
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            base_name = os.path.basename(clue_file)
            name, _ = os.path.splitext(base_name)
            output_file = os.path.join(output_dir, f"{name}.solution")
            save_solution(solution, output_file)
            
            # Add visualization
            image_output = os.path.join(output_dir, f"{name}.png")
            visualize_solution(solution, nonogram.colors, image_output)
            
            if verbose:
                print(f"Solution saved to {output_file}")
                print_solution(solution)
        
        return True, solution
    else:
        if verbose:
            print("No solution found.")
        return False, None

def main():
    """Main entry point for the nonogram solver"""
    parser = argparse.ArgumentParser(description='Solve nonogram puzzles using SAT techniques')
    parser.add_argument('--input-dir', required=True, help='Directory containing .clues files')
    parser.add_argument('--output-dir', default='solutions', help='Directory to save solution files')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Find all .clues files in the input directory
    clue_files = glob.glob(os.path.join(args.input_dir, "*.clues"))
    
    if not clue_files:
        print(f"No .clues files found in {args.input_dir}")
        return
    
    if args.verbose:
        print(f"Found {len(clue_files)} nonogram puzzles to solve")
    
    for clue_file in clue_files:
        solve_nonogram(clue_file, args.output_dir, args.verbose)

if __name__ == '__main__':
    main()
