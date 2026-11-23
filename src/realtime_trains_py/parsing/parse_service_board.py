from realtime_trains_py.internal.details import ServiceData
from realtime_trains_py.internal.utilities import check_cancel, fmt


def arrange_output(service: ServiceData, mode: str = "LCD") -> str:
    format = fmt.copy()

    if mode == "DMI.W":
        format["white"] = "\033[1;39m"
        format["grey"] = "\033[1;39m"
        format["red"] = "\033[1;39m"
        format["yellow"] = "\033[1;39m"
        format["green"] = "\033[1;39m"
        format["blue"] = "\033[1;39m"

    elif mode == "DMI.Y":
        format["white"] = "\033[1;33m"
        format["grey"] = "\033[1;33m"
        format["red"] = "\033[1;33m"
        format["yellow"] = "\033[1;33m"
        format["green"] = "\033[1;33m"
        format["blue"] = "\033[1;33m"

    # Set the initial line
    lines = f"{format['blue']}{service.service_uid}:{format['white']} {service.start_time} {service.origin} to {service.destination}\n  │\n"

    # Iterate over each calling point
    for calling_point in service.calling_points:

        # If the stop name isn't the destination, add the calling point line to the line
        if service.destination != calling_point.stop_name:
            lines += calling_point_line(
                calling_point.expected_departure,
                calling_point.scheduled_departure,
                calling_point.stop_name,
                calling_point.platform,
                format=format,
            )

        # If the stop name is the destination, add the final calling point to the line
        else:
            lines += final_calling_point(
                calling_point.expected_arrival,
                calling_point.scheduled_arrival,
                calling_point.stop_name,
                calling_point.platform,
                format=format,
            )

    # Add the operator to the lines
    lines += f"{format['white']}Operated by {format['blue']}{service.operator} {format['white']}"

    # If there is a number of coaches, add this information to the lines
    if service.coaches != 0:
        lines += f"\nFormed of {service.coaches} coaches"

    return lines + "\n\n"


def final_calling_point(
    exp_arr: str, sch_arr: str, stop: str, platform: str, format: dict[str, str] | None = None
):
    if format is None:
        format = fmt

    # Check if the calling point is cancelled
    exp_arr = check_cancel(exp_arr, sch_arr, True)

    # If the calling point isn't equal, strike through the scheduled arrival time and display the expected arrival time.
    # Otherwise, display the scheduled arrival time in green.
    if "On time" in exp_arr:
        #   ╰─ 10:30 Stevenage P3
        return f"  {format['white']}╰─ {format['green']}{sch_arr}{format['white']} {exp_arr} {stop} {f'P{platform}' if platform != '' else ''} \n\n"

    else:
        #   ╰─ 10:30 Cancelled Stevenage P3
        return f"  {format['white']}╰─ {format['grey']}{format['s_strike']}{sch_arr}{format['e_strike']} {exp_arr}{format['white']} {stop} {f'P{platform}' if platform != '' else ''} \n\n"


def calling_point_line(
    exp_dep: str, sch_dep: str, stop: str, platform: str, format: dict[str, str] | None = None
):
    if format is None:
        format = fmt

    # Check if the calling point is cancelled
    exp_dep = check_cancel(exp_dep, sch_dep, True)

    # If the calling point isn't equal, strike through the scheduled departure time and display the expected departure time.
    # Otherwise, display the scheduled departure time in green.
    if "On time" in exp_dep:
        #   ├─ 10:30 Stevenage P3
        #   │
        return f"  {format['white']}├─ {format['green']}{sch_dep}{format['white']} {exp_dep} {stop} {f'P{platform}' if platform != '' else ''} \n  │\n"

    else:
        #   ├─ 10:30 Cancelled Stevenage P3
        #   │
        return f"  {format['white']}├─ {format['grey']}{format['s_strike']}{sch_dep}{format['e_strike']} {exp_dep}{format['white']} {stop} {f'P{platform}' if platform != '' else ''} \n  │\n"
