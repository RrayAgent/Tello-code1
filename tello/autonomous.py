import struct
from djitellopy import Tello
import djitellopy as dp
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

"""r= rectangle, c = circle(x and y measure is the radius), ir = irregular rectangle (like one that doesn't completely go to the ground),
cs= compound shape"""

building_positions = [Buildings("School", 30, 107, 24, 18, 18, 'r'),
                      Buildings("Hospital", 73, 100, 36, 36, 36, 'r'),
                      Buildings("base Apartments", 36, 36, 48, 106, 24, 'r'),
                      Buildings("lower apartment 1", 347, 33, 40, 18, 24, 'r'),
                      Buildings("lower apartment 2", 347, 113, 40, 18, 24, 'r'),
                      Buildings("middle apartment 1", 392, 35, 64, 24, 36, 'r'),
                      Buildings("middle apartment 2", 392, 99, 64, 24, 36, 'r'),
                      Buildings("upper apartment 1", 412, 38, 106, 24, 24, 'r'),
                      Buildings("upper apartment 2", 412, 108, 106, 24, 24, 'r'),
                      Buildings("bridge", 424, 62, 106, 10, 45, 'ir'),
                      Buildings("tello landing", 180, 116, 0, 2.865, 2.865, 'c'),
                      Buildings("avr landing", 180, 50, 0, 5.730, 5.730, 'c'),
                      Buildings("field", 0, 0, 0, 472, 170, 'ir'),
                      Buildings("final doc", 292, 85, 32, 36, 69, 'cs')]

def move_over_500(dist, drone, speed):
    try:
        if round(dist[0]).__abs__()<500 and round(dist[1]).__abs__():
            drone.go_xyz_speed(round(dist[0]).__abs__()+25, round(dist[1]).__abs__(), 0, speed)
        else:
            drone.go_xyz_speed(0,-round(dist[1]).__abs__()-50,0,speed)
            i = round(dist[0]+85).__abs__()
            while True:
                drone.go_xyz_speed(500, 0, 0, speed)
                i-=500
                if i<=500:
                    drone.go_xyz_speed(i, 0, 0, speed)
                    break
    except dp.tello.TelloException as exception:
        raise exception("Move forward isn't working")

def move_to_location(all_loc: dict, start_loc: str, end_loc: str, drone: Tello, height, speed) -> [int | float, int | float, int | float, int | float]:
    start_position = []
    start_height = float(height)
    end_position = []
    end_height = None
    pos_difference = []
    
    if all_loc.__contains__(start_loc) and all_loc.__contains__(end_loc):
        
        start_position = [all_loc[start_loc][0]+all_loc[start_loc][3]/2, all_loc[start_loc][1]+all_loc[start_loc][4]/2]

        end_position = [all_loc[end_loc][0]+(all_loc[end_loc][3]/2), all_loc[end_loc][1]+(all_loc[end_loc][4]/2)]
        end_height = int(25+all_loc[end_loc][2])
    
    print(end_position[0]-start_position[0])

    pos_difference = [round(end_position[0])-round(start_position[0]+25), round(end_position[1]-start_position[1]+25), round(end_height-start_height)]
    
    for a in all_loc.keys():
        try:
            if drone.get_height()<=round(all_loc[a][1]).__pos__() and height<=end_height+10:
                if (start_position[0] <= all_loc[a][0] <= end_position[0] or start_position[0] >= all_loc[a][0] <= end_position[0]) and round(all_loc[a][2]+5).__abs__()-height>=0:
                    drone.go_xyz_speed(0,0, round(all_loc[a][2]+5).__abs__()-height, 10)
                    
                    height+=round(all_loc[a][2]).__pos__()-height
        except WindowsError as win:
            raise win("Sys crash")
    
    print((drone.get_height()/2.54)/12)
    move_over_500(pos_difference, drone, speed)
    
    return [round(pos_difference[0]).__abs__(), round(pos_difference[1]).__abs__(), -1*drone.get_height(), speed]
    

class Auto(object):
    
    """landing pads, field size, and final doc"""


    drone_start = (building_positions[10].x, building_positions[10].y, building_positions[10].z)

    def __init__(self, img):
        self.img = img

    def edge_mask(self):
        gray_frames = cv2.cvtColor(self.img, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray_frames, (3, 3), 0)
        return cv2.Canny(blur, 25, 75)

    def find_direction_to_target(self, reference):
        h = self.edge_mask()

    def color_sensor(self, lower, upper):
        school_mask = cv2.inRange(self.img, lowerb=lower, upperb=upper)
        return cv2.bitwise_and(self.img, self.img, mask=school_mask)


