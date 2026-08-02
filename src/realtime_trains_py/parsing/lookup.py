from typing import Any


def location_lookup(location: str, data: Any):
    codes: list = []

    # Iterate over each stop. Check if the location is the same as the stop description.
    # If they are equal, check if there's a shortCode (CRS code). Add this to codes if
    # there is one. All locations have a longCode (TIPLOC), so add this to codes
    for stop in data["locations"]:
        if stop["description"].lower() == location.lower():
            if "shortCode" in stop:
                codes.append(stop["shortCode"])

            codes.append(stop["longCode"])

    # If some data has been found, print a list of the CRS codes and TIPLOCs. If no data
    # was found, print a message saying no codes were found.
    if codes != []:
        print(f"{len(codes)} CRS codes and TIPLOCs for '{location.lower()}':")
        for code in codes:
            print(f"- {code}")

    else:
        print(
            f"No CRS codes or TIPLOCs found for '{location.lower()}'. Double check your spelling."
        )


def code_lookup(code: str, data: Any):
    locations: list = []

    # Iterate over each stop. Check if the code is the same as the stop shortCode or longCode.
    # If they are equal, add the stop description to the locations
    for stop in data["locations"]:
        if stop["longCode"].lower() == code.lower():
            if stop["description"] not in locations:
                locations.append(stop["description"])

        elif "shortCode" in stop:
            if stop["shortCode"].lower() == code.lower():
                if stop["description"] not in locations:
                    locations.append(stop["description"])

    # If some data has been found, print a list of the CRS codes and TIPLOCs. If no data
    # was found, print a message saying no codes were found.
    if locations != []:
        print(f"Location(s) for '{code.upper()}':")
        for location in locations:
            print(f"- {location}")

    else:
        print(f"No location found for '{code.upper()}'. Double check your spelling.")
