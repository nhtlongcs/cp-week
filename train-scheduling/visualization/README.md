# Train Scheduling Visualization

This project provides a visualization tool for train scheduling solutions.

## Overview

The visualization displays train schedules based on solution data in JSON format. It helps analyze and debug scheduling algorithms.

The dashboard includes:
- A Gantt chart showing driver and train assignments .
- A warning panel highlighting potential issues in the schedule.
- A summary of key statistics.

![Screenshot](./Screenshot.png)

## Installation

Ensure you have [Node.js](https://nodejs.org/) and [pnpm](https://pnpm.io/) installed.

```bash
pnpm install
```

## Solution JSON Format

The visualization expects a solution file in the following format:

```json
{
    "trips": [
        {
            "nr": <trip_number_int>,
            "train": <train_id_string>,
            "driver": <driver_id_string>,
            "departure": <departure_time_in_minutes_int>,
            "arrival": <arrival_time_in_minutes_int>,
            "destination": <destination_string>
        },
        // More trips...
    ],
    "drivers": [
        {
            "driver": <driver_id_string>,
            "start": <start_time_in_minutes_int>,
            "end": <end_time_in_minutes_int>,
            "breaks_window_start": <break_window_start_in_minutes_int>,
            "breaks_window_end": <break_window_end_in_minutes_int>
        },
        // More drivers...
    ]
}
```

If you don't have the drivers section, you can generate it by using the assumption that each driver starts before their first assigned trip 15minutes early, works for 9 hours, and must take a break between 3 to 6 hours after starting. A script to convert existing solutions is provided in `monday/convert_to_viz.py`.

## Usage
Start the development server, defaulting to port 3000:

```bash
pnpm dev
```

Build and start the production server:

```bash
pnpm build
pnpm start
```
