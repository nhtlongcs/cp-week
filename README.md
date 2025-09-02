# CP Training Week

This repository contains my implementations and solutions for problems covered during Constraint Programming (CP) training week. The goal is to understand and practice different optimization approaches including OR-Tools constraint programming and linear programming with Gurobi.

## About the implementations

- **OR-Tools**: Google's optimization tools for constraint programming
- **Gurobi**: Commercial optimization solver for linear/integer programming
- **Python**: Primary programming language
- **UV Package Manager**: Dependency management and environment setup

## Requirements

Install uv based on [this instruction](https://docs.astral.sh/uv/getting-started/installation/)

```bash
cd <your_project_directory>
uv sync
cd <project_path>
uv run solve_<method>.py
```

## Problems List

### Warm-up Problems

<!-- hide/unhide -->

<details>
<summary>SEND MORE MONEY</summary>
This is a cryptarithmetic puzzle where each letter represents a unique digit.

The goal is to find the digit for each letter such that the equation is satisfied.

This is a classic cryptarithmetic puzzle where each letter represents a unique digit from 0-9. The goal is to find the digit assignment that makes the arithmetic equation valid.

```
  SEND
+ MORE
------
 MONEY
```

The detailed problem [here](/01_money/problem.md).

Both OR-Tools and Gurobi can be used to solve this problem. The key difference is in CP modeling, we have the "AllDifferent" constraint to ensure all letters are assigned different digits. In Linear Programming (LP), we need to model the uniqueness constraint explicitly using sum of the binary variables equal to 1.

Read more about the CP implementation details [here](/01_money/solve_cp.py).

Read more about the ILP implementation details [here](/01_money/solve_ilp.py).

</details>