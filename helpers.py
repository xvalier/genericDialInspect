import os
import cv2 as cv 
import numpy as np
import configparser


#PATTERN FUNCTIONS-------------------------------------------------------
#Finds pattern within search region of image
#TODO: Test out other methods of template matching to get fastest one
#TODO: Try to make an 'edge/shape' matching algorithm instead
def find_pattern(image, pattern, search):
    #Create a heatmap for best location for pattern 
    match = cv.matchTemplate(
        image[search[-2][1]:search[-1][1], search[-2][0]:search[-1][0]],
        pattern, 
        cv.TM_CCORR_NORMED
    )
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(match)
    #Offset the pattern location based on size of pattern and search region offset
    coordinates = [
        max_loc[0] + pattern.shape[0]/2 + search[0][0], 
        max_loc[1] + pattern.shape[1]/2 + search[0][1]
    ]
    coordinates = [int(point) for point in coordinates]
    return coordinates



#GUI FUNCTIONS------------------------------------------------------------
#TODO: Show the rectangle and make it draggable/scalable
#TODO: Combine with search region (also make that draggable/scalable)
#Global variable for rectangle ROI
rect = []
#Use mouse to define pattern region 
def define_pattern_region(image):
    cv.namedWindow('Pattern', cv.WINDOW_NORMAL)
    cv.resizeWindow('Pattern', 480,300)
    cv.setMouseCallback('Pattern', on_mouse)
    while True:
        cv.imshow('Pattern', image)
        k = cv.waitKey(1) & 0xFF
        if k == 27:
            cv.destroyAllWindows()  
            break
        if len(rect) >1:
            pattern = image[rect[-2][1]:rect[-1][1], rect[-2][0]:rect[-1][0]]
            rect.clear()
            cv.destroyAllWindows()  
            break
    return pattern

#Use mouse to define search region for pattern
def define_search_region(image):
    cv.namedWindow('Search', cv.WINDOW_NORMAL)
    cv.resizeWindow('Search', 480,300)
    cv.setMouseCallback('Search', on_mouse)
    while True:
        cv.imshow('Search', image)
        k = cv.waitKey(1) & 0xFF
        if k == 27:
            cv.destroyAllWindows()  
            break
        if len(rect) >1:
            coordinates = [rect[0], rect[1]]
            rect.clear()
            cv.destroyAllWindows()  
            break
    return coordinates
    
#Mouse Event Handler which records start and end positions for ROI
def on_mouse(event, x, y, flags, params):
    if event == cv.EVENT_LBUTTONDOWN:
        rect.append([x,y])
    if event == cv.EVENT_LBUTTONUP:
        rect.append([x,y])
        
#DATABASE FUNCTIONS-------------------------------------------------------
#Store pattern as an image file
def store_patternROI(template, name):
    path = os.getcwd() + '\\templates\\'
    cv.imwrite(path+name+'.bmp', template)
    
#Store coordinates in an .ini file 
#TODO: Eventually store these in a database, and load them into SQLLite
def store_searchROI(coordinates, name):
    path = os.getcwd() + '\\regions\\'
    config = configparser.ConfigParser()
    config.add_section("Coordinates")
    config.set("Coordinates",'x1',str(coordinates[0][0]))
    config.set("Coordinates",'y1',str(coordinates[0][1]))
    config.set("Coordinates",'x2',str(coordinates[1][0]))
    config.set("Coordinates",'y2',str(coordinates[1][1]))
    file = open(path+name + '.ini','w')
    config.write(file)
    file.close()
    
#Load template from image file
def load_patternROI(name):
    path = os.getcwd() + '\\templates\\'
    image = cv.imread(path + name+'.bmp', 1)
    return image 
    
#Load coordinates from an .ini file (eventually make this a database read)
def load_searchROI(name):
    path = os.getcwd() + '\\regions\\'
    config = configparser.ConfigParser()
    config.read(path+name+'.ini')
    coordinates = [[0,0],[0,0]]
    coordinates[0][0] = int(config['Coordinates']['x1'])
    coordinates[0][1] = int(config['Coordinates']['y1'])
    coordinates[1][0] = int(config['Coordinates']['x2'])
    coordinates[1][1] = int(config['Coordinates']['y2'])
    return coordinates