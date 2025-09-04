

## Constraint Programming Approach

To solve the updated problem with additional constraints, we need some more variables and constraints.

For each driver `d`, we need to know their start and end times of working hours. We cannot use the first departure and last arrival of trips assigned to them because of some reasons:
- The clock-on and clock-off times. This makes the start time can be earlier than the first departure, and the end time can be later than the last arrival.
- The breaks. We cannot sure the break is happened between which trips, but the break time must between 3 hours after the start and before 6 hours of continuous work. Thus, the start and end times cannot be simply calculated from the trips assigned to the driver.

Based on these reasons, we need to model the driver's shift span. 

The idea for break variables is inspired from the binpacking problem. We can think of the trips assigned to a driver as intervals in a bin (from 3 to 6 hours). The break is another interval that must fit in the bin without overlapping with the other intervals (trips)The implementation for this can be found [here](src/solve_cp_minmax_optimized.py).

### New Constants

* $C_{on} = 15$: The required clock-on buffer time in minutes before a driver's first trip.
* $C_{off} = 15$: The required clock-off buffer time in minutes after a driver's last trip.
* $T_{B_{start}} = 180$: The earliest a break can start after a shift begins (3 hours).
* $T_{B_{end}} = 360$: The latest a break must be completed after a shift begins (6 hours).
* $T_{B_{dur}} = 60$: The fixed duration of the mandatory break.
* $T_{max} = 2880$: The end of the planning horizon in minutes (48 hours).

For each trip $t \in T$:
* $D_t$: The scheduled departure time of trip $t$.
* $R_t$: The scheduled arrival time of trip $t$.

### New Variables

To model the driver shifts and breaks, we introduce the following variables for each driver $d \in D$.

* **Decision Variables:**
    * $A_{t,d} \in \{0, 1\}$: A binary variable that is 1 if trip $t$ is assigned to driver $d$, and 0 otherwise.
    * $u^D_d \in \{0, 1\}$: A binary variable that is 1 if driver $d$ is assigned at least one trip, and 0 otherwise. This is linked by the constraint $u^D_d = 1 \iff \sum_{t \in T} A_{t,d} \ge 1$.

* **Shift Span Variables:**
    * $S_d \in [0, T_{max}]$: An integer variable representing the start time of driver $d$'s shift.
    * $E_d \in [0, T_{max}]$: An integer variable representing the end time of driver $d$'s shift.

* **Interval Variables:**
    * $I_{t,d}$: An optional interval variable with start time $D_t$ and end time $R_t$. This interval is present if and only if trip $t$ is assigned to driver $d$ (i.e., if $A_{t,d} = 1$).
    * $B_d$: An optional interval variable of fixed length $T_{B_{dur}}$. This interval is present if and only if driver $d$ is used (i.e., if $u^D_d = 1$). Let its start time be denoted by $b_{start,d}$.


### New Constraints
#### Driver Shift Span

The start time ($S_d$) and end time ($E_d$) of a driver's shift must encompass all assigned trips, including the clock-on and clock-off buffers. These conditional constraints ensure that if a trip is assigned to a driver, their shift is adjusted accordingly.

$$A_{t,d} = 1 \implies S_d \le D_t - C_{on} \quad \forall t \in T, \forall d \in D$$

$$A_{t,d} = 1 \implies E_d \ge R_t + C_{off} \quad \forall t \in T, \forall d \in D$$

The solver will find the tightest possible window $[S_d, E_d]$ that satisfies these constraints for all trips assigned to driver $d$.

####  Break Placement

If a driver is assigned any trips, they must take a mandatory break. The break interval, $B_d$, must be scheduled within a specific window relative to the start of their shift.

$$u^D_d = 1 \implies S_d + T_{B_{start}} \le \text{startOf}(B_d)$$

$$u^D_d = 1 \implies \text{endOf}(B_d) \le S_d + T_{B_{end}}$$

Since $\text{endOf}(B_d) = \text{startOf}(B_d) + T_{B_{dur}}$, the second constraint can also be written as:
$$u^D_d = 1 \implies \text{startOf}(B_d) + T_{B_{dur}} \le S_d + T_{B_{end}}$$

#### Non-Overlapping Activities

Considering the break as an additional interval that must not overlap with any trips assigned to the driver, we need to ensure that the break interval also does not overlap with any trip intervals. This is enforced using a global `NoOverlap` constraint on the set of all interval variables associated with that driver.

