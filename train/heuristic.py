# "trips": [
#         {
#             "duration": 55,
#             "nr": 1,
#             "arrival": 385,
#             "destination": "cobh",
#             "drivingTime": 51,
#             "departure": 330
#         },
#         {
#             "duration": 55,
#             "nr": 2,
#             "arrival": 445,
#             "destination": "cobh",
#             "drivingTime": 51,
#             "departure": 390
#         },
#         ...
# ----------------------------------
# [
#     {
#         "timestamp": 1,
#         "train": "A",
#         "driver": "John",
#         "action": "depart",
#         "destination": "Dublin"
#     },
#     {
#         "timestamp": 2,
#         "train": "A",
#         "driver": "John",
#         "action": "depart",
#         "destination": "Galway"
#     },
#     {
#         "timestamp": 3,
#         "train": "A",
#         "driver": "John",
#         "action": "depart",
#         "destination": "Galway"
#     }
# ]
import json
from heapq import heappush, heappop

def greedy_assign(trips):
    # trips sorted by departure time
    trips = sorted(trips, key=lambda x: x["departure"])

    trains = []   # min-heap of (available_time, train_id)
    drivers = []  # min-heap of (available_time, driver_id)

    assignments = []
    next_train_id = 1
    next_driver_id = 1

    for trip in trips:
        dep = trip["departure"]
        arr = trip["arrival"]

        # assign train - check if any available train can be used
        if trains and trains[0][0] <= dep:
            # reuse an available train
            _, train_id = heappop(trains)
        else:
            # create new train
            train_id = f"T{next_train_id}"
            next_train_id += 1

        # assign driver - check if any available driver can be used
        if drivers and drivers[0][0] <= dep:
            # reuse an available driver
            _, driver_id = heappop(drivers)
        else:
            # create new driver
            driver_id = f"D{next_driver_id}"
            next_driver_id += 1

        # push them back with new availability time
        heappush(trains, (arr, train_id))
        heappush(drivers, (arr, driver_id))

        assignments.append({
            "nr": trip["nr"],
            "train": train_id,
            "driver": driver_id,
            "departure": dep,
            "arrival": arr,
            "destination": trip["destination"]
        })

    return assignments

with open("monfri.json", "r") as f:
    trips = json.load(f)["trips"]

assignments = greedy_assign(trips)
for a in assignments:
    print(a)

with open("solution.json", "w") as f:
    json.dump(assignments, f, indent=4)