import json
import gurobipy as gp
from gurobipy import GRB
from utils import load_wsl_lic

LICENSE_DICT = load_wsl_lic('./gurobi.lic')

env = gp.Env(params=LICENSE_DICT)
env.setParam('OutputFlag', 1) # Enable Gurobi output
env.setParam('TimeLimit', 300)  # 5 minutes time limit
    
env.start()


def solve_with_gurobi():
    """Solve train scheduling problem using only Gurobi optimization"""
    
    # Load trip data
    with open("monfri.json", "r") as f:
        data = json.load(f)
    trips = data["trips"]
    
    # Constants
    WORKING_TIME = 9 * 60  # 9 hours in minutes
    DRIVING_TIME = 7 * 60  # 7 hours in minutes
    n_trips = len(trips)
    
    # Estimate reasonable upper bounds for drivers and trains
    max_drivers = n_trips  # Upper bound: one driver per trip
    max_trains = n_trips   # Upper bound: one train per trip
    
    print(f"Problem size: {n_trips} trips")
    print(f"Maximum resources: {max_drivers} drivers, {max_trains} trains")
    
    # Create optimization model
    model = gp.Model("train_scheduling", env=env)
    # Decision variables
    # x[t,d,tr] = 1 if trip t is assigned to driver d and train tr
    x = model.addVars(n_trips, max_drivers, max_trains, vtype=GRB.BINARY, name="x")
    
    # Binary variables for resource usage
    driver_used = model.addVars(max_drivers, vtype=GRB.BINARY, name="driver_used")
    train_used = model.addVars(max_trains, vtype=GRB.BINARY, name="train_used")
    
    # Additional variables for working time constraints
    # For each driver, track the earliest start time and latest end time
    driver_start_time = model.addVars(max_drivers, vtype=GRB.CONTINUOUS, name="driver_start_time")
    driver_end_time = model.addVars(max_drivers, vtype=GRB.CONTINUOUS, name="driver_end_time")
    
    # Big M constant for linearization
    BIG_M = 24 * 60  # 24 hours in minutes (larger than any possible time difference)
    
    print("Adding constraints...")
    
    # Constraint 1: Each trip must be assigned to exactly one driver-train pair
    for t in range(n_trips):
        model.addConstr(
            gp.quicksum(x[t, d, tr] for d in range(max_drivers) for tr in range(max_trains)) == 1,
            name=f"trip_assignment_{t}"
        )
    
    # Constraint 2: Link resource usage variables
    for d in range(max_drivers):
        # Driver is used if they have at least one trip assigned
        total_trips_for_driver = gp.quicksum(x[t, d, tr] for t in range(n_trips) for tr in range(max_trains))
        model.addConstr(
            driver_used[d] * n_trips >= total_trips_for_driver,
            name=f"driver_usage_upper_{d}"
        )
        model.addConstr(
            driver_used[d] <= total_trips_for_driver,
            name=f"driver_usage_lower_{d}"
        )
        
    for tr in range(max_trains):
        # Train is used if it has at least one trip assigned
        total_trips_for_train = gp.quicksum(x[t, d, tr] for t in range(n_trips) for d in range(max_drivers))
        model.addConstr(
            train_used[tr] * n_trips >= total_trips_for_train,
            name=f"train_usage_upper_{tr}"
        )
        model.addConstr(
            train_used[tr] <= total_trips_for_train,
            name=f"train_usage_lower_{tr}"
        )
    
    # Constraint 3: No time conflicts for trains (trains cannot overlap)
    for tr in range(max_trains):
        for t1 in range(n_trips):
            for t2 in range(t1 + 1, n_trips):
                trip1, trip2 = trips[t1], trips[t2]
                # Check if trips overlap in time
                if not (trip1["arrival"] <= trip2["departure"] or trip2["arrival"] <= trip1["departure"]):
                    model.addConstr(
                        gp.quicksum(x[t1, d, tr] for d in range(max_drivers)) + 
                        gp.quicksum(x[t2, d, tr] for d in range(max_drivers)) <= 1,
                        name=f"train_conflict_{tr}_{t1}_{t2}"
                    )
    
    # Constraint 4: Driver working time constraints
    for d in range(max_drivers):
        # Initialize start and end times when driver is not used
        model.addConstr(
            driver_start_time[d] >= 0,
            name=f"driver_start_init_{d}"
        )
        model.addConstr(
            driver_end_time[d] <= BIG_M,
            name=f"driver_end_init_{d}"
        )
        
        # For each trip, if assigned to this driver, update start/end times
        for t in range(n_trips):
            trip = trips[t]
            trip_assigned_to_driver = gp.quicksum(x[t, d, tr] for tr in range(max_trains))
            
            # If trip is assigned to driver, start time must be <= trip departure
            model.addConstr(
                driver_start_time[d] <= trip["departure"] + BIG_M * (1 - trip_assigned_to_driver),
                name=f"driver_start_time_{d}_{t}"
            )
            
            # If trip is assigned to driver, end time must be >= trip arrival
            model.addConstr(
                driver_end_time[d] >= trip["arrival"] - BIG_M * (1 - trip_assigned_to_driver),
                name=f"driver_end_time_{d}_{t}"
            )
        
        # Working time constraint: end_time - start_time <= WORKING_TIME
        # Only enforce when driver is used
        model.addConstr(
            driver_end_time[d] - driver_start_time[d] <= WORKING_TIME + BIG_M * (1 - driver_used[d]),
            name=f"working_time_span_{d}"
        )

    # Constraint 5: Driver driving time constraints
    for d in range(max_drivers):
        # Total driving time for this driver across all trains and trips
        total_driving_time = gp.quicksum(
            x[t, d, tr] * trips[t]["drivingTime"] 
            for t in range(n_trips) 
            for tr in range(max_trains)
        )
        model.addConstr(
            total_driving_time <= DRIVING_TIME,
            name=f"driving_time_{d}"
        )
    
    # Constraint 6: Driver cannot be in two places at once (no overlapping trips)
    for d in range(max_drivers):
        for t1 in range(n_trips):
            for t2 in range(t1 + 1, n_trips):
                trip1, trip2 = trips[t1], trips[t2]
                # Check if trips overlap in time
                if not (trip1["arrival"] <= trip2["departure"] or trip2["arrival"] <= trip1["departure"]):
                    model.addConstr(
                        gp.quicksum(x[t1, d, tr] for tr in range(max_trains)) + 
                        gp.quicksum(x[t2, d, tr] for tr in range(max_trains)) <= 1,
                        name=f"driver_conflict_{d}_{t1}_{t2}"
                    )
    
    # Objective: Minimize total number of drivers and trains used
    model.setObjective(
        gp.quicksum(driver_used[tr] for tr in range(max_drivers)),
        GRB.MINIMIZE
    )
    
    print("Starting optimization...")
    model.optimize()
    
    if model.status == GRB.OPTIMAL:
        print("Optimal solution found!")
        
        # Extract solution
        solution = []
        drivers_count = 0
        trains_count = 0
        
        for t in range(n_trips):
            for d in range(max_drivers):
                for tr in range(max_trains):
                    if x[t, d, tr].X > 0.5:  # Binary variable is 1
                        trip = trips[t]
                        solution.append({
                            "nr": trip["nr"],
                            "train": f"T{tr + 1}",
                            "driver": f"D{d + 1}",
                            "departure": trip["departure"],
                            "arrival": trip["arrival"],
                            "destination": trip["destination"]
                        })
                        drivers_count = max(drivers_count, d + 1)
                        trains_count = max(trains_count, tr + 1)
        
        print(f"Solution uses {drivers_count} drivers and {trains_count} trains")
        return solution
        
    elif model.status == GRB.TIME_LIMIT:
        print("Time limit reached, using best solution found so far...")
        if model.SolCount > 0:
            # Extract best solution found
            solution = []
            drivers_count = 0
            trains_count = 0
            
            for t in range(n_trips):
                for d in range(max_drivers):
                    for tr in range(max_trains):
                        if x[t, d, tr].X > 0.5:  # Binary variable is 1
                            trip = trips[t]
                            solution.append({
                                "nr": trip["nr"],
                                "train": f"T{tr + 1}",
                                "driver": f"D{d + 1}",
                                "departure": trip["departure"],
                                "arrival": trip["arrival"],
                                "destination": trip["destination"]
                            })
                            drivers_count = max(drivers_count, d + 1)
                            trains_count = max(trains_count, tr + 1)
            
            print(f"Best solution uses {drivers_count} drivers and {trains_count} trains")
            return solution
        else:
            raise Exception("No feasible solution found within time limit")
    else:
        raise Exception(f"Optimization failed with status: {model.status}")
        
# Main execution
if __name__ == "__main__":
    print("Solving train scheduling problem using Gurobi optimization only")
    print("=" * 60)
    
    try:
        # Solve with Gurobi
        solution = solve_with_gurobi()
        
        print(f"Optimization completed:")
        print(f"  - All {len(solution)} trips scheduled")
        
        # Sort by departure time and save
        solution.sort(key=lambda x: x["departure"])
        
        with open("solution.json", "w") as f:
            json.dump(solution, f, indent=4)
        
        print(f"\nSolution saved to solution.json")
        print(f"Solution uses {len(set(s['driver'] for s in solution))} drivers and {len(set(s['train'] for s in solution))} trains")
        
        print("\nSolution is ready for validation with checker.py")
        
    except Exception as e:
        print(f"Failed to solve problem: {e}")
        print("Please check Gurobi license and installation")
