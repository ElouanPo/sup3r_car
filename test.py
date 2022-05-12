#!/usr/bin/env micropython
# coding: utf-8

from car import Car

mycar = Car('Interceptor')
mycar.light = 90
mycar.dark = 2
steering = mycar.get_steering()
steering.set_max_angle(120)
steering._steering_divider = 3.5
pid = mycar.get_pid()
pid.Kp = 1
pid.Ki = 0.5
pid.Kd = 0
mycar.configure()
#mycar.launch(speed = 50, measures = True)

