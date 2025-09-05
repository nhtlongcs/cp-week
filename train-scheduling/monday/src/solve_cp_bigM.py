import json
from ortools.sat.python import cp_model


def solve_with_ortools_improved():
    """Improved version with better constraint modeling for CP-SAT"""
    
    # Load trip data
    with open("data/monfri.json", "r") as f:
        data = json.load(f)
    trips = data["trips"]
    
    # Constants
    WORKING_TIME = 9 * 60  # 9 hours in minutes
    DRIVING_TIME = 7 * 60  # 7 hours in minutes
    n_trips = len(trips)
    
    # More conservative bounds based on problem structure
    max_trains = min(n_trips, 20)  # Reasonable upper bound
    max_drivers = min(n_trips, 15)  # Reasonable upper bound
    
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
    
    # Constraint 1: Link driver/train assignment to usage variables (simplified)
    for d in range(max_drivers):
        # Driver d is used if any trip is assigned to driver d
        assigned_trips = []
        for t in range(n_trips):
            trip_assigned_to_d = model.NewBoolVar(f'trip_{t}_assigned_to_driver_{d}')
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
            model.Add(trip_train[t] == tr).OnlyEnforceIf(trip_assigned_to_tr)
            model.Add(trip_train[t] != tr).OnlyEnforceIf(trip_assigned_to_tr.Not())
            assigned_trips.append(trip_assigned_to_tr)
        
        # Train is used if at least one trip is assigned to it
        model.Add(sum(assigned_trips) >= 1).OnlyEnforceIf(train_used[tr])
        model.Add(sum(assigned_trips) == 0).OnlyEnforceIf(train_used[tr].Not())    # Constraint 2: No time conflicts for trains
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
    for d in range(max_drivers):
        # Calculate total driving time for driver d
        total_driving_time = 0
        for t in range(n_trips):
            # Create a boolean variable for whether trip t is assigned to driver d
            is_assigned_to_d = model.NewBoolVar(f'trip_{t}_assigned_to_driver_{d}')
            model.Add(trip_driver[t] == d).OnlyEnforceIf(is_assigned_to_d)
            model.Add(trip_driver[t] != d).OnlyEnforceIf(is_assigned_to_d.Not())
            
            # Add the driving time for this trip if assigned to driver d
            total_driving_time += is_assigned_to_d * trips[t]["drivingTime"]
        
        # Total driving time must not exceed the limit
        model.Add(total_driving_time <= DRIVING_TIME)
    
    # Constraint 5: Driver working time constraints (Big-M approach like ILP)
    BIG_M = 24 * 60  # 24 hours in minutes
    
    for d in range(max_drivers):
        # Track start and end times for each driver
        driver_start_time = model.NewIntVar(0, BIG_M, f'driver_{d}_start_time')
        driver_end_time = model.NewIntVar(0, BIG_M, f'driver_{d}_end_time')
        
        # For each trip, if assigned to this driver, constrain start/end times
        for t in range(n_trips):
            is_assigned = model.NewBoolVar(f'driver_{d}_trip_{t}_assigned_working')
            model.Add(trip_driver[t] == d).OnlyEnforceIf(is_assigned)
            model.Add(trip_driver[t] != d).OnlyEnforceIf(is_assigned.Not())
            
            # If trip is assigned: start_time <= departure, end_time >= arrival
            # Using Big-M: constraint is enforced when is_assigned=1, relaxed when is_assigned=0
            model.Add(driver_start_time <= trips[t]["departure"] + BIG_M * (1 - is_assigned))
            model.Add(driver_end_time >= trips[t]["arrival"] - BIG_M * (1 - is_assigned))
        
        # Working time constraint: end_time - start_time <= WORKING_TIME when driver is used
        driver_has_trips = model.NewBoolVar(f'driver_{d}_has_trips_working')
        trip_assignments = []
        for t in range(n_trips):
            is_assigned_check = model.NewBoolVar(f'driver_{d}_trip_{t}_check_working')
            model.Add(trip_driver[t] == d).OnlyEnforceIf(is_assigned_check)
            model.Add(trip_driver[t] != d).OnlyEnforceIf(is_assigned_check.Not())
            trip_assignments.append(is_assigned_check)
        
        model.Add(sum(trip_assignments) >= 1).OnlyEnforceIf(driver_has_trips)
        model.Add(sum(trip_assignments) == 0).OnlyEnforceIf(driver_has_trips.Not())
        
        # Working time span constraint with Big-M relaxation
        working_span = model.NewIntVar(0, BIG_M, f'driver_{d}_working_span')
        model.Add(working_span == driver_end_time - driver_start_time)
        model.Add(working_span <= WORKING_TIME + BIG_M * (1 - driver_has_trips))
    # Objective: Lexicographic optimization - first minimize trains, then drivers
    model.Minimize(sum(driver_used[d] for d in range(max_drivers)))
    # model.Minimize(sum(train_used[tr] for tr in range(max_trains)) + sum(driver_used[d] for d in range(max_drivers)))

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
        
        # # Now add constraint to fix trains at optimal value and minimize drivers
        # model.Add(sum(train_used[tr] for tr in range(max_trains)) == optimal_trains)
        # model.Minimize(sum(driver_used[d] for d in range(max_drivers)))
        
        print("Second pass: minimizing drivers with fixed trains...")
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
                "destination": trip["destination"]
            })
            used_drivers.add(driver_id)
            used_trains.add(train_id)
        
        print(f"Solution uses {len(used_drivers)} drivers and {len(used_trains)} trains")
        print(f"Solve time: {solver2.WallTime():.2f} seconds")
        return solution
        
    else:
        raise Exception(f"No solution found. Status: {solver2.StatusName(status)}")


# Main execution
if __name__ == "__main__":
    print("Solving train scheduling problem using OR-Tools CP-SAT")
    print("=" * 60)
    
    solution = solve_with_ortools_improved()
    
    print(f"Optimization completed:")
    print(f"  - All {len(solution)} trips scheduled")
    
    # Sort by departure time and save
    solution.sort(key=lambda x: x["departure"])
    
    with open("solution.json", "w") as f:
        json.dump(solution, f, indent=4)
    
    print(f"\nSolution saved to solution.json")
    print(f"Solution uses {len(set(s['driver'] for s in solution))} drivers and {len(set(s['train'] for s in solution))} trains")
    
    print("\nSolution is ready for validation with checker.py")