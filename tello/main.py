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

def move_over_500(dist, drone):
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

def move_to_location(all_loc: dict, start_loc: str, end_loc: str, drone: Tello, height) -> [int | float, int | float, int | float, int | float]:
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
                if (start_position[0] <= all_loc[a][0] <= end_position[0] or start_position[0] >= all_loc[a][0] <= end_position[0]) and round(all_loc[a][2]-10).__abs__()-height>=0:
                    try:
                        drone.go_xyz_speed(0,0, round(all_loc[a][2]).__abs__()-height, 10)
                    except dp.tello.TelloException as annoy:
                        raise annoy("not rising")
                    height+=round(all_loc[a][2]).__pos__()-height
        except WindowsError as win:
            raise win("Sys crash")
    
    print((drone.get_height()/2.54)/12)
    move_over_500(pos_difference, drone)
    
    return [round(pos_difference[0]).__abs__(), round(pos_difference[1]).__abs__(), -1*drone.get_height(), speed]
    
    

def main():
    con.init()
    tello = Tello()
    tello.connect()
    tello.streamon()
    #upper_brown = (37, 66, 201)
    #lower_brown = (0, 27, 74)
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
            
            cv2.imshow("cTello_control", edge_frames)
            cv2.imshow("nTello_control", fr.img)
    vid = Thread(target=video)
    vid.start()
    manual_con = False
    m1_comlpete = True
    m2 = True
    
    while True:
        
        if con.get_keys('c'):
            break
        elif con.get_keys('y'):
            try:
                tello.takeoff()
            except dp.tello.TelloException as tell:
                raise tell("not taking off")
            m1_comlpete=False
            m2=False
        elif con.get_keys('m'):
            manual_con = True
            m1_comlpete=True
            m2=True

        if manual_con:
            val: [int, int, int, int] = drone_control()
            tello.send_rc_control(val[0], val[1], val[2], val[3])

        if m1_comlpete != True:
            t=time.time()
            height=move_to_location(new_buildings, "tello landing", "School", tello, tello.get_height())
            try:
                tello.go_xyz_speed(10,0,0,1)
                tello.go_xyz_speed(0,5,0,1)
            except dp.tello.TelloException as f:
                f("no move")
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
            
        elif m1_comlpete and m2 ==False:
            tello.takeoff()
            height=move_to_location(new_buildings, "tello landing", "bridge", tello, tello.get_height())
            #tello.flip_back()
            
            tello.rotate_clockwise(180)
            
            try:
                tello.go_xyz_speed(0,0,-65,speed)
            except dp.TelloException as tell:
                tell("not lowering")
            try:
                tello.go_xyz_speed(0,0,65,speed)
            except dp.TelloException as tell:
                tell("not rising")
            move_to_location(new_buildings, "bridge", "final doc", tello, tello.get_height())
            tello.land()
            m2 = True
        

        cv2.waitKey(1)

    tello.streamoff()
    cv2.destroyAllWindows()
    vid.join()


if __name__ == '__main__':
    main()
