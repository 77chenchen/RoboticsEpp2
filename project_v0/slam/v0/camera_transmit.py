import camera_handler as CameraHandler 
import time 


CameraHandler.camera_connect() 

try: 
    while True: 
        CameraHandler.camera_capture() 
        time.sleep(0.2) 
except KeyboardInterrupt as k: 
    print("Keyboard Interrupt.")
finally: 
    CameraHandler.camera_close() 

