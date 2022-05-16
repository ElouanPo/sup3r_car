#!/usr/bin/env micropython
# coding: utf-8

from car import Car

mycar = Car('Interceptor')
mycar.light = 82
mycar.dark = 4
steering = mycar.get_steering()
steering.set_max_angle(120)
steering._steering_divider = 3
pid = mycar.get_pid()
pid.Kp = 1.2
pid.Ki = 1.5
pid.Kd = 0.1
mycar.configure()
#mycar.launch(speed = 50, measures = True)

