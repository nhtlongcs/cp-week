## 1. Problem Clarification

Based on the provided data and observations:

* Each **trip is a round trip**: it starts from **Cork Kent** and returns to **Cork Kent**.
* We **ignore infrastructure constraints** such as single/double track and intermediate stations for now.
* Each trip cost a certain amount of **driving time** (≤ duration).
* Each trip requires **one train** and **one driver**.
* A driver can operate multiple trips as long as working-time limits are not exceeded.
* Our focus is on a **single-day assignment**.

### Checker

To verify the solution, I have created a simple validation script [src/checker.py](src/checker.py) that checks the `solution.json` file. 

### Visualization

We have a timetable visualization in [src/viz/viz_timetable.py](src/viz/viz_timetable.py). We can visualize the schedule of trips and some statistics. 

To draw the solution simply, we can use [src/viz/draw.py](src/viz/draw.py) to visualize the assignment of trips to trains and drivers.

We also have a better visualization tool to visualize the schedule in [visualization/]/train-scheduling/visualization/). However, the visualization does not support this format yet (because it implements for the more complex problems which require drivers information). So you can convert the solution to a visualization format using [src/viz/convert_to_viz.py](src/viz/convert_to_viz.py).

## 2. Estimating Minimum Resources

A simple way to estimate the minimum number of trains and drivers:

* **Lower bound**: count the **maximum number of overlapping trips**.

  * If at some point in time **K trips overlap**, then at least **K trains** and **K drivers** are needed.
* **Upper bound**: equal to the total number of trips (worst case, each trip uses a separate train and driver).

So the required resources are between:

```
max overlap  ≤  required trains/drivers  ≤  number of trips
```

## 3. Simple Assignment (Naive Algorithm)

We implement a **greedy allocation method**, which trying to **reuse the earliest finishing train/driver**. It guarantees that the number of trains/drivers used is **close to the minimum**, though not always optimal. Check out the implementation [here](src/solve_naive.py).

### Algorithm Idea
* Sort trips by **departure time**.
* Maintain two min-heaps:
  * **trains**: available trains, keyed by their next available time.
  * **drivers**: available drivers, keyed by their next available time.
* For each trip:
  1. Check if any train is free before the trip departs.

     * If yes, reuse it.
     * Otherwise, assign a new train.
  2. Do the same for drivers.
  3. After the trip finishes, mark the train and driver as available at the trip’s **arrival time**.
* Record the assignment of `(train, driver)` to each trip.

This ensures:

* **Reuse whenever possible** → reduces total number of trains and drivers.
* **Greedy assignment** works well because trips are sorted by start time, so the earliest finishing resource is always considered first.

## 4. Strict Heuristic for Working/Driving Time Limits
While the above method works well for trains, we need to be more careful with drivers due to break requirements. The goal is to assign each trip to a driver and a train, while respecting:

- Drivers cannot work more than 9 hours total per day.
- Drivers cannot drive more than 7 hours total per day.

So in this approach, just carefully track each driver's total working time and driving time, and ensure that no driver exceeds these limits when assigning trips. Check out the implementation [here](src/solve_greedy.py).

## 5. Constraint Programming (CP) Approach

We can also formulate the problem as a **Constraint Programming (CP)** problem, which allows us to express the constraints and objectives more naturally. The full implementation is in [src/solve_cp.py](src/solve_cp_minmax.py).

### Sets and Parameters

* $T = \{1, \dots, n\}$: set of trips.

* $D = \{1, \dots, D_{\max}\}$: set of possible drivers.

* $R = \{1, \dots, R_{\max}\}$: set of possible trains.

* For each trip $t \in T$:

  * $dep_t$: departure time from Cork Kent.
  * $arr_t$: arrival time back at Cork Kent.
  * $dur_t = arr_t - dep_t$: duration of trip.
  * $drv_t$: driving time (a subset of duration).

* Working time limit: $W = 540$ minutes (9 hours).

* Driving time limit: $L = 420$ minutes (7 hours).

---

### Decision Variables

* $x_{td} \in \{0,1\}$: 1 if trip $t$ is assigned to driver $d$, 0 otherwise.

