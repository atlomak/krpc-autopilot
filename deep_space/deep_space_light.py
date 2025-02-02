import krpc
import threading
from throttle import throttle_thread
from gravity_turn import gravity_turn_thread
from stage import booster_thread
import time


if __name__ == "__main__":
    conn = krpc.connect(name="Throttle Control")
    vessel = conn.space_center.active_vessel

    target_ap = 75000
    print("MAIN: Start sequence initialized")
    t1: threading.Thread
    t2: threading.Thread
    t3: threading.Thread
    for i in range(5, 0, -1):
        print(f"MAIN: {i} to start")
        if i == 1:
            t1 = threading.Thread(
                target=throttle_thread, args=(vessel, conn, target_ap)
            )
            t2 = threading.Thread(
                target=gravity_turn_thread, args=(vessel, conn, target_ap)
            )
            t3 = threading.Thread(target=booster_thread, args=(vessel, conn))
            t1.start()
            t2.start()
            t3.start()
        time.sleep(1)
    print("MAIN: Ignition")
    vessel.control.activate_next_stage()

    # flight_info = vessel.flight()
    # altitude = conn.add_stream(getattr, flight_info, 'mean_altitude')
    # while True:
    #     a = altitude()
    #     print(f"MAIN: {a}")
    #     if a >= 70000:
    #         break
    #     time.sleep(1)

    t1.join()
    t2.join()
    t3.join()
