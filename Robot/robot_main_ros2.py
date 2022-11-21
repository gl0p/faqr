import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from subprocess import Popen
from neuralintents import GenericAssistant
import atexit
import re
from ast import literal_eval
from math import sqrt, cos
from time import sleep, time
from threading import Thread


class MainNode(Node):
    def __init__(self):
        super().__init__("main_node") # Node Name #
        # setup speech ai responses to call functions #
        mappings = {'search': self.begin_search, 'clear': self.clear_everything}

        # load model, mappings and intent file #
        self.assistant = GenericAssistant('intents.json', intent_methods=mappings, model_name="speech_response_model_V1")
        self.assistant.load_model('speech_response_model_V1')

        # set up a timer for response handling, function will run every 0.25 seconds #
        # self.create_timer(0.25, self.main)

        # set up subscriptions #
        self.speech_sub = self.create_subscription(String, "speech", self.main, 10)
        self.cam_sub = self.create_subscription(String, "cam_return", self.cam_func, 10)
        self.raspi_sub = self.create_subscription(String, "raspi_cam_ang", self._cam_ang, 10)
        self.lidar_sub = self.create_subscription(String, "lidar_pub", self.data_acq, 10)

        # set up publishing channels #
        self.speech_pub = self.create_publisher(String, "listen", 10)
        self.cam_pub = self.create_publisher(String, "cam_search", 10)
        self.raspi_pub = self.create_publisher(String, "raspi_search", 10)
        self.lidar_pub = self.create_publisher(String, "lidar_sub", 10)

        # self.t3 = Thread(target=self.lost_search)

        # set up variables #
        with open('coco.names', 'rt') as f:
            self.classNames = f.read().rstrip('\n').split('\n')
        self.word = ""
        self.p_flag = False
        self.view_center = None
        self.cc = [0] * 50
        self.hztl = ""
        self.lost_count = 0
        self.cam_ang = 0.0
        self.found = False
        self.move_indicator = ""
        self.x = 0.0
        self.y = 0.0
        self.dist = 0.0
        self.ang = 0.0
        self.theta = 0.0

    def data_acq(self, msg):
        if "dian" in msg.data:
            var = msg.data
            var = re.split("=", var)
            var = literal_eval(var[1])
            self.dist, self.ang = var
            # print("DIAN:", self.dist, self.ang)
        if "pos" in msg.data:
            var = msg.data
            var = re.split("=", var)
            var = literal_eval(var[1])
            self.x, self.y = var
            # print("MY POS:", self.x, self.y)
        if "theta" in msg.data:
            var = msg.data
            var = re.split("=", var)
            var = literal_eval(var[1])
            self.theta = var
            # print(self.theta)

    def cam_func(self, msg):
        if "have_object" in msg.data:
            resp = String()
            resp.data = f'stop'
            self.raspi_pub.publish(resp)
            cs = String()
            cs.data = f'search_flag_false'
            self.cam_pub.publish(cs)
        if "cntr_obj" in msg.data:
            var = msg.data
            var = re.split("=", var)
            var = literal_eval(var[1])
            self.view_center = var[0]
            self.cam_rotation()
            self.movement()
            print("OBJECT LOCATION:", self.object_location())
            print("DSTANCE:", self.dist)
        if "obj_lost" in msg.data:
            self.found = False
            self.lost_search()

    def object_location(self):
        cs = String()
        cs.data = f'get_dian={self.cam_ang}'
        self.lidar_pub.publish(cs)
        cs = String()
        cs.data = f'get_pos'
        self.lidar_pub.publish(cs)
        obj_x = self.dist * cos(self.ang)
        obj_y = sqrt((int(self.dist) * int(self.dist) - obj_x))
        return self.x + obj_x, self.y + obj_y

    def movement(self):
        if self.cam_ang > 210:
            cs = String()
            cs.data = f'rotate_right={0.01}'
            self.raspi_pub.publish(cs)

        if self.cam_ang < 150:
            cs = String()
            cs.data = f'rotate_left={0.01}'
            self.raspi_pub.publish(cs)

        if 190 > self.cam_ang > 170:
            cs = String()
            cs.data = f'forward={0.01}'
            self.raspi_pub.publish(cs)

    def _cam_ang(self, msg):
        if "cam_ang" in msg.data:
            var = msg.data
            var = re.split("=", var)
            var = literal_eval(var[1])
            self.cam_ang = var
            self.cam_ang = self._map(self.cam_ang * -1, -90, 90, 90, 270)
            # print(self.cam_ang)

    def lost_search(self):
        print('Object lost attempting to find object.')
        if not self.found:
            if "right" in self.hztl:
                cs = String()
                cs.data = f'center_right={3.0}'
                self.raspi_pub.publish(cs)
            if "left" in self.hztl:
                cs = String()
                cs.data = f'center_left={3.0}'
                self.raspi_pub.publish(cs)
                print(self.cam_ang)
            if self.cam_ang < 100 or self.cam_ang > 260:
                print("Begin search")
                self.begin_search()

    def main(self, msg):
        self.word = msg.data
        print(self.word)
        if "huh" in self.word:
            self.word = ""
        response = self.assistant.request(self.word)
        if response is not None:
            resp = String()
            resp.data = f'{response}'
            self.speech_pub.publish(resp)

    def begin_search(self):
        for x in self.classNames:
            if x in self.word:
                qury = String()
                qury.data = f'Oh, I Suppose I can help'
                self.speech_pub.publish(qury)

                cs = String()
                cs.data = f'search_flag_true'
                self.cam_pub.publish(cs)

                cs = String()
                cs.data = f'{x}'
                self.cam_pub.publish(cs)
                # print("Sent cam search", self.word)

                cs = String()
                cs.data = f'search'
                self.raspi_pub.publish(cs)

    def clear_everything(self):
        print("Everything cleared")
        cs = String()
        cs.data = f''
        self.cam_pub.publish(cs)

    def cam_rotation(self):
        if self.view_center < 300:
            if self.view_center < 200:
                cs = String()
                cs.data = f'center_right={3.0}'
                self.raspi_pub.publish(cs)
                self.lft_rht_chk()
            cs = String()
            cs.data = f'center_right={1.5}'
            self.raspi_pub.publish(cs)
            self.lft_rht_chk()
        if self.view_center > 340:
            if self.view_center > 440:
                cs = String()
                cs.data = f'center_left={3.0}'
                self.raspi_pub.publish(cs)
                self.lft_rht_chk()
            cs = String()
            cs.data = f'center_left={1.5}'
            self.raspi_pub.publish(cs)
            self.lft_rht_chk()


    def lft_rht_chk(self):
        self.cc.append(self.view_center)
        self.cc.pop(0)
        res = all(i < j for i, j in zip(self.cc, self.cc[1:]))
        # print(self.cc, res)
        if res:
            self.hztl = "right"
        else:
            self.hztl = "left"
        # print(self.hztl)

    @staticmethod
    def _map(x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


if __name__ == "__main__":
    speech_proc = Popen("/home/f1/Robot/speech_to_txt.py")
    # Popen("/home/f1/Robot/vision.py")
    rclpy.init()
    main_node = MainNode()
    rclpy.spin(main_node)
    atexit.register(speech_proc.terminate())

