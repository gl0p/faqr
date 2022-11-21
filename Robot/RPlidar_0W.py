#!/usr/bin/env python3

'''
rpslam.py : BreezySLAM Python with SLAMTECH RP A1 Lidar

Copyright (C) 2018 Simon D. Levy

This code is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This code is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this code.  If not, see <http://www.gnu.org/licenses/>.
'''

MAP_SIZE_PIXELS = 500
MAP_SIZE_METERS = 10
LIDAR_DEVICE = '/dev/serial0'

# Ideally we could use all 250 or so samples that the RPLidar delivers in one
# scan, but on slower computers you'll get an empty map and unchanging position
# at that rate.
MIN_SAMPLES = 80

from time import sleep
from gpiozero import LED
from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel
from rplidar import RPLidar as Lidar
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from threading import Thread
import re
from ast import literal_eval

r = LED(17)
r.on()


class LidarNode(Node):
    def __init__(self):
        super().__init__("lidar_node") # Node Name #

        self.lidar_pub = self.create_publisher(String, "lidar_pub", 10)
        self.lidar_sub = self.create_subscription(String, "lidar_sub", self.data_acq, 10)


        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.distances = []
        self.angles = []
        self.dian = [[]]

    def data_acq(self, msg):
        if "get_pos" in msg.data:
            cs = String()
            cs.data = f'pos={self.x, self.y}'
            self.lidar_pub.publish(cs)
        if "get_theta" in msg.data:
            cs = String()
            cs.data = f'theta={self.theta}'
            self.lidar_pub.publish(cs)
        if "get_dian" in msg.data:
            var = msg.data
            var = re.split("=", var)
            var = literal_eval(var[1])
            for k in self.dian:
                for z in range(len(k)):
                    dist = k[0]
                    ang = k[1]
                    if var+1 > ang > var:
                        cs = String()
                        cs.data = f'dian={dist, ang}'
                        self.lidar_pub.publish(cs)


    def lidar(self):
        # Connect to Lidar unit
        lidar = Lidar(LIDAR_DEVICE)

        # Create an RMHC SLAM object with a laser model and optional robot model
        slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)

        # Set up a SLAM display
        #    viz = MapVisualizer(MAP_SIZE_PIXELS, MAP_SIZE_METERS, 'SLAM')

        # Initialize an empty trajectory
        trajectory = []

        # Initialize empty map
        mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)

        # Create an iterator to collect scan data from the RPLidar
        iterator = lidar.iter_scans()

        # We will use these to store previous scan in case current scan is inadequate
        previous_distances = None
        previous_angles = None

        # First scan is crap, so ignore it
        next(iterator)
        sleep(2)
        while True:

            # Extract (quality, angle, distance) triples from current scan
            items = [item for item in next(iterator)]

            # Extract distances and angles from triples
            distances = [item[2] for item in items]
            angles = [item[1] for item in items]
            self.distances = distances
            self.angles = angles
            for y, x in enumerate(angles):
                self.dian.append([distances[y], x])
                if len(self.dian) > 360:
                    self.dian.pop(0)

            # Update SLAM with current Lidar scan and scan angles if adequate
            if len(distances) > MIN_SAMPLES:
                slam.update(distances, scan_angles_degrees=angles)
                previous_distances = distances.copy()
                previous_angles = angles.copy()

            # If not adequate, use previous
            elif previous_distances is not None:
                slam.update(previous_distances, scan_angles_degrees=previous_angles)

            # Get current robot position
            self.x, self.y, self.theta = slam.getpos()
            # Get current map bytes as grayscale
            slam.getmap(mapbytes)

        # Shut down the lidar connection
        lidar.stop()
        lidar.disconnect()



if __name__ == '__main__':
    rclpy.init()
    lidar_node = LidarNode()
    t1 = Thread(target=lidar_node.lidar)
    t1.start()
    rclpy.spin(lidar_node)
