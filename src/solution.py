def save_solution(solution, filename):
    """Save the solution to a file in the specified format"""
    with open(filename, 'w') as f:
        for row in solution:
            f.write(''.join(row) + '\n')

def print_solution(solution):
    """Print the solution in a readable format"""
    for row in solution:
        print(''.join(row))
