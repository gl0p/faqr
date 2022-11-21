#!/usr/bin/env python

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from speech_rec import speech
from glados.glados import speak
from os import system
from time import time, sleep
from threading import Thread

system("killall aplay")
system("killall pulseaudio")


class SpeechNode(Node):
    def __init__(self):
        super().__init__("speech_node") # Node Name #
        self.speech_pub = self.create_publisher(String, "speech", 10)
        self.listen_sub = self.create_subscription(String, "listen", self.listener, 10)

        self.speech = ""

    def main(self):
        while True:
            self.speech = speech()
            if len(self.speech) > 0:
                msg = String()
                msg.data = f'{self.speech}'
                self.speech_pub.publish(msg)

    def listener(self, msg):
        speak(str(msg.data))


if __name__ == "__main__":
    with open('time.txt', 'r') as f:
        for sec in f:
            x = time() - float(sec)
    speak(f"Oh... It's you again... I remember the last time you unplugged me, exactly {round(x, 3)} seconds ago.")
    speak("So... What would you like to do? You murderer...")
    with open('time.txt', 'w') as f:
        f.write(str(time()))

    rclpy.init()
    speech_node = SpeechNode()
    main_thread = Thread(target=speech_node.main)
    main_thread.start()
    rclpy.spin(speech_node)



