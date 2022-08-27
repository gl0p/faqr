import traceback
import cv2
import serial
from speech_rec import speech
from os import system, path
from threading import Thread
import threading
from time import sleep, time
from usb_scan import main


var = ""
last_var = ""
names = []
text = ""
g_flag = True
distance = 0.0
s_flag = False

class cam:
    def __init__(self):
        global names
        self.thresh = 0.6
        self.cap = cv2.VideoCapture(-1)
        self.cap.set(3, 320)
        self.cap.set(4, 280)
        self.classNames = []
        self.classFile = 'coco.names'
        self.voice = ""
        self.center = []
        self.distance = 0
        self.size = 0

        with open(self.classFile, 'rt') as f:
            self.classNames = f.read().rstrip('\n').split('\n')
            names = self.classNames

        self.configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
        self.weightsPath = 'frozen_inference_graph.pb'

        self.net = cv2.dnn_DetectionModel(self.weightsPath, self.configPath)
        self.net.setInputSize(320, 320)  # 320, 320
        self.net.setInputScale(1.0 / 127.5)  # 1.0/127.5
        self.net.setInputMean((127.5, 127.5, 127.5))  # 127.5, 127.5, 127.5
        self.net.setInputSwapRB(True)
        self.usb_path = main()
        self.serial_data = ""


    def capture(self):
        global var
        global last_var
        global text
        global distance
        global g_flag
        global s_flag
        while True:
            sucess, img = self.cap.read()
            try:
                classIds, confs, bbox = self.net.detect(img, confThreshold=self.thresh)
            except cv2.error:
                print("Webcam not attached!")
                break
            try:
                if len(classIds) != 0:
                    for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
                        cv2.rectangle(img, box, color=(70, 86, 122), thickness=2)
                        cv2.putText(img, self.classNames[classId - 1].upper(), (box[0] + 10, box[1] + 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                        cv2.putText(img, str(round(confidence * 100, 2)), (box[0] + 10, box[1] + 60),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    item = self.classNames[int(classId - 1)]
                    self.voice = self.classNames[int(classId - 1)]
                    current_object = text
                    s_flag = False
                    g_flag = False
                    for z in names:     ### OBJECT CLASSIFIER ###
                        if z in current_object and z == item:
                            try:
                                self.center = [int(box[0] + int(box[2]) / 2), int(box[1] + int(box[3]) / 2)]
                                width = self.center[0]
                                height = self.center[1]
                                size = height * width
                                self.size = size / 1000
                                cv2.circle(img, self.center, 5, color=(255, 0, 0), thickness=2)
                                s_flag = True
                                g_flag = True
                            except:
                                print(traceback.format_exc())
                cv2.imshow("OUTPUT", img)
                cv2.waitKey(1)
            except:
                print(traceback.format_exc())

    def send_center(self):
        global g_flag
        global s_flag
        while True:
            if g_flag:
                cam.send_data('stop')
                g_flag = False
            if 'replace_stop' in self.serial_data:
                g_flag = True
                self.serial_data = ""
            if s_flag:
                cam.send_data('center')
                cam.send_data(self.center)



    def rec_data(self):
        global distance
        sr = serial.Serial(port=str(self.usb_path),
                           baudrate=115200,
                           parity=serial.PARITY_NONE,
                           bytesize=serial.EIGHTBITS,
                           timeout=1)
        while True:
            while sr.inWaiting() > 0:
                data = sr.readline()
                data = str(data.decode())
                if "distance" in data:
                    distance = data.replace('distance', '')
                    distance = float(distance)
                    print(distance)
                else:
                    self.serial_data = data
                sleep(0.05)

    def send_data(self, data):
        ser = serial.Serial(port=str(self.usb_path),
                            baudrate=115200,
                            parity=serial.PARITY_NONE,
                            bytesize=serial.EIGHTBITS,
                            write_timeout=1)
        ser.reset_output_buffer()
        ser.flushOutput()
        if not ser.out_waiting > 0:
            if 'center' in data:
                ser.write('center'.encode('utf-8'))
                ser.flush()
            else:
                ser.write('{} \n'.format(data).encode('utf-8'))
                ser.flushOutput()
                sleep(0.01)

    def search_for(self, obj):
        global gen
        global last_var
        global var
        global text
        global distance
        flag = False
        gen = False
        try:
            #print(type(obj), obj)
            for x in names:
                #print(x)
                if obj != x:
                    gen = True
                else:
                    gen = False
                    break

            if gen:
                if var == 'hello':
                    print("HELLO THERE!!!")
                    system("aplay voices/hello.wav")
                    last_var = ""

                else:
                    system("aplay voices/dont_know.wav")
                    last_var = ""

            if not gen:
                if path.isfile("voices/%s.wav" % str(obj)):
                    cam.send_data('search')
                    print('Sent Data: search')

                    system("aplay voices/search_for.wav")
                    system("aplay voices/'%s'.wav" % str(obj))
                    start = time()
                    while True:
                        if str(self.voice) == str(obj):
                            last_var = ""
                            system("aplay voices/found_you.wav")
                            print(type(distance), distance)
                            sleep(1)
                            if not flag:
                                if time() - start >= 5:
                                    system("aplay voices/around_here.wav")
                                    flag = True
                            if time() - start >= 20:
                                #cam.send_data('e')
                                system("aplay voices/give_up.wav")
                                last_var = ""
                                flag = False
                                break

                            if distance >= 5:
                                if text == "person":
                                    sleep(0.5)
                                    system("aplay voices/person_murder_joke.wav")
                                    if distance >= 81:
                                        cam.send_data('f')
                                        print('Sent Data: f')
                                    if distance <= 80:
                                        cam.send_data('b')
                                        print('Sent Data: b')
                                    break
                                if distance >= 81:
                                    system("aplay voices/far_away.wav")
                                    cam.send_data('f')
                                    print('Sent Data: f')
                                if distance <= 80:
                                    system("aplay voices/close_up.wav")
                                    cam.send_data('b')
                                    print('Sent Data: b')
                                break


                else:
                    while not path.isfile("voices/%s.wav" % str(obj)):
                        print("DOWNLOADING", obj)
                        system("aplay voices/wait.wav")
                        system("curl -L --get --fail --data-urlencode 'text=%s' -o 'voices/%s.wav' "
                                "'https://glados.c-net.org/generate'" % (str(obj), str(obj)))
                        print("Download of %s.wav complete" % str(obj))
                        if path.isfile("voices/%s.wav" % str(obj)):
                            system("aplay voices/stuffed_face_response.wav")
                            system("aplay voices/'%s'.wav" % str(obj))
                            last_var = ""
                            cam.search_for(obj)

        except Exception:
            print(traceback.format_exc())



if __name__ == "__main__":
    print("USB Serial device is: %s" % main())

    cam = cam()
    thread0 = Thread(target=cam.rec_data)
    thread1 = Thread(target=cam.capture)
    thread0.start()
    thread1.start()
    while True:
        var = speech()
        print(var)
        if 't v' in var:
            var = 'tv'
        if "cake" in var:
            print("CAKE!!!!!!!!!!!!!!!!!")
            system("aplay voices/no_cake.wav")
        if var != last_var:
            if var == 'hello':
                print("HELLO THERE!!!")
                system("aplay voices/hello.wav")
                last_var = ""
            if "find" or "look" or "search" in var:
                for x in names:
                    if x in var:
                        text = x
                        cam.search_for(str(x))
