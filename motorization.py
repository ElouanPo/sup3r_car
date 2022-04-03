#!/usr/bin/env micropython
# coding: utf-8
from ev3dev2.motor import LargeMotor, SpeedDPS # DPS stands for Degree Per Second

class Motorization:
    """
    Une classe représentant la motorisation de la sup3r car
    """
    # Constructor
    def __init__(self):
        # motors
        self.lm = LargeMotor('outB');   # left motor
        self.rm = LargeMotor('outC');   # right motor

    def run(speed, direction = 0):
        """Fait tourner les moteurs

        Args:
            speed (int): un nombre compris entre -100 et 100
            direction (int, optional): L'angle des roues avant. Defaults to 0.
        """
        for i in range (0, 5000, 100):
            self.lm.on_for_seconds(speed=SpeedDPM(i), seconds=0.1)

motors = Motorization()
motors.run(0)