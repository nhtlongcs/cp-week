import gurobipy as gp
from gurobipy import GRB

def read_sudoku(filename):
	grid = []
	with open(filename) as f:
		for line in f:
			line = line.strip()
			if line:
				line = line.replace(" ", "")
				grid.append([int(c) for c in line])
	return grid

def solve_sudoku(grid):
	n = 9
	model = gp.Model("sudoku")
	# x[i][j][k] = 1 if cell (i,j) is k+1
	x = model.addVars(n, n, n, vtype=GRB.BINARY, name="x")

	# Each cell has one value
	for i in range(n):
		for j in range(n):
			model.addConstr(gp.quicksum(x[i, j, k] for k in range(n)) == 1)

	# Each value appears once per row
	for i in range(n):
		for k in range(n):
			model.addConstr(gp.quicksum(x[i, j, k] for j in range(n)) == 1)

	# Each value appears once per column
	for j in range(n):
		for k in range(n):
			model.addConstr(gp.quicksum(x[i, j, k] for i in range(n)) == 1)

	# Each value appears once per 3x3 block
	for block_i in range(3):
		for block_j in range(3):
			for k in range(n):
				model.addConstr(gp.quicksum(
					x[i, j, k]
					for i in range(block_i*3, (block_i+1)*3)
					for j in range(block_j*3, (block_j+1)*3)
				) == 1)

	# Set known values
	for i in range(n):
		for j in range(n):
			if grid[i][j] != 0:
				model.addConstr(x[i, j, grid[i][j]-1] == 1)

	model.setParam('OutputFlag', 0)
	model.optimize()

	if model.status == GRB.OPTIMAL:
		solution = [[0]*n for _ in range(n)]
		for i in range(n):
			for j in range(n):
				for k in range(n):
					if x[i, j, k].X > 0.5:
						solution[i][j] = k+1
		return solution
	else:
		return None

def print_sudoku(grid, file=None):
    for row in grid:
        line = ' '.join(str(num) for num in row)
        if file:
            print(line, file=file)
        else:
            print(line)

def main():
	grid = read_sudoku("input")
	solution = solve_sudoku(grid)
	if solution:
		with open("output", "w") as f:
			print_sudoku(solution, file=f)
		print("Solution written to 'output'.")
	else:
		print("No solution found.")

if __name__ == "__main__":
	main()
