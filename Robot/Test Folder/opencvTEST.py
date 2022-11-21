import cv2
import psutil
import serial
import traceback
from speech_rec import speech
from os import system, path
from time import sleep, time
from usb_scan import main
from threading import Thread, Lock
from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel
from rplidar import RPLidar as Lidar
from roboviz import MapVisualizer
import queue
# import intent_function
#
# from glados.glados import speak
from neuralintents import GenericAssistant



system("killall aplay")
system("killall pulseaudio")


class cam:
    def __init__(self):
        self.thresh = 0.7
        self.cap = cv2.VideoCapture(-1)
        self.cap.set(3, 320)
        self.cap.set(4, 280)
        self.classNames = []
        self.classFile = 'coco.names'
        self.center = []
        self.size = 0

        self.lock = Lock()
        self.usb_path = main()
        self.obj = ""
        self.speech_text = ""
        self.cond_speech = ""
        self.cam_ang = 0.0
        self.distance = 0.0
        self.case = 0
        self.last_location = None
        self.stop = False
        self.last_location_count = 0

        self.cpu_flag = False

        with open(self.classFile, 'rt') as f:
            self.classNames = f.read().rstrip('\n').split('\n')

        self.configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
        self.weightsPath = 'frozen_inference_graph.pb'

        self.net = cv2.dnn_DetectionModel(self.weightsPath, self.configPath)
        self.net.setInputSize(500, 200)  # 320, 320 BEST (500, 200)
        self.net.setInputScale(1.0 / 127.5)  # 1.0/127.5
        self.net.setInputMean((127.5, 127.5, 127.5))  # 127.5, 127.5, 127.5
        self.net.setInputSwapRB(True)

    def capture(self):
        last_location_count = 0
        while True:
            print(self.stop)
            if self.stop:
                cv2.destroyAllWindows()
                self.stop = False
                break
            sucess, img = self.cap.read()
            print(img)
            cv2.rectangle(img, (270, 130), (370, 230), color=(199, 183, 62), thickness=2)
            # try:
            classIds, confs, bbox = self.net.detect(img, confThreshold=self.thresh)
            # except cv2.error:
            #     print("Webcam not attached!")
            #     break
            try:
                if len(classIds) != 0:
                    for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
                        cv2.rectangle(img, box, color=(70, 86, 122), thickness=2)
                        cv2.putText(img, self.classNames[classId - 1].upper(), (box[0] + 10, box[1] + 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                        cv2.putText(img, str(round(confidence * 100, 2)), (box[0] + 10, box[1] + 60),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    item = self.classNames[int(classId - 1)]
                    self.obj = item

                    self.center = [0, 0]
                    self.last_location_flag = False
                    for z in self.classNames:  ### OBJECT CLASSIFIER, found object ###
                        if z in self.cond_speech and z == item:
                            try:
                                self.center = [int(box[0] + int(box[2]) / 2), int(box[1] + int(box[3]) / 2)]
                                cv2.circle(img, self.center, 5, color=(255, 0, 0), thickness=2)

                            except:
                                print(traceback.format_exc())


                cv2.imshow("OUTPUT", img)
                cv2.waitKey(1)


            except:
                print(traceback.format_exc())

    def search_for(self, obj, location_mark=False):
        flag = False
        gen = False
        try:
            for x in self.classNames:
                if obj != x:
                    gen = True
                else:
                    gen = False
                    break

            if gen:
                system("aplay --buffer-size=0 voices/responses/dont_know.wav &")

            if not gen:
                if path.isfile("voices/objects/%s.wav" % str(obj)):
                    if "cake" in self.speech_text:
                        speak('Lets get some cake then you fat fuck')
                    # system("aplay --buffer-size=0 voices/responses/search_for.wav")
                    # system("aplay --buffer-size=0 voices/objects/'%s'.wav" % str(obj))
                    sleep(0.25)
                    if location_mark:
                        serialHandler.send_data('last_location' + self.last_location)
                        self.last_location = None
                        sleep(0.25)
                        serialHandler.send_data('search')
                        sleep(0.25)
                    else:
                        serialHandler.send_data('search')
                        sleep(0.25)
                    start = time()
                    while True:
                        if self.stop:
                            break
                        if str(self.obj) == str(obj):
                            serialHandler.send_data('stop')
                            sleep(0.25)
                            speak(ai_assistant.assistant.request('found you'))
                            self.speech_text = ""
                            serialHandler.send_data('cam_ang')
                            self.cam_ang = serialHandler.rec_data()
                            self.init_movement()
                            break

                        if str(self.obj) != str(obj):
                            if not flag:
                                if time() - start >= 10:
                                    speak(ai_assistant.assistant.request('around here some where'))
                                    flag = True
                            if time() - start >= 30:
                                serialHandler.send_data('stop')
                                sleep(0.25)
                                speak(ai_assistant.assistant.request('give up'))
                                self.stop = True
                                # start wandering around, keep object in background
                                # if object is found, announce it and wait
                                flag = False
                                break
                else:
                    while not path.isfile("voices/objects/%s.wav" % str(obj)):
                        print("DOWNLOADING", obj)
                        system("aplay --buffer-size=0 voices/responses/wait.wav")
                        system("curl -L --get --fail --data-urlencode 'text=%s' -o 'voices/objects/%s.wav' "
                               "'https://glados.c-net.org/generate'" % (str(obj), str(obj)))
                        print("Download of %s.wav complete" % str(obj))
                        if path.isfile("voices/objects/%s.wav" % str(obj)):
                            system("aplay --buffer-size=0 voices/responses/stuffed_face_response.wav")
                            system("aplay --buffer-size=0 voices/objects/'%s'.wav" % str(obj))
                            self.search_for(obj)

        except Exception:
            print(traceback.format_exc())

    def cam_lock(self):
        try:
            # if self.center[0] == 0:
            #     print('object lost')
            #     print(self.last_location_count)
            #     #self.last_location_count += 1
            #     if self.last_location_count < 7 or self.last_location_count > 5:
            #         serialHandler.send_data('cam_ang')
            #         self.last_location = serialHandler.rec_data()
            #         print('LAST LOCATION AT:', self.last_location)
            #         sleep(0.25)

            if self.center[0] < 270:
                self.last_location_count = 0
                serialHandler.send_data('cam_ang')
                self.cam_ang = serialHandler.rec_data()
                print('Cam_ang is:', self.cam_ang)
                serialHandler.send_data('center_right')
                sleep(0.25)

            if self.center[0] > 370:
                self.last_location_count = 0
                serialHandler.send_data('cam_ang')
                self.cam_ang = serialHandler.rec_data()
                print('Cam_ang is:', self.cam_ang)
                serialHandler.send_data('center_left')
                sleep(0.25)
            if self.cam_ang is not None:
                return self.cam_ang
        except:
            pass

    def while_moving(self):
        flag = False
        while True:
            if self.stop:
                self.stop = False
                break
            if self.cpu_flag:
                print(psutil.cpu_percent())
            self.cam_lock()
            serialHandler.send_data('distance')
            sleep(0.25)
            distance = serialHandler.rec_data()

            if distance is not None:
                self.distance = float(distance)

            if self.distance < 60:
                serialHandler.send_data('end')
                sleep(0.25)
                serialHandler.send_data('sit')
                break

            if self.cam_ang is not None:
                if not flag:
                    if float(self.cam_ang) > 20:
                        serialHandler.send_data('end')
                        sleep(0.25)
                        serialHandler.send_data('right_turn')
                        sleep(0.25)
                        while True:
                            if self.stop:
                                break
                            self.cam_lock()
                            sleep(0.25)
                            if int(self.cam_ang) < 20:
                                cam.init_movement()
                                break
                    if float(self.cam_ang) < 0:
                        serialHandler.send_data('end')
                        sleep(0.25)
                        serialHandler.send_data('left_turn')
                        sleep(0.25)
                        while True:
                            if self.stop:
                                break
                            self.cam_lock()
                            sleep(0.25)
                            if float(self.cam_ang) > -10:
                                self.init_movement()
                                break

    def init_movement(self):
        flag_2 = True
        while True:
            if self.stop:
                self.stop = False
                break
            if self.cpu_flag:
                print(psutil.cpu_percent())
            self.cam_lock()
            try:
                if self.cam_ang is not None:
                    if 20 > float(self.cam_ang) > -10:
                        serialHandler.send_data('end')
                        sleep(0.25)
                        serialHandler.send_data('distance')
                        sleep(0.25)
                        distance = serialHandler.rec_data()
                        self.distance = float(distance)

                        if self.distance >= 0:
                            if self.cond_speech == "person":
                                system("aplay voices/responses/person_murder_joke.wav")

                            if self.distance >= 61:
                                serialHandler.send_data('end')
                                sleep(0.25)
                                # system("aplay voices/responses/far_away.wav")
                                serialHandler.send_data('forward')
                                sleep(0.25)
                                flag_2 = True
                                self.while_moving()
                                break

                            if self.distance <= 60:
                                '''Object is close enough, stop moving and sit'''
                                serialHandler.send_data('end')
                                sleep(0.25)
                                system("aplay voices/responses/close_up.wav")
                                serialHandler.send_data('sit')
                                sleep(0.25)
                                flag_2 = True
                                break
                    else:
                        if flag_2:
                            if self.cam_ang is not None:
                                if float(self.cam_ang) > 16:
                                    serialHandler.send_data('end')
                                    sleep(0.25)
                                    serialHandler.send_data('right_turn')
                                    sleep(0.25)
                                    flag_2 = False
                                elif float(self.cam_ang) < 0:
                                    serialHandler.send_data('end')
                                    sleep(0.25)
                                    serialHandler.send_data('left_turn')
                                    sleep(0.25)
                                    flag_2 = False
                                else:
                                    flag_2 = False
            except:
                print(traceback.format_exc())


class ai_assistant(cam):
    def __init__(self):
        super(ai_assistant, self).__init__()
        mappings = {'search': self.search, 'quit': self.stop_p}
        self.assistant = GenericAssistant('intents.json', intent_methods=mappings, model_name="test_model")
        self.assistant.load_model('test_model')

        self.robo_time = 0.0

        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

    def listen(self):
        with open('time.txt', 'w') as f:
            f.write(str(time()))
        while True:
            # print(time()-self.robo_time)
            # if time()-self.robo_time > 2:
            #     rel = Thread(target=ai_assistant.roboviz)
            #     rel.start()
            #     print('RESTARTED ROBOVIZ ???')
            if self.cpu_flag:
                print(psutil.cpu_percent())
            self.speech_text = speech()
            print(self.speech_text)
            if 't v' in self.speech_text:
                self.speech_text = 'find tv'
            if 'sit' in self.speech_text:
                serialHandler.send_data('sit')
                sleep(0.25)
            # if len(self.speech_text) > 0:
            #     response = self.assistant.request(self.speech_text)
            #     speak(response)

    def go_to(self, X=0.0, Y=0.0):
        current_pos = self.x, self.y

    def roboviz(self):

        MAP_SIZE_PIXELS = 128
        MAP_SIZE_METERS = 10
        LIDAR_DEVICE = '/dev/ttyUSB0'
        MIN_SAMPLES = 80

        lidar = Lidar(LIDAR_DEVICE)
        lidar.reset()
        slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)
        viz = MapVisualizer(MAP_SIZE_PIXELS, MAP_SIZE_METERS, 'SLAM')
        mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)
        iterator = lidar.iter_scans()
        previous_distances = None
        previous_angles = None
        print("Restarting LIDAR...")

        next(iterator)

        # slam.update(a, scan_angles_degrees=b)
        try:
            while True:
                self.robo_time = time()
                items = [item for item in next(iterator)]
                distances = [item[2] for item in items]
                angles = [item[1] for item in items]
                if len(distances) > MIN_SAMPLES:
                    slam.update(distances, scan_angles_degrees=angles)
                    previous_distances = distances.copy()
                    previous_angles = angles.copy()
                elif previous_distances is not None:
                    slam.update(previous_distances, scan_angles_degrees=previous_angles)

                # Get current robot position
                self.x, self.y, self.theta = slam.getpos()
                # print('X_pos:', self.x/1000, 'Y_pos:', self.y/1000)
                slam.getmap(mapbytes)

                # Display map and robot pose, exiting gracefully if user closes it
                # if not viz.display(self.x / 1000., self.y / 1000., self.theta, mapbytes):
                #     exit(0)
        except:
            print("ERROR")
        #
        # # Shut down the lidar connection
        # lidar.stop()
        # lidar.disconnect()

    def search(self):
        flag = True
        for x in self.classNames:
            if x in self.speech_text:
                self.stop = False
                # pCam = Thread(target=self.capture)
                # pCam.start()
                flag = False
                speak('Oh, I suppose I can help.')
                self.cond_speech = x
                thread1 = Thread(target=self.search_for, args=[str(x)],)
                thread1.start()

        if flag:
            speak("I could not understand that item, maybe if you didn't have so much, cake in your mouth, i could understand you.")

    #@staticmethod
    def stop_p(self):
        self.stop = True
        serialHandler.send_data('stop')
        sleep(0.25)
        serialHandler.send_data('reset')
        sleep(0.25)

    ''' use lidar system to map environment,
        autonomously wonder around, detect obstacles and
         maneuver around them, render height of object, 
          climb stairs, follow person or object, go to location 
          on generated map, detect location on generated map, '''


class SerialHandler:
    def __init__(self, device: str):
        self.device = device
        self.ser = serial.Serial(port=self.device,
                                 baudrate=115200,
                                 parity=serial.PARITY_NONE,
                                 bytesize=serial.EIGHTBITS,
                                 write_timeout=1)
        self.queue_receive = queue.Queue()
        self.queue_send = queue.Queue()

        self.thread_receive = Thread(target=self._run_receive, name="_run_receive")
        self.thread_receive.start()
        self.thread_send = Thread(target=self._run_send, name="_run_send")
        self.thread_send.start()

    def _run_receive(self):
        while True:
            data = self.ser.readline()
            data = data.decode('utf-8')
            data = data.strip()
            self.queue_receive.put(data)

    def _run_send(self):
        while True:
            data = self.queue_send.get()
            self.ser.write(data.encode('utf-8'))

    def send_data(self, data):
        self.queue_send.put(data)
        #print('SENT:', data)

    def rec_data(self, timeout=10):
        """provide a ten sec timeout, will return None in case of timeout"""
        try:
            data = self.queue_receive.get(block=True, timeout=timeout)
            #print('RECEIVED:', data)
            return data
        except queue.Empty:
            return None


serialHandler = SerialHandler(str(main()))


class display:
    def __init__(self):
        self.ser = serial.Serial(port='/dev/ttyACM0',
                            baudrate=115200,
                            parity=serial.PARITY_NONE,
                            bytesize=serial.EIGHTBITS,
                            write_timeout=1)



if __name__ == "__main__":
    # display = display()
    # display.ser.write(str("green").encode('utf-8'))
    # with open('time.txt', 'r') as f:
    #     for sec in f:
    #         x = time()-float(sec)
    # speak(f"Oh. It's you again... I remember the last time you unplugged me, exactly {round(x, 3)} seconds ago. You murderer.")

    # print("USB Serial device is: %s" % main())

    ai_assistant = ai_assistant()
    cam = cam()
    # viz = Thread(target=ai_assistant.roboviz)
    # viz.start()
    # pCam = Thread(target=cam.capture)
    # pCam.start()
    cam.capture()
    #ai_assistant.listen()
