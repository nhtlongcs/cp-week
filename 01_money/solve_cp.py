from ortools.sat.python import cp_model

def solve_send_more_money():
    # Create the model
    model = cp_model.CpModel()
    
    # Define the variables - each letter is a digit from 0-9
    letters = ['S', 'E', 'N', 'D', 'M', 'O', 'R', 'Y']
    letter_vars = {}
    
    for letter in letters:
        letter_vars[letter] = model.NewIntVar(0, 9, letter)
    
    # Constraint: All letters must have different values (all different constraint)
    model.AddAllDifferent([letter_vars[letter] for letter in letters])
    
    # Constraint: Leading digits cannot be zero
    model.Add(letter_vars['S'] >= 1)  # S is the leading digit of SEND
    model.Add(letter_vars['M'] >= 1)  # M is the leading digit of MONEY
    
    # Constraint: SEND + MORE = MONEY
    # SEND = 1000*S + 100*E + 10*N + D
    # MORE = 1000*M + 100*O + 10*R + E  
    # MONEY = 10000*M + 1000*O + 100*N + 10*E + Y
    
    send = (1000 * letter_vars['S'] + 
            100 * letter_vars['E'] + 
            10 * letter_vars['N'] + 
            letter_vars['D'])
    
    more = (1000 * letter_vars['M'] + 
            100 * letter_vars['O'] + 
            10 * letter_vars['R'] + 
            letter_vars['E'])
    
    money = (10000 * letter_vars['M'] + 
             1000 * letter_vars['O'] + 
             100 * letter_vars['N'] + 
             10 * letter_vars['E'] + 
             letter_vars['Y'])
    
    model.Add(send + more == money)
    
    # Create a solver and solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("Solution found:")
        solution = {}
        for letter in letters:
            value = solver.Value(letter_vars[letter])
            solution[letter] = value
            print(f"{letter} = {value}")
        
        # Calculate and display the values
        send_value = (1000 * solution['S'] + 
                     100 * solution['E'] + 
                     10 * solution['N'] + 
                     solution['D'])
        
        more_value = (1000 * solution['M'] + 
                     100 * solution['O'] + 
                     10 * solution['R'] + 
                     solution['E'])
        
        money_value = (10000 * solution['M'] + 
                      1000 * solution['O'] + 
                      100 * solution['N'] + 
                      10 * solution['E'] + 
                      solution['Y'])
        
        print(f"\nSEND = {send_value}")
        print(f"MORE = {more_value}")
        print(f"MONEY = {money_value}")
        print(f"\nVerification: {send_value} + {more_value} = {send_value + more_value} == {money_value}")
        
        if send_value + more_value == money_value:
            print("✓ Solution is correct!")
        else:
            print("✗ Solution is incorrect!")
            
    else:
        print("No solution found!")

if __name__ == "__main__":
    solve_send_more_money()
