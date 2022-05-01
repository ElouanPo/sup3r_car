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
    def __init__(self, car):
        # motors
        self._lm = LargeMotor('outB');   # left motor
        self._rm = LargeMotor('outC');   # right motor
        self._wheelbase = 19             # empattement (distance entre essieux)
        self._track_width = 15           # voie (distance entre pneux)
        self._car = car

    #############################################################################
    #   GETTERS
    #############################################################################

    def get_car(self):
        """Return the car instance the steering is attached to"""
        return self._car

    def get_left_motor(self):
        return self._lm

    def get_right_motor(self):
        return self._rm

    def get_wheelbase(self):
        return self._wheelbase

    def get_track_width(self):
        return self._track_width

    def run(self, speed):
        """Fait tourner les moteurs

        Arguments:
            speed (int): un nombre compris entre -100 et 100
        """
        speed = -speed #sinon marche arrière
        if speed > 100 : speed = 100
        elif speed < -100 : speed = -100

        angle = self.get_car().get_steering().get_angle()
        compute = self.get_track_width()*tan(angle * pi / 180)/(2*self.get_wheelbase()) # voir le fichier geogebra
        speed_left = (1 - compute)*speed/100
        speed_right = (1 + compute)*speed/100

        if speed_right > 1 or speed_right < -1:
            divider = abs(speed_right)
        elif speed_left > 1 or speed_left < -1:
            divider = abs(speed_left)
        else:
            divider = 1
        
        self.get_left_motor().on(speed=SpeedDPS(speed_left*1040/divider), block=False) # 1050 is the max RPM for large motor
        self.get_right_motor().on(speed=SpeedDPS(speed_right*1040/divider), block=False)
        
    def stop(self):
        """Stop the motorization
        """
        self.get_left_motor().off()
        self.get_right_motor().off()
        self.get_car().get_steering().turn(0)