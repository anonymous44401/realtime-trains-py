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
# - LST (London Liverpool Street)
# - LIVST (London Liverpool Street)
# - LIVSTLL (London Liverpool Street)


# You can add `raw=True` to example 1 or example 2 to get a list of LookupData objects returned


#### EXAMPLE 3 ####

rtt.lookup()  # Get a new file with all locations saved

### EXAMPLE OUTPUT ###
# Will return a json format for all locations and TIPLOCs across the country


#### EXAMPLE 4 ####

# Check if a code matches a given location
rtt.lookup(location="London Kings Cross", code="KNGX")

### EXAMPLE OUTPUT ###
# KNGX is a code for london kings cross
