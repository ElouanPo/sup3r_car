#!/usr/bin/env micropython
# coding: utf-8

# Import the EV3-robot library
from ev3dev2.motor import MediumMotor, LargeMotor
from ev3dev2.sensor.lego import ColorSensor, UltrasonicSensor
from ev3dev2.button import Button
from ev3dev2.led import Leds 
from ev3dev2.sound import Sound
# Import time
from time import sleep


class LineFollower:
    """
    Une classe représentant notre suiveur de ligne.
    """
    # Constructor
    def __init__(self):
        self.btn = Button()
        self.leds = Leds()
        self.sound = Sound()
        self.voice_options = '-a 200 -s 100 -v fr+f2' # voir https://sites.google.com/site/ev3devpython/learn_ev3_python/sound 
        # Capteur de couleur
        self.cs = ColorSensor()
        self.light = None               # Initialisation de la partie claire à None
        self.dark = None                # Initialisation de la partie foncée à None
        # motors
        self.lm = LargeMotor('outB');   # left motor
        self.rm = LargeMotor('outC');   # right motor
        self.dir = MediumMotor('outA'); # medium motor

    def get_threshold(self):
        """
        Retourne la valeur de consigne
        """
        return (self.light+self.dark)//2

    ###############################################
    #
    #  PARTIE CALIBRATION DU CAPTEUR
    #
    ###############################################
    def speak(self, message, display = True):
        """
        Speak the message.
        if display is True, print the message
        """
        self.sound.speak(message, espeak_opts = self.voice_options)
        if display:
            print(message)

    def calibrate(self):
        """
        Launch the calibration of the color sensor
        """

        def calibrate_light(state):
            if state:
                self.calibrate_zone(1)

        def calibrate_dark(state):
            if state:
                self.calibrate_zone(0)

        self.cs.MODE_REFLECT = 'REFLECT'

        self.leds.all_off()
        self.speak("Calibration du capteur de couleur.")
        self.leds.set_color('LEFT', 'GREEN')
        print("Mettez le capteur de couleur sur la partie claire et appuyez sur le bouton gauche pour démarrer.")
        self.light = None
        while self.light == None:
            self.btn.on_left = calibrate_light
            self.btn.process()
            sleep(0.01)
        print("Mettez le capteur de couleur sur la partie foncée et appuyez sur le bouton gauche pour demarrer.")
        self.dark = None
        while self.dark == None:
            self.btn.on_left = calibrate_dark
            self.btn.process()
            sleep(0.01)
        self.speak("Calibration terminée")
        self.speak("La valeur de consigne est "+str(self.get_threshold()))

    def calibrate_zone(self, zone):
        """
        Calibration de la zone.
        zone : 1 pour la partie claire, 0 pour la partie foncée
        """
        self.leds.all_off()
        measures = []
        for i in range(5):
            self.leds.set_color('RIGHT', 'GREEN')
            sleep(0.2)
            measure = self.cs.reflected_light_intensity
            print(measure)
            measures.append(measure)
            self.leds.set_color('RIGHT', 'BLACK')
            sleep(0.2)
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

    def other(self):
        # motors
        lm = LargeMotor('outB');  # left motor
        rm = LargeMotor('outC');  # right motor
        mm = MediumMotor('outA'); # medium motor

        speed = -360  # deg/sec, [-1000, 1000]
        dt = 500       # milliseconds
        stop_action = "coast"

        # PID tuning
        Kp = 1  # proportional gain
        Ki = 0  # integral gain
        Kd = 0  # derivative gain

        integral = 0
        previous_error = 0

        # initial measurment
        target_value = cs.value()

        # Start the main loop
        while not self.shut_down:

            # deal with obstacles
            #distance = us.value() // 10  # convert mm to cm

            #if distance <= 5:  # sweep away the obstacle
            #    mm.run_timed(time_sp=600, speed_sp=+150, stop_action="hold").wait()
            #    mm.run_timed(time_sp=600, speed_sp=-150, stop_action="hold").wait()

            # Calculate steering using PID algorithm

            error = target_value - cs.value()
            print(error)
            integral += (error * dt)
            derivative = (error - previous_error) / dt

            # u zero:     on target,  drive forward
            # u positive: too bright, turn right
            # u negative: too dark,   turn left

            u = (Kp * error) + (Ki * integral) + (Kd * derivative)

            # limit u to safe values: [-1000, 1000] deg/sec
            if speed + abs(u) > 1000:
                if u >= 0:
                    u = 1000 - speed
                else:
                    u = speed - 1000

            # run motors
            if u >= 0:
                lm.run_timed(time_sp=dt, speed_sp=speed + u, stop_action=stop_action)
                rm.run_timed(time_sp=dt, speed_sp=speed - u, stop_action=stop_action)
                sleep(dt / 1000)
            else:
                lm.run_timed(time_sp=dt, speed_sp=speed - u, stop_action=stop_action)
                rm.run_timed(time_sp=dt, speed_sp=speed + u, stop_action=stop_action)
                sleep(dt / 1000)

            previous_error = error

            # Check if buttons pressed (for pause or stop)
            if not self.btn.down:  # Stop
                print("Exit program... ")
                self.shut_down = True
            elif not self.btn.left:  # Pause
                print("[Pause]")
                self.pause()

    # 'Pause' method
    def pause(self, pct=0.0, adj=0.01):
        while self.btn.right or self.btn.left:  # ...wait 'right' button to unpause
            ev3.Leds.set_color(ev3.Leds.LEFT, ev3.Leds.AMBER, pct)
            ev3.Leds.set_color(ev3.Leds.RIGHT, ev3.Leds.AMBER, pct)
            if (pct + adj) < 0.0 or (pct + adj) > 1.0:
                adj = adj * -1.0
            pct = pct + adj

        print("[Continue]")
        #ev3dev2.Leds.set_color(ev3.Leds.LEFT, ev3.Leds.GREEN)
        #ev3.Leds.set_color(ev3.Leds.RIGHT, ev3.Leds.GREEN)


# Main function
if __name__ == "__main__":
    robot = LineFollower()
    robot.calibrate()
    #robot.run()
