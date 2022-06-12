import numpy as np
import cv2 as cv2
import sys
import copy
import os
import argparse

save_name = "/Area_of_interest"
areas = [] # a global
def handle_input(PreliminaryImage):
    image = PreliminaryImage
    global areas
    area = [(), ()]
    def click_and_crop(event, x, y, flags, area):
        if event == cv2.EVENT_LBUTTONDOWN:
            print("Cursor: " , str(x)+", ",  str(y))
            area[0] = (x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            area[1] = (x, y)
            # draw a rectangle around the region of interest
            Newimage = cv2.rectangle(image, area[0], area[1], (0, 255, 0), 1)
            x1 = int((area[0][0] + area[1][0])/2.0)
            y1 = int((area[0][1] + area[1][1])/2.0)
            cv2.circle(Newimage, (x1, y1), 1, (255,0,0), -1)
            cv2.putText(Newimage, str(len(areas) + 1), area[0], cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,255))
            cv2.imshow('image', Newimage)
            areas.append(copy.copy(area))
        

    clone = image.copy()
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('image', image.shape[1], image.shape[0])
    cv2.setMouseCallback("image", click_and_crop, area)
 
    # keep looping until the 'c' key is pressed
    while True:
        # display the image and wait for a keypress
        cv2.imshow("image", image)
        key = cv2.waitKey(1) & 0xFF
 
        # if the 'r' key is pressed, reset the cropping region
        if key == ord("r"):
            image = clone.copy()
            areas = []
 
            # if the 'c' key is pressed, break from the loop
        elif key == ord("c"):
            break
    return 0


def show_area(area, image_mat):
    # Show the dimesnsions of the aoi
    tl = (area[0][0], area[0][1])
    bl = (area[0][0], area[1][1])
    tr = (area[1][0], area[0][1])
    br = (area[1][0], area[1][1])
    width = (br[0]-bl[0])
    length = (br[1]-tr[1])
    cv2.line(image_mat, tr, br, (0,255,0),1)
    cv2.line(image_mat, tl, tr, (0,255,0),1)
    cv2.line(image_mat, bl, br, (0,255,0),1)
    cv2.line(image_mat, tl, bl, (0,255,0),1)


def get_area_of_interest(log_path, ref_image):

    image_mat = cv2.imread(ref_image)
    print("get_area_of_interest on image ", ref_image)
    handle_input(image_mat)

    # Remove the old green stuff
    image_mat = cv2.imread(ref_image)

    # save the AOIs into an image file 
    area_num = 1
    for area in areas:
        show_area(area, image_mat)
        x1 = int((area[0][0] + area[1][0])/2.0)
        y1 = int((area[0][1] + area[1][1])/2.0)
        cv2.circle(image_mat, (x1, y1), 1, (255,0,0), -1)
        text = str(area_num)
        cv2.putText(image_mat, text, area[0], cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,255))
        area_num += 1
    cv2.imwrite(log_path + save_name + ".tiff", image_mat)

    print(areas)

    return areas




if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Get Displacements in a sequence of DIC images .')
    parser.add_argument('--ref_image', required=True, metavar='<path>', type=str, help='The path to the images to be parsed')
    parser.add_argument('--log_path', required=True, metavar='<path>', type=str, help='The path to the log directory (where the data Area_of_interes.md is stored) and the results will be saved. ')
    args = parser.parse_args()
    log_path = args.log_path
    ref_image = args.ref_image

    get_area_of_interest(log_path, ref_image)



