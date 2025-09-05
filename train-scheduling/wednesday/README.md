## Just more trips to schedule, my solution is still working fine!

For more realistic scheduling, I have added the following constraints:
- Drivers start their work no earlier than 5:00 AM.
- Drivers end must be after their break.

These 2 constraints are easy to implement and do not require new variables. The implementation can be found [here](src/solve_cp_minmax_optimized.py).