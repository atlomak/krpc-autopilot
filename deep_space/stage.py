def booster_thread(vessel, conn):
    print("B_THREAD: STAGING THREAD INITIALIZED")

    solid_fuel = vessel.resources.with_resource("SolidFuel")[0]
    solid_level = conn.get_call(getattr, solid_fuel, "amount")
    expr = conn.krpc.Expression.less_than_or_equal(
        conn.krpc.Expression.call(solid_level),
        conn.krpc.Expression.constant_float(0.1),
    )
    event = conn.krpc.add_event(expr)
    with event.condition:
        event.wait()
    print("B_THREAD: eject boosters.")
    vessel.control.activate_next_stage()
    event.remove()

    liquid_fuel = vessel.resources_in_decouple_stage(0).with_resource("LiquidFuel")[0]
    liquid_level = conn.get_call(getattr, liquid_fuel, "amount")
    expr = conn.krpc.Expression.less_than_or_equal(
        conn.krpc.Expression.call(liquid_level),
        conn.krpc.Expression.constant_float(0.1),
    )
    event = conn.krpc.add_event(expr)
    with event.condition:
        event.wait()
    print("B_THREAD: eject first stage")
    vessel.control.activate_next_stage()
    event.remove()
    print("B_THREAD: finished")
