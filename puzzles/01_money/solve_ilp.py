import gurobipy as gp
from gurobipy import GRB

letters = ['S','E','N','D','M','O','R','Y']
digits = range(10)

m = gp.Model("SEND+MORE=MONEY")

# Binary vars: assign letter l to digit d
x = m.addVars(letters, digits, vtype=GRB.BINARY, name="x")

# Each letter gets exactly one digit
m.addConstrs((gp.quicksum(x[l,d] for d in digits) == 1 for l in letters), "letter_unique")

# Each digit assigned to at most one letter
m.addConstrs((gp.quicksum(x[l,d] for l in letters) <= 1 for d in digits), "digit_unique")

# Build integer vars for letters
val = {}
for l in letters:
    val[l] = m.addVar(vtype=GRB.INTEGER, lb=0, ub=9, name=l)
    m.addConstr(val[l] == gp.quicksum(d * x[l,d] for d in digits))

# Leading letters not zero
m.addConstr(val['S'] >= 1)
m.addConstr(val['M'] >= 1)

# SEND + MORE = MONEY
send = 1000*val['S'] + 100*val['E'] + 10*val['N'] + val['D']
more = 1000*val['M'] + 100*val['O'] + 10*val['R'] + val['E']
money = 10000*val['M'] + 1000*val['O'] + 100*val['N'] + 10*val['E'] + val['Y']
m.addConstr(send + more == money)

m.setObjective(0, GRB.MINIMIZE)
m.optimize()

if m.status == GRB.OPTIMAL:
    for l in letters:
        print(f"{l} = {int(val[l].X)}")
    print(f"SEND = {int(send.getValue())}")
    print(f"MORE = {int(more.getValue())}")
    print(f"MONEY = {int(money.getValue())}")
    print(f'{send.getValue()} + {more.getValue()} = {send.getValue() + more.getValue()} == {money.getValue()}')
