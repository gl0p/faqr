# FAQR
## Fully Autonomous Quadruped Robot 

Ask it to find something and it will walk right up to it. Ask it to follow you, and it will stalk you. Tell it to stop and it will wait right there. Just dont ask it for cake.

Uses coco.names, a list of 91 objects you can ask it to find. 


### Build Uses:

            UDOO Bolt V8
            Raspberry Pi 4B 2 gb (in serial mode)
            Raspberry Pi Zero 2 (in serial mode with UART enabled (for RpLidar))
            Webcam
            Sonar (HC-SR04) **Soon to be replaced with LIDAR
            13 servos (12 for movement, 1 for cam rotation)
            5.2 Ah 7.4 Volt lithium battery for servos
            PD Battery pack for remote operation
            1 or 2 speakers (amplifier optional)
            RpLidar 
           
            You might be able to get away with three Raspberry Pi's and an arduino.

## Soon to come: 

              Stair recognition and climbing
              LIDAR Support (replaces sonar), *IN PROGRESS*
              Room Mapping *IN PROGRESS*
              Last object location *IN PROGRESS*
              Waypoint GoTo from generated map *IN PROGRESS*
              Autonomous lingering (wanlking around when nothing to do, search the room to update map)
              Android app??? 
              Speech intention *IN PROGRESS*
              Lights or vocal display *IN PROGRESS*
              AI incorperation other than cam and speech
              
              
## Notes:

Setting up each USB serial device (arduino and both pi's) are better to symlink tty address with a unique name incase of swapping of ports occures when device is reset or powered off. Since raspberry pi's may have the same vendor and product id, using manufacture attribute may be benificial in place of product id. If using two identical products, other attributes may need to be used instead as an "unique identifier" for the device when symlinking. Follow https://unix.stackexchange.com/questions/66901/how-to-bind-usb-device-under-a-static-name 


            
              
              
