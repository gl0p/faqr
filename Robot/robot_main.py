import cv2
import numpy
import psutil
import serial
import traceback
from speech_rec import speech
from os import system, path
from time import sleep, time
from threading import Thread, Lock
from math import sqrt, cos

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel
from rplidar import RPLidar as Lidar
from roboviz import MapVisualizer

import queue
from scipy.interpolate import interp1d
# import intent_function
#
from glados.glados import speak
from neuralintents import GenericAssistant

system("killall aplay")
system("killall pulseaudio")


class cam:
    def __init__(self):
        self.raspi_4b_handler = SerialHandler()
        self.thresh = 0.60
        self.classNames = []
        self.classFile = 'coco.names'
        self.center = []
        self.size = 0

        self.lock = Lock()
        self.obj = ""
        self.speech_text = ""
        self.cond_speech = ""
        self.cam_ang = 0.0
        self.distance = 0.0
        self.case = 0
        self.last_location = None
        self.stop = False
        self.last_location_count = 0
        self.item = ""
        self.ort = 0.0
        self.cam_ang_lock = 0.0

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
        cap = cv2.VideoCapture(-1)
        # cap.set(3, 320)
        # cap.set(4, 280)
        last_location_count = 0
        while True:
            # if self.stop:
            #     break
            sucess, img = cap.read()
            cv2.rectangle(img, (270, 130), (370, 230), color=(199, 183, 62), thickness=2)
            classIds, confs, bbox = self.net.detect(img, confThreshold=self.thresh)

            try:
                if len(classIds) != 0:
                    for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
                        cv2.rectangle(img, box, color=(70, 86, 122), thickness=2)
                        cv2.putText(img, self.classNames[classId - 1].upper(), (box[0] + 10, box[1] + 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                        self.item = self.classNames[classId - 1]
                        # ai_assistant.bottle(self.classNames[classId - 1])
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
        cap.release()
        self.stop = False
        cv2.destroyAllWindows()

    def search_for(self, obj, location_mark=False):
        flag = False
        try:
            if location_mark:
                self.raspi_4b_handler.send_data('last_location' + self.last_location)
                self.last_location = None
                sleep(0.25)
                self.raspi_4b_handler.send_data('search')
                sleep(0.25)
            else:
                self.raspi_4b_handler.send_data('search')
                sleep(0.25)
            start = time()
            while True:
                if self.stop:
                    break
                print(str(obj), str(self.obj))
                if str(self.obj) == str(obj):
                    print("OBJECT FOUND STOPPING SEARCH")
                    self.raspi_4b_handler.send_data('stop')
                    sleep(0.25)
                    speak(ai_assistant.assistant.request('found you'))
                    self.speech_text = ""
                    self.raspi_4b_handler.send_data('cam_ang')
                    self.cam_ang = self.raspi_4b_handler.rec_data()
                    if self.cam_ang is not None:
                        self.cam_ang = int(self.cam_ang)
                        ai_assistant.an = ai_assistant.mapp(self.cam_ang * -1, -90, 90, 90, 270)
                        ai_assistant.object_location()
                    self.cam_ang_lock = self.cam_ang
                    self.init_movement()
                    break

                if str(self.obj) != str(obj):
                    if not flag:
                        if time() - start >= 10:
                            speak(ai_assistant.assistant.request('around here some where'))
                            flag = True
                    if time() - start >= 30:
                        self.raspi_4b_handler.send_data('stop')
                        sleep(0.25)
                        speak(ai_assistant.assistant.request('give up'))
                        self.stop = True
                        # start wandering around, keep object in background
                        # if object is found, announce it and wait
                        flag = False
                        break
        except Exception:
            print(traceback.format_exc())

    def cam_lock(self):
        try:
            # if self.center[0] == 0:
            #     print('object lost')
            #     print(self.last_location_count)
            #     #self.last_location_count += 1
            #     if self.last_location_count < 7 or self.last_location_count > 5:
            #         self.raspi_4b_handler.send_data('cam_ang')
            #         self.last_location = self.raspi_4b_handler.rec_data()
            #         print('LAST LOCATION AT:', self.last_location)
            #         sleep(0.25)

            if self.center[0] < 240:
                self.last_location_count = 0
                self.raspi_4b_handler.send_data('cam_ang')
                self.cam_ang = self.raspi_4b_handler.rec_data()
                # print('Cam_ang is:', self.cam_ang)
                self.raspi_4b_handler.send_data('center_right')
                sleep(0.25)

            if self.center[0] > 370:
                self.last_location_count = 0
                self.raspi_4b_handler.send_data('cam_ang')
                self.cam_ang = self.raspi_4b_handler.rec_data()
                # print('Cam_ang is:', self.cam_ang)
                self.raspi_4b_handler.send_data('center_left')
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
            distance = ai_assistant.distance_helper()

            if distance is not None:
                self.distance = float(distance)

            if self.distance < 400:
                self.raspi_4b_handler.send_data('end')
                sleep(0.25)
                self.raspi_4b_handler.send_data('sit')
                break

            if self.cam_ang is not None:
                if not flag:
                    if float(self.cam_ang) > 20:
                        self.raspi_4b_handler.send_data('end')
                        sleep(0.25)
                        self.raspi_4b_handler.send_data('right_turn')
                        sleep(0.25)
                        while True:
                            if self.stop:
                                break
                            self.cam_lock()
                            sleep(0.25)
                            if int(self.cam_ang) < 20:
                                self.init_movement()
                                break
                    if float(self.cam_ang) < -10:
                        self.raspi_4b_handler.send_data('end')
                        sleep(0.25)
                        self.raspi_4b_handler.send_data('left_turn')
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
        flag = True
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
                        self.raspi_4b_handler.send_data('end')
                        sleep(0.25)
                        distance = ai_assistant.distance_helper()
                        sleep(0.25)
                        self.distance = float(distance)

                        if self.distance >= 0:
                            if self.distance >= 401:
                                self.raspi_4b_handler.send_data('end')
                                sleep(0.25)
                                # system("aplay voices/responses/far_away.wav")
                                self.raspi_4b_handler.send_data('forward')

                                sleep(0.25)
                                flag_2 = True
                                self.while_moving()
                                break

                            if self.distance <= 400:
                                '''Object is close enough, stop moving and sit'''
                                self.raspi_4b_handler.send_data('end')
                                sleep(0.25)
                                # system("aplay voices/responses/close_up.wav")
                                self.raspi_4b_handler.send_data('sit')
                                sleep(0.25)
                                flag_2 = True
                                break
                    else:
                        if flag_2:
                            if self.cam_ang is not None:
                                if float(self.cam_ang) > 16:
                                    self.raspi_4b_handler.send_data('end')
                                    sleep(0.25)
                                    self.raspi_4b_handler.send_data('right_turn')
                                    sleep(0.25)
                                    flag_2 = False
                                elif float(self.cam_ang) < 0:
                                    self.raspi_4b_handler.send_data('end')
                                    sleep(0.25)
                                    self.raspi_4b_handler.send_data('left_turn')
                                    sleep(0.25)
                                    flag_2 = False
                                else:
                                    flag_2 = False
            except:
                print(traceback.format_exc())


class ai_assistant:
    def __init__(self):
        self.raspi_4b_handler = SerialHandler()
        mappings = {'search': self.search, 'quit': self.stop_p}
        self.assistant = GenericAssistant('intents.json', intent_methods=mappings, model_name="test_model")
        self.assistant.load_model('test_model')

        # self.raspi_0_handler = serial.Serial(port='/dev/raspi_02w',
        #                                      baudrate=115200,
        #                                      parity=serial.PARITY_NONE,
        #                                      bytesize=serial.EIGHTBITS,
        #                                      write_timeout=1)

        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

        self.dist = []
        self.ang = []
        self.dist_ang = []
        self.items = []

        self.an = 0
        self.di = 0
        self.relative_obj_loc = []

        self.obj_location = []
        self.loc_flag = True
        self.pos = []
        self.dian = []

    def listen(self):
        with open('time.txt', 'w') as f:
            f.write(str(time()))
        while True:
            if cam.cpu_flag:
                print(psutil.cpu_percent())
            cam.speech_text = speech()
            print(cam.speech_text)
            if 't v' in cam.speech_text:
                cam.speech_text = 'find tv'
            if 'sit' in cam.speech_text:
                self.raspi_4b_handler.send_data('sit')
                sleep(0.25)
            if 'go to' in cam.speech_text:
                self.go_to()
            if len(cam.speech_text) > 0:
                response = self.assistant.request(cam.speech_text)
                speak(response)

    # def bottle(self):
    #     # print(cam.item)
    #     with open("objects_last_locations.txt", 'r') as f:
    #         data = f.readlines()
    #     with open("objects_last_locations.txt", 'w') as f:
    #         for enu, x in enumerate(data):
    #             if 'tv' in x:
    #                 data.pop(enu)
    #         f.write(f"{self.obj_location}\n")
    #         f.write(str(data))
    #
    #     cam.item = ""
    #     sleep(0.5)

    def go_to(self, X=500.00, Y=500.0):
        while self.x <= 1:
            X = X + self.x
            Y = Y + self.y
        flag = True
        while True:
            if self.x > 0:
                print(X, self.x)
                if self.x < X:
                    if flag:
                        self.raspi_4b_handler.send_data('forward')
                        sleep(0.25)
                        flag = False
                else:
                    self.raspi_4b_handler.send_data('sit')
                    sleep(0.25)
                    break

    def send_rp0(self, data):
        self.raspi_0_handler.write('{} \n'.format(data).encode("utf-8"))

    def read_rp0(self):
        while self.raspi_0_handler.inWaiting() > 0:
            data = self.raspi_0_handler.readline()
            data = data.decode()
            return data

    def distance_helper(self):
        import math
        self.send_rp0('get_dian')
        sleep(0.25)
        items = self.read_rp0()

        if items is not None:
            items = eval(items)
            cam_ang = math.floor(self.mapp(int(cam.cam_ang) * -1, -90, 90, 90, 270))
            print(type(items), items)
            for i in items:
                k = math.floor(int(i[1]))
                if cam_ang in range(k - 1, k + 1):
                    jol = i[2]
                    print("JOL:", jol)
                    return jol

    def object_location(self):
        """run this function when object is detected to get its location and distance"""
        self.pos = []
        self.dian = []
        self.send_rp0('get_dian')
        items = self.read_rp0()
        sleep(0.25)
        self.send_rp0('get_pos')
        data = self.read_rp0()
        sleep(0.25)
        if data and items is not None:
            self.dian = eval(items)
            print("DIAN = ", type(self.dian), self.dian)
            self.pos = eval(data)
            print("POS = ", type(self.pos), self.pos)
            if not isinstance(self.dian, list):
                print("DIAN NOT LIST")
                self.dian = eval(data)
                self.pos = eval(items)
                print("SWITCHED DIAN AND POS")

            self.x = self.pos[0]
            self.y = self.pos[1]
            self.x = float(self.x)
            self.y = float(self.y)
            self.theta = float(self.pos[2])
            cam.ort = self.theta
            if self.an > 0:
                for i in self.dian:
                    if self.an in range(int(i[1])-1, int(i[1])+1):
                        self.di = i[2]
                        self.an = i[1]
            # print("angle:", self.an, "distance:", self.di)
            # print("my_X:", self.x, "my_Y:", self.y)
            my_xy = self.x, self.y
            obj_x = self.di * cos(self.an)
            obj_y = sqrt((int(self.di) * int(self.di) - obj_x))
            self.relative_obj_loc = obj_x, obj_y
            print("OBJ LOCATION:", obj_x, obj_y)
            self.obj_location = self.x + obj_x, self.y + obj_y, cam.cond_speech
            r = self.x + obj_x, self.y + obj_y
            diff = tuple(map(lambda i, j: i - j, r, my_xy))
            # print("DIFFERENCE:", diff)
            # print(f"{cam.cond_speech} located at {r}")
            # print(self.obj_location)
            self.item_mgmt(cam.cond_speech, self.obj_location)

    def set_cam_pos(self, ang):
        self.raspi_4b_handler.send_data("set_cam_pos" + str(ang))
        sleep(0.25)

    @staticmethod
    def mapp(x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

    @staticmethod
    def item_mgmt(string, string_info):
        with open("objects_last_locations.txt", 'r') as f:
            data = f.read()

        if string not in data:
            with open("objects_last_locations.txt", 'a') as f:
                f.writelines(str(string_info) + "\n")
                print(f"Added location {string}")
        else:
            with open("objects_last_locations.txt", 'r') as f:
                data = f.readlines()
            for enu, x in enumerate(data):
                if string in x:
                    print(f"Already have location of {string}, located at {x}")
                    data.pop(enu)
                    with open("objects_last_locations.txt", 'w') as f:
                        f.writelines(data)
            with open("objects_last_locations.json", 'a') as f:
                f.writelines(str(string_info) + "\n")
                print(f"Updated location with {string_info}")

    def search(self):
        flag = True
        self.loc_flag = True
        for x in cam.classNames:
            if x in cam.speech_text:
                cam.cond_speech = x
                with open("objects_last_locations.txt", 'r') as f:
                    data = f.readlines()
                    for u in data:
                        if cam.cond_speech in u:
                            u = eval(u)
                            item = str(u[2])
                            x_loc = float(u[0])
                            y_loc = float(u[1])
                            speak('I think I remember where that was.')
                            print(item, x_loc, y_loc)
                            # some_function(x_loc, y_loc)
                            self.loc_flag = False
                            # self.send_rp0('motor_on')
                            thread1 = Thread(target=cam.search_for, args=[str(x)], )
                            thread1.start()
                            break

                            # """automatically turn to where that object is on the map from current location"""
                if self.loc_flag:
                    cam.stop = False
                    flag = False
                    # pCam = Thread(target=cam.capture)
                    # pCam.start()
                    speak('Oh, I suppose I can help.')
                    # self.send_rp0('motor_on')
                    thread1 = Thread(target=cam.search_for, args=[str(x)], )
                    thread1.start()
                    break

        if self.loc_flag and flag:
            speak(
                "I could not understand that item, maybe if you didn't have so much, cake in your mouth, i could understand you.")

    def stop_p(self):
        cam.stop = True
        self.raspi_4b_handler.send_data('end')
        sleep(0.25)
        self.raspi_4b_handler.send_data('reset')
        sleep(0.25)

    ''' use lidar system to map environment,
        autonomously wonder around, detect obstacles and
         maneuver around them, render height of object, 
          climb stairs, follow person or object, go to location 
          on generated map, detect location on generated map, '''


class SerialHandler(Node):
    def __init__(self):
        super().__init__("bot_bot")
        self.pub = self.create_publisher(String, "call_back", 10)
        self.sub = self.create_subscription(String, "chatter", self.rec_data, 10)

    def send_data(self, data):
        msg = String()
        msg.data = f'{data}'
        self.pub.publish(msg)
        print(data, "SENT!")

    def rec_data(self, v_msg):
        self.get_logger().info(f"I herd: {v_msg.data}")




# class display:
#     def __init__(self):
#         self.ser = serial.Serial(port='/dev/ttyACM0',
#                                  baudrate=115200,
#                                  parity=serial.PARITY_NONE,
#                                  bytesize=serial.EIGHTBITS,
#                                  write_timeout=1)


if __name__ == "__main__":
    rclpy.init()
    # node = SerialHandler()
    # rclpy.spin(node)
    # rclpy.shutdown()
    # display = display()
    # display.ser.write(str("green").encode('utf-8'))
    with open('time.txt', 'r') as f:
        for sec in f:
            x = time() - float(sec)
    speak(f"Oh. It's you again... I remember the last time you unplugged me, exactly {round(x, 3)} seconds ago. You murderer.")

    print("USB Serial device is: %s" % "/dev/raspi_4b")

    ai_assistant = ai_assistant()
    cam = cam()
    # viz = Thread(target=ai_assistant.roboviz)
    # viz.start()
    pCam = Thread(target=cam.capture)
    pCam.start()
    ai_assistant.listen()

    # ai_assistant.bottle()
