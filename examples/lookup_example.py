from realtime_trains_py import RealtimeTrainsPy

# Initialise RealtimeTrainsPy
rtt = RealtimeTrainsPy(request_token="YOUR_REQUEST_TOKEN")  # <----- CHANGE ME

#### EXAMPLE 1 ####

rtt.lookup(code="ELYY")  # Get a list of locations for ELYY

### EXAMPLE OUTPUT ###
# Location(s) for 'ELYY':
# - Ely


#### EXAMPLE 2 ####

rtt.lookup(
    location="London Liverpool Street"
)  # Get a list of CRS codes and TIPLOCs for London Liverpool Street

### EXAMPLE OUTPUT ###
# 3 CRS codes and TIPLOCs for 'london liverpool street':
# - LST
# - LIVST
# - LIVSTLL


#### EXAMPLE 3 ####

rtt.lookup()  # Get a new file with all locations saved

### EXAMPLE OUTPUT ###
# Data saved to file:
#   realtime_trains_py_data/locations_ungrouped_data.json.


#### EXAMPLE 4 -- INVALID EXAMPLE ####

rtt.lookup(location="London Kings Cross", code="KNGX")
# Returns an error. DO NOT use this implementation.

### EXAMPLE OUTPUT ###
# realtime_trains_py.internal.errors.TooManyArguments:
# realtime-trains-py error:
# Too too many arguments provided for this method.
#  Method: 'lookup' only takes one argument. Remove one of:
#  - Code: 'KNGX'
#  - Location: 'London Kings Cross'.
