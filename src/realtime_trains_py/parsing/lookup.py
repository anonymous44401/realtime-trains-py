from typing import Any

from realtime_trains_py.internal.details import LookupData


def code_lookup(code: str, data: Any, raw: bool) -> list[LookupData]:
    locations: list[LookupData] = []
    seen: set[str] = set()

    # Iterate over each stop. Check if the code is the same as the stop shortCode or longCode.
    # If they are equal, add the stop description to the locations
    for stop in data["locations"]:
        matched = False
        if stop.get("longCode", "").lower() == code.lower():
            matched = True
        elif "shortCode" in stop and stop["shortCode"].lower() == code.lower():
            matched = True

        if matched:
            description = stop["description"]
            if description not in seen:
                seen.add(description)
                locations.append(LookupData(code, description))

    # If some data has been found, print a list of the CRS codes and TIPLOCs. If no data
    # was found, print a message saying no codes were found.
    if locations and not raw:
        print(f"Location(s) for '{code.upper()}':")
        for item in locations:
            print(f"- {item.location}")

    elif not raw:
        print(
            f"No location(s) found for code '{code.upper()}'. Double check your spelling."
        )

    return locations


def location_lookup(location: str, data: Any, raw: bool) -> list[LookupData]:
    codes: list[LookupData] = []

    # Iterate over each stop. Check if the location is the same as the stop description.
    # If they are equal, check if there's a shortCode (CRS code). Add this to codes if
    # there is one. All locations have a longCode (TIPLOC), so add this to codes
    for stop in data["locations"]:
        if location.lower() in stop["description"].lower():
            if "shortCode" in stop:
                codes.append(LookupData(stop["shortCode"], stop["description"]))

            codes.append(LookupData(stop["longCode"], stop["description"]))

    # If some data has been found, print a list of the CRS codes and TIPLOCs. If no data
    # was found, print a message saying no codes were found.
    if codes and not raw:
        print(f"{len(codes)} CRS codes and TIPLOCs for '{location.lower()}':")
        # for code, description in codes:
        for item in codes:
            # print(f"- {code} ({description})")
            print(f"- {item.code} ({item.location})")

    elif not raw:
        print(
            f"No CRS codes or TIPLOCs found for location '{location.lower()}'. Double check your spelling."
        )

    return codes


def lookup_check(code: str, location: str, data: Any, raw: bool) -> bool:
    # Set found
    found = False

    # Iterate over each stop. Check if the code is the same as the stop shortCode or longCode.
    # If they are the same, check the description against the location. If they match, set the
    # found flag to True and break
    for stop in data["locations"]:
        matched = False
        if stop.get("longCode", "").lower() == code.lower():
            matched = True
        elif "shortCode" in stop and stop["shortCode"].lower() == code.lower():
            matched = True

        if matched and stop["description"].lower() == location.lower():
            found = True
            break

    # If not raw, output a message stating if the code is a code for the location
    if not raw:
        print(
            f"{code.upper()} is{'' if found else ' not'} a code for {location.lower()}"
        )

    return found
