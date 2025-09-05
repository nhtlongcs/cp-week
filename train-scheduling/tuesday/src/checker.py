import pandas as pd
import json

VERBOSE = True
WORKING_TIME = 9 * 60
DRIVING_TIME = 7 * 60
CLOCK_ON = 15  # minutes
CLOCK_OFF = 15  # minutes
BREAK_START = 3 * 60  # minutes after shift start
BREAK_END = 6 * 60    # minutes after shift start
BREAK_DURATION = 60   # minutes

with open("solution.json", "r") as f:
    data = json.load(f)

plan = pd.DataFrame(data['trips']).sort_values("departure")
nr_plan = set(plan['nr'])

assert plan['nr'].nunique() == len(nr_plan), "Duplicate trips in solution"

with open("data/monfri.json", "r") as f:
    trips = json.load(f)["trips"]
        # Additional constraints
nr_gt = set([x['nr'] for x in trips])

assert len(nr_gt - nr_plan) == 0, f"Missing trips in solution: {nr_gt - nr_plan}"
assert len(nr_plan - nr_gt) == 0, f"Unexpected trips in solution: {nr_plan - nr_gt}"

# Build cost table
cost_table = pd.DataFrame(trips).set_index("nr").to_dict()["drivingTime"]

# Init drivers
driver_data = data['drivers']
driver_data = {str(d['driver']): d for d in driver_data}
driver_names_pred = set(driver_data.keys())
driver_names = set([str(d) for d in plan.driver.unique()])
assert len(driver_names - driver_names_pred) == 0, "Unexpected driver names in plan"

drivers = pd.DataFrame([
    {
        "name": name,
        "location": "Cork",
        "driving_time": DRIVING_TIME,
        "work_start": driver_data[name]['start'],
        "work_end": driver_data[name]['end'],
        "status": "free",
        "busy_until": 0  # Thời điểm driver bận xong
    }
    for name in driver_names
]).set_index("name")

# Init trains
train_ids = plan.train.unique()
trains = pd.DataFrame([
    {"id": tid, "location": "Cork", "status": "free", "busy_until": 0}
    for tid in train_ids
]).set_index("id")

print('Used Resources:')
print(f"Drivers: {len(driver_names)}")
print(f"Trains: {train_ids.shape[0]}")

log = []
inventory_records = []

# Check for 1-hour break for each driver between 3rd and 6th hour of shift
for d, row in drivers.iterrows():

    driver_trips = plan[plan.driver == d].sort_values("departure")
    shift_start = row.work_start
    shift_end = row.work_end

    if (shift_end - shift_start) > WORKING_TIME:
        print(f"Driver {d} exceeds working time")
        print(f"Driver started to work at {shift_start}")
        print(f"Driver ended their work at {shift_end}")


    busy_intervals = [(trip.departure, trip.arrival, trip.nr) for _, trip in driver_trips.iterrows()]
    busy_intervals = sorted(busy_intervals)
    break_window_start = shift_start + BREAK_START 
    break_window_end = shift_start + BREAK_END
    last_end = break_window_start
    found_break = False
    for start, end, _ in busy_intervals:
        if end <= break_window_start:
            continue
        if start >= break_window_end:
            break
        # print(f"Break window start {break_window_start}")
        # print(f"start {start}")
        # print(f"Break window end {break_window_end}")
        # print(f"end {end}")
        free_start = max(last_end, break_window_start)
        free_end = min(start, break_window_end)
        if free_end - free_start >= BREAK_DURATION:
            found_break = True
            break
        # print(free_start, free_end, free_end - free_start)
        last_end = max(last_end, end)
    if last_end <= break_window_end:
        if break_window_end - last_end >= BREAK_DURATION:
            found_break = True
        # print(last_end, break_window_end, break_window_end - last_end)
    if not found_break:
        reason = f"Driver {d} does not have a 1-hour ({BREAK_DURATION}) break between 3rd and 6th hour of shift"
        # print all work interval of drivers
        print(reason)
        print(f"Break time available from {break_window_start} to {break_window_end}")
        print(f"- shift_start at {shift_start}")
        for start, end, trip_id in busy_intervals:
            print(f" - {start}-{end} (Trip ID: {trip_id})")
        print(f"- shift_end at {shift_end}")
