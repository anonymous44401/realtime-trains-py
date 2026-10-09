from realtime_trains_py import RealtimeTrainsPy

# Initialise RealtimeTrainsPy
rtt = RealtimeTrainsPy(request_token="YOUR_REQUEST_TOKEN")  # <----- CHANGE ME

#### EXAMPLE 1 ####

rtt.watch_service("G38953")  # Get live service board for G38953


#### EXAMPLE 2 ####

rtt.watch_service(
    "G90229", mode="DMI_yellow", refresh=120
)  # Get live service board for G90229 in DMI (Yellow) mode, refreshing every 120 seconds
