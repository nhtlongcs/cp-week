import json 

with open('solution.json', 'r') as f:
    data = json.load(f)
    for driver in data['drivers']:
        driver['breaks_window_start'] = driver['start'] + 3 * 60  # 3 hours in minutes
        driver['breaks_window_end'] = driver['start'] + 6 * 60    # 6 hours in minutes

with open('solution.json', 'w') as f:
    json.dump(data, f, indent=4)
