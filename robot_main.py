import cv2
import serial
import traceback
from arduino_scan import returned_port
from speech_rec import speech
from os import system, path
from time import sleep, time
from usb_scan import main
from threading import Thread, Lock


class cam:
    def __init__(self):
        self.thresh = 0.6
        self.cap = cv2.VideoCapture(-1)
        self.cap.set(3, 320)
        self.cap.set(4, 280)
        self.classNames = []
        self.classFile = 'coco.names'
        self.center = []
        self.distance = 0
        self.size = 0

        self.lock = Lock()
        self.usb_path = main()
        self.obj = ""
        self.speech_text = ""
        self.cond_speech = ""
        self.cam_ang = 0.0
        self.distance = 0.0

        with open(self.classFile, 'rt') as f:
            self.classNames = f.read().rstrip('\n').split('\n')

        self.configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
        self.weightsPath = 'frozen_inference_graph.pb'

        self.net = cv2.dnn_DetectionModel(self.weightsPath, self.configPath)
        self.net.setInputSize(320, 320)  # 320, 320
        self.net.setInputScale(1.0 / 127.5)  # 1.0/127.5
        self.net.setInputMean((127.5, 127.5, 127.5))  # 127.5, 127.5, 127.5
        self.net.setInputSwapRB(True)

    def capture(self):
        # print("CAM:", current_process())
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
                    self.obj = item

                    for z in self.classNames:  ### OBJECT CLASSIFIER ###
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

    def rec_data(self):
        start = time()
        sr = serial.Serial(port=str(self.usb_path),
                           baudrate=115200,
                           parity=serial.PARITY_NONE,
                           bytesize=serial.EIGHTBITS,
                           timeout=1)
        while True:
            if time() - start > 10:
                #  system("aplay voices/responses/no_data_response.wav")
                break
            while sr.inWaiting() > 0:
                data = sr.readline()
                data = str(data.decode())
                data = data.replace('\n', '')
                data = data.replace(' ', '')
                return data

    def send_data(self, data):
        self.lock.acquire()
        ser = serial.Serial(port=str(self.usb_path),
                            baudrate=115200,
                            parity=serial.PARITY_NONE,
                            bytesize=serial.EIGHTBITS,
                            write_timeout=1)
        ser.reset_output_buffer()
        ser.flushOutput()
        if not ser.out_waiting > 0:
            ser.write('{} \n'.format(data).encode('utf-8'))
            ser.flushOutput()
            sleep(0.01)
        self.lock.release()

    def search_for(self, obj):
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
                system("aplay voices/responses/dont_know.wav &")

            if not gen:
                if path.isfile("voices/objects/%s.wav" % str(obj)):
                    cam.send_data('search')
                    print('Sent Data: search')

                    system("aplay voices/responses/search_for.wav")
                    system("aplay voices/objects/'%s'.wav" % str(obj))
                    start = time()
                    while True:
                        if str(self.obj) == str(obj):
                            cam.send_data('stop')
                            print("STOP SENT")
                            system("aplay voices/responses/found_you.wav")
                            self.speech_text = ""
                            cam.send_data('cam_ang')
                            self.cam_ang = cam.rec_data()
                            print('Cam ang is:', self.cam_ang)
                            break

                        if str(self.obj) != str(obj):
                            if not flag:
                                if time() - start >= 5:
                                    system("aplay voices/responses/around_here.wav")
                                    flag = True
                            if time() - start >= 20:
                                cam.send_data('stop')
                                system("aplay voices/responses/give_up.wav")
                                flag = False
                                break
                else:
                    while not path.isfile("voices/objects/%s.wav" % str(obj)):
                        print("DOWNLOADING", obj)
                        system("aplay voices/responses/wait.wav")
                        system("curl -L --get --fail --data-urlencode 'text=%s' -o 'voices/objects/%s.wav' "
                               "'https://glados.c-net.org/generate'" % (str(obj), str(obj)))
                        print("Download of %s.wav complete" % str(obj))
                        if path.isfile("voices/objects/%s.wav" % str(obj)):
                            system("aplay voices/responses/stuffed_face_response.wav")
                            system("aplay voices/objects/'%s'.wav" % str(obj))
                            cam.search_for(obj)

        except Exception:
            print(traceback.format_exc())

    def cam_lock(self):
        while True:
            if self.center[0] < 270:
                print('doing cam rotation stuff..')
                print('Center is at:', self.center[0])
                cam.send_data('cam_ang')
                print('In Movement, sending cam_ang signal.')
                self.cam_ang = cam.rec_data()
                print('Cam_ang is:', type(self.cam_ang), self.cam_ang)
                cam.send_data('center_right')
                print()
                sleep(0.25)

            if self.center[0] > 370:
                print('doing cam rotation stuff..')
                print('Center is at:', self.center[0])
                print()
                cam.send_data('cam_ang')
                print('sending cam_ang signal.')
                self.cam_ang = cam.rec_data()
                print('Cam_ang is:', type(self.cam_ang), self.cam_ang)
                cam.send_data('center_left')
                sleep(0.25)

    def movement(self):
        flag = False
        flag_2 = True
        while True:
            sleep(0.5)
            try:
                if 5 > int(self.cam_ang) > -5:
                    if flag:
                        cam.send_data('end')
                        print('Halt sent')
                        flag = False
                        flag_2 = True

                        cam.send_data('distance')
                        distance = cam.rec_data()
                        print("Distance Request sent")
                        self.distance = float(distance)
                        print("Distance received:", distance)

                    if self.distance >= 5:
                        if self.cond_speech == "person":
                            sleep(0.5)
                            system("aplay voices/responses/person_murder_joke.wav &")
                            if self.distance >= 81:
                                cam.send_data('forward')
                                print('Sent Data: forward')
                            if self.distance <= 80:
                                cam.send_data('backward')
                                print('Sent Data: backward')
                        if self.distance >= 81:
                            system("aplay voices/responses/far_away.wav &")
                            cam.send_data('forward')
                            print('Sent Data: forward')

                        if self.distance <= 80:
                            system("aplay voices/responses/close_up.wav &")
                            cam.send_data('backward')
                            print('Sent Data: backward')
                else:
                    if flag_2:
                        print('in rotate loop')
                        sleep(0.25)
                        if int(self.cam_ang) > 5:
                            cam.send_data('right_turn')
                            print('Right Turn Sent')
                            flag = True
                            flag_2 = False
                        if int(self.cam_ang) < -5:
                            cam.send_data('left_turn')
                            flag = True
                            flag_2 = False
            except TypeError:
                pass

    def main(self):
        while True:
            self.speech_text = speech()
            print(self.speech_text)
            if 'stop' in self.speech_text:
                #system('killall aplay')
                cam.send_data('end')
            if self.speech_text == 'hello':
                print("HELLO THERE!!!")
                system("aplay voices/responses/hello.wav &")
            if 't v' in self.speech_text:
                self.speech_text = 'tv'
            if "cake" in self.speech_text:
                print("CAKE!!!!!!!!!!!!!!!!!")
                system("aplay voices/responses/no_cake.wav")
            if "find" or "look" or "search" in self.speech_text:
                for x in self.classNames:
                    if x in self.speech_text:
                        print(x)
                        self.cond_speech = x
                        cam.search_for(str(x))
                        camLock = Thread(target=cam.cam_lock)
                        camLock.start()
                        #cam.movement()




if __name__ == "__main__":
    print("USB Serial device is: %s" % main())
    cam = cam()
    pCam = Thread(target=cam.capture)
    pCam.start()
    move = Thread(target=cam.movement)
    move.start()
    cam.main()
