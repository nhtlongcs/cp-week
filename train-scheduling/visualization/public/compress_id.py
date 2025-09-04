import json 

# trips: [{
#     "nr": 53,
#     "train": "T17",
#     "driver": "D4",
#     "departure": 945,
#     "arrival": 998,
#     "destination": "midleton"
# },..]
# drivers: [{
#     {
#         "driver": "D13",
#         "start": 130,
#         "end": 670,
#         "breaks_window_start": 310,
#         "breaks_window_end": 490
# },..]

# compress driver id and train id eg we have D1, D2, D5 -> D1, D2, D3, same for train


with open('solution.json', 'r') as f:
    data = json.load(f)
    train_ids = {}
    driver_ids = {}

    next_train_id = 1
    next_driver_id = 1

    for trip in data['trips']:
        train = trip['train']
        if train not in train_ids:
            train_ids[train] = f"T{next_train_id}"
            next_train_id += 1
        trip['train'] = train_ids[train]

        driver = trip['driver']
        if driver not in driver_ids:
            driver_ids[driver] = f"D{next_driver_id}"
            next_driver_id += 1
        trip['driver'] = driver_ids[driver]
        
    for driver in data['drivers']:
        driver_name = driver['driver']
        if driver_name in driver_ids:
            driver['driver'] = driver_ids[driver_name]
        else:
            # This should not happen, but just in case
            driver['driver'] = f"D{next_driver_id}"
            next_driver_id += 1



with open('solution.json', 'w') as f:
    json.dump(data, f, indent=4)
