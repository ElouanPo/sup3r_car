#!/usr/bin/env micropython
# coding: utf-8

from ev3dev2.motor import LargeMotor, SpeedDPS # DPS stands for Degree Per Second
from math import sqrt, tan, pi
from time import sleep

class Motorization:
    """
    Une classe représentant la motorisation de la sup3r car
    """
    # Constructor
    def __init__(self):
        # motors
        self.lm = LargeMotor('outB');   # left motor
        self.rm = LargeMotor('outC');   # right motor
        self.wheelbase = 19             # empattement (distance entre essieux)
        self.track_width = 15           # voie (distance entre pneux)

    def run(self, speed, angle = 0):
        """Fait tourner les moteurs

        Args:
            speed (int): un nombre compris entre -100 et 100
            angle (int, optional): L'angle des roues avant. Defaults to 0.
        """
        speed = - speed
        for angle in range(-40, 41, 1):
            print("angle: "+str(angle))
            compute = self.track_width*tan(angle * pi / 180)/(2*self.wheelbase)
            speed_left = (1 + compute)*speed
            speed_right = (1 - compute)*speed
            print(str(speed_left) + "-<" + str(speed) + "->" + str(speed_right))
            self.lm.on(speed=SpeedDPS(speed_left), block=False)
            self.rm.on(speed=SpeedDPS(speed_right), block=False)
            sleep(0.1)
        sleep(2)
        self.lm.off()
        self.rm.off()

motors = Motorization()
motors.run(500)