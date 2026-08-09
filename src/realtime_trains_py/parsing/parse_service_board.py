from realtime_trains_py.internal.details import ServiceData
from realtime_trains_py.internal.utilities import check_cancel, fmt


def arrange_output(service: ServiceData) -> str:
    # Set the initial line
    lines = f"{fmt['blue']}{service.service_uid}:{fmt['white']} {service.start_time} {service.origin} to {service.destination}\n  │\n"

    # Iterate over each calling point
    for calling_point in service.calling_points:

        # If the stop name isn't the desination, add the calling point line to the line
        if service.destination != calling_point.stop_name:
            lines += calling_point_line(
                calling_point.expected_departure,
                calling_point.scheduled_departure,
                calling_point.stop_name,
                calling_point.platform,
            )

        # If the stop name is the destination, add the final calling point to the line
        else:
            lines += final_calling_point(
                calling_point.expected_arrival,
                calling_point.scheduled_arrival,
                calling_point.stop_name,
                calling_point.platform,
            )

    # Add the operator to the lines
    lines += f"{fmt['white']}Operated by {fmt['blue']}{service.operator} {fmt['white']}"

    # If there is a number of coaches, add this information to the lines
    if service.coaches != 0:
        lines += f"\nFormed of {service.coaches} coaches"

    return lines + "\n\n"


def final_calling_point(exp_dep: str, sch_dep: str, stop: str, platform: str):
    # Check if the calling point is cancelled
    exp_dep = check_cancel(exp_dep, True)

    # If the calling point isn't equal, strike through the scheduled arrival time and display the expected arrival time.
    # Otherwise, display the scheduled arrival time in green.
    if "On time" in exp_dep:
        #   ╰─ 10:30 Stevenage P3
        return f"  {fmt['white']}╰─ {fmt['green']}{sch_dep}{fmt['white']} {stop} {f"P{platform}" if platform != "-" else ""} \n\n"

    else:
        #   ╰─ 10:30 Cancelled Stevenage P3
        return f"  {fmt['white']}╰─ {fmt['grey']}{fmt['s_strike']}{sch_dep}{fmt['e_strike']} {exp_dep}{fmt['white']} {stop} {f"P{platform}" if platform != "-" else ""} \n\n"


def calling_point_line(exp_arr: str, sch_arr: str, stop: str, platform: str):
    # Check if the calling point is cancelled
    exp_arr = check_cancel(exp_arr, True)

    # If the calling point isn't equal, strike through the scheduled arrival time and display the expected arrival time.
    # Otherwise, display the scheduled arrival time in green.
    if "On time" in exp_arr:
        #   ├─ 10:30 Stevenage P3
        #   │
        return f"  {fmt['white']}├─ {fmt['green']}{sch_arr}{fmt['white']} {stop} {f"P{platform}" if platform != "-" else ""} \n  │\n"

    else:
        #   ├─ 10:30 Cancelled Stevenage P3
        #   │
        return f"  {fmt['white']}├─ {fmt['grey']}{fmt['s_strike']}{sch_arr}{fmt['e_strike']} {exp_arr}{fmt['white']} {stop} {f"P{platform}" if platform != "-" else ""} \n  │\n"