# Lặp theo sự kiện thời gian: departure
for t in sorted(plan.departure.unique()):
    # Cập nhật trạng thái driver/train: check busy_until
    for d, row in drivers.iterrows():
        if row.status == "driving" and t >= row.busy_until:
            drivers.at[d, "status"] = "free"
    for tr, row in trains.iterrows():
        if row.status == "driving" and t >= row.busy_until:
            trains.at[tr, "status"] = "free"

    # Ghi inventory trước khi thực hiện trip
    for d, row in drivers.iterrows():
        inventory_records.append({
            "time": t, "entity": d, "type": "driver",
            "location": row.location, "status": row.status, "driving_time": row.driving_time
        })
    for tr, row in trains.iterrows():
        inventory_records.append({
            "time": t, "entity": tr, "type": "train",
            "location": row.location, "status": row.status
        })

    # Xử lý các trip scheduled tại thời điểm này
    for _, trip in plan[plan.departure == t].iterrows():
        driver = drivers.loc[trip.driver]
        train = trains.loc[trip.train]

        valid = True
        reason = []

        # Constraint 1: driver/trains đang bận
        if driver.status == "driving":
            valid = False
            reason.append("Driver is already on a trip")
        if train.status == "driving":
            valid = False
            reason.append("Train is already on a trip")

        # Constraint 3: driving time
        trip_cost = cost_table[trip["nr"]]
        if driver.driving_time < trip_cost:
            valid = False
            reason.append("Driver has insufficient driving time left")

        # Constraint 4: working hours
        if not (driver.work_start <= trip.departure <= trip.arrival <= driver.work_end):
            valid = False
            reason.append(f"Driver outside work hours {driver.work_start}-{driver.work_end} (Trip: {trip.departure}-{trip.arrival})")

            # Constraint: 15-min clock-on/off periods
            if not (driver.work_start + CLOCK_ON <= trip.departure):
                valid = False
                reason.append(f"Trip starts before clock-on period ends ({driver.work_start + CLOCK_ON})")
            if not (trip.arrival <= driver.work_end - CLOCK_OFF):
                valid = False
                reason.append(f"Trip ends after clock-off period starts ({driver.work_end - CLOCK_OFF})")

        if valid:
            # Update states
            drivers.at[trip.driver, "location"] = trip["destination"]
            drivers.at[trip.driver, "driving_time"] -= trip_cost
            drivers.at[trip.driver, "status"] = "driving"
            drivers.at[trip.driver, "busy_until"] = trip.arrival

            trains.at[trip.train, "location"] = trip["destination"]
            trains.at[trip.train, "status"] = "driving"
            trains.at[trip.train, "busy_until"] = trip.arrival

            log.append((trip.departure, trip.driver, trip.train, trip["destination"], driver.driving_time, trip_cost, "SUCCESS"))
        else:
            log.append((trip.departure, trip.driver, trip.train, trip["destination"], driver.driving_time, trip_cost, "; ".join(reason)))

log_df = pd.DataFrame(log, columns=["time", "driver", "train", "destination", "driving_time_left", "cost_driving_time", "result"])
log_df = log_df.sort_values(by=["time", "driver", "train", "destination"])
print(log_df)
if log_df[log_df.result != "SUCCESS"].shape[0] == 0:
    print("All trips were successfully scheduled.")
else:
    print("Some trips could not be scheduled:")
    print(log_df[log_df.result != "SUCCESS"])
    log_df[log_df.result != "SUCCESS"].to_csv("failed.csv", index=False)

log_df.to_csv("log.csv", index=False)
inventory_records_df = pd.DataFrame(inventory_records)
inventory_records_df = inventory_records_df.sort_values(by=["type", "entity", "time"])
inventory_records_df = inventory_records_df[["type", "entity", "time", "location", "status", "driving_time"]]
inventory_records_df.to_csv("inventory.csv", index=False)
