import os
from math import cos, sin, pi, floor
import pygame
from adafruit_rplidar import RPLidar

# Set up pygame and the display
# os.putenv('SDL_FBDEV', '/dev/fb1')
pygame.init()

screen_width = 600
screen_height = 600

lcd = pygame.display.set_mode((screen_width, screen_height))
pygame.mouse.set_visible(False)
pygame.display.update()

# Setup the RPLidar
PORT_NAME = '/dev/ttyUSB0'
lidar = RPLidar(None, PORT_NAME, timeout=3)

# used to scale data to fit on the screen
max_distance = 0

# pylint: disable=redefined-outer-name,global-statement


def process_data(data):
    global max_distance
    lcd.fill((0, 0, 0))
    for angle in range(360):
        distance = data[angle]
        if distance > 0:                  # ignore initially ungathered data points
            max_distance = max([min([5000, distance]), max_distance])
            radians = angle * pi / 180.0
            x = distance * cos(radians)
            y = distance * sin(radians)
            point = (int(screen_width/2) + int(x / max_distance * int(screen_width/2)), int(screen_height/2) + int(y / max_distance * int(screen_height/2)))
            lcd.set_at(point, pygame.Color(255, 255, 255))
            if distance < 400:
                # print(angle)
                point = (int(screen_width / 2) + int(x / max_distance * int(screen_width / 2)),
                         int(screen_height / 2) + int(y / max_distance * int(screen_height / 2)))
                lcd.set_at(point, pygame.Color(255, 0, 0))
                pygame.display.update()
    pygame.display.update()


scan_data = [0]*360
color = (255, 0, 0)
rear_dist = 0.0
front_dist = 0.0

try:
    print(lidar.info)
    for scan in lidar.iter_scans():
        for (_, angle, distance) in scan:
            scan_data[min([359, floor(angle)])] = distance
            if 359 > angle > 360:
                rear_dist = distance
            if 180 > angle > 179:
                front_dist = distance
            print(rear_dist-front_dist)


        process_data(scan_data)

except KeyboardInterrupt:
    print('Stoping.')
lidar.stop()
lidar.disconnect()


def roboviz(self):
    MAP_SIZE_PIXELS = 256
    MAP_SIZE_METERS = 10
    LIDAR_DEVICE = '/dev/ttyUSB0'
    MIN_SAMPLES = 40

    lidar = Lidar(LIDAR_DEVICE, timeout=3)
    lidar.reset()
    slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)
    # viz = MapVisualizer(MAP_SIZE_PIXELS, MAP_SIZE_METERS, 'SLAM')
    mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)
    iterator = lidar.iter_scans()
    previous_distances = None
    previous_angles = None
    print("Restarting LIDAR...")

    next(iterator)
    while True:
        self.robo_time = time()
        self.items = [item for item in next(iterator)]
        distances = [item[2] for item in self.items]
        angles = [item[1] for item in self.items]
        if len(distances) > MIN_SAMPLES:
            f = interp1d(angles, distances, fill_value='extrapolate')
            distances = list(f(numpy.arange(360)))
            slam.update(distances)
            previous_distances = distances.copy()
        elif previous_distances is not None:
            slam.update(previous_distances)
        self.x, self.y, self.theta = slam.getpos()

        if self.an > 0:
            for i in self.items:
                if self.an in range(int(i[1] - 5), int(i[1] + 5)):
                    self.di = i[2]
                    return self.di
            break

        # for i in self.items:
        #     if i[1] in range(90, 270):
        #         if i[2] < 400:
        #             k = self.mapp(i[1], 90, 270, -90, 90)
        #             print(k)
        #             self.set_cam_pos(k * -1)

        slam.getmap(mapbytes)
        # break
        # if not viz.display(self.x / 1000., self.y / 1000., self.theta, mapbytes):
        #     exit(0)
