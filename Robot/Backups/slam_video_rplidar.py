	MAP_SIZE_PIXELS = 128
        MAP_SIZE_METERS = 10
        LIDAR_DEVICE = '/dev/ttyUSB0'
        MIN_SAMPLES = 70

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
        # img = cv2.VideoCapture()
        # slam.update(a, scan_angles_degrees=b)
        # try:
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
            self.dist = distances
            self.ang = angles
            # for i in range(len(self.ang)):
            #     print(f"{i}", self.dist[i], self.ang[i])


            # Get current robot position
            self.x, self.y, self.theta = slam.getpos()
            if self.x < 1000 or self.y < 1000:
                print(self.theta)
            # print('X_pos:', self.x/1000, 'Y_pos:', self.y/1000)
            slam.getmap(mapbytes)


            # Display map and robot pose, exiting gracefully if user closes it
            if not viz.display(self.x / 1000., self.y / 1000., self.theta, mapbytes):
                exit(0)
        # except:
        #     print("ERROR")
        #
        # # Shut down the lidar connection
        # lidar.stop()
        # lidar.disconnect()
