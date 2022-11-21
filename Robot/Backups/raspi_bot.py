import serial  ### /dev/ttyAMA0
import board
import queue
import logging
from os import system
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from time import sleep, time

try:
    system("sudo killall pigpiod")

except:
    pass
system("sudo pigpiod")
from gpiozero import AngularServo, Device, LED, DistanceSensor
from gpiozero.pins.pigpio import PiGPIOFactory
from threading import Thread, Lock
import threading
from multiprocessing import Process

###     0, 1,  2,  3,  4,  5,  6, 7, 8,  9, 10, 11, 12, 13, 14
pins = [4, 17, 27, 22, 10, 9, 11, 5, 6, 13, 19, 26, 20, 21]
servo = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']

servo[0] = AngularServo(pins[0], min_angle=-90, max_angle=90, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000,
                        frame_width=5 / 1000, pin_factory=PiGPIOFactory(), initial_angle=0)
servo[1] = AngularServo(pins[1], min_angle=-90, max_angle=90, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000,
                        frame_width=5 / 1000, pin_factory=PiGPIOFactory(), initial_angle=0)
servo[2] = AngularServo(pins[2], min_angle=-90, max_angle=90, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000,
                        frame_width=5 / 1000, pin_factory=PiGPIOFactory(), initial_angle=60)
servo[3] = AngularServo(pins[3], min_angle=-90, max_angle=90, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000,
                        frame_width=5 / 1000, pin_factory=PiGPIOFactory(), initial_angle=-10)
servo[4] = AngularServo(pins[4], min_angle=-90, max_angle=90, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000,
                        frame_width=5 / 1000, pin_factory=PiGPIOFactory(), initial_angle=0)
servo[5] = AngularServo(pins[5], min_angle=-90, max_angle=90, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000,
                        frame_width=5 / 1000, pin_factory=PiGPIOFactory(), initial_angle=-60)
servo[6] = AngularServo(pins[6], min_angle=-90, max_angle=90, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000,
                        frame_width=5 / 1000, pin_factory=PiGPIOFactory(), initial_angle=0)
servo[7] = AngularServo(pins[7], min_angle=-90, max_angle=90, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000,
                        frame_width=5 / 1000, pin_factory=PiGPIOFactory(), initial_angle=0)
servo[8] = AngularServo(pins[8], min_angle=-90, max_angle=90, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000,
                        frame_width=5 / 1000, pin_factory=PiGPIOFactory(), initial_angle=60)
servo[9] = AngularServo(pins[9], min_angle=-90, max_angle=90, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000,
                        frame_width=5 / 1000, pin_factory=PiGPIOFactory(), initial_angle=0)
servo[10] = AngularServo(pins[10], min_angle=-90, max_angle=90, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000,
                         frame_width=5 / 1000, pin_factory=PiGPIOFactory(), initial_angle=0)
servo[11] = AngularServo(pins[11], min_angle=-90, max_angle=90, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000,
                         frame_width=5 / 1000, pin_factory=PiGPIOFactory(), initial_angle=-60)
servo[12] = AngularServo(20, min_angle=-90, max_angle=90, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000,
                         frame_width=5 / 1000, pin_factory=PiGPIOFactory(), initial_angle=10)


# servo[13] = AngularServo(21, min_angle=-90, max_angle=90, min_pulse_width=0.5 / 1000, max_pulse_width=2.5 / 1000,
#                          frame_width=5 / 1000, pin_factory=PiGPIOFactory(), initial_angle=10)


def ang(ang):
    return int(servo[ang].angle)


def zero_pos():
    #     t = 0.01
    #     if ang(_0) <= 0:
    #         if ang(_1) <= 0:
    #             if ang(_2) <= 0:
    #                 a = ang(_2)
    #                 for i in range(0, a, -1):
    #                     servo[2].angle = a-i
    #                     sleep(t)
    #             b = ang(_1)
    #             for i in range(0, b, -1):
    #                 servo[1].angle = b-i
    #                 sleep(t)
    #         c = ang(_0)
    #         for i in range(0, c, -1):
    #             servo[0].angle = c-i
    #             sleep(t)
    #     if ang(_3) != -10:
    #         x = ang(_3)
    #         for i in range(0,x, -1):
    #             servo[_3].angle = x-i
    #             sleep(t)
    #     if ang(_6) != 0:
    #         x = ang(_6)
    #         for i in range(0,x, -1):
    #             servo[_6].angle = x-i
    #             sleep(t)
    #     if ang(_9) != 0:
    #         x = ang(_9)
    #         for i in range(0,x, -1):
    #             servo[_9].angle = x-i
    #             sleep(t)

    ### HIPS ###
    servo[0].angle = 0
    servo[3].angle = -10
    servo[6].angle = 0
    servo[9].angle = 0

    ### FEMER ###
    servo[1].angle = 0
    servo[7].angle = 0

    servo[4].angle = 0
    servo[10].angle = 0

    ### LEGS ###
    servo[2].angle = 60
    servo[8].angle = 60

    servo[5].angle = -60
    servo[11].angle = -60

    print("ZERO_POS COMPLETE")
    sleep(0.25)


