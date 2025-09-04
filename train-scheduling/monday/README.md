## Train Scheduling Problem 

### Problem Description
The challenge is about train crew allocation for the Cork commuter rail network. The network connects Cork Kent station with three endpoints: Mallow, Cobh, and Midleton.

- The Cobh and Midleton lines share a double-tracked section until Glounthaune, but the Midleton branch is currently single-tracked (work is ongoing to double-track it).

- Each train requires one driver.

- A driver’s shift starts when their first train departs and ends when their last train arrives back at Cork Kent.

### Constraints:

- Maximum 9 hours working time per day.

- Maximum 7 hours driving time per day.

- All drivers are qualified for all trains, and only a single day (e.g., Monday) is considered. Multi-day rostering is excluded.

### Data Provided

Timetable for Cork train services (Monday–Friday).

Provided as a JSON structure (`monfri.json`), where each trip includes:


```bash
1. Destination

2. Trip number

3. Departure time (from Cork Kent, minutes after midnight)

4. Arrival time (back at Cork Kent)

5. Duration (minutes, equal to arrival - departure)

6. Driving time (minutes, excludes turnaround).
```

### Main Questions

**Drivers required:** How many drivers are needed to cover all services on a normal weekday?

**Trains required:** How many trains are necessary to run the schedule?

**Estimation method:** Is there a simple way to estimate the minimum number of drivers required, without solving the full optimization?

Check out my solution in [SOLUTION.md](SOLUTION.md).

### Bonus Question

Beyond minimizing the number of drivers, what could be a second objective to choose the “best” schedule (e.g., fairness, minimizing idle time, balanced workloads, etc.)?

