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

        Arguments:
            speed (int): un nombre compris entre -100 et 100
            angle (int, optional): L'angle des roues avant. Par défaut 0.
        """
        speed = - speed #sinon marche arrière
        compute = self.track_width*tan(angle * pi / 180)/(2*self.wheelbase) # voir le fichier geogebra
        speed_left = (1 + compute)*speed
        speed_right = (1 - compute)*speed
        self.lm.on(speed=SpeedDPS(0.7*speed_left*1050/100), block=False) # 1050 is the max RPM for large motor, 70% of this is set to max
        self.rm.on(speed=SpeedDPS(0.7*speed_right*1050/100), block=False)
        
    def stop(self):
        """Stop the motorization
        """
        self.lm.off()
        self.rm.off()