class move:
    def __init__(self):
        pass

    def walk(self, walk, speed):
        global run_flag_move
        run_flag_move = True
        flag = False
        t = speed
        end = False
        if walk == 1:
            direction = [[0, 3, 6, 9], [1, 4, 7, 10], [2, 5, 8, 11]]
        if walk == 0:
            direction = [[6, 9, 0, 3], [7, 10, 1, 4], [8, 11, 2, 5]]
        zero_pos()
        _0 = direction[0][0]
        _1 = direction[1][0]
        _2 = direction[2][0]
        _3 = direction[0][1]
        _4 = direction[1][1]
        _5 = direction[2][1]
        _6 = direction[0][2]
        _7 = direction[1][2]
        _8 = direction[2][2]
        _9 = direction[0][3]
        _10 = direction[1][3]
        _11 = direction[2][3]

        while True:
            a = 0
            b = -10
            c = 0
            d = 0
            e = 60
            f = -60
            g = 0
            h = 0

            if flag:
                print("ENDED")
                flag = False
                end = False
                run_flag_move = False
                zero_pos()
                break

            # print("MOVE ALL FORWEARD 0")
            for i in range(0, 20):
                if end:
                    flag = True
                    break
                servo[direction[0][0]].angle = a + i
                servo[direction[0][1]].angle = b + i
                servo[direction[0][2]].angle = c - i
                servo[direction[0][3]].angle = d - i
                servo[direction[2][2]].angle = e - i
                servo[direction[2][1]].angle = f + i
                servo[direction[1][1]].angle = g + i
                servo[direction[1][2]].angle = h - i
                sleep(t)

            # input("Press ENTER to continue...")
            # print("REAR LEFT LEG FORWARD")
            a = ang(direction[1][1])
            b = ang(direction[1][3])
            c = ang(direction[1][2])
            d = ang(direction[2][2])
            e = ang(direction[2][3])
            for i in range(0, 40):
                if end:
                    flag = True
                    break
                servo[direction[1][1]].angle = a - i
                servo[direction[1][3]].angle = b - i / 2
                servo[direction[1][2]].angle = c + i / 2
                servo[direction[2][2]].angle = d + i / 2
                servo[direction[2][3]].angle = e - i / 4
                sleep(t)
            a = ang(direction[0][1])
            e = ang(direction[0][0])
            f = ang(direction[0][2])
            g = ang(direction[0][3])
            for i in range(0, 80):
                if end:
                    flag = True
                    break  ###REAR LEFT LEG FORWARD
                servo[direction[0][1]].angle = a - i
                servo[direction[0][0]].angle = e + i / 8
                servo[direction[0][2]].angle = f - i / 8
                servo[direction[0][3]].angle = g - i / 8
                sleep(t)
            a = ang(direction[1][1])
            b = ang(direction[2][1])
            e = ang(direction[2][3])
            d = ang(direction[1][3])
            for i in range(0, 20):
                if end:
                    flag = True
                    break
                servo[direction[1][1]].angle = a + i
                servo[direction[2][1]].angle = b - i
                servo[direction[2][3]].angle = e + i / 2
                servo[direction[1][3]].angle = d + i
                sleep(t)

            # input("Press ENTER to continue...")
            # print("FRONT LEFT LEG FORWARD")
            a = ang(direction[1][0])
            b = ang(direction[1][2])
            c = ang(direction[2][2])
            for i in range(0, 20):
                if end:
                    flag = True
                    break
                servo[direction[1][0]].angle = a + i
                servo[direction[1][2]].angle = b + i
                servo[direction[2][2]].angle = c + i / 2
                sleep(t)
            a = ang(direction[0][0])
            e = ang(direction[0][1])
            f = ang(direction[0][2])
            g = ang(direction[0][3])
            h = ang(_8)
            for i in range(0, 60):
                if end:
                    flag = True
                    break  ###FRONT LEFT LEG FORWARD
                servo[direction[0][0]].angle = a - i
                servo[direction[0][1]].angle = e + i / 6
                servo[direction[0][2]].angle = f - i / 6
                servo[direction[0][3]].angle = g - i / 6
                servo[_8].angle = h - i / 6
                sleep(t)
            a = ang(direction[1][0])
            b = ang(direction[1][2])
            c = ang(direction[2][2])
            for i in range(0, 20):
                if end:
                    flag = True
                    break
                servo[direction[1][0]].angle = a - i
                servo[direction[1][2]].angle = b - i
                servo[direction[2][2]].angle = c - i / 2
                sleep(t)

            # input("Press ENTER to continue...")
            # print("ALL FORWARD 1")
            a = ang(direction[0][0])
            b = ang(direction[0][1])
            c = ang(direction[1][2])
            d = ang(direction[0][3])
            e = ang(direction[2][2])
            for i in range(0, 20):
                if end:
                    flag = True
                    break
                servo[direction[0][0]].angle = a + i
                servo[direction[0][1]].angle = b + i
                servo[direction[1][2]].angle = c - i
                servo[direction[0][3]].angle = d - i
                servo[direction[2][2]].angle = e - i
                sleep(t)

            # input("Press ENTER to continue...")
            # print("REAR RIGHT LEG FORWARD")
            a = ang(direction[1][2])  # 4
            b = ang(direction[1][0])  # 1
            c = ang(direction[2][2])  # 8
            d = ang(direction[2][0])
            h = ang(_8)
            for i in range(0, 20):
                if end:
                    flag = True
                    break
                servo[direction[1][2]].angle = a + i * 2
                servo[direction[1][0]].angle = b + i
                servo[direction[2][2]].angle = c + i
                servo[direction[2][0]].angle = d + i / 2
                servo[_8].angle = h + i * 1.5
                sleep(t)
            a = ang(direction[0][2])
            e = ang(direction[0][1])
            f = ang(direction[0][0])
            g = ang(direction[0][3])
            for i in range(0, 80):
                if end:
                    flag = True
                    break  ###REAR RIGHT LEG FORWARD
                servo[direction[0][2]].angle = a + i
                servo[direction[0][1]].angle = e + i / 8
                servo[direction[0][0]].angle = f + i / 8
                servo[direction[0][3]].angle = g - i / 8
                sleep(t)
            a = ang(direction[1][2])
            c = ang(direction[1][0])
            d = ang(direction[2][0])
            for i in range(0, 20):
                if end:
                    flag = True
                    break
                servo[direction[1][2]].angle = a - i
                servo[direction[1][0]].angle = c - i
                servo[direction[2][0]].angle = d - i / 2
                sleep(t)

            # input("Press ENTER to continue...")
            # print("FRONT RIGHT LEG FORWARD")
            a = ang(direction[1][3])
            b = ang(direction[1][1])
            c = ang(direction[2][1])
            for i in range(0, 20):
                if end:
                    flag = True
                    break
                servo[direction[1][3]].angle = a - i
                servo[direction[1][1]].angle = b - i
                servo[direction[2][1]].angle = c - i / 2
                sleep(t)
            a = ang(direction[0][3])
            e = ang(direction[0][1])
            f = ang(direction[0][0])
            g = ang(direction[0][2])
            for i in range(0, 80):
                if end:
                    flag = True
                    break  ###FRONT RIGHT LEG FORWARD
                servo[direction[0][3]].angle = a + i
                servo[direction[0][1]].angle = e + i / 8
                servo[direction[0][0]].angle = f + i / 8
                servo[direction[0][2]].angle = g - i / 8
                sleep(t)
            a = ang(direction[1][3])
            b = ang(direction[1][1])
            c = ang(direction[2][1])
            for i in range(0, 20):
                if end:
                    flag = True
                    break
                servo[direction[1][3]].angle = a + i
                servo[direction[1][1]].angle = b + i
                servo[direction[2][1]].angle = c + i / 2
                sleep(t)

            # input("Press ENTER to continue...")
            # print("ALL FORWARD 2")
            a = ang(direction[0][0])
            b = ang(direction[0][1])
            c = ang(direction[0][2])
            d = ang(direction[0][3])
            for i in range(0, 10):
                if end:
                    flag = True
                    break
                servo[direction[0][0]].angle = a + i
                servo[direction[0][1]].angle = b + i / 2
                servo[direction[0][2]].angle = c - i
                servo[direction[0][3]].angle = d - i
                sleep(t)

            if ang(_0) != 0:
                x = ang(_0)
                for i in range(0, x):
                    servo[_0].angle = x - i
                    sleep(t)
            if ang(_3) != -10:
                x = ang(_3)
                for i in range(0, x):
                    servo[_3].angle = x - i
                    sleep(t)
            if ang(_6) != 0:
                x = ang(_6)
                for i in range(0, x):
                    servo[_6].angle = x - i
                    sleep(t)
            if ang(_9) != 0:
                x = ang(_9)
                for i in range(0, x):
                    servo[_9].angle = x - i
                    sleep(t)

    def rotate(self, rotation, speed):
        global run_flag_rotate
        run_flag_rotate = True
        zero_pos()
        end = False
        print(end)
        flag = False
        print('Inside rotate()')
        while True:
            if flag:
                print("ENDED")
                flag = False
                end = False
                run_flag_rotate = False
                zero_pos()
                break
            if rotation == 1:
                zero_pos()
                direction = [[0, 3, 6, 9], [1, 4, 7, 10], [2, 5, 8, 11]]
                _0 = direction[0][0]
                _1 = direction[1][0]
                _2 = direction[2][0]
                _3 = direction[0][1]
                _4 = direction[1][1]
                _5 = direction[2][1]
                _6 = direction[0][2]
                _7 = direction[1][2]
                _8 = direction[2][2]
                _9 = direction[0][3]
                _10 = direction[1][3]
                _11 = direction[2][3]

                t = speed

                a = ang(_3)
                b = ang(_9)
                c = ang(_7)
                d = ang(_8)
                e = ang(_1)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_3].angle = a - i * 1.5
                    servo[_9].angle = b + i * 1.5
                    servo[_7].angle = c + i
                    servo[_8].angle = d + i
                    servo[_1].angle = e + i
                    sleep(t)

                a = ang(_0)
                b = ang(_3)
                c = ang(_6)
                d = ang(_9)
                # e = ang(12)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    # servo[12].angle = e-i/2
                    servo[_0].angle = a - i * 2
                    servo[_3].angle = b + i / 2
                    servo[_6].angle = c + i / 2
                    servo[_9].angle = d - i / 2
                    sleep(t)
                a = ang(_1)
                b = ang(_7)
                c = ang(_8)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_1].angle = a - i
                    servo[_7].angle = b - i
                    servo[_8].angle = c - i
                    sleep(t)

                a = ang(_0)
                b = ang(_3)
                c = ang(_6)
                d = ang(_9)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_0].angle = a + i
                    servo[_3].angle = b + i
                    servo[_6].angle = c + i
                    servo[_9].angle = d + i
                    sleep(t)

                a = ang(_10)
                b = ang(_4)
                c = ang(_5)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_10].angle = a - i
                    servo[_4].angle = b - i
                    servo[_5].angle = c - i / 2
                    sleep(t)

                a = ang(_9)
                b = ang(_0)
                c = ang(_3)
                d = ang(_6)
                for i in range(0, 80):
                    if end:
                        flag = True
                        break
                    servo[_9].angle = a - i
                    servo[_0].angle = b + i / 8
                    servo[_3].angle = c + i / 8
                    servo[_6].angle = d + i / 8
                    sleep(t)

                a = ang(_10)
                b = ang(_4)
                c = ang(_5)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_10].angle = a + i
                    servo[_4].angle = b + i
                    servo[_5].angle = c + i / 2
                    sleep(t)

                a = ang(_0)
                b = ang(_3)
                c = ang(_6)
                d = ang(_9)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_0].angle = a + i
                    servo[_3].angle = b + i
                    servo[_6].angle = c + i
                    servo[_9].angle = d + i
                    sleep(t)

                a = ang(_7)
                b = ang(_1)
                c = ang(_2)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_7].angle = a + i
                    servo[_1].angle = b + i
                    servo[_2].angle = c + i / 2
                    sleep(t)

                a = ang(_6)
                b = ang(_0)
                c = ang(_3)
                d = ang(_9)
                for i in range(0, 80):
                    if end:
                        flag = True
                        break
                    servo[_6].angle = a - i
                    servo[_0].angle = b + i / 8
                    servo[_3].angle = c + i / 8
                    servo[_9].angle = d + i / 8
                    sleep(t)

                a = ang(_7)
                b = ang(_1)
                c = ang(_2)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_7].angle = a - i
                    servo[_1].angle = b - i
                    servo[_2].angle = c - i / 2
                    sleep(t)

                a = ang(_0)
                b = ang(_3)
                c = ang(_6)
                d = ang(_9)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_0].angle = a + i
                    servo[_3].angle = b + i
                    servo[_6].angle = c + i
                    servo[_9].angle = d + i
                    sleep(t)

                a = ang(_4)
                b = ang(_10)
                c = ang(_11)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_4].angle = a - i
                    servo[_10].angle = b - i
                    servo[_11].angle = c - i
                    sleep(t)

                a = ang(_0)
                b = ang(_3)
                c = ang(_6)
                d = ang(_9)
                for i in range(0, 60):
                    if end:
                        flag = True
                        break
                    servo[_0].angle = a + i / 6
                    servo[_3].angle = b - i
                    servo[_6].angle = c + i / 6
                    servo[_9].angle = d + i / 6
                    sleep(t)

                a = ang(_4)
                b = ang(_10)
                c = ang(_11)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_4].angle = a + i
                    servo[_10].angle = b + i
                    servo[_11].angle = c + i
                    sleep(t)

                a = ang(_1)
                b = ang(_7)
                c = ang(_8)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_1].angle = a + i
                    servo[_7].angle = b + i
                    servo[_8].angle = c + i
                    sleep(t)

                a = ang(_0)
                for i in range(0, 50):
                    if end:
                        flag = True
                        break
                    servo[_0].angle = a - i
                    sleep(t)

                a = ang(_1)
                b = ang(_7)
                c = ang(_8)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_1].angle = a - i
                    servo[_7].angle = b - i
                    servo[_8].angle = c - i
                    sleep(t)

            if rotation == 0:
                zero_pos()
                direction = [[0, 3, 6, 9], [1, 4, 7, 10], [2, 5, 8, 11]]
                _0 = direction[0][0]
                _1 = direction[1][0]
                _2 = direction[2][0]
                _3 = direction[0][1]
                _4 = direction[1][1]
                _5 = direction[2][1]
                _6 = direction[0][2]
                _7 = direction[1][2]
                _8 = direction[2][2]
                _9 = direction[0][3]
                _10 = direction[1][3]
                _11 = direction[2][3]

                t = speed

                a = ang(_3)
                b = ang(_9)
                c = ang(_7)
                d = ang(_2)
                e = ang(_1)
                # print(0)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_3].angle = a + i * 1.5
                    servo[_9].angle = b - i * 1.5
                    servo[_7].angle = c + i
                    servo[_2].angle = d + i
                    servo[_1].angle = e + i
                    sleep(t)

                a = ang(_6)
                b = ang(_3)
                c = ang(_0)
                d = ang(_9)
                # print(1)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_6].angle = a + i * 2
                    servo[_3].angle = b - i / 2
                    servo[_0].angle = c - i / 2
                    servo[_9].angle = d - i / 2
                    sleep(t)
                a = ang(_1)
                b = ang(_7)
                c = ang(_2)
                # print(2)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_1].angle = a - i
                    servo[_7].angle = b - i
                    servo[_2].angle = c - i
                    sleep(t)

                a = ang(_0)
                b = ang(_3)
                c = ang(_6)
                d = ang(_9)
                # print(3)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_0].angle = a - i
                    servo[_3].angle = b - i
                    servo[_6].angle = c - i
                    servo[_9].angle = d - i
                    sleep(t)

                a = ang(_10)
                b = ang(_4)
                c = ang(_5)
                # print(4)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_10].angle = a - i
                    servo[_4].angle = b - i
                    servo[_5].angle = c - i / 2
                    sleep(t)

                a = ang(_9)
                b = ang(_0)
                c = ang(_3)
                d = ang(_6)
                # print(5)
                for i in range(0, 80):
                    if end:
                        flag = True
                        break
                    servo[_9].angle = a + i
                    servo[_0].angle = b - i / 8
                    servo[_3].angle = c - i / 8
                    servo[_6].angle = d - i / 8
                    sleep(t)

                a = ang(_10)
                b = ang(_4)
                c = ang(_5)
                # print(6)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_10].angle = a + i
                    servo[_4].angle = b + i
                    servo[_5].angle = c + i / 2
                    sleep(t)

                a = ang(_0)
                b = ang(_3)
                c = ang(_6)
                d = ang(_9)
                # print(7)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_0].angle = a - i
                    servo[_3].angle = b - i
                    servo[_6].angle = c - i
                    servo[_9].angle = d - i
                    sleep(t)

                a = ang(_7)
                b = ang(_1)
                c = ang(_8)
                # print(8)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_7].angle = a + i
                    servo[_1].angle = b + i
                    servo[_8].angle = c + i / 2
                    sleep(t)

                a = ang(_0)
                b = ang(_6)
                c = ang(_3)
                d = ang(_9)
                # print(9)
                for i in range(0, 80):
                    if end:
                        flag = True
                        break
                    servo[_0].angle = a + i
                    servo[_6].angle = b - i / 8
                    servo[_3].angle = c - i / 8
                    servo[_9].angle = d - i / 8
                    sleep(t)

                a = ang(_7)
                b = ang(_1)
                c = ang(_8)
                # print(10)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_7].angle = a - i
                    servo[_1].angle = b - i
                    servo[_8].angle = c - i / 2
                    sleep(t)

                a = ang(_0)
                b = ang(_3)
                c = ang(_6)
                d = ang(_9)
                # print(11)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_0].angle = a - i
                    servo[_3].angle = b - i
                    servo[_6].angle = c - i
                    servo[_9].angle = d - i
                    sleep(t)

                a = ang(_4)
                b = ang(_10)
                c = ang(_11)
                # print(12)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_4].angle = a - i
                    servo[_10].angle = b - i
                    servo[_11].angle = c - i / 2
                    sleep(t)

                a = ang(_0)
                b = ang(_3)
                c = ang(_6)
                d = ang(_9)
                # print(13)
                for i in range(0, 60):
                    if end:
                        flag = True
                        break
                    servo[_0].angle = a - i / 6
                    servo[_3].angle = b + i
                    servo[_6].angle = c - i / 6
                    servo[_9].angle = d - i / 6
                    sleep(t)

                a = ang(_4)
                b = ang(_10)
                c = ang(_11)
                # print(14)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_4].angle = a + i
                    servo[_10].angle = b + i
                    servo[_11].angle = c + i / 2
                    sleep(t)

                a = ang(_1)
                b = ang(_7)
                c = ang(_2)
                # print(15)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_1].angle = a + i
                    servo[_7].angle = b + i
                    servo[_2].angle = c + i / 2
                    sleep(t)

                a = ang(_6)
                # print(16)
                for i in range(0, 60):
                    if end:
                        flag = True
                        break
                    servo[_6].angle = a + i
                    sleep(t)

                a = ang(_1)
                b = ang(_7)
                c = ang(_2)
                # print(17)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[_1].angle = a - i
                    servo[_7].angle = b - i
                    servo[_2].angle = c - i / 2
                    sleep(t)

                a = ang(10)
                b = ang(4)
                c = ang(5)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[10].angle = a - i
                    servo[4].angle = b - i
                    servo[5].angle = c - i / 2
                    sleep(t)

                a = ang(_9)
                # print(a)
                for i in range(0, 35):
                    if end:
                        flag = True
                        break
                    servo[_9].angle = a + i
                    sleep(t)

                a = ang(10)
                b = ang(4)
                c = ang(5)
                for i in range(0, 20):
                    if end:
                        flag = True
                        break
                    servo[10].angle = a + i
                    servo[4].angle = b + i
                    servo[5].angle = c + i / 2
                    sleep(t)

    def dance(self):
        t = 0.05
        zero_pos()
        const = 3
        sleep(1)
        a = ang(4)
        b = ang(7)
        c = ang(5)
        d = ang(8)
        e = ang(1)
        f = ang(2)
        g = ang(10)
        h = ang(11)
        for i in range(0, 15):
            servo[4].angle = a + i * const
            servo[5].angle = c + i
            servo[7].angle = b - i * const
            servo[8].angle = d - i
            servo[1].angle = e + i * const
            servo[2].angle = f + i
            servo[10].angle = g - i * const
            servo[11].angle = h - i
            sleep(t)
        a = ang(4)
        b = ang(7)
        c = ang(5)
        d = ang(8)
        e = ang(1)
        f = ang(2)
        g = ang(10)
        h = ang(11)
        for i in range(0, 15):
            servo[4].angle = a - i * const
            servo[5].angle = c - i
            servo[7].angle = b + i * const
            servo[8].angle = d + i
            servo[1].angle = e - i * const
            servo[2].angle = f - i
            servo[10].angle = g + i * const
            servo[11].angle = h + i
            sleep(t)
        a = ang(4)
        b = ang(7)
        c = ang(5)
        d = ang(8)
        e = ang(1)
        f = ang(2)
        g = ang(10)
        h = ang(11)
        for i in range(0, 15):
            servo[4].angle = a - i * const
            servo[5].angle = c - i
            servo[7].angle = b + i * const
            servo[8].angle = d + i
            servo[1].angle = e - i * const
            servo[2].angle = f - i
            servo[10].angle = g + i * const
            servo[11].angle = h + i
            sleep(t)
        a = ang(4)
        b = ang(7)
        c = ang(5)
        d = ang(8)
        e = ang(1)
        f = ang(2)
        g = ang(10)
        h = ang(11)
        for i in range(0, 15):
            servo[4].angle = a + i * const
            servo[5].angle = c + i
            servo[7].angle = b - i * const
            servo[8].angle = d - i
            servo[1].angle = e + i * const
            servo[2].angle = f + i
            servo[10].angle = g - i * const
            servo[11].angle = h - i
            sleep(t)

    def sit(self):
        zero_pos()
        t = 0.01
        a = ang(1)
        b = ang(2)
        c = ang(4)
        d = ang(5)
        e = ang(7)
        f = ang(8)
        g = ang(10)
        h = ang(11)
        for i in range(0, 5):
            servo[2].angle = b + i
            servo[5].angle = d - i
            servo[8].angle = f + i
            servo[11].angle = h - i
            sleep(t)
        for i in range(0, 50):
            servo[1].angle = a - i
            servo[4].angle = c + i
            servo[7].angle = e - i
            servo[10].angle = g + i
            sleep(t)


class port:
    def __init__(self):
        self.data = ""
        self.dist = DistanceSensor(echo=24, trigger=23, queue_len=30, pin_factory=PiGPIOFactory())
        self.stop = False
        self.movement = move()
        self.center = []
        self.lock = Lock()
        self.v_flag = False
        self.lr = 0
        self.pRotate_right = Process(target=self.movement.rotate, args=(0, 0.01,))
        self.pRotate_left = Process(target=self.movement.rotate, args=(1, 0.01,))
        self.pBackwards = Process(target=self.movement.walk, args=(0, 0.01,))
        self.pForwards = Process(target=self.movement.walk, args=(1, 0.01,))
        self.last_location = None
        self.cam_angle = None

        # self.ser = serial.Serial(
        #     port='/dev/ttyGS0',
        #     baudrate=115200,
        #     parity=serial.PARITY_NONE,
        #     bytesize=serial.EIGHTBITS,
        #     timeout=0)

    def send_data(self, data):
        print('DATA TO BE SENT IS:', data)
        self.ser.write('{} \n'.format(data).encode("utf-8"))

    def rec_data(self):
        while True:
            while self.ser.inWaiting() > 0:
                self.data = self.ser.readline()
                self.data = str(self.data.decode())
                print('Data RECIEVED is:', self.data)
                if 'last_location' in self.data:
                    self.last_location = self.data
                    self.last_location = self.last_location.replace('last_location', "")
                    if len(self.last_location) > 0:
                        print('LAST LOCATION MARK:', self.last_location)
                        self.last_location = float(self.last_location)
                    self.data = ''
                if 'set_cam_pos' in self.data:
                    ang_cam = self.data
                    ang_cam = ang_cam.replace('set_cam_pos', "")
                    print(ang_cam)

                    servo[12].angle = float(ang_cam)
                    self.data = ''
                if 'stop' in self.data:
                    self.stop = True
                    print("stop recieved")
                    self.data = ""
                if 'reset' in self.data:
                    servo[12].angle = 10
                    zero_pos()
                if 'end' in self.data:
                    if self.pRotate_right.is_alive():
                        self.pRotate_right.terminate()
                    if self.pRotate_left.is_alive():
                        self.pRotate_left.terminate()
                    if self.pBackwards.is_alive():
                        self.pBackwards.terminate()
                    if self.pForwards.is_alive():
                        self.pForwards.terminate()
                    print("end recieved")
                    self.data = ""
                    sleep(0.25)
                    print('FORWARD:', self.pForwards.is_alive(), 'BACKWARD:', self.pBackwards.is_alive())
                if 'center_right' in self.data:
                    self.data = ""
                    self.v_flag = True
                    self.lr = 0
                if 'center_left' in self.data:
                    self.data = ""
                    self.v_flag = True
                    self.lr = 1

    def main(self):
        center = 320
        while True:
            if self.data is not None:
                if 'distance' in self.data:
                    self.data = ""
                    print("DATA IS:", self.data)
                    port.sonar()

                if 'cam_ang' in self.data:
                    self.send_data(str((ang(12))))
                    print("sent cam angle")
                    self.data = ""

                if 'sit' in self.data:
                    self.movement.sit()
                    self.data = ""

                if 'right_turn' in self.data:
                    print("DATA IS:", self.data)
                    self.data = ""
                    self.pRotate_right = Process(target=self.movement.rotate, args=(0, 0.01,))
                    if not self.pRotate_right.is_alive():
                        self.pRotate_right.start()

                if 'left_turn' in self.data:
                    print("DATA IS:", self.data)
                    self.data = ""
                    self.pRotate_left = Process(target=self.movement.rotate, args=(1, 0.01,))
                    if not self.pRotate_left.is_alive():
                        self.pRotate_left.start()

                if 'backward' in self.data:
                    print("DATA IS:", self.data)
                    self.data = ""
                    self.pBackwards = Process(target=self.movement.walk, args=(0, 0.01,))
                    self.pBackwards.start()

                if 'forward' in self.data:
                    print("DATA IS:", self.data)
                    self.data = ""
                    self.pForwards = Process(target=self.movement.walk, args=(1, 0.01,))
                    self.pForwards.start()

                if 'search' in self.data:
                    print("DATA IS:", self.data)
                    self.data = ""
                    p5 = Thread(target=port.search(0.05))
                    p5.start()
                    p5.join()
            # else:
            #    sleep(0.5)

    def sonar(self):
        distance = round(self.dist.distance * 100, 2)
        port.send_data(distance)
        print('Distance sent:', distance)

    def cam_rotation(self):

        # self.data = ""
        while True:
            sleep(0.25)
            if self.v_flag:
                if self.lr == 0:
                    print("Cam_rotation engaged!")
                    a = ang(12)
                    if a > 80:
                        a = 80
                    if a < -80:
                        a = -80
                    servo[12].angle = a + 4.0
                    self.v_flag = False
                if self.lr == 1:
                    a = ang(12)
                    if a > 80:
                        a = 80
                    if a < -80:
                        a = -80
                    servo[12].angle = a - 4.0
                    self.v_flag = False

    def search(self, speed=None):
        t = 0.05  ### Hard coded time delay, make cam x and y random ###
        flag_break = False
        self.stop = False
        print("Searching...")
        ang_12 = 10
        if self.last_location is not None:
            print('Last Location:', self.last_location)
            ang_12 = self.last_location
            self.last_location = None
        while True:
            if flag_break:
                data = ""
                print("Search Stopped")
                break
            a = ang_12
            # b = 0
            if a >= 0:
                for i in range(0, 179):
                    servo[12].angle = a + i
                    if servo[12].angle >= 89:
                        break
                    # servo[13].angle = b+i
                    sleep(t)
                    if self.stop:
                        flag_break = True
                        break
            if a <= -1:
                for i in range(0, 179):
                    servo[12].angle = a - i
                    if servo[12].angle <= -89:
                        break
                    # servo[13].angle = b+i
                    sleep(t)
                    if self.stop:
                        flag_break = True
                        break

            a = ang(12)
            # b = ang(13)
            for i in range(0, 179):
                if self.stop:
                    flag_break = True
                    break
                servo[12].angle = a - i
                # servo[13].angle = b-i
                sleep(t)

            a = ang(12)
            # b = ang(13)
            for i in range(0, 90):
                if self.stop:
                    flag_break = True
                    break
                servo[12].angle = a + i
                # servo[13].angle = b+i
                sleep(t)


