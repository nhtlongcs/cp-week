import json 
new_data = {
    "trips": [],
    "drivers": []
}
with open('solution.json', 'r') as f:
    data = json.load(f)

new_data['trips'] = data

# loop through trips to get drivers departure times
drivers = {}
for trip in data:
    driver = trip['driver']
    if driver not in drivers:
        drivers[driver] = {}
    drivers[driver]["start"] = int(min(drivers[driver].get("start", float('inf')), trip['departure']))

driver_ls = []
for driver in drivers:
    drivers[driver]["end"] = drivers[driver]["start"] + 9*60
    drivers[driver]["breaks_window_start"] = drivers[driver]["start"] + 3*60
    drivers[driver]["breaks_window_end"] = drivers[driver]["start"] + 6*60
    drivers[driver]["driver"] = driver
    driver_ls.append(drivers[driver])

new_data['drivers'] = driver_ls

with open('solution_viz.json', 'w') as f:
    json.dump(new_data, f, indent=4)


# for each driver, start time is the earliest earliest departure time of their trips
# end time is start time + 9 hours (9*60 minutes)
# breaks_window_start is start time + 3 hours
# breaks_window_end is start time + 6 hours

# "drivers": [
# {
#     "driver": "D1",
#     "start": 315,
#     "end": 820
# },

