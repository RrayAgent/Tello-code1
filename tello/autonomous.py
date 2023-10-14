import struct

import cv2
import matplotlib.pyplot as plt
import numpy as np
from typing import NamedTuple


class Buildings(NamedTuple):
    name: str
    x: int | float
    y: int | float
    z: int | float
    x_mes: int | float
    y_mes: int | float
    shape: str


building_positions = [Buildings("School", 30, 107, 24, 18, 18, 'r'),
                      Buildings("Hospital", 73, 100, 36, 36, 36, 'r'),
                      Buildings("base Apartments", 36, 36, 48, 106, 24, 'r'),
                      Buildings("lower apartment 1", 347, 33, 40, 18, 24, 'r'),
                      Buildings("lower apartment 2", 347, 113, 40, 18, 24, 'r'),
                      Buildings("middle apartment 1", 392, 35, 64, 24, 36, 'r'),
                      Buildings("middle apartment 2", 392, 99, 64, 24, 36, 'r'),
                      Buildings("upper apartment 1", 412, 38, 106, 24, 24, 'r'),
                      Buildings("upper apartment 1", 412, 108, 106, 24, 24, 'r'),
                      Buildings("bridge", 424, 62, 106, 10, 45, 'ir'),
                      Buildings("tello landing", 180, 116, 0, 2.865, 2.865, 'c'),
                      Buildings("avr landing", 180, 50, 0, 5.730, 5.730, 'c'),
                      Buildings("field", 0, 0, 0, 472, 170, 'ir'),
                      Buildings("final doc", 292, 85, 32, 36, 69, 'cs')]

class Auto(object):
    """r= rectangle, c = circle(x and y measure is the radius), ir = irregular rectangle (like one that doesn't completely go to the ground),
     cs= compound shape"""
    """landing pads, field size, and final doc"""


    drone_start = (building_positions[10].x, building_positions[10].y, building_positions[10].z)

    def __init__(self, img, height):
        self.img = img
        self.height = height

    def edge_mask(self):
        gray_frames = cv2.cvtColor(self.img, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray_frames, (3, 3), 0)
        return cv2.Canny(blur, 25, 75)

    def find_direction_to_target(self, reference):
        h = self.edge_mask()

    def color_sensor(self, lower, upper):
        school_mask = cv2.inRange(self.img, lowerb=lower, upperb=upper)
        return cv2.bitwise_and(self.img, self.img, mask=school_mask)


