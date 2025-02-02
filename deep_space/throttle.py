import time


def _atm_speed(vessel, flight_stream):
    vessel.control.throttle = 1
    time.sleep(1)
    while flight_stream().mean_altitude < 10000:
        current_speed = flight_stream().speed
        if current_speed >= 300:
            vessel.control.throttle = 0.2
        else:
            vessel.control.throttle = 0.4


def _upper_atm_speed(vessel, ap_stream, target_ap):
    vessel.control.throttle = 0.6
    while ap_stream() < target_ap - 1000:
        current_ap = ap_stream()
        remaining = target_ap - current_ap
        print(f"TH_THREAD: current ap {current_ap}")

        if remaining < 40000:
            throttle = max(0.1, min(1.0, remaining / 40000))
            vessel.control.throttle = throttle

        time.sleep(0.1)
    print("TH_THREAD: Target apopapsis achieved. Set 0.")
    vessel.control.throttle = 0.0


def throttle_thread(vessel, conn, target_ap):
    print("TH_THREAD: THROTTLE THREAD INITIALIZED")
    flight_stream = conn.add_stream(vessel.flight, vessel.orbit.body.reference_frame)

    apoapsis = conn.add_stream(getattr, vessel.orbit, "apoapsis_altitude")
    periapsis = conn.add_stream(getattr, vessel.orbit, "periapsis_altitude")

    print("TH_THREAD: Starting inital phase (atm).")
    _atm_speed(vessel, flight_stream)

    print(f"TH_THREAD: Starting secondary phase (target {target_ap} apoapsis)")
    _upper_atm_speed(vessel, apoapsis, target_ap)

    mean_altitude = conn.get_call(getattr, vessel.flight(), "mean_altitude")
    expr = conn.krpc.Expression.greater_than(
        conn.krpc.Expression.call(mean_altitude),
        conn.krpc.Expression.constant_double(target_ap - 4000),
    )
    event = conn.krpc.add_event(expr)
    with event.condition:
        event.wait()
    event.remove()

    print("TH_THREAD: Start orbit manouver")
    while True:
        if periapsis() >= target_ap - 10000:
            break
        if flight_stream().mean_altitude >= (apoapsis() - 1000):
            vessel.control.throttle = 0.9
        elif flight_stream().mean_altitude >= (apoapsis() - 5000):
            vessel.control.throttle = 0.1
            time.sleep(0.5)
        else:
            vessel.control.throttle = max(0.0, min(1, vessel.control.throttle - 0.01))

    while True:
        if periapsis() >= target_ap - 1000:
            break
        if flight_stream().mean_altitude >= (apoapsis() - 200):
            vessel.control.throttle = 0.2
    vessel.control.throttle = 0.0
    print("TH_THREAD: Target orbit achieved!")
