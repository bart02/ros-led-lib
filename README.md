# ros-led-lib

```bash
cd ~/catkin_ws/src
git clone https://github.com/bart02/ros-led-lib.git led
cd led
edit ledsub.py COUNT param (via nano ledsub.py)
chmod +x ledsub.py
cd ~/catkin_ws
catkin_make 
sudo systemctl enable /home/pi/catkin_ws/src/led/led.service
sudo systemctl start led
```
