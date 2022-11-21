#!/usr/bin/env python

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

import cv2
import traceback
from threading import Thread
from time import sleep



class Cam(Node):
    def __init__(self):
        super().__init__("cam_node") # Node Name #
        self.cam_sub = self.create_subscription(String, "cam_search", self.name_to_var, 10)
        self.cam_pub = self.create_publisher(String, "cam_return", 10)

        # set cam variables #
        self.thresh = 0.63
        self.classNames = []
        self.classFile = 'coco.names'
        self.center = [1, 0]
        self.obj = ""
        self.item = ""
        self.search_flag = True
        self.found = False

        with open(self.classFile, 'rt') as f:
            self.classNames = f.read().rstrip('\n').split('\n')
        self.configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
        self.weightsPath = 'frozen_inference_graph.pb'
        self.net = cv2.dnn_DetectionModel(self.weightsPath, self.configPath)
        self.net.setInputSize(500, 200)  # 320, 320 BEST (500, 200)
        self.net.setInputScale(1.0 / 127.5)  # 1.0/127.5
        self.net.setInputMean((127.5, 127.5, 127.5))  # 127.5, 127.5, 127.5
        self.net.setInputSwapRB(True)

    def name_to_var(self, msg):
        if "t v" in self.obj:
            self.obj = "tv"
        elif "search_flag_true" in msg.data:
            self.search_flag = True
        elif "search_flag_false" in msg.data:
            self.search_flag = False
        else:
            self.obj = str(msg.data)

    def capture(self):
        cap = cv2.VideoCapture(-1)
        # cap.set(3, 320)
        # cap.set(4, 280)
        while True:
            sucess, img = cap.read()
            cv2.rectangle(img, (300, 220), (340, 260), color=(199, 183, 62), thickness=2)
            classIds, confs, bbox = self.net.detect(img, confThreshold=self.thresh)
            self.center = [0, 0]
            try:
                if len(classIds) != 0:
                    for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
                        cv2.rectangle(img, box, color=(70, 86, 122), thickness=2)
                        cv2.putText(img, self.classNames[classId - 1].upper(), (box[0] + 10, box[1] + 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                        self.item = self.classNames[classId - 1]
                        cv2.putText(img, str(round(confidence * 100, 2)), (box[0] + 10, box[1] + 60),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                    for z in self.classNames:  ### OBJECT CLASSIFIER, found object ###
                        if z in self.obj and z == self.item:
                            try:
                                self.center = [int(box[0] + int(box[2]) / 2), int(box[1] + int(box[3]) / 2)]
                                cv2.circle(img, self.center, 5, color=(255, 0, 0), thickness=2)
                                if self.search_flag:
                                    resp = String()
                                    resp.data = f'have_object'
                                    self.cam_pub.publish(resp)
                                resp = String()
                                resp.data = f'cntr_obj={self.center}'
                                self.cam_pub.publish(resp)
                            except:
                                print(traceback.format_exc())
                #         else:
                #             self.lost()
                # else:
                #     self.lost()
                cv2.imshow("OUTPUT", img)
                cv2.waitKey(1)

            except:
                print(traceback.format_exc())





        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    rclpy.init()
    cam = Cam()
    main_thread = Thread(target=cam.capture)
    main_thread.start()
    # t1 = Thread(target=cam.lost)
    # t1.start()

    rclpy.spin(cam)
