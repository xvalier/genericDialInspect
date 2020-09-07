import cv2 as cv 
import numpy as np

#TODO:
#Augment find_pattern for model usage
#Augment find_edges for model usage
#Augment fixture_edge_region for model usage 
#Create pipeline tasks


#TASKS AND PIPELINE------------------------------------------------------------------
def find_refences(image, model):
    centerline, graphics = find_centerline(image, image.copy(), model)
    #Find centerline 
    #Find Circumference
    #Find Y Ref 1 
    #Find Y Ref 2
    #Find X Ref 
    #Find Print Offset
   
#Task to look for the 'fin' location on right side of dial   
def find_centerline(image, graphics, model):
    search_pts, offset, template, fixture, edge_pts = extract_model(model, 0, [0])
    coordinates = find_pattern(image, search_pts[0], template, offset[0])
    edge_pts    = offset_edge_region(edge_pts, fixture, coordinates)
    edges       = find_edges(image, edge_pts, 60, 80, 0, 1)
    centerline  = (edges[0] + edges[1])/2
    graphics    = create_graphics(graphics, edge_pts, edges, centerline)
    return centerline, graphics
    
#Task to look for 'slot' location twice in order to get degrees for rotation
def find_circumference(image, graphics, model):
    search_pts, offset, template, fixture, edge_pts = extract_model(model, 1, [0,1])
    midpoints = []
    for i in range(0,2):
        coordinates = find_pattern(image, search_pts[i], template, offset[i])
        edge_pts    = offset_edge_region(edge_pts, fixture, coordinates)
        edges       = find_edges(image, edge_pts, 60, 80, 0, 1)
        midpoints.append((edges[0] + edges[1])/2)
        #graphics    = create_graphics(graphics, edge_pts, edges, midpoints[i])
    circumference = np.abs(midpoint[0]-midpoint[1])
    return circumference, graphics 

#Task to look for 'dash' location near the '0 degree' area
def find_yref_1(image, graphics, model):
    search_pts, offset, template, fixture, edge_pts = extract_model(model, 2, [0,1])
    midpoints = []
    for i in range(0,2):
        coordinates = find_pattern(image, search_pts[i], template, offset[i])
        edge_pts    = offset_edge_region(edge_pts, fixture, coordinates)
        edges       = find_edges(image, edge_pts, 60, 80, 0, 1)
        midpoints.append((edges[0] + edges[1])/2)
        #graphics    = create_graphics(graphics, edge_pts, edges, midpoints)
    horizontal_line = midpoint[0]-midpoint[1]/2
    return horizontal_line, graphics 
    
#Task to look for 'dash' location near the '0 degree' area
def find_yref_2(image, graphics, model):
    search_pts, offset, template, fixture, edge_pts = extract_model(model, 3, [0,1])
    midpoints = []
    for i in range(0,2):
        coordinates = find_pattern(image, search_pts[i], template, offset[i])
        edge_pts    = offset_edge_region(edge_pts, fixture, coordinates)
        edges       = find_edges(image, edge_pts, 60, 80, 0, 1)
        midpoints.append((edges[0] + edges[1])/2)
        #graphics    = create_graphics(graphics, edge_pts, edges, midpoints)
    horizontal_line = midpoint[0]-midpoint[1]/2
    return horizontal_line, graphics 
    

#PRIMITIVE FUNCTIONS----------------------------------------------------------------
#Extract relevant portions of model 
def extract_model(model, i, search_indices):
    search_pts = [model.regions[i][j].save_position() for j in search_indices]
    offset = [search[j][0:2] for j in search_pts]
    template = model.templates[i]
    fixture  = model.fixtures[i]
    edge_roi = model.regions[i][4].save_position()
    return search_pts, offset, template, fixture, edge_roi
  
#Cut out the region from full image  
def extract_region(image, roi):
    x0, y0, x1, y1 = roi
    return image[y0:y1, x0:x1]

#Finds template within search region
def find_pattern(image, search_pts, template, offset):
    roi = extract_region(image, search_pts)
    #Create a heatmap for best location for template
    match = cv.matchTemplate(roi, template, cv.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(match)
    #Offset template location with offsets for template and search regions
    offset = np.add(np.divide(template.shape,2),offset)
    coordinates = [int(point) for point in np.add(max_loc, offset)]
    return coordinates
  
#Offset the edge region based on difference between template's reference and current points
def offset_edge_region(roi, fixture, coordinates):
    offset = np.subtract(coordinates, fixture)
    new_roi = np.add(roi, offset)
    return new_roi

#gx=60, gy=80. gx,gy are hough kernels which are dependent on the search region
#Find two edges within edge region based on given direction (ignore second one if not needed)
def find_edges(image, edge_pts, gx, gy, horiz_flag, double_flag):
    roi = cv.cvtColor(extract_region(image, edge_pts), cv.COLOR_BGR2GRAY)
    #Perform canny edge detection
    canny = cv.Canny(roi, gx, gy)
    #Rotate canny image if looking for edges in horizontal direction 
    histogram = np.transpose(canny) if horiz_flag else canny 
    peaks = np.gradient(histogram)
    #Get edge by looking for maximum in histogram 
    edges = np.array([0,0]) 
    first_edge = np.where(peaks == np.max(peaks))[0][0]
    edges[0] = first_edge
    #Get a second edge by removing first peak, then looking for maximum
    if double_flag:
        edges[first_edge] = 0 
        second_edge = np.where(peaks == np.max(peak))[0][0]
        edges[1] = second_edge 
    #Offset edge locations based on edge region location
    offset = edge_pts[0][1] if horiz_flag else edge_pts[0][0]
    edges = np.add(edges, offset) 
    return edges
  
#GRAPHICS FUNCTIONS----------------------------------------------------------------  
color = {
    'green':(0,255,0),
    'red' : (0,0,255),
    'blue': (255,0,0),
    'cyan': (255,255,0),
    'pink': (255,0,255),
    'yellow':(0,255,255)
}

#Draws detected edges and lines
def create_graphics(graphics, edge_pts, edges, mid):
    edge_top  = [(edge_pts[0][0], edges[0]), (edge_pts[1][0], edges[0])]
    edge_bot  = [(edge_pts[0][0], edges[1]), (edge_pts[1][0], edges[1])]
    graphics = cv.line(graphics, edge_top[0], edge_top[1], color['cyan'],10)
    graphics = cv.line(graphics, edge_bot[0], edge_bot[1], color['cyan'],10)
    return graphics 
    
    
def check_quality(image, model):