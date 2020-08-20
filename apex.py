import os
import cv2 as cv 
import numpy as np
import helpers
from matplotlib import pyplot as plt

#Sources:
#https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_template_matching/py_template_matching.html

def main():
    img = import_images()[0]
    origin, graphics = find_centerline(img, img)
    #circumference = find_circumference(img, graphics)
    #y_pos1, tilt, graphics = find_yref1(img, graphics)
    #y_pos2, graphics = find_yref2(img, graphics)
    #x_pos, graphics = find_xref(img, graphics)
    #print_offset, graphics = find_printloc(img, graphics, x_pos)
    #print(
    #    "Origin:    " + str(origin) + "\n"
    #    "Circumference:    " + str(circumference) + "\n"
    #    "Y1:    " + str(y_pos1) + "\n"
    #    "Y2:    " + str(y_pos2) + "\n"
    #    "X:    " + str(x_pos) + "\n"
    #    "Print Offset:    " + str(print_offset) + "\n"
    #)
    show_image('test', graphics)
    
#HELPER FUNCTION----------------------------------------------------------------------------------------------------------
def find_centerline(img, graphics):
    fixture, edges, midpoint = find_position(img, graphics, 'centerline',1)
    #Graphics
    graphics = cv.line(graphics, (0, midpoint), (len(img)-1,midpoint), (255,0,0),10)
    graphics = cv.circle(graphics, fixture, 5, (0,0,255), 10)    
    graphics = cv.line(graphics, edges[0][0], edges[0][1], (255,255,0),10)                    
    graphics = cv.line(graphics, edges[1][0], edges[1][1], (255,255,0),10)
    return midpoint, graphics
     
def find_circumference(img, graphics):
    fixture1, edges1, midpoint1 = find_position(img, graphics, 'circumference1',0)
    fixture2, edges2, midpoint2 = find_position(img, graphics, 'circumference2',0)
    circumference = np.abs(midpoint1 - midpoint2)
    return circumference
   
def find_yref1(img, graphics):
    fixture1, edges1, midpoint1 = find_position(img, graphics, 'yref00',1)
    fixture2, edges2, midpoint2 = find_position(img, graphics, 'yref60',1)
    y_pos = (midpoint1 + midpoint2)/2 
    tilt  = np.arctan2(edges1[0], edges2[0])
    #Graphics
    graphics = cv.line(graphics, (0, midpoint1), (len(img)-1,midpoint2), (255,0,0),10)
    graphics = cv.circle(graphics, fixture1, 5, (0,0,255), 10) 
    graphics = cv.circle(graphics, fixture2, 5, (0,0,255), 10) 
    graphics = cv.line(graphics, edges1[0][0], edges1[0][1], (255,255,0),10)                    
    graphics = cv.line(graphics, edges1[1][0], edges1[1][1], (255,255,0),10)
    graphics = cv.line(graphics, edges2[0][0], edges2[0][1], (255,255,0),10)                    
    graphics = cv.line(graphics, edges2[1][0], edges2[1][1], (255,255,0),10)
    return y_pos, tilt, graphics

def find_yref2(img, graphics):
    fixture1, edges1, midpoint1 = find_position(img, graphics, 'yref18',1)
    fixture2, edges2, midpoint2 = find_position(img, graphics, 'yref78',1)
    y_pos = (midpoint1 + midpoint2)/2 
    #Graphics
    graphics = cv.line(graphics, (0, midpoint1), (len(img)-1,midpoint2), (255,0,0),10)
    graphics = cv.circle(graphics, fixture1, 5, (0,0,255), 10) 
    graphics = cv.circle(graphics, fixture2, 5, (0,0,255), 10) 
    graphics = cv.line(graphics, edges1[0][0], edges1[0][1], (255,255,0),10)                    
    graphics = cv.line(graphics, edges1[1][0], edges1[1][1], (255,255,0),10)
    graphics = cv.line(graphics, edges2[0][0], edges2[0][1], (255,255,0),10)                    
    graphics = cv.line(graphics, edges2[1][0], edges2[1][1], (255,255,0),10)
    return y_pos, graphics    
   
