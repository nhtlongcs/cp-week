# trip 60 (cork) : driver 7, train 3, dep=1155, arr=1208
# convert this to json

import json
import re
sol = []
with open('solution.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
        if line.strip():
            trip_id, location, driver_id, train_id, dep, arr = re.match(r'trip (\d+) \((.*?)\) : driver (\d+), train (\d+), dep=(\d+), arr=(\d+)', line).groups()
            sol.append({
                "nr": int(trip_id),
                "destination": location,
                "driver": driver_id,
                "train": train_id,
                "departure": int(dep),
                "arrival": int(arr)
            })
drivers = []
with open('drivers.txt', 'r') as f:
    lines = f.readlines()
    # driver 7: start=340, break=608 .. 668, end=880
    for line in lines:
        if line.strip():
            driver_id, start, brk_start, brk_end, end = re.match(r'driver (\d+): start=(\d+), break=(\d+) .. (\d+), end=(\d+)', line).groups()
            driver = {
                "driver": int(driver_id),
                "start": int(start),
                "break_start": int(brk_start),
                "break_end": int(brk_end),
                "end": int(end)
            }
            drivers.append(driver)
with open('solution.json', 'w') as f:
    json.dump({"trips": sol, "drivers": drivers}, f)