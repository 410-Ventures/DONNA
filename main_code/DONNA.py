
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  3 13:53:26 2019
@author: serge
"""

# importing EEG interface...
import json
import main_code.DONNA_controller_classSetup as EEG
# importing drone controls...
from pyparrot.Bebop import Bebop


# setting EEG parameters...
username = "eegdroneftw"
password = "Eegdroneftw123"
key = "316d02a3-025a-41b3-8fbe-edb854926e3b"
client_secret = "tUH4bTFVE65zWXrvisTkGXRwgNtjmhKQiA9h9wKa8EehsL9Xq8lwJbOx21Ha7Y1RnuwCCkQKzsc0sRht3HjIkY8gLOLtLJ2QzfIYw4z2b2pxjJMR6A5yCR9mH1qVwdej"
client_id = "8zcF9vDpF2QCHGsUAkchcMxf45lJfvhsDLtxbsdB" 
authorization = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBJZCI6ImNvbS5lZWdkcm9uZWZ0dy5taW5kZnVsZHJvbmUiLCJleHAiOjE1NTE2NTU1ODcsImZpcnN0TmFtZSI6IkpvcmRhbiIsImxhc3ROYW1lIjoiQnJvb2tzIiwibGljZW5zZSI6eyJpc19jb21tZXJjaWFsIjpmYWxzZSwibGljZW5zZUlkIjoiMzE2ZDAyYTMtMDI1YS00MWIzLThmYmUtZWRiODU0OTI2ZTNiIiwibGljZW5zZVNjb3BlIjoyLCJsaWNlbnNlX2V4cGlyZSI6MTU1MjUyMTU5OSwibGljZW5zZV9oYXJkTGltaXQiOjE1NTMxMjYzOTksImxpY2Vuc2Vfc29mdExpbWl0IjoxNTUyNTIxNTk5fSwibGljZW5zZUlkIjoiMzE2ZDAyYTMtMDI1YS00MWIzLThmYmUtZWRiODU0OTI2ZTNiIiwibGljZW5zZVNjb3BlIjoyLCJsaWNlbnNlX2FncmVlbWVudCI6eyJhY2NlcHRlZCI6dHJ1ZSwibGljZW5zZV91cmwiOiJodHRwczovL3d3dy5lbW90aXZjbG91ZC5jb20vZGJhcGkvcHJpdmFjeS9kb2MvZXVsYS8ifSwibGljZW5zZV9leHBpcmUiOjE1NTI1MjE1OTksImxpY2Vuc2VfaGFyZExpbWl0IjoxNTUzMTI2Mzk5LCJsaWNlbnNlX3NvZnRMaW1pdCI6MTU1MjUyMTU5OSwibmJmIjoxNTUxMzk2Mzg3LCJ1c2VyQ2xvdWRJZCI6NDYwMTUsInVzZXJuYW1lIjoiZWVnZHJvbmVmdHcifQ.QX53YebiK_ZxubDN9FuEC0hHTYCKoxLZ9uEvzBhFwJg"
needAuth = True

# connecting to EEG and training...
DONNA = EEG.EPOC_Interface(username,password,key,client_id,client_secret,authorization)
DONNA.logout()          # Log out from previous open websocket connection.
DONNA.login()           # Log in with websocket client.
if needAuth:            # If first time running in 48 hours,
    DONNA.authorize()   # request an authorization code
DONNA.createSession()   # Create session (duh)
print("\nOpening 'sys' stream...")
DONNA.subsribe("sys")   # Subscribe to sys stream
input("\nPress enter to continue to training 'neutral' command.")
DONNA.train("neutral")  # Train neutral command
input("\nPress enter to continue to training 'push' command.")
DONNA.train("push")     # Train push command
"""
input("\nPress enter to continue to training 'left' command.")
DONNA.train("left")     # Train push command
input("\nPress enter to continue to training 'right' command.")
DONNA.train("right")     # Train push command
input("\nPress enter to continue to training 'pull' command.")
DONNA.train("pull")     # Train push command
"""
## TODO: (2) train more commands: left, right, up, down, pull
print("\nDone training. Opening 'com' stream...")
DONNA.subsribe("com")   # Subscribe to com stream


## TODO: (1) set max distance
## TODO: (?) make drone land instead of return if max vals exceeded
# loop for drone control
usingdrone = True
if usingdrone:
    InTheAir=False
    bebop = Bebop(drone_type="Bebop2")
    print("\nWaking the propellor flailing flying feller...")
    success = bebop.connect(10)
    if success:
        print("\nSuccess! Drone is awake and listening!")
    else:
        print("\nNope. Drone isn't connecting.")
    print("sleeping")
    bebop.smart_sleep(5)
    bebop.ask_for_state_update()
    bebop.set_max_altitude(20) ##TODO: change to distance when using x and y movement
#    bebop.set_max_distance(20)
    bebop.enable_geofence(1)
    chillcounter = 10
    altitude = 0
going = True
justatest = True
if justatest:
    usingdrone = False
#simplecount = 0
try:
    while going:
#        print(simplecount)
        print(json.loads(DONNA.ws.recv())["com"])
        thought = json.loads(DONNA.ws.recv())["com"][0]
        if usingdrone:
            state = bebop.sensors.flying_state
            print(state)
            if state == "hovering":
                if(thought == "push"): #flying
                    if InTheAir:
                        bebop.fly_direct(roll=0, pitch=0, yaw=0, vertical_movement=30, duration=1)
                        altitude = altitude + 30
                    else:
                        bebop.safe_takeoff(10)
                        InTheAir=True
                elif(thought == "neutral"):
                    if InTheAir:
                        if altitude <= 50:
                            bebop.smart_sleep(1)
                            bebop.safe_land(5)
                            InTheAir=False
                        else:
                            bebop.fly_direct(roll=0, pitch=0, yaw=0, vertical_movement=-30, duration=1)
                            altitude = altitude - 30
                    else:
                        if chillcounter==10:
                            print("j chillin on the ground...")
                            chillcounter=0
                        else:
                            chillcounter+=1
        else:
            if(thought == "push"): #not flying
                print("push command")
            elif(thought == "neutral"):
                print("neutral")
#        simplecount+=1
except KeyboardInterrupt:
    bebop.emergency_land()
#    bebop.smart_sleep(5) #probably not a good idea
#    bebop.disconnect() #probably not a good idea
    print("When drone lands, press enter on prompt.")
    print("But if it doesn't land for a few minutes, you better go chase that sucker!!!")
    input("Prompt: ")
    going = False