def find_xref(img, graphics):
    fixture1, edge1, midpoint1 = find_position_xref(img, graphics, 'xref1')
    fixture2, edge2, midpoint2 = find_position_xref(img, graphics, 'xref2')
    x_pos = (midpoint1 + midpoint2)/2
    #Graphics
    graphics = cv.line(graphics, (0, midpoint1), (len(img)-1,midpoint2), (255,0,0),10)
    graphics = cv.circle(graphics, fixture1, 5, (0,0,255), 10) 
    graphics = cv.circle(graphics, fixture2, 5, (0,0,255), 10) 
    graphics = cv.line(graphics, edge1[0], edge1[1], (255,255,0),10)  
    graphics = cv.line(graphics, edge2[0], edge2[1], (255,255,0),10)  
    return x_pos, graphics
    
   
def find_printloc(img, graphics, xref_midpoint):
    fixture, edges, midpoint = find_position(img, graphics, 'printloc',0)
    printloc = np.abs(midpoint - xref_midpoint)
    graphics = cv.line(graphics, (0, midpoint), (len(img)-1,midpoint), (255,0,0),10)
    graphics = cv.circle(graphics, fixture, 5, (0,0,255), 10)
    graphics = cv.line(graphics, edges[0][0], edges[0][1], (255,255,0),10)    
    graphics = cv.line(graphics, edges[1][0], edges[1][1], (255,255,0),10) 
    return printloc, graphics
    
#Generic task fixture double edge search via pattern and get midpoint
def find_position(img, graphics, name, horiz_flag):
    #Load pattern and search regions
    pattern, original_pos = helpers.load_pattern(name)
    region  = helpers.load_search_region(name)
    edge_region  = helpers.load_search_region('edge-'+name)
    
    #Find pattern in search region and use its position as fixture for edge search region
    current_pos  = helpers.find_pattern(img, pattern, region)
    print(original_pos)
    print(current_pos)
    print(edge_region)
    
    #edge_region  = helpers.offset_fixture(edge_region, original_pos, current_pos)
    #search =region
    #roi = img[search[-2][1]:search[-1][1], search[-2][0]:search[-1][0]]
    #show_image('a',roi)
    #Use edge detection near the pattern to get precise horizontal midpoint of pattern
    edges  = helpers.find_edges(img,edge_region, horiz_flag, gx=60, gy=80)   
    midpoint = int((edges[0] + edges[1]) / 2)
    if horiz_flag:
        edges = [
            [(edge_region[0][0], edges[0]), (edge_region[1][0], edges[0])],
            [(edge_region[0][0], edges[1]), (edge_region[1][0], edges[1])]
        ]
    else:
        edges = [
            [(edges[0],edge_region[0][0]), (edges[0],edge_region[1][0])],
            [(edges[1],edge_region[0][0]), (edges[1],edge_region[1][0])],
        ]
    return tuple(current_pos), edges, midpoint
    
#Generic task fixture double edge search via pattern and get midpoint
def find_position_xref(img, graphics, name):
    #Load pattern and search regions
    pattern, original_pos = helpers.load_pattern(name)
    region  = helpers.load_search_region(name)
    edge_region  = helpers.load_search_region('edge-'+name)
    #Find pattern in search region and use its position as fixture for edge search region
    current_pos  = helpers.find_pattern(img, pattern, region)
    edge_region = helpers.offset_fixture(edge_region, original_pos, current_pos)
    #Use edge detection near the pattern to get precise horizontal midpoint of pattern
    midpoint  = helpers.find_single_edge(img,edge_region, 1, gx=60, gy=80)    
    edge = [(edge_region[0][0], midpoint), (edge_region[1][0], midpoint)]
    return tuple(current_pos), edge, midpoint

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