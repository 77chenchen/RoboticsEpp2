import shutil
import sys
import numpy as np
import time
import alex_camera 
import struct
import socket

from connection_params import CAMERA_CONNECTION_PARAMS as CONNECTION_PARAMS

# ==============================================================================
# GLOBAL CONFIGURATION
# ==============================================================================
PORT = "/dev/ttyUSB0"

camera = None 

def camera_connect():
    global camera
    camera = alex_camera.cameraOpen()
    

def camera_capture(): # returns bool of success or not
    retval = False

    
    assert camera is not None, "Camera has not been connected yet!" 


    s = socket.socket()
    s.connect(CONNECTION_PARAMS) 

    try:

        greyscale_arr = alex_camera.captureGreyscaleFrame(camera)
        assert greyscale_arr.dtype == np.uint8, "Camera error: wrong data type, got {}".format(greyscale_arr.dtype) 
        data = greyscale_arr.tobytes()

        header = struct.pack('!II', alex_camera.RENDER_HEIGHT, alex_camera.RENDER_WIDTH)

        s.sendall(header+data)
        retval = True 


    except (BrokenPipeError, ConnectionResetError, OSError) as e:
        print(f"Socket send failed: {e}")
    except KeyboardInterrupt:
        # Move to bottom of the scan area for clean exit
        #sys.stdout.write("\n" * 2)
        print("Scan stopped by user.")
    finally:
        try:
            s.sendall(b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF') #struct.pack('!II', 4294967295, 4294967295)) # -1, -1 is exit
        except OSError:
            # Peer may already be closed.
            pass
        s.close() 
        #ui_show_cursor()
        sys.stdout.flush()

    return retval 

def camera_close():
    if camera is not None:
        alex_camera.cameraClose(camera) 


if __name__ == "__main__":
    camera_connect() 
    print(camera_capture()) 
    camera_close() 
