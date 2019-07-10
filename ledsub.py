#!/usr/bin/env python

from __future__ import print_function
import threading
from threading import Thread
import math
import time

import rospy
from led.msg import LedModeColor

from rpi_ws281x import Adafruit_NeoPixel
from rpi_ws281x import Color

LED_COUNT = 2 #q
LED_PIN = 18  # pin
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 100  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0  # Set to '1' for GPIOs 13, 19, 41, 45 or 53

# define led strip
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)

# variables
mode = ""
r = 0
g = 0
b = 0

r_prev = 0
g_prev = 0
b_prev = 0

l = 1
wait_ms = 10


# functions
def math_wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


def rainbow(wait=10):
    global wait_ms, mode
    wait_ms = wait
    mode = "rainbow"


def fill(red, green, blue):
    global r, g, b, mode
    r = red
    g = green
    b = blue
    mode = "fill"


def blink(red, green, blue, wait=250):
    global r, g, b, wait_ms, mode
    r = red
    g = green
    b = blue
    wait_ms = wait
    mode = "blink"


def chase(red, green, blue, wait=50):
    global r, g, b, wait_ms, mode
    r = red
    g = green
    b = blue
    wait_ms = wait
    mode = "chase"


def wipe_to(red, green, blue, wait=50):
    global r, g, b, wait_ms, mode
    r = red
    g = green
    b = blue
    wait_ms = wait
    mode = "wipe_to"


def fade_to(red, green, blue, wait=20):  # do not working with rainbow (solid colors only)
    global r, g, b, r_prev, g_prev, b_prev, wait_ms, mode
    r_prev = r
    g_prev = g
    b_prev = b
    r = red
    g = green
    b = blue
    wait_ms = wait
    mode = "fade_to"


def run(red, green, blue, length=strip.numPixels(), wait=25):
    global r, g, b, l, wait_ms, mode
    r = red
    g = green
    b = blue
    l = length
    wait_ms = wait
    mode = "run"


def off():
    global mode
    mode = "off"


def strip_set(color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()


def strip_rainbow_frame(iteration):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, math_wheel((int(i * 256 / strip.numPixels()) + iteration) & 255))
    strip.show()


def strip_chase_step(color):
    for q in range(3):
        for i in range(0, strip.numPixels(), 3):
            strip.setPixelColor(i + q, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)
        for i in range(0, strip.numPixels(), 3):
            strip.setPixelColor(i + q, 0)


def strip_wipe(color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        time.sleep(wait_ms / 1000.0)
        strip.show()


def strip_fade(r1, g1, b1, r2, g2, b2, frames=51):
    r_delta = (r2-r1)//frames
    g_delta = (g2-g1)//frames
    b_delta = (b2-b1)//frames
    for i in range(frames):
        red = r1 + (r_delta * i)
        green = g1 + (g_delta * i)
        blue = b1 + (b_delta * i)
        strip_set(Color(red, green, blue))
        time.sleep(wait_ms / 1000.0)
    strip_set(Color(r2, g2, b2))


def strip_run_step(red, green, blue, length, iteration):
    r_delta = red // length
    g_delta = green // length
    b_delta = blue // length
    for i in range(strip.numPixels()):
        n = (i+iteration) % strip.numPixels()
        r_fin = max(0, (red - (r_delta * i)))
        g_fin = max(0, (green - (g_delta * i)))
        b_fin = max(0, (blue - (b_delta * i)))
        strip.setPixelColor(n, Color(r_fin, g_fin, b_fin))
    strip.show()


def strip_off():
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()



def callback(data):
    global r,g,b,mode
    r = int(data.color.r)
    g = int(data.color.g)
    b = int(data.color.b)
    mode = data.mode
    # rospy.loginfo(data)


def listener():
    # In ROS, nodes are uniquely named. If two nodes with the same
    # name are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaneously.
    rospy.init_node('listener', anonymous=True)

    rospy.Subscriber("ledtopic", LedModeColor, callback)

    # # spin() simply keeps python from exiting until this node is stopped
    # rospy.spin()


# init
strip.begin()

print('lib intited')
print("Starting thread")
iteration = 0

listener()

while not rospy.is_shutdown():
    # print(mode)
    if mode == "rainbow":
        if iteration >= 256:
            iteration = 0
        strip_rainbow_frame(iteration)
        time.sleep(wait_ms / 1000.0)
        iteration += 1
    elif mode == "fill":
        strip_set(Color(r, g, b))
        time.sleep(wait_ms / 1000.0)
        mode = ""
    elif mode == "blink":
        strip_set(Color(r, g, b))
        time.sleep(wait_ms / 1000.0)
        strip_set(Color(0, 0, 0))
        time.sleep(wait_ms / 1000.0)
    elif mode == "chase":
        strip_chase_step(Color(r, g, b))
    elif mode == "wipe_to":
        strip_wipe(Color(r, g, b))
        mode = ""
    elif mode == "fade_to":
        strip_fade(r_prev, g_prev, b_prev, r, g, b)
        mode = ""
    elif mode == "run":
        strip_run_step(r, g, b, l, iteration)
        time.sleep(wait_ms / 1000.0)
        iteration += 1
    elif mode == "off":
        strip_off()
        mode = ""
    else:
        time.sleep(wait_ms / 1000.0)
