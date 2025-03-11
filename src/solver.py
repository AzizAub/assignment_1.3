from pysat.solvers import Glucose3

class NonogramSolver:
    def __init__(self, sat_formula, var_mapping):
        self.formula = sat_formula
        self.var_mapping = var_mapping
        self.solver = Glucose3()
        
        # Add all clauses to the solver
        for clause in self.formula.clauses:
            self.solver.add_clause(clause)
    
    def solve(self):
        """Solve the SAT problem and return the model if satisfiable"""
        if self.solver.solve():
            return self.solver.get_model()
        else:
            return None
    
    def extract_solution(self, model, nonogram):
        """Extract the nonogram solution from the SAT model"""
        # Initialize solution grid with empty cells
        solution = [['-' for _ in range(nonogram.width)] for _ in range(nonogram.height)]
        
        # Fill in colored cells based on cell variables
        for var, value in enumerate(model, 1):
            if value > 0 and var in self.var_mapping:
                var_info = self.var_mapping[var]
                if var_info[0] == 'cell':
                    r, c, color = var_info[1], var_info[2], var_info[3]
                    solution[r][c] = color
        
        return solution