import os
import cv2 as cv 
import numpy as np

#TODO:
#Augment find_pattern for model usage
#Augment find_edges for model usage
#Augment fixture_edge_region for model usage 
#Create pipeline tasks

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
    if horiz_flag:
        edge_locations = (search[0][1] + edge_locations[0], search[0][1] + edge_locations[1])
    else:
        edge_locations = (search[0][0] + edge_locations[0], search[0][0] + edge_locations[1])
    return edge_locations

def find_single_edge(image, search, horiz_flag, gx,gy):
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
    peak1 = np.where(edges == np.max(edges))[0][0]
    #Offset calculated values by location of search region in image 
    if horiz_flag:
        peak1 = peak1 + search[0][1]
    else:
        peak1 = peak1 + search[0][0]
    return peak1

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
