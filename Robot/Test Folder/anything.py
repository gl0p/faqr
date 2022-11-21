import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from threading import Thread
import re
from ast import literal_eval
from time import sleep


class LidarNode(Node):
    def __init__(self):
        super().__init__("lidar_recv") # Node Name #

        self.lidar_pub = self.create_publisher(String, "lidar_sub", 10)
        self.lidar_sub = self.create_subscription(String, "lidar_pub", self.data_acq, 10)
        self.x = 0.0
        self.y = 0.0
        self.dist = 0.0
        self.ang = 0.0


    def data_acq(self, msg):
        if "dian" in msg.data:
            var = msg.data
            var = re.split("=", var)
            var = literal_eval(var[1])
            self.dist, self.ang = var
            print(self.dist, self.ang)

    def run_trigger(self):
        while True:
            for x in range(200,250):
                cs = String()
                cs.data = f'get_dian={x}'
                self.lidar_pub.publish(cs)
                sleep(0.5)




if __name__ == '__main__':
    rclpy.init()
    lidar_node = LidarNode()
    t1 = Thread(target=lidar_node.run_trigger)
    t1.start()
    rclpy.spin(lidar_node)