$$\text{NoOverlap}\Big( \{B_d\} \cup \{ I_{t,d} \mid t \in T \} \Big) \quad \forall d \in D$$

This single constraint ensures that for a given driver $d$, the break interval $B_d$ (if present) and all trip intervals $I_{t,d}$ (for which $A_{t,d}=1$) are mutually disjoint in time.



## Mixed-Integer Linear Programming Approach


Constraint Programming (CP): Is a declarative paradigm. You describe the properties of a valid solution using high-level, often global, constraints (e.g., NoOverlap, AllDifferent). The CP solver uses specialized algorithms (propagators) for these constraints to prune the search space efficiently. It excels at complex scheduling and sequencing problems.

(Mixed-Integer) Linear Programming (MILP): Is a prescriptive paradigm. You must express your entire problem using only linear equations and inequalities (ax+by≤c). Complex logical conditions, like "either-or" or non-overlapping requirements, must be manually converted into a linear form, typically using auxiliary binary variables and the "Big-M" method.

--- 

The idea for break constraints is:
**For all trips assigned to a driver, the trip must either occur entirely before the break or entirely after the break.**

### New Variables

The other variables (`A[t,d]`, `uD[d]`, `Sd`, `Ed`) are the same as in the CP model. However to represent the break constraints, we need the additional variables.
* $b_{start,d}$: The start time of the break for driver $d$.
* $Z_{d,t}$: A binary variable that is 1 if trip $t$ occurs before the break for driver $d$, and 0 otherwise. 

* **Reminder**: $R_t$ is the scheduled arrival time of trip $t$, $T_{B_{dur}}$ is the fixed duration of the mandatory break, and $D_t$ is the scheduled departure time of trip $t$.

### New Constraints

#### 1. Shift Span Constraints

Instead of using logical implication (if-then), use linear inequalities with Big-M standard linearization trick to enforce the same conditions.

    $$
    S_d \le (D_t - C_{on}) + M \cdot (1 - A_{t,d})
    $$
    $$
    E_d \ge (R_t + C_{off}) - M \cdot (1 - A_{t,d})
    $$

#### 2. Non-Overlapping Trips

Creates pairwise constraints for every possible conflicting pair of trips. For every pair of trips $(t_1, t_2)$ that overlap in time:

    $$
    A_{t_1, d} + A_{t_2, d} \le 1 \quad \forall d \in D
    $$

The CP model's `NoOverlap` is a "global" constraint that considers all trips assigned to a driver simultaneously. The MILP model must decompose this single logical rule into a potentially huge number of simple pairwise constraints ($O(T^2)$ per driver). 

#### 3. Break Placement and Non-Overlap with Trips



Manually express the non-overlap condition for the break with *every single trip* using a disjunctive ("either-or") constraint, which is then linearized with the auxiliary variable `trip_before_break` and Big-M.
For each driver $d$ and trip $t$:

    $$
    \text{IF } A_{t,d} = 1 \text{ THEN } \Big( (R_t \le b_{start,d}) \lor (b_{start,d} + T_{B_{dur}} \le D_t) \Big)
    $$

This logical statement is linearized into the following two constraints using the binary variable $Z_{d,t}$ (which is `trip_before_break[d,t]` in your code):

    $$
    R_t \le b_{start,d} + M \cdot (1 - Z_{d,t}) + M \cdot (1 - A_{t,d})
    $$   
    $$
    b_{start,d} + T_{B_{dur}} \le D_t + M \cdot Z_{d,t} + M \cdot (1 - A_{t,d})
    $$

This is the difference that most clearly illustrates the power of CP. By treating the break as just another "interval", it fits naturally into the global `NoOverlap` constraint. The MILP model has to do a lot of works with numberical relaxations and auxiliary variables

We need a new binary variable `trip_before_break` for *every potential combination of driver and trip* just to decide if that trip occurs before or after the break. 
- If `trip_before_break[d, t] is 1`, the first linear inequality is relaxed by Big-M, forcing the break to end before the trip starts. 
- If `trip_before_break[d, t] is 0`, the second is relaxed, forcing the trip to end before the break starts. 

This is a powerful but cumbersome technique that significantly increases the number of variables and constraints in the model.


