import json
import gurobipy as gp
from gurobipy import GRB
from utils import load_wsl_lic

# Tải thông tin license cho Gurobi, nếu cần
LICENSE_DICT = load_wsl_lic('./gurobi.lic')

# Tạo môi trường Gurobi với các tham số license
env = gp.Env(params=LICENSE_DICT)
# Kích hoạt log đầu ra của Gurobi để theo dõi tiến trình
env.setParam('OutputFlag', 1)
# Giới hạn thời gian giải là 5 phút (300 giây)
env.setParam('TimeLimit', 300)

env.start()


def solve_with_gurobi():
    """Giải bài toán lập lịch tàu hỏa sử dụng Gurobi."""
    
    # Tải dữ liệu các chuyến đi
    with open("data/monfri.json", "r") as f:
        data = json.load(f)
    trips = data["trips"]
    
    # Các hằng số
    WORKING_TIME = 9 * 60  # 9 giờ tính bằng phút
    DRIVING_TIME = 7 * 60  # 7 giờ tính bằng phút
    CLOCK_ON = 15
    CLOCK_OFF = 15
    BREAK_START = 3 * 60
    BREAK_END = 6 * 60
    BREAK_DURATION = 60
    n_trips = len(trips)
    
    # Giới hạn trên hợp lý cho số tài xế và tàu
    max_drivers = min(n_trips, 15)
    max_trains = min(n_trips, 20)
    
    # Hằng số Big-M để tuyến tính hóa các ràng buộc điều kiện
    # Phải đủ lớn để không ảnh hưởng đến các ràng buộc khi chúng bị "tắt"
    BIG_M = 2 * 24 * 60  # 2 ngày tính bằng phút

    print(f"Quy mô bài toán: {n_trips} chuyến đi")
    print(f"Tài nguyên tối đa: {max_drivers} tài xế, {max_trains} tàu")
    
    # Tạo mô hình tối ưu hóa
    model = gp.Model("train_scheduling_ilp", env=env)
    
    # --- BIẾN QUYẾT ĐỊNH ---
    
    # x[t,d] = 1 nếu chuyến đi t được giao cho tài xế d
    x = model.addVars(n_trips, max_drivers, vtype=GRB.BINARY, name="x")
    # y[t,tr] = 1 nếu chuyến đi t được giao cho tàu tr
    y = model.addVars(n_trips, max_trains, vtype=GRB.BINARY, name="y")
    
    # Biến nhị phân cho việc sử dụng tài nguyên
    driver_used = model.addVars(max_drivers, vtype=GRB.BINARY, name="driver_used")
    train_used = model.addVars(max_trains, vtype=GRB.BINARY, name="train_used")
    
    # Biến cho ràng buộc thời gian làm việc
    driver_start_time = model.addVars(max_drivers, vtype=GRB.CONTINUOUS, ub=BIG_M, name="driver_start_time")
    driver_end_time = model.addVars(max_drivers, vtype=GRB.CONTINUOUS, ub=BIG_M, name="driver_end_time")
    
    # Biến cho ràng buộc thời gian nghỉ
    break_start_time = model.addVars(max_drivers, vtype=GRB.CONTINUOUS, ub=BIG_M, name="break_start_time")
    # trip_before_break[d,t]=1 nếu chuyến đi t của tài xế d kết thúc trước giờ nghỉ
    trip_before_break = model.addVars(max_drivers, n_trips, vtype=GRB.BINARY, name="trip_before_break")
    
    print("Đang thêm các ràng buộc...")
    
    # --- RÀNG BUỘC ---
    
    # Ràng buộc 1: Mỗi chuyến đi phải được giao cho đúng một tài xế và một tàu
    model.addConstrs((x.sum(t, '*') == 1 for t in range(n_trips)), name="trip_driver_assignment")
    model.addConstrs((y.sum(t, '*') == 1 for t in range(n_trips)), name="trip_train_assignment")

    # Ràng buộc 2: Liên kết biến sử dụng tài nguyên
    for d in range(max_drivers):
        model.addConstr(driver_used[d] * n_trips >= x.sum('*', d), name=f"driver_usage_link_upper_{d}")
        model.addConstr(driver_used[d] <= x.sum('*', d), name=f"driver_usage_link_lower_{d}")
        
    for tr in range(max_trains):
        model.addConstr(train_used[tr] * n_trips >= y.sum('*', tr), name=f"train_usage_link_upper_{tr}")
        model.addConstr(train_used[tr] <= y.sum('*', tr), name=f"train_usage_link_lower_{tr}")

    # Ràng buộc 3: Không xung đột thời gian cho tàu
    for tr in range(max_trains):
        for t1 in range(n_trips):
            for t2 in range(t1 + 1, n_trips):
                trip1, trip2 = trips[t1], trips[t2]
                if not (trip1["arrival"] <= trip2["departure"] or trip2["arrival"] <= trip1["departure"]):
                    model.addConstr(y[t1, tr] + y[t2, tr] <= 1, name=f"train_conflict_{tr}_{t1}_{t2}")

    # Ràng buộc 4: Không xung đột thời gian cho tài xế
    for d in range(max_drivers):
        for t1 in range(n_trips):
            for t2 in range(t1 + 1, n_trips):
                trip1, trip2 = trips[t1], trips[t2]
                if not (trip1["arrival"] <= trip2["departure"] or trip2["arrival"] <= trip1["departure"]):
                    model.addConstr(x[t1, d] + x[t2, d] <= 1, name=f"driver_conflict_{d}_{t1}_{t2}")

    # Ràng buộc 5: Thời gian lái xe của tài xế
    model.addConstrs(
        (gp.quicksum(x[t, d] * trips[t]["drivingTime"] for t in range(n_trips)) <= DRIVING_TIME
         for d in range(max_drivers)), name="driving_time"
    )

    # Ràng buộc 6: Thời gian làm việc của tài xế (bao gồm CLOCK_ON, CLOCK_OFF)
    for d in range(max_drivers):
        for t in range(n_trips):
            trip = trips[t]
            # Nếu chuyến t được gán cho tài xế d, cập nhật thời gian bắt đầu/kết thúc
            model.addConstr(driver_start_time[d] <= (trip["departure"] - CLOCK_ON) + BIG_M * (1 - x[t, d]), name=f"start_time_update_{d}_{t}")
            model.addConstr(driver_end_time[d] >= (trip["arrival"] + CLOCK_OFF) - BIG_M * (1 - x[t, d]), name=f"end_time_update_{d}_{t}")
        
        # Tổng thời gian làm việc phải <= WORKING_TIME, chỉ áp dụng nếu tài xế được sử dụng
        model.addConstr(driver_end_time[d] - driver_start_time[d] <= WORKING_TIME + BIG_M * (1 - driver_used[d]), name=f"working_span_{d}")
        # Đảm bảo end_time >= start_time nếu tài xế được sử dụng
        model.addConstr(driver_end_time[d] >= driver_start_time[d] - BIG_M * (1 - driver_used[d]), name=f"time_order_{d}")


    # Ràng buộc 7: Thời gian nghỉ bắt buộc của tài xế
    for d in range(max_drivers):
        # Giờ nghỉ phải nằm trong khoảng [3h, 6h] sau khi bắt đầu ca làm việc
        model.addConstr(break_start_time[d] >= driver_start_time[d] + BREAK_START - BIG_M * (1 - driver_used[d]), name=f"break_window_start_{d}")
        model.addConstr(break_start_time[d] + BREAK_DURATION <= driver_start_time[d] + BREAK_END + BIG_M * (1 - driver_used[d]), name=f"break_window_end_{d}")
        model.addConstr(break_start_time[d]  + BREAK_DURATION <= driver_end_time[d] + BIG_M * (1 - driver_used[d]), name=f"break_before_end_{d}")

        for t in range(n_trips):
            trip = trips[t]
            # Ràng buộc không chồng chéo giữa giờ nghỉ và các chuyến đi
            # HOẶC: chuyến đi kết thúc trước giờ nghỉ
            model.addConstr(
                trip["arrival"] <= break_start_time[d] + BIG_M * (1 - trip_before_break[d, t]) + BIG_M * (1 - x[t, d]),
                name=f"break_no_overlap_A_{d}_{t}"
            )
            # HOẶC: giờ nghỉ kết thúc trước khi chuyến đi bắt đầu
            model.addConstr(
                break_start_time[d] + BREAK_DURATION <= trip["departure"] + BIG_M * trip_before_break[d, t] + BIG_M * (1 - x[t, d]),
                name=f"break_no_overlap_B_{d}_{t}"
            )

    # --- MỤC TIÊU (TỐI ƯU HÓA ĐA MỤC TIÊU) ---
    
    # Ưu tiên 1 (cao nhất): Tối thiểu hóa số lượng tàu
    model.setObjectiveN(train_used.sum(), index=0, priority=2, name='minimize_trains')
    # Ưu tiên 2 (thấp hơn): Tối thiểu hóa số lượng tài xế
    model.setObjectiveN(driver_used.sum(), index=1, priority=1, name='minimize_drivers')
    
    print("Bắt đầu tối ưu hóa...")
    model.optimize()
    
    # --- XỬ LÝ KẾT QUẢ ---
    
    if model.SolCount > 0:
        if model.status == GRB.OPTIMAL:
            print("Đã tìm thấy lời giải tối ưu!")
        else:
            print("Đã hết thời gian, sử dụng lời giải tốt nhất tìm được.")
        
        # Trích xuất lời giải
        solution = []
        driver_times = []
        trip_assignments = {}

        # Trích xuất thời gian làm việc của tài xế
        for d in range(max_drivers):
            if driver_used[d].X > 0.5: # Chỉ lấy thông tin của tài xế được sử dụng
                driver_times.append({
                    "driver": f"D{d + 1}",
                    "start": round(driver_start_time[d].X),
                    "end": round(driver_end_time[d].X)
                })

        # Trích xuất lịch trình các chuyến đi
        for t in range(n_trips):
            for d in range(max_drivers):
                if x[t, d].X > 0.5: # Biến nhị phân là 1
                    trip_assignments[t] = {"driver": f"D{d + 1}"}
                    break
            for tr in range(max_trains):
                if y[t, tr].X > 0.5:
                    trip_assignments[t]["train"] = f"T{tr + 1}"
                    break
        
        for t, trip in enumerate(trips):
            solution.append({
                "nr": trip["nr"],
                "train": trip_assignments[t]["train"],
                "driver": trip_assignments[t]["driver"],
                "departure": trip["departure"],
                "arrival": trip["arrival"],
                "destination": trip["destination"]
            })
            
        final_drivers = int(driver_used.sum().getValue())
        final_trains = int(train_used.sum().getValue())

        print(f"Lời giải sử dụng {final_drivers} tài xế và {final_trains} tàu")
        return solution, driver_times
        
    else:
        raise Exception(f"Không tìm thấy lời giải. Trạng thái: {model.status}")
        
# Hàm thực thi chính
if __name__ == "__main__":
    print("Giải bài toán lập lịch tàu bằng Gurobi (ILP)")
    print("=" * 60)
    
    try:
        solution, driver_times = solve_with_gurobi()
        
        print(f"Tối ưu hóa hoàn tất:")
        print(f"  - Đã lập lịch cho tất cả {len(solution)} chuyến đi")
        
        solution.sort(key=lambda x: x["departure"])
        
        with open("solution.json", "w") as f:
            json.dump({"trips": solution, "drivers": driver_times}, f, indent=4)
        
        print(f"\nLời giải đã được lưu vào solution.json")
        print(f"Lời giải sử dụng {len(set(s['driver'] for s in solution))} tài xế và {len(set(s['train'] for s in solution))} tàu")
        
        print("\nLời giải đã sẵn sàng để kiểm tra bằng checker.py")
        
    except gp.GurobiError as e:
        print(f"Lỗi Gurobi: {e.message} (mã lỗi {e.errno})")
        print("Vui lòng kiểm tra license và cài đặt Gurobi.")
    except Exception as e:
        print(f"Không thể giải bài toán: {e}")

