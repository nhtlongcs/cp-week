## Problem Update 

The problem was updated because the initial model was too simple and overlooked some real-world requirements for drivers.

- Drivers may only clock on or clock off (15 minutes) at the beginning and end of their scheduled working hours.
- These clock-on and clock-off periods contribute to a driver's total working time but are not counted as driving time.
- Breaks must commence no earlier than three hours after the start of a shift and must conclude before six hours of continuous work.

## New Questions 

Taking these additional duties into account, how many drivers are now required to cover all the services?

Check out my solution in [SOLUTION.md](SOLUTION.md).


## Bonus Question

The train crew only requires a 45 minute
break if the working time is 8 hours or more, and a 30 minute break if the working time is less than that. If we were to implement these rules, how many
train crew are required?

*Note: I havent solve this question yet*

## Checking the Solution

For verification purposes, please export the start and end times in the following JSON format:

```
{
    "trips": [
        {
            "nr": int,
            "driver": str,
            "train": str,
            "departure": int,
            "arrival": int
        },
        ...
    ],
    "drivers": [
        {
            "name": str,
            "start": int,
            "end": int
        },
        ...
    ]
}
```