#!/usr/bin/env micropython
# coding: utf-8

# Import the EV3-robot library
from ev3dev2.motor import MediumMotor, LargeMotor
from ev3dev2.sensor.lego import ColorSensor, UltrasonicSensor, TouchSensor
from ev3dev2.button import Button
from ev3dev2.led import Leds 
from ev3dev2.sound import Sound
# Import time
import time
import json


# Appels des autres classes
from motorization import Motorization
from steering import Steering
from PID import PID



class Car:
    """
    Une classe représentant notre voiture suiveuse de ligne.
    """
    # Constructor
    def __init__(self, name = ''):
        self._name = name
        self.btn = Button()
        self.leds = Leds()
        self.sound = Sound()
        self.voice_options = '-a 200 -s 100 -v fr+f2' # voir https://sites.google.com/site/ev3devpython/learn_ev3_python/sound 
        # Capteur de couleur
        self.cs = ColorSensor()
        self.light = None               # Initialisation de la partie claire à None
        self.dark = None                # Initialisation de la partie foncée à None
        # Touch Sensor
        self._touch_sensor = TouchSensor()
        # motorization
        self._motorization = Motorization(self)
        self._pid = PID(0, 0, 0)
        self._plots = {}
        
        # steering
        self._steering = Steering(self)
        
    def set_name(self, name):
        """
        Set the name of the car
        """
        self._name = name

    def get_name(self):
        """Return the name of the car
        """
        return self._name

    def get_motorization(self):
        """Return the instance of the motorization"""
        return self._motorization

    def get_steering(self):
        """Return the instance of the steering"""
        return self._steering

    def get_touch_sensor(self):
        """Return the instance of the touch sensor"""
        return self._touch_sensor

    def get_pid(self):
        """Return the instance of the PID"""
        return self._pid

    def get_threshold(self):
        """
        Return the threshold value, None if not set
        """
        if self.light and self.dark:
            return (self.light+self.dark)//2

    def speak(self, message, display = True):
        """
        Speak the message.
        if display is True, print the message
        """
        if display:
            print(message)
        self.sound.speak(message, espeak_opts = self.voice_options)

    def launch(self, speed = 100, measures = False):
        """
        Launch the line follower
        """
        pid = self.get_pid()
        cs = self.cs
        touch_sensor = self.get_touch_sensor()
        #if not self.get_threshold():
        #    self.calibrate()
        pid.SetPoint = self.get_threshold()
        if measures:
            self._plots['Kp'] = self.get_pid().Kp
            self._plots['Ki'] = self.get_pid().Ki
            self._plots['Kd'] = self.get_pid().Kd
            self._plots['threshold'] = self.get_threshold()
            self._plots['datas'] = []
        while not touch_sensor.is_pressed:
            feedback = cs.reflected_light_intensity
            if measures:
                now = time.time()
                self._plots['datas'].append((now, feedback))
            pid.update(feedback)
            print(pid.output)
            self.get_steering().turn(pid.output, speed=100)
            self.get_motorization().run(speed)
        
        if measures:
            with open('json_data.json', 'w') as outfile:
                json_string = json.dumps(self._plots)
                json.dump(json_string, outfile)

        self.get_motorization().stop()



    ###############################################
    #
    #  Interface de configuration
    #
    ###############################################

    def configure(self):
        liste = (('1',"Configuration de la direction"),
                 ('2',"Configuration du capteur de lumière"),
                 ('3',"Configuration du PID"),
                 ('4',"Executer le suiveur de ligne"),
                 ('Q',"Quitter"),
        )
        quitter = False
        self.get_motorization().stop()
        while not quitter:
            print("\n##################################\n Menu Principal \n##################################\n")
            for char, description in liste:
                print(char + ' : ' +description)
            choix = input("Votre choix : ")

            if choix == '1':
                self._configure_steering()
            elif choix == '2':
                self._configure_light_sensor()
            elif choix == '3':
                self._configure_PID()
            elif choix == '4':
                self._run_line_follower()
            elif choix == 'Q' or choix == 'q':
                quitter = True
        print('Fin du programme')


    def _configure_steering(self):
        print("--------------------------\nConfiguration de la direction\n--------------------------\n")
        liste = (('U',"Revenir au menu principal"),
                 ('1',"Déterminer l'angle maximal de rotation du moteur de direction."),
                 ('2',"Déterminer l'angle maximal de braquage des roues."),
        )
        for char, description in liste:
            print(char + ' : ' +description)
        choix = input("Votre choix : ")
        if choix == 'U' or choix == 'u':
            self.configure()
        elif choix == '1':
            self.get_steering().set_max_angle(720)
            max_angle = False
            while not max_angle:
                angle = int(input("Entrez l'angle de rotation du moteur de direction : "))
                self.get_steering().turn(angle)
                time.sleep(1)
                self.get_steering().turn(-angle)
                time.sleep(1)
                self.get_steering().turn(0)
                new_angle = input("Voulez vous tester un nouvel angle (Y/n)? : ")
                if new_angle == 'N' or new_angle == 'n':
                    self.get_steering().set_max_angle(abs(angle))
                    print("Affectation de l'angle maximal du moteur de direction : " + str(self.get_steering().get_max_angle()))
                    max_angle = True
        elif choix == '2':
            steering = self.get_steering()
            max_angle = steering.get_max_angle()
            print("Mesurer l'angle de braquage des roues")
            print("Angle zéro : ")
            steering.turn(0)
            time.sleep(1)
            print("Angle maximal de rotation du moteur de direction : " + str(max_angle) )
            steering.turn(max_angle)
            print("Mesurer l'angle de rotation roues.")
            wheel_angle = int(input("Entrer l'angle de rotation des roues : "))
            divider = steering.get_max_angle()/wheel_angle
            steering._steering_divider = divider
            print("Rapport de division : " + str(divider))
            steering.turn(0)


    def _configure_light_sensor(self):
        print("--------------------------\nConfiguration du capteur de lumière\n--------------------------\n")
        liste = (('U',"Revenir au menu principal"),
                 ('1',"Calibration du capteur de lumière"),
        )
        for char, description in liste:
            print(char + ' : ' +description)
        choix = input("Votre choix : ")
        if choix == 'U' or choix == 'u':
            self.configure()
        elif choix == '1':
            calibration_OK = False
            while not calibration_OK:
                self.calibrate()
                answer_calibration = input("Voulez vous refaire une calibration (Y/n)? : ")
                if answer_calibration == 'N' or answer_calibration == 'n':
                    calibration_OK = True
        self.configure()
        

    def _configure_PID(self):
        print("--------------------------\nConfiguration du PID\n--------------------------\n")
        PID_OK = False
        while not PID_OK:
            kp = input("Entrer la valeur du KP  : [%s]"%(self.get_pid().Kp))
            if kp == '':
                kp = self.get_pid().Kp
            else:
                kp = float(kp)
            self.get_pid().Kp = kp
            ki = input("Entrer la valeur du KI : [%s]"%(self.get_pid().Ki))
            if ki == '':
                ki = self.get_pid().Ki
            else:
                ki = float(ki)
            self.get_pid().Ki = ki
            kd = input("Entrer la valeur du KD : [%s]"%(self.get_pid().Kd))
            if kd == '':
                kd = self.get_pid().Kd
            else:
                kd = float(kd)
            self.get_pid().Kd = kd
            answer_pid = input("Voulez vous reconfigurer le PID (y/N)? : ")
            if answer_pid =='Y' or answer_pid =='y':
                PID_OK = False
            else:
                PID_OK = True
        
        self.configure()

    def _run_line_follower(self):
        print("--------------------------\nLancement du programme\n--------------------------\n")
        speed = int(input("Entrer la vitesse entre 0 et 100 : "))
        print("###### Press the touch sensor to stop the car ########.")
        self.launch(speed)

    

    def calibrate(self):
        """
        Launch the calibration of the color sensor
        """

        def calibrate_light(state):
            if state:
                self._calibrate_zone(1)

        def calibrate_dark(state):
            if state:
                self._calibrate_zone(0)

        self.cs.MODE_REFLECT = 'REFLECT'

        self.leds.all_off()
        self.speak("Calibration du capteur de couleur.")
        self.leds.set_color('LEFT', 'GREEN')
        print("Mettez le capteur de couleur sur la partie claire et appuyez sur le bouton gauche pour démarrer.")
        self.light = None
        while self.light == None:
            self.btn.on_left = calibrate_light
            self.btn.process()
            time.sleep(0.01)
        print("Mettez le capteur de couleur sur la partie foncée et appuyez sur le bouton gauche pour demarrer.")
        self.dark = None
        while self.dark == None:
            self.btn.on_left = calibrate_dark
            self.btn.process()
            time.sleep(0.01)
        if self.get_name():
            self.speak("Calibration de " + self.get_name() + " terminée")
        else:
            self.speak("Calibration terminée")
        self.speak("La valeur de consigne est "+str(self.get_threshold()))

    def _calibrate_zone(self, zone):
        """
        Calibration de la zone.
        zone : 1 pour la partie claire, 0 pour la partie foncée
        """
        self.leds.all_off()
        measures = []
        for i in range(5):
            self.leds.set_color('RIGHT', 'GREEN')
            time.sleep(0.2)
            measure = self.cs.reflected_light_intensity
            print(measure)
            measures.append(measure)
            self.leds.set_color('RIGHT', 'BLACK')
            time.sleep(0.2)
        # calcul de la moyenne des mesures
        average = int(sum(measures)/len(measures))
        # Partie claire
        if zone == 1:
            self.light = average
            message = "Partie claire : "+str(self.light)
        # Partie foncée
        elif zone == 0:
            self.dark = average
            message = "Partie foncée : "+str(self.dark)
        self.speak(message)