* $y_{tr} \in \{0,1\}$: 1 if trip $t$ is assigned to train $r$, 0 otherwise.

* $u_d \in \{0,1\}$: 1 if driver $d$ is used.

* $v_r \in \{0,1\}$: 1 if train $r$ is used.

* $s_d$: start time of driver $d$’s shift.

* $e_d$: end time of driver $d$’s shift.

* $w_d = e_d - s_d$: working span (minutes).

---

### Constraints

#### 1. Trip assignment

Every trip must be assigned to exactly one driver and one train, so the sum of assignments for each trip must be 1:

$$
\sum_{d \in D} x_{td} = 1 \quad \forall t \in T
$$

$$
\sum_{r \in R} y_{tr} = 1 \quad \forall t \in T
$$

---

#### 2. Resource usage linking

In order to count the number of drivers and trains used, we cannot simply sum the assignments. Instead, we introduce binary variables $u_d$ and $v_r$ to indicate if a driver or train is used, and by link them to assignments, we can calculate the total number drivers/trains used.

A driver is marked as used if any trip is assigned to them:

$$
u_d = 1 \iff \sum_{t \in T} x_{td} \geq 1 \quad \forall d \in D
$$

Similarly for trains:

$$
v_r = 1 \iff \sum_{t \in T} y_{tr} \geq 1 \quad \forall r \in R
$$

---

#### 3. No overlapping trips for the same train / driver

Two trips cannot use the same train if they overlap in time. So if trips $t_1$ and $t_2$ overlap, the sum of their assignments to the same train must be at most 1.

$$
\text{Trips } t_1, t_2 \text{ overlap if } \neg(arr_{t1} \leq dep_{t2} \ \vee \ arr_{t2} \leq dep_{t1})
$$

If overlap holds:

$$
y_{t_1r} + y_{t_2r} \leq 1 \quad \forall r \in R
$$

Similarly for drivers if trips overlap:

$$
x_{t_1d} + x_{t_2d} \leq 1 \quad \forall d \in D
$$

---

#### 4. Driver driving time constraint

The driving time is different from total working time. For each trip, the driving time $drv_t$ is given, and the driving time is smaller than total duration $dur_t$.

The total driving time per driver must respect the limit:

$$
\sum_{t \in T} drv_t \cdot x_{td} \leq L \quad \forall d \in D
$$

---

#### 5. Driver working span constraint

In this case, we define working span as the difference between the earliest departure and latest arrival of trips assigned to the driver. More simple than using additional variables for start and end times.

Let

$$
s_d = \min_{t \in T} \{ dep_t \cdot x_{td} \}, \quad
e_d = \max_{t \in T} \{ arr_t \cdot x_{td} \}
$$

Then:

$$
w_d = e_d - s_d \leq W \quad \forall d \in D
$$

If driver is unused, then:

$$
u_d = 0 \implies w_d = 0
$$

However, there is one more way to represent the working span constraint without using min/max functions. That is uses a **Big-M linear relaxation** to model start and end:

For each trip $t$ and driver $d$:

$$
s_d \leq dep_t + M(1 - x_{td})
$$

$$
e_d \geq arr_t - M(1 - x_{td})
$$

Then defines:

$$
w_d = e_d - s_d \leq W + M (1 - u_d)
$$

This ensures the working span constraint only applies if the driver is used ( if $u_d = 1$ then $w_d \leq W$, else if $u_d = 0$ then $w_d \leq W + M$ which is always true).

The first implementation is tighter and more structured (stronger constraints, better pruning), while the second is more flexible but weaker due to Big-M relaxation and a simpler objective. But this concept can be useful in other problems. Check out the implementation [here](src/solve_cp_bigM.py).


### Objective

There are multiple way to define the objective. E.g., minimize total number of trains and drivers used:
$$
\min \sum_{r \in R} v_r + \sum_{d \in D} u_d
$$

Or in the implementation, we use the lexicographic optimization in two passes:

1. **First stage**: minimize number of trains.

$$
\min \sum_{r \in R} v_r
$$

2. **Second stage**: fix optimal number of trains and minimize number of drivers.

$$
\min \sum_{d \in D} u_d
$$

All objectives are leading to the same result in this case.

