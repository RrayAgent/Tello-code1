import math

import cv2
import numpy as np
from djitellopy import Tello
import controls as con
import autonomous as at
import matplotlib.pyplot as plt
import time

speed = 100


def drone_control() -> [int, int, int, int]:

    rotation = 100
    lr, fb, ud, yv = 0, 0, 0, 0

    if con.get_keys('w'):
        fb = speed
    elif con.get_keys('s'):
        fb = -speed
    if con.get_keys('a'):
        lr = -speed
    elif con.get_keys('d'):
        lr = speed
    if con.get_keys('j'):
        ud = speed
    elif con.get_keys('l'):
        ud = -speed
    if con.get_keys('k'):
        yv = rotation
    elif con.get_keys('i'):
        yv = -rotation

    return lr, fb, ud, yv


# Press the green button in the gutter to run the script.

def move_to_location(all_loc: dict, start_loc: str, end_loc: str, drone: Tello) -> (int | float, int | float, int | float):
    start_position = ()
    start_height = None
    end_position = ()
    end_height = None
    pos_difference = ()
    
    if all_loc.__contains__(start_loc) and all_loc.__contains__(end_loc):
        start_height = drone.get_height()
        start_position = (all_loc[start_loc][0], all_loc[start_loc][1])

        end_position = (all_loc[end_loc][0], all_loc[end_loc][1])
        end_height = 10+all_loc[end_loc][2]

    
    print(-start_position[0]+end_position[0])
    pos_difference = (end_position[0]-start_position[0], end_position[1]-start_position[1], end_height-start_height)
    
    for a in all_loc.keys():
        if drone.get_height()<=math.ceil(all_loc[a][2]).__pos__():
            if (start_position[0] <= all_loc[a][0] <= end_position[0] or start_position[0] >= all_loc[a][0] <= end_position[0]) and math.ceil(all_loc[a][2]).__pos__()!=0:
                drone.go_xyz_speed(0,0, math.ceil(all_loc[a][2]+10).__pos__(), speed)
    
    drone.go_xyz_speed(math.floor(pos_difference[0]).__abs__(), 0, 0, speed)
    if drone.get_height()<=math.ceil(all_loc[a][2]).__pos__() and pos_difference[2]>0:
        drone.go_xyz_speed(0,0, math.ceil(pos_difference[2]).__pos__(), int(speed/10))
    
    

def main():
    con.init()
    tello = Tello()
    tello.connect()
    tello.streamon()
    upper_brown = (37, 66, 201)
    lower_brown = (0, 27, 74)
    new_buildings = {}
    for i in at.building_positions:
        new_buildings[i.name] = [i.x*2.5, i.y*2.5, i.z*2.5, i.x_mes*2.5, i.y_mes*2.5, i.shape]

    def video(fr):

        edge_frames = fr.edge_mask()

        color_im = fr.color_sensor(lower=lower_brown, upper=upper_brown)
        """try:
            lines = cv2.HoughLinesP(edge_frames, 1, np.pi / 100, 100, minLineLength=100, maxLineGap=10)
            for i in lines:
                x1, y1, x2, y2 = i[0]
                cv2.line(n_frame, (x1,y1), (x2,y2), (0, 255, 0), 2)
        except TypeError:
            print("error")"""
        cv2.imshow("cTello_control", edge_frames)
        cv2.imshow("nTello_control", fr.img)

    manual_con = False
    m1_comlpete = False
    tello.takeoff()
    while True:
        if con.get_keys('c'):
            tello.flip_back()
            break

        elif con.get_keys('m'):
            manual_con = True

        if manual_con:
            val: [int, int, int, int] = drone_control()
            tello.send_rc_control(val[0], val[1], val[2], val[3])

        if m1_comlpete != True:
            move_to_location(new_buildings, "tello landing", "School", tello)
            tello.flip_back()
            tello.rotate_clockwise(180)
            move_to_location(new_buildings, "School", "tello landing", tello)
            m1_comlpete=True

        fr = at.Auto(cv2.cvtColor(tello.get_frame_read().frame, cv2.COLOR_RGB2BGR), tello.get_height())
        video(fr)

        cv2.waitKey(1)

    tello.streamoff()
    cv2.destroyAllWindows()


if __name__ == '__main__':

    main()
