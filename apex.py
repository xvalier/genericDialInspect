import os
import cv2 as cv 
import numpy as np
import helpers
from matplotlib import pyplot as plt

#Sources:
#https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_template_matching/py_template_matching.html

def main():
    img = import_images()[0]
    centerline, graphics = find_position(img, img, 'centerline')
    #For circumference, have to do find_position twice (once for each notch), then find distance between
    circumference, graphics = find_position(img, graphics, 'circumference')
    #For xReference, need to find 2x slot patterns and detect 2x edges horizontally
    xReference, graphics = find_position(img, graphics, 'xReference')
    #For yreference00 and yReference80, need to find 3x edges and their midpoints, and also calculate tilt
    yreference00, graphics = find_position(img, graphics, 'yreference00')
    yReference80, graphics = find_position(img, graphics, 'yReference80')
    #For printlocation, need to find edge horizontally
    printlocation, graphics = find_position(img, graphics, 'printlocation')
    #Also need to need measurements section, to calculate intersection points, print offset, etc

#HELPER FUNCTION----------------------------------------------------------------------------------------------------------
def find_position(img, graphics, name)
    pattern, original_pos = helpers.load_pattern(name)
    region  = helpers.load_search_region(name)
    edge_region  = helpers.load_search_region('edge-'+name)
    #Find pattern in search region, use its position to fixture edge region 
    current_pos  = helpers.find_pattern(img, pattern, region)
    edge_search  = helpers.offset_fixture(edge_region, original_pos, current_pos)
    #Find edges of pattern for precise positioning of midpoint
    edge_pos  = helpers.find_edges(img,edge_region, horiz_flag = 0, gx=60, gy=80)   
    midpoint = int((edge_pos[0] + edge_pos[1]) / 2)
    #Graphics
    fixture = cv.circle(graphics, tuple(new_pos), 2, (0,255,0), 10)
    slot_edge1  = cv.line(fixture, (edge_region[0][0], edge_pos[0]), (edge_region[1][0], edge_pos[0]), (255,255,0), 10)
    slot_edge2  = cv.line(edge1, (edge_region[0][0], edge_pos[1]), (edge_region[1][0], edge_pos[1]), (255,255,0), 10)
    graphics  = cv.line(edge2, (0, midpoint), (len(img[0])-1, midpoint), (0,255,0), 10)
    #show_image('result',graphics)
    return midpoint, graphics    
    
    





#Loads all images from input directory
def import_images():
    path = os.getcwd() + '\\input\\'
    images = []
    for file in os.listdir(path):
        image = cv.imread(path + file, 1)
        images.append(image)
    return images 
    
#Show image in window
def show_image(name, image):
    cv.namedWindow(name, cv.WINDOW_NORMAL)
    cv.imshow(name, image)
    cv.resizeWindow(name, 600,400)
    while(1):
        k = cv.waitKey(1) & 0xFF
        if k == 27:
            cv.destroyAllWindows()
    
main()