from realtime_trains_py import RealtimeTrainsPy

# Initialise RealtimeTrainsPy
rtt = RealtimeTrainsPy(
    request_token="YOUR_REQUEST_TOKEN" # <----- CHANGE ME
)

#### EXAMPLE 1 ####

rtt.get_live("ELYY") # Get live departure board for Ely

### EXAMPLE OUTPUT ###
# Ely Live:
# 1st 22:21 Norwich 2    Exp 23:05
# Calling at: Thetford, Attleborough, Wymondham & Norwich. East Midlands Railway service formed of 6 coaches.
# 2nd 22:58 Cambridge 2    Exp 23:07
# 3rd 23:07 Kings Lynn 1    Exp 23:24
#          22:50:34


#### EXAMPLE 2 ####

rtt.get_live("KNGX") # Get live departure board for London Kings Cross

### EXAMPLE OUTPUT ###
# London Kings Cross Live:
# 1st 22:32 Terminates here. Service from Kings Lynn.
# Calling at: London Kings Cross only. Great Northern service formed of 8 coaches.
# 2nd 22:52 Terminates here. Service from Cambridge.
# 3rd 23:02 Terminates here. Service from Ely.
#          22:51:29


#### EXAMPLE 3 ####

rtt.get_live("LEEDS", "DMI_white") # Get live departure board for Leeds in DMI (White) mode

### EXAMPLE OUTPUT ###
# Leeds Live:
# 1st 22:55 Terminates here. Service from Knottingley.
# Calling at: Leeds only. Northern service formed of 2 coaches.
# 2nd 22:56 Skipton 2  On time
# 3rd 22:58 Terminates here. Service from Wigan Wallgate.
#          22:52:30
