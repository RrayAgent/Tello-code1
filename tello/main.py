import time
import datetime as dt
import os
import cv2
from djitellopy import Tello
import djitellopy as dp
import controls as con
import autonomous as at
from threading import Thread

speed = 85


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


    

def main():
    con.init()
    tello = Tello()
    tello.connect()
    tello.streamon()
    upper_brown = (37, 66, 201)
    lower_brown = (0, 27, 74)
    new_buildings = {}
    for i in at.building_positions:
        new_buildings[i.name] = [i.x*2.54, i.y*2.54, i.z*2.54, i.x_mes*2.54, i.y_mes*2.54, i.shape]
    
    def video():
        h = tello.get_frame_read()
        while True:
            if con.get_keys('c'):
                break
            fr=at.Auto(cv2.cvtColor(h.frame, cv2.COLOR_RGB2BGR))
            edge_frames = fr.edge_mask()
            
            #color_im = fr.color_sensor(lower=lower_brown, upper=upper_brown)
            
            cv2.imshow("lTello_control", edge_frames)
            cv2.imshow("nTello_control", fr.img)
            #cv2.imshow("cTello_control", color_im)
    vid = Thread(target=video)
    vid.start()
    manual_con = True
    m1_comlpete = True
    m2 = True
    i=0
    while True:
        
        if con.get_keys('c'):
            break
        if con.get_keys('y'): 
            try:
                tello.takeoff()
            except dp.tello.TelloException as tell:
                raise tell("not taking off")
            if i == 0:
                m1_comlpete=False
                m2=True
        if con.get_keys('m'):
            manual_con = True
            m1_comlpete=True
            m2=True

        if manual_con:
            if con.get_keys('f'):
                tello.flip_back()
            if con.get_keys('v'):
                tello.land()
            val: [int, int, int, int] = drone_control()
            tello.send_rc_control(val[0], val[1], val[2], val[3])

        if m1_comlpete != True:
            t=time.time()
            height=at.move_to_location(new_buildings, "tello landing", "School", tello, tello.get_height(),speed)
            tello.flip_back()
            tello.rotate_clockwise(180)
            try:
                tello.go_xyz_speed(height[0]-10,height[1]+5,0,height[3])
            except dp.tello.TelloException as f:
                f("no move 2")
            
            tello.land()
            t2=time.time()
            sleep=0
            if t2-t<30:
                sleep=30-(t2-t)
                print(sleep)
            time.sleep(sleep)
            m1_comlpete=True
            i=1
        elif m1_comlpete and m2 ==False:
            
            #tello.takeoff()
            height=at.move_to_location(new_buildings, "tello landing", "bridge", tello, tello.get_height(), speed)
            #tello.flip_back()
            
            tello.rotate_clockwise(180)
            
            try:
                tello.go_xyz_speed(0,0,new_buildings["bridge"][2]-tello.get_height,speed)
            except dp.TelloException as tell:
                tell("not lowering")
            time.sleep(30)
            try:
                tello.go_xyz_speed(0,0,65,speed)
            except dp.TelloException as tell:
                tell("not rising")
            at.move_to_location(new_buildings, "bridge", "final doc", tello, tello.get_height(), speed)
            tello.go_xyz_speed(0,65,0,speed)
            tello.land()
            m2 = True
            
        
        
        cv2.waitKey(1)

    tello.streamoff()
    cv2.destroyAllWindows()
    vid.join()


if __name__ == '__main__':
    main()
