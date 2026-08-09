from realtime_trains_py import RealtimeTrainsPy

# Initialise RealtimeTrainsPy
rtt = RealtimeTrainsPy(
    request_token="YOUR_REQUEST_TOKEN" # <----- CHANGE ME
)

#### EXAMPLE 1 ####

rtt.watch_service("G38953") # Get live service board for G38953


#### EXAMPLE 2 ####

rtt.get_live("G90229") # Get live service board for G90229