class Reciever(Node):
    def __init__(self):
        super().__init__("raspi_bot")
        # self.create_timer(0.25, self.timer_callback)
        self.portt = port()
        self.pub = self.create_publisher(String, "chatter", 10)
        self.sub = self.create_subscription(String, "call_back", self.listener_callback, 10)

        # self.count = 0

    # def timer_callback(self):
    #     msg = String()
    #     self.get_logger().info(f"Sending > {self.count}")
    #     self.count += 1
    #     msg.data = f'{self.count}'
    #     self.pub.publish(msg)

    def listener_callback(self, v_msg):
        self.data = v_msg
        self.data = str(self.data)
        if 'last_location' in self.data:
            self.last_location = self.data
            self.last_location = self.last_location.replace('last_location', "")
            if len(self.last_location) > 0:
                print('LAST LOCATION MARK:', self.last_location)
                self.last_location = float(self.last_location)
            self.data = ''
        if 'set_cam_pos' in self.data:
            ang_cam = self.data
            ang_cam = ang_cam.replace('set_cam_pos', "")
            print(ang_cam)

            servo[12].angle = float(ang_cam)
            self.data = ''
        if 'stop' in self.data:
            self.stop = True
            print("stop recieved")
            self.data = ""
        if 'reset' in self.data:
            servo[12].angle = 10
            zero_pos()
        if 'end' in self.data:
            if self.pRotate_right.is_alive():
                self.pRotate_right.terminate()
            if self.pRotate_left.is_alive():
                self.pRotate_left.terminate()
            if self.pBackwards.is_alive():
                self.pBackwards.terminate()
            if self.pForwards.is_alive():
                self.pForwards.terminate()
            print("end recieved")
            self.data = ""
            sleep(0.25)
            print('FORWARD:', self.pForwards.is_alive(), 'BACKWARD:', self.pBackwards.is_alive())
        if 'center_right' in self.data:
            self.data = ""
            self.v_flag = True
            self.lr = 0
        if 'center_left' in self.data:
            self.data = ""
            self.v_flag = True
            self.lr = 1
        if 'distance' in self.data:
            self.data = ""
            print("DATA IS:", self.data)
            port.sonar()

        if 'cam_ang' in self.data:
            self.send_data(str((ang(12))))
            print("sent cam angle")
            self.data = ""

        if 'sit' in self.data:
            self.movement.sit()
            self.data = ""

        if 'right_turn' in self.data:
            print("DATA IS:", self.data)
            self.data = ""
            self.pRotate_right = Process(target=self.movement.rotate, args=(0, 0.01,))
            if not self.pRotate_right.is_alive():
                self.pRotate_right.start()

        if 'left_turn' in self.data:
            print("DATA IS:", self.data)
            self.data = ""
            self.pRotate_left = Process(target=self.movement.rotate, args=(1, 0.01,))
            if not self.pRotate_left.is_alive():
                self.pRotate_left.start()

        if 'backward' in self.data:
            print("DATA IS:", self.data)
            self.data = ""
            self.pBackwards = Process(target=self.movement.walk, args=(0, 0.01,))
            self.pBackwards.start()

        if 'forward' in self.data:
            print("DATA IS:", self.data)
            self.data = ""
            self.pForwards = Process(target=self.movement.walk, args=(1, 0.01,))
            self.pForwards.start()

        if 'search' in self.data:
            print("DATA IS:", self.data)
            self.data = ""
            p5 = Thread(target=self.portt.search)
            p5.start()
            p5.join()
        self.get_logger().info(f"I herd: {v_msg.data}")


def main(args=None):
    rclpy.init(args=args)

    node = Reciever()
    rclpy.spin(node)

    rclpy.shutdown()


if __name__ == "__main__":
    print("RUNNING ROS2 VERSION OF RASPI_BOT!")
    main()



    # for th in threading.enumerate():
    #     print(th.name)
    # port = port()
    # camRotation = Thread(target=port.cam_rotation)
    # camRotation.start()
    # port.main()







