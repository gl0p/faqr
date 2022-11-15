# FAQR V2.0 (Comming soon with ros2)
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

Setting up each USB serial device (arduino and both pi's) are better to symlink tty address with a unique name incase of swapping of ports occures when device is reset or powered off. Since raspberry pi's may have the same vendor and product id, using manufacture attribute may be benificial in place of product id. If using two identical products, other attributes may need to be used instead as an "unique identifier" for the device when symlinking. Follow https://unix.stackexchange.com/questions/66901/how-to-bind-usb-device-under-a-static-name for instructions. 

## How it works:

MainNode handles all I/O operations for peripheral scripts including but not limited to opencv object detection, speech, lidar, movement control, determining object location... etc.

Raspi Bot executes requests from MainNode for physical movement of servos and sends back servo posistion data.

On startup, MainNode starts speech_to_txt.py and vision.py. After initialization, it is in a "waiting" state, waiting for user input. So far "find" or "I am looking for" and several other keywords are programmed to get a response. If the user does not state a command within a random time peroid, it will begin to map out its surroundings with objects location. Creating a somewhat detailed map where objects are located in a room.

### Finding Things

When asked to "find" an object speech_to_txt sends the input to MainNode. MainNode then runs main() to send a request back to speech_to_txt for text to speech output if a response is generated from intents.json. Otherwise the variable mappings will run a function. In this case "find" will result in executing begin_search() and will also save the request to self.word. 

begin_search() will search coco.names for matches in self.word for finding the desired object. If there is a match, begin_search() will send self.word to vision.py and also send "search" to Raspi Bot to start rotating the camera left and right, "scanning" the area 180°.

Once the object has been found, vision.py will show a circle in the center of the object and will end search() and enable lidar support. This "center" data will also be sent to MainNode to determine where to rotate the camera, either left or right and will send a "center_left" or "center_right" to Raspi Bot to adjust the camera posistion to "center" the object. MainNode will also keep track of the object movement with lft_rht_chk() and save the value in self.hztl. If the object is lost for more than a set peroid of time MainNode will use self.hztl for the last known direction and will send rquests to Raspi Bot to move the camera in the same direction untill the object is found again. If the object is still not found when the servo reaches the max value, then search() will be called again. 

After locking onto the object MainNode will start requesting lidar data. By using the distance referenced by ±1° of the camera servo angle, the relative location of the object can be determined by: 

                                                obj_x = distance*cos(angle)
                                                obj_y = √(distance^2-x)
                                                
                                                Then added to the robots x, y location from lidar.

After the location and distance is determined, MainNode will send a request to Raspi Bot to either rotate left or right or move towards the object. If the object is close enough by a set distance it will send a "sit" request to Raspi Bot and will sit in place. Waiting for user input again.

During the handling of the movement, interupts are handled via "break" within the loops. If needing to change direction or stop moving, MainNode will send a "stop" request to Raspi Bot first before issuing the next command.


                                             
                                                
                                                            









            
              
              