## 6. Integer Linear Programming (ILP) Approach


The full implementation is in [src/solve_ilp.py](src/solve_ilp.py).

We can also formulate the problem as a **Mixed Integer Linear Program (MILP)**, which is similar to CP but uses linear inequalities instead of logical constraints.

However, some constraints are more challenging to express linearly. So the modelling choices can affect the strength of the formulation.

### **Sets and Parameters**

* $T = \{1, \dots, n\}$: set of trips.
* $D = \{1, \dots, n\}$: potential drivers (upper bound = one driver per trip).
* $R = \{1, \dots, n\}$: potential trains (upper bound = one train per trip).

For each trip $t \in T$:

* $\text{dep}_t$: departure time.
* $\text{arr}_t$: arrival time.
* $\text{dur}_t = \text{arr}_t - \text{dep}_t$: trip duration.
* $\text{drv}_t$: required driving time (≤ duration).

**Constants:**

* $W = 540$ minutes (max working time = 9h).
* $L = 420$ minutes (max driving time = 7h).
* $M = 1440$ minutes (big-M = 24 hours).


### **Decision Variables**

* $x_{t,d,r} \in \{0,1\}$:
  $=1$ if trip $t$ is assigned to driver $d$ and train $r$.

* $u_d \in \{0,1\}$:
  $=1$ if driver $d$ is used.

* $v_r \in \{0,1\}$:
  $=1$ if train $r$ is used.

* $s_d \in [0, M]$: earliest departure time among trips assigned to driver $d$.

* $e_d \in [0, M]$: latest arrival time among trips assigned to driver $d$.


### **Constraints**

#### 1. Trip Coverage

Each trip must be assigned exactly once:

$$
\sum_{d \in D} \sum_{r \in R} x_{t,d,r} = 1, 
\quad \forall t \in T
$$


#### 2. Resource Usage

A driver is marked as used if assigned to any trip:

$$
\sum_{t \in T} \sum_{r \in R} x_{t,d,r} \leq n \cdot u_d, 
\quad \forall d \in D
$$

$$
u_d \leq \sum_{t \in T} \sum_{r \in R} x_{t,d,r}, 
\quad \forall d \in D
$$

A train is marked as used if assigned to any trip:

$$
\sum_{t \in T} \sum_{d \in D} x_{t,d,r} \leq n \cdot v_r, 
\quad \forall r \in R
$$

$$
v_r \leq \sum_{t \in T} \sum_{d \in D} x_{t,d,r}, 
\quad \forall r \in R
$$


#### 3. Train Non-Overlap

A train cannot be assigned to overlapping trips:
If $[\text{dep}_{t_1}, \text{arr}_{t_1}]$ and $[\text{dep}_{t_2}, \text{arr}_{t_2}]$ overlap, then:

$$
\sum_{d \in D} x_{t_1,d,r} + \sum_{d \in D} x_{t_2,d,r} \leq 1,
\quad \forall r \in R
$$


Similarly for drivers:

$$
\sum_{r \in R} x_{t_1,d,r} + \sum_{r \in R} x_{t_2,d,r} \leq 1, 
\quad \forall d \in D
$$
#### 4. Driver Working Span

Define working start/end for each driver. So in this case, we use the Big-M linear relaxation to model start and end. Instead of using min/max functions which are non-linear.

If trip $t$ is assigned to driver $d$:

$$
s_d \leq \text{dep}_t + M (1 - \sum_{r \in R} x_{t,d,r}), 
$$

$$
e_d \geq \text{arr}_t - M (1 - \sum_{r \in R} x_{t,d,r})
$$

Total span ≤ working time:

$$
e_d - s_d \leq W + M (1 - u_d), 
\quad \forall d \in D
$$

#### 5. Driver Driving Time Limit

Total driving time ≤ 7 hours:

$$
\sum_{t \in T} \sum_{r \in R} x_{t,d,r} \cdot \text{drv}_t \leq L, 
\quad \forall d \in D
$$


## **Objective Function**

Primary objective is the same as CP: minimize total number of drivers and trains used.

$$
\min \sum_{d \in D} u_d + \sum_{r \in R} v_r
$$

Thanks for reading this far! 