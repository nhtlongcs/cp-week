import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
from datetime import timedelta, datetime

# Load plan
plan = pd.read_json("solution.json")
plan = plan.sort_values("departure")

destinations = plan["destination"].unique()

# Gán màu cho driver
drivers = plan["driver"].unique()
cmap = plt.get_cmap("tab10")
driver_colors = {driver: cmap(i % 10) for i, driver in enumerate(drivers)}

for dest in destinations:
    sub = plan[plan["destination"] == dest].copy()

    # sort trains để giảm mũi tên chồng
    train_order = list(sub.groupby("train")["driver"].apply(lambda x: list(x)).sort_values().index)
    train_map = {train: j for j, train in enumerate(train_order)}

    # Chuyển minutes -> datetime
    start_date = datetime(2000,1,1,0,0)
    sub["dep_time"] = sub["departure"].apply(lambda m: start_date + timedelta(minutes=m))
    sub["arr_time"] = sub["arrival"].apply(lambda m: start_date + timedelta(minutes=m))

    fig, ax = plt.subplots(figsize=(16, 4))

    # highlight background track
    for y in range(len(train_order)):
        ax.axhspan(y-0.4, y+0.4, color="lightgrey", alpha=0.1)

    # Vẽ trips
    for _, trip in sub.iterrows():
        y = train_map[trip["train"]]
        ax.broken_barh(
            [(trip["dep_time"], trip["arr_time"]-trip["dep_time"])],
            (y-0.35, 0.7),
            facecolors=driver_colors[trip["driver"]],
            edgecolor="black",
            alpha=0.8
        )
        ax.text(
            trip["dep_time"] + (trip["arr_time"]-trip["dep_time"])/2,
            y,
            trip["driver"],
            ha="center",
            va="center",
            fontsize=8,
            color="black"
        )

    # Vẽ mũi tên khi driver đổi train
    for driver, d_trips in sub.groupby("driver"):
        d_trips = d_trips.sort_values("dep_time")
        for t1, t2 in zip(d_trips.iloc[:-1].itertuples(), d_trips.iloc[1:].itertuples()):
            if t1.train != t2.train:
                ax.annotate("",
                            xy=(t2.dep_time, train_map[t2.train]),
                            xytext=(t1.arr_time, train_map[t1.train]),
                            arrowprops=dict(arrowstyle="->", color=driver_colors[driver], lw=1.5, alpha=0.7))

    # Trục Y
    ax.set_yticks(range(len(train_order)))
    ax.set_yticklabels(train_order)
    ax.set_ylabel("Trains")

    # Trục X
    ax.set_xlabel("Time (HH:MM)")
    min_time = sub["dep_time"].min()
    max_time = sub["arr_time"].max()
    ax.set_xlim(min_time, max_time)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    fig.autofmt_xdate()

    ax.set_title(f"Destination: {dest}")
    plt.tight_layout()
    plt.savefig(f"timeline_{dest}.png", dpi=300)
    plt.close(fig)
