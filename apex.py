import os
import cv2 as cv 
import numpy as np
import helpers

#Sources:
#https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_template_matching/py_template_matching.html

#TODO: Make separate 'modes' for training and production
def main():
    #Import images
    images = import_images()
    
    #TRAINING MODE
    #pattern = helpers.define_pattern_region(images[0])
    #search  = helpers.define_search_region(images[0])
    #helpers.store_patternROI(pattern, 'test')
    #helpers.store_searchROI(search, 'test')
    
    #PRODUCTION MODE
    #pattern = helpers.load_patternROI('test')
    search  = helpers.load_searchROI('test')
    #coordinates = helpers.find_pattern(images[0], pattern, search)
    #Render result
    #result = cv.circle(images[0], tuple(coordinates), 2, (0,255,0), 10)
    #show_image('result',result)
    
    #CHECK FOR EDGES?
    #TODO: Create a new search region for edge only
    #TODO: Get the top and bottom edges for region
    #TODO: Maybe perform hough transform/canny edge detection on reference image prior to looking for edges as a whole?
    img = images[0][search[-2][1]:search[-1][1], search[-2][0]:search[-1][0]]
    gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY) 
    edges = cv.Canny(gray,1,90)#Figure out how edges work, maybe create a new file for this?
    show_image('edge',edges)
    lines = cv.HoughLines(edges,1,np.pi/180, 200) 
    for r,theta in lines[0]: 
        a = np.cos(theta) 
        b = np.sin(theta) 
        x1 = int(a*r + 1000*(-b)) + search[0][0]
        y1 = int(b*r + 1000*(a))  + search[0][1]
        x2 = int(a*r - 1000*(-b)) + search[0][0]
        y2 = int(b*r - 1000*(a))  + search[0][1]
        result = cv.line(images[0],(x1,y1), (x2,y2), (0,0,255),2) 
    show_image('result',result)
    


    
#def find_edge(image, search, 


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
#Training Functions


#def store_region(coordinates, path):  

'''#Production Functions
def find_edge(image, region, fixture, polarity):
    return coordinates
def load_region(path):
    return coordinates
def load_template(path):
    return template
'''
    
main()