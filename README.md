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

The detailed problem [here](/puzzles/01_money/problem.md).

Both OR-Tools and Gurobi can be used to solve this problem. The key difference is in CP modeling, we have the "AllDifferent" constraint to ensure all letters are assigned different digits. In Linear Programming (LP), we need to model the uniqueness constraint explicitly using sum of the binary variables equal to 1.

Read more about the CP implementation details [here](/puzzles/01_money/solve_cp.py).

Read more about the ILP implementation details [here](/puzzles/01_money/solve_ilp.py).

</details>

<details>
<summary>Sudoku</summary>
This is a classic Sudoku puzzle where the goal is to fill a 9x9 grid with digits so that each column, each row, and each of the nine 3x3 subgrids that compose the grid (also called "boxes") contains all of the digits from 1 to 9.

The detailed problem [here](/puzzles/02_sudoku/problem.md).

</details>


<details>
<summary>N-Queens</summary>
This is a classic N-Queens puzzle where the goal is to place N queens on an N x N chessboard so that no two queens threaten each other.

The detailed problem [here](/puzzles/03_n_queens/problem.md).

</details>

---

### Cork Railway Scheduling Problem

Every years, the challenge of the CP training week is changing. This year, we have a railway scheduling problem based on the real-world scenario of managing train and driver schedules for a railway company in Cork, Ireland.

There are three versions of the same scheduling problem with increasing complexity. You can find the detailed problem description of each version in their respective folders.
![Train Timeline](/assets/train_timeline_cobh_00h-12h.png)
1. **Basic Scheduling Problem**: Assign trips to drivers and trains while minimizing the number of drivers and trains used. [[Detailed Problem Description]](/train-scheduling/monday/monday.pdf) [[Simplified Problem Description]](/train-scheduling/monday/README.md) [[Solution]](/train-scheduling/monday/SOLUTION.md)
2. **Scheduling with Breaks**: Similar to the basic problem but includes mandatory breaks for drivers. [[Detailed Problem Description]](/train-scheduling/tuesday/tuesday.pdf) [[Simplified Problem Description]](/train-scheduling/tuesday/README.md) [[Solution]](/train-scheduling/tuesday/SOLUTION.md)
3. **With Higher Complexity**: Adds more trips that require more drivers and trains. [[Detailed Problem Description]](/train-scheduling/wednesday/wednesday.pdf) [[Solution]](/train-scheduling/wednesday/README.md)

---

### Hospital Capacity Management Problem

This problem involves managing hospital resources such as beds, doctors, and nurses to handle patient admissions while minimizing costs. The problem includes various constraints such as resource availability, patient types, and treatment requirements. The detailed problem description can be found in the [competition-page](https://ihtc2024.github.io/).

At the scope of the training week, I dont have time to implement the solution. However, I have a basic understanding of the problem and some ideas on how to approach it using CP and LP techniques.

A very detailed approach to solve this problem can be found in [Modelling Alternatives for the IHTC 2024 Competition - A Modelling Tutorial](/hospital-management/slide.pdf) - This is a tutorial presented by Dr. Helmut Simonis - The lecturer of the CP training week.

## Acknowledgements

- Dr. Helmut Simonis - For the excellent lectures and guidance during the CP training week.

## References
- Google OR-Tools Documentation 
- Gurobi Documentation