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

#Find two edges on specified ROI and direction
#TODO: Replace canny detector with something more robust
#TODO: Make this a lot faster
def find_edges(image, search, horiz_flag, gx, gy):
    #Offset the search region based on fixture points 
    #TODO: WHen taking the template for 'edges', make sure to also get the coordinates of the point too
    region = image[search[-2][1]:search[-1][1], search[-2][0]:search[-1][0]]
    region = cv.cvtColor(region, cv.COLOR_BGR2GRAY)
    edge_image  = cv.Canny(region,gx,gy)
    #Perform a cross section of the image (obtain a graph of the median value of each row)
    if horiz_flag:
        hist = [np.median(col) for col in np.transpose(edge_image)]
    else:
        hist = [np.median(row) for row in edge_image] 
    #Plot to show where edges are
    #plt.plot(hist)
    #plt.show()
    #Differente the pixel value distribution to find y locations of edges
    edges = np.gradient(hist)
    #Find the first peak (indicating a rising edge) by finding max value
    edge_locations = np.array([0,0])
    peak1 = np.where(edges == np.max(edges))[0][0]
    edge_locations[0] = peak1
    #Remove the first peak by padding it, then find max value to get second peak
    edges[peak1] = 0
    peak2 = np.where(edges == np.max(edges))[0][0]
    edge_locations[1] = peak2
    #Offset calculated values by location of search region in image 
    edge_locations = (search[0][1] + edge_locations[0], search[0][1] + edge_locations[1])
    return edge_locations
    

#GUI FUNCTIONS------------------------------------------------------------
#TODO: Show the rectangle and make it draggable/scalable
#TODO: Combine with search region (also make that draggable/scalable)
#Global variable for rectangle ROI
rect = []

#Used to offset search regions based on differences of current and trained fixture points
def offset_fixture(region, ref_fixture, curr_fixture):
    offset = np.subtract(curr_fixture, ref_fixture)
    new_region = np.add(region, offset)
    return new_region

#Use mouse to define pattern region 
def define_pattern(name, image):
    cv.namedWindow(name+'-pattern', cv.WINDOW_NORMAL)
    cv.resizeWindow(name+'-pattern', 480,300)
    cv.setMouseCallback(name+'-pattern', on_mouse)
    while True:
        cv.imshow(name+'-pattern', image)
        k = cv.waitKey(1) & 0xFF
        if k == 27:
            cv.destroyAllWindows()  
            break
        if len(rect) >1:
            pattern = image[rect[-2][1]:rect[-1][1], rect[-2][0]:rect[-1][0]]
            coordinates = [(rect[0][0]+rect[1][0])/2, (rect[0][1]+rect[1][1])/2]
            rect.clear()
            cv.destroyAllWindows()  
            break
    return pattern ,coordinates

#Use mouse to define search region for pattern
def define_search_region(name, image):
    cv.namedWindow(name+'-pattern', cv.WINDOW_NORMAL)
    cv.resizeWindow(name+'-pattern', 480,300)
    cv.setMouseCallback(name+'-pattern', on_mouse)
    while True:
        cv.imshow(name+'-pattern', image)
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
def store_pattern(name, template, coordinates):
    path = os.getcwd() + '\\templates\\'
    cv.imwrite(path+name+'.bmp', template)
    config = configparser.ConfigParser()
    config.read(path+name+'.ini')
    config.add_section("Coordinates")
    config.set("Coordinates",'x1',str(int(coordinates[0])))
    config.set("Coordinates",'y1',str((coordinates[1])))
    file = open(path+name + '.ini','w')
    config.write(file)
    file.close()
    
#Store coordinates in an .ini file 
#TODO: Eventually store these in a database, and load them into SQLLite
def store_search_region(name, coordinates):
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
def load_pattern(name):
    path = os.getcwd() + '\\templates\\'
    image = cv.imread(path + name+'.bmp', 1)
    config = configparser.ConfigParser()
    config.read(path+name+'.ini')
    coordinates = [0,0]
    coordinates[0] = int(config['Coordinates']['x1'])
    coordinates[1] = int(config['Coordinates']['y1'])
    return image, coordinates 
    
#Load coordinates from an .ini file (eventually make this a database read)
def load_search_region(name):
    path = os.getcwd() + '\\regions\\'
    config = configparser.ConfigParser()
    config.read(path+name+'.ini')
    coordinates = [[0,0],[0,0]]
    coordinates[0][0] = int(config['Coordinates']['x1'])
    coordinates[0][1] = int(config['Coordinates']['y1'])
    coordinates[1][0] = int(config['Coordinates']['x2'])
    coordinates[1][1] = int(config['Coordinates']['y2'])
    return coordinates