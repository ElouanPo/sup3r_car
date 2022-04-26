#!/usr/bin/env micropython
# coding: utf-8

from ev3dev2.motor import MediumMotor

class Direction:
    """
    Une classe représentant la direction de la sup3r car
    """
    # Constructor
    def __init__(self):
        # motors
        self.dir = MediumMotor('outA'); # medium motor
        
    def turn(self, angle, speed=50):
        """
        Tourne le moteur de direction à la position 'angle'. Angle positif à droite, négatif à gauche
        La valeur par défaut de la vitesse de rotation est 50.
        """
        self.dir.on_to_position(speed, - angle)
        


