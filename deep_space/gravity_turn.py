def gravity_turn(vessel, conn, alt, pitch):
    mean_altitude = conn.get_call(getattr, vessel.flight(), "mean_altitude")
    expr = conn.krpc.Expression.greater_than(
        conn.krpc.Expression.call(mean_altitude),
        conn.krpc.Expression.constant_double(alt),
    )
    event = conn.krpc.add_event(expr)
    with event.condition:
        event.wait()
    event.remove()
    print(f"G_THREAD: gravity turn alt: {alt}, angle: {pitch}")
    vessel.auto_pilot.engage()
    vessel.auto_pilot.target_pitch_and_heading(pitch, 90)


def gravity_turn_thread(vessel, conn, target_ap):
    print("G_THEAD: GRAVITY TURN THREAD INITIALIZED")

    vessel.control.sas = True
    vessel.auto_pilot.sas_mode = vessel.auto_pilot.sas_mode.stability_assist
    for i in range(60):
        alt = 20000 + 800 * i
        pitch = 90 - i / 2
        gravity_turn(vessel, conn, alt=alt, pitch=pitch)

    gravity_turn(vessel, conn, target_ap - 7000, 4.0)
    gravity_turn(vessel, conn, target_ap - 1000, 2.5)
    print("G_THREAD: Heading 2.5 degrees")
