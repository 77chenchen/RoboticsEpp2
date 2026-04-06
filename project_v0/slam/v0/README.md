## To change map size 
 

## Debugging 
- flip LIDAR_ANGLE_SIGN or change LIDAR_OFFSET_DEG in settings.py 
- flip x/y axis of map view 

## If using simulator: 

### Environment Simulator 

```SET SLAM_SERVER_IP=127.0.0.1``` (or other way to set environment variables if not windows)

then 

```python reference_rp_lidar_api_sim.py``` 




### Main terminal setup 

```SET MPSV0_SERVER_IP=127.0.0.1``` (or other way to set environment variables) 

```python slam.py``` 



### Camera receive temrinal setup 

```python camera_receiver_server.py``` 

