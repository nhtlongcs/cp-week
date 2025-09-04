import json
from ortools.sat.python import cp_model

def solve_with_ortools_improved():
    # Load trip data
    with open("monfri.json", "r") as f:
        data = json.load(f)
    trips = data["trips"]
    
    # Constants
    WORKING_TIME = 9 * 60  # 9 hours in minutes
    DRIVING_TIME = 7 * 60  # 7 hours in minutes
    CLOCK_ON = 15
    CLOCK_OFF = 15
    BREAK_START = 3 * 60
    BREAK_END = 6 * 60
    BREAK_DURATION = 60
    END_OF_DAY = 24 * 60 * 2
    n_trips = len(trips)
    
    # More conservative bounds based on problem structure
    max_trains = min(n_trips, 30)  # Reasonable upper bound
    max_drivers = min(n_trips, 50)  # Reasonable upper bound
    
    print(f"Problem size: {n_trips} trips")
    print(f"Maximum resources: {max_drivers} drivers, {max_trains} trains")
    
    # Create the CP-SAT model
    model = cp_model.CpModel()
    
    # Decision variables: which driver and train is assigned to each trip
    trip_driver = {}
    trip_train = {}
    for t in range(n_trips):
        trip_driver[t] = model.NewIntVar(0, max_drivers - 1, f'trip_driver_{t}')
        trip_train[t] = model.NewIntVar(0, max_trains - 1, f'trip_train_{t}')
    
    # Binary variables for resource usage
    driver_used = {}
    train_used = {}
    for d in range(max_drivers):
        driver_used[d] = model.NewBoolVar(f'driver_used_{d}')
    for tr in range(max_trains):
        train_used[tr] = model.NewBoolVar(f'train_used_{tr}')
    
    print("Adding constraints...")
    
    # Constraint 1: Link driver/train assignment to usage variables 
    assigned_dr = {}
    assigned_tr = {}
    for d in range(max_drivers):
        # Driver d is used if any trip is assigned to driver d
        assigned_trips = []
        for t in range(n_trips):
            trip_assigned_to_d = model.NewBoolVar(f'trip_{t}_assigned_to_driver_{d}')
            assigned_dr[(t, d)] = trip_assigned_to_d
            model.Add(trip_driver[t] == d).OnlyEnforceIf(trip_assigned_to_d)
            model.Add(trip_driver[t] != d).OnlyEnforceIf(trip_assigned_to_d.Not())
            assigned_trips.append(trip_assigned_to_d)
        
        # Driver is used if at least one trip is assigned to it
        model.Add(sum(assigned_trips) >= 1).OnlyEnforceIf(driver_used[d])
        model.Add(sum(assigned_trips) == 0).OnlyEnforceIf(driver_used[d].Not())

    for tr in range(max_trains):
        # Train tr is used if any trip is assigned to train tr
        assigned_trips = []
        for t in range(n_trips):
            trip_assigned_to_tr = model.NewBoolVar(f'trip_{t}_assigned_to_train_{tr}')
            assigned_tr[(t, tr)] = trip_assigned_to_tr
            model.Add(trip_train[t] == tr).OnlyEnforceIf(trip_assigned_to_tr)
            model.Add(trip_train[t] != tr).OnlyEnforceIf(trip_assigned_to_tr.Not())
            assigned_trips.append(trip_assigned_to_tr)
        
        # Train is used if at least one trip is assigned to it
        model.Add(sum(assigned_trips) >= 1).OnlyEnforceIf(train_used[tr])
        model.Add(sum(assigned_trips) == 0).OnlyEnforceIf(train_used[tr].Not())    # Constraint 2: No time conflicts for trains
    
    # Constraint 2: No time conflicts for drivers
    for t1 in range(n_trips):
        for t2 in range(t1 + 1, n_trips):
            trip1, trip2 = trips[t1], trips[t2]
            # Check if trips overlap in time (corrected logic)
            # Trips overlap if NOT (one ends before the other starts)
            if not (trip1["arrival"] <= trip2["departure"] or trip2["arrival"] <= trip1["departure"]):
                # If trips overlap, they cannot use the same train
                model.Add(trip_train[t1] != trip_train[t2])

    # Constraint 3: No time conflicts for drivers
    for t1 in range(n_trips):
        for t2 in range(t1 + 1, n_trips):
            trip1, trip2 = trips[t1], trips[t2]
            # Check if trips overlap in time (corrected logic)
            # Trips overlap if NOT (one ends before the other starts)
            if not (trip1["arrival"] <= trip2["departure"] or trip2["arrival"] <= trip1["departure"]):
                # If trips overlap, they cannot use the same driver
                model.Add(trip_driver[t1] != trip_driver[t2])    # Constraint 4: Driver driving time constraints (simplified)

    # Constraint 4: Total Driving Time < DRIVING_TIME
    for d in range(max_drivers):
        # Calculate total driving time for driver d
        total_driving_time = 0
        for t in range(n_trips):
            total_driving_time += assigned_dr[(t, d)] * trips[t]["drivingTime"]
        
        model.Add(total_driving_time <= DRIVING_TIME)
    
    # Constraint 5: Driver working time span constraints 

    driver_start_time_vars = []
    driver_end_time_vars = []
    for d in range(max_drivers):
        assigned_vars = [assigned_dr[(t, d)] for t in range(n_trips)]
        driver_has_trips = model.NewBoolVar(f'driver_{d}_has_trips')
        model.Add(sum(assigned_vars) >= 1).OnlyEnforceIf(driver_has_trips)
        model.Add(sum(assigned_vars) == 0).OnlyEnforceIf(driver_has_trips.Not())

        # Find earliest departure and latest arrival for assigned trips
        driver_start_time = model.NewIntVar(0, 24*60*2, f'driver_{d}_start_time')
        driver_end_time = model.NewIntVar(0, 24*60*2, f'driver_{d}_end_time')
        driver_start_time_vars.append(driver_start_time)
        driver_end_time_vars.append(driver_end_time)

        # For each trip, if assigned, update start/end
        for t in range(n_trips):
            is_assigned = assigned_dr[(t, d)]
            model.Add(driver_start_time <= trips[t]["departure"] - CLOCK_ON).OnlyEnforceIf(is_assigned)
            model.Add(driver_end_time >= trips[t]["arrival"] + CLOCK_OFF).OnlyEnforceIf(is_assigned)

        # Working span
        working_span = model.NewIntVar(0, 24*60, f'driver_{d}_working_span')
        model.Add(driver_end_time >= driver_start_time).OnlyEnforceIf(driver_has_trips)
        model.Add(working_span == driver_end_time - driver_start_time).OnlyEnforceIf(driver_has_trips)
        model.Add(working_span == 0).OnlyEnforceIf(driver_has_trips.Not())
        model.Add(working_span <= WORKING_TIME).OnlyEnforceIf(driver_has_trips)

        # Trip intervals for assigned trips
        trip_intervals = []
        for t in range(n_trips):
            is_assigned = assigned_dr[(t, d)]
            start = trips[t]["departure"]
            duration = trips[t]["arrival"] - trips[t]["departure"]
            interval = model.NewOptionalIntervalVar(start, duration, trips[t]["arrival"], is_assigned, f'driver_{d}_trip_{t}_interval')
            trip_intervals.append(interval)

        # Break interval: must be present if driver has trips, and between 3rd and 6th hour after start
        break_start = model.NewIntVar(0, 24*60*2, f'driver_{d}_break_start')
        break_interval = model.NewOptionalIntervalVar(
            break_start,
            BREAK_DURATION,
            break_start + BREAK_DURATION,
            driver_has_trips,
            f'driver_{d}_break_interval')
        # Break must be within [start + BREAK_START, start + BREAK_END] if driver has trips
        model.Add(break_start >= driver_start_time + BREAK_START).OnlyEnforceIf(driver_has_trips)
        model.Add(break_start + BREAK_DURATION <= driver_start_time + BREAK_END).OnlyEnforceIf(driver_has_trips)
        # Break must not overlap with any trip interval
        model.AddNoOverlap([break_interval] + trip_intervals)


    # Objective: Lexicographic optimization - first minimize trains, then drivers
    # First solve for minimum trains
    print("First pass: minimizing trains...")
    model.Minimize(sum(train_used[tr] for tr in range(max_trains)))
    # model.Minimize(sum(train_used[tr] for tr in range(max_trains)) + sum(driver_used[d] for d in range(max_drivers)))
    # model.Minimize(sum(driver_used[d] for d in range(max_drivers)))

    # Create solver and set time limit
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 300.0  # 5 minutes time limit
    solver.parameters.log_search_progress = True
    
    # Solve the model
    status = solver.Solve(model)
    
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        # Get the optimal number of trains
        optimal_trains = sum(solver.Value(train_used[tr]) for tr in range(max_trains))
        print(f"Optimal number of trains: {optimal_trains}")
        
        # # # Now add constraint to fix trains at optimal value and minimize drivers
        print("Second pass: minimizing drivers with fixed trains...")
        model.Add(sum(train_used[tr] for tr in range(max_trains)) == optimal_trains)
        model.Minimize(sum(driver_used[d] for d in range(max_drivers)))
        
        solver2 = cp_model.CpSolver()
        solver2.parameters.max_time_in_seconds = 300.0
        solver2.parameters.log_search_progress = True
        status = solver2.Solve(model)
    
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        if status == cp_model.OPTIMAL:
            print("Optimal solution found!")
        else:
            print("Feasible solution found!")
        
        # Extract solution
        solution = []
        used_drivers = set()
        used_trains = set()
        
        driver_times = []
        for d in range(max_drivers):
            driver_times.append({
                "driver": f"D{d + 1}",
                "start": solver2.Value(driver_start_time_vars[d]),
                "end": solver2.Value(driver_end_time_vars[d])
            })
        for t in range(n_trips):
            driver_id = solver2.Value(trip_driver[t])
            train_id = solver2.Value(trip_train[t])
            trip = trips[t]
            solution.append({
                "nr": trip["nr"],
                "train": f"T{train_id + 1}",
                "driver": f"D{driver_id + 1}",
                "departure": trip["departure"],
                "arrival": trip["arrival"],
                "destination": trip["destination"],
            })
            used_drivers.add(driver_id)
            used_trains.add(train_id)

        print(f"Solution uses {len(used_drivers)} drivers and {len(used_trains)} trains")
        print(f"Solve time: {solver2.WallTime():.2f} seconds")
        return solution, driver_times
        
    else:
        raise Exception(f"No solution found. Status: {solver.StatusName(status)}")


# Main execution
if __name__ == "__main__":
    print("Solving train scheduling problem using OR-Tools CP-SAT")
    print("=" * 60)
    
    solution, driver_times = solve_with_ortools_improved()
    
    print(f"Optimization completed:")
    print(f"  - All {len(solution)} trips scheduled")
    
    # Sort by departure time and save
    solution.sort(key=lambda x: x["departure"])
    
    with open("solution.json", "w") as f:
        json.dump({"trips": solution, "drivers": driver_times}, f, indent=4)
    
    print(f"\nSolution saved to solution.json")
    print(f"Solution uses {len(set(s['driver'] for s in solution))} drivers and {len(set(s['train'] for s in solution))} trains")
    
    print("\nSolution is ready for validation with checker.py")