import json
from datetime import datetime

# Load trip data
with open("monfri.json", "r") as f:
    data = json.load(f)

trips = data["trips"]
print(f"Solving train scheduling problem with {len(trips)} trips using greedy heuristic")

# Constants
WORKING_TIME = 9 * 60  # 9 hours in minutes
DRIVING_TIME = 7 * 60  # 7 hours in minutes

# Sort trips by departure time
trips_sorted = sorted(trips, key=lambda x: x["departure"])

# Initialize resources
drivers = []
trains = []
solution = []

def trips_overlap(trip1, trip2):
    """Check if two trips overlap in time"""
    return not (trip1["arrival"] <= trip2["departure"] or trip2["arrival"] <= trip1["departure"])

def can_assign_driver(driver_trips, new_trip):
    """Check if a driver can take this trip based on constraints"""
    if not driver_trips:
        return True
    
    # Check overlap with existing trips
    for existing_trip in driver_trips:
        if trips_overlap(existing_trip, new_trip):
            return False
    
    # Check working time constraint
    all_trips = driver_trips + [new_trip]
    start_time = min(trip["departure"] for trip in all_trips)
    end_time = max(trip["arrival"] for trip in all_trips)
    if (end_time - start_time) > WORKING_TIME:
        return False
    
    # Check driving time constraint
    total_driving = sum(trip["drivingTime"] for trip in all_trips)
    if total_driving > DRIVING_TIME:
        return False
    
    return True

def can_assign_train(train_trips, new_trip):
    """Check if a train can take this trip (no overlap)"""
    for existing_trip in train_trips:
        if trips_overlap(existing_trip, new_trip):
            return False
    return True

# Greedy assignment
for trip in trips_sorted:
    assigned = False
    
    # Try to assign to existing driver-train pairs
    for driver_id in range(len(drivers)):
        for train_id in range(len(trains)):
            if (can_assign_driver(drivers[driver_id], trip) and 
                can_assign_train(trains[train_id], trip)):
                
                # Assign trip
                drivers[driver_id].append(trip)
                trains[train_id].append(trip)
                solution.append({
                    "nr": trip["nr"],
                    "train": f"T{train_id + 1}",
                    "driver": f"D{driver_id + 1}",
                    "departure": trip["departure"],
                    "arrival": trip["arrival"],
                    "destination": trip["destination"]
                })
                assigned = True
                break
        
        if assigned:
            break
    
    # If not assigned, try to use existing driver with new train
    if not assigned:
        for driver_id in range(len(drivers)):
            if can_assign_driver(drivers[driver_id], trip):
                # Create new train
                trains.append([trip])
                drivers[driver_id].append(trip)
                solution.append({
                    "nr": trip["nr"],
                    "train": f"T{len(trains)}",
                    "driver": f"D{driver_id + 1}",
                    "departure": trip["departure"],
                    "arrival": trip["arrival"],
                    "destination": trip["destination"]
                })
                assigned = True
                break
    
    # If still not assigned, try to use existing train with new driver
    if not assigned:
        for train_id in range(len(trains)):
            if can_assign_train(trains[train_id], trip):
                # Create new driver
                drivers.append([trip])
                trains[train_id].append(trip)
                solution.append({
                    "nr": trip["nr"],
                    "train": f"T{train_id + 1}",
                    "driver": f"D{len(drivers)}",
                    "departure": trip["departure"],
                    "arrival": trip["arrival"],
                    "destination": trip["destination"]
                })
                assigned = True
                break
    
    # If still not assigned, create new driver and train
    if not assigned:
        drivers.append([trip])
        trains.append([trip])
        solution.append({
            "nr": trip["nr"],
            "train": f"T{len(trains)}",
            "driver": f"D{len(drivers)}",
            "departure": trip["departure"],
            "arrival": trip["arrival"],
            "destination": trip["destination"]
        })

# Sort solution by departure time
solution.sort(key=lambda x: x["departure"])

# Save solution
with open("solution.json", "w") as f:
    json.dump(solution, f, indent=4)

print(f"Greedy solution completed!")
print(f"Drivers used: {len(drivers)}")
print(f"Trains used: {len(trains)}")
print(f"All {len(solution)} trips scheduled")

# Print driver schedules
print("\nDriver Work Schedules:")
for i, driver_trips in enumerate(drivers):
    if driver_trips:
        start_time = min(trip["departure"] for trip in driver_trips)
        end_time = max(trip["arrival"] for trip in driver_trips)
        total_driving = sum(trip["drivingTime"] for trip in driver_trips)
        print(f"  D{i + 1}: {start_time}-{end_time} ({end_time - start_time} min work, {total_driving} min driving, {len(driver_trips)} trips)")

print(f"\nSolution saved to solution.json")
