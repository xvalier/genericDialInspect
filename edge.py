import os
import cv2 as cv 
import numpy as np
from functools import partial
import helpers

def main():
    images = import_images()
    render_gui(images)
    
def render_gui(lst):
    search  = helpers.load_searchROI('test')
    img = lst[0][search[-2][1]:search[-1][1], search[-2][0]:search[-1][0]]
    images = []
    images.append(img)
    cv.namedWindow("HoG", cv.WINDOW_NORMAL)
    cv.resizeWindow('HoG', 400,1000)
    concat = np.concatenate((images[0], images[0], images[0]), axis=1)
    cv.imshow('HoG', img)
    cv.namedWindow("Trackbars", cv.WINDOW_NORMAL)
    cv.createTrackbar('CannyX', 'Trackbars', 1, 300, partial(on_change, images))
    cv.createTrackbar('CannyY', 'Trackbars', 1, 255, partial(on_change, images))
    cv.createTrackbar('HoughRho', 'Trackbars', 1, 1000, partial(on_change, images))
    cv.createTrackbar('HoughTheta', 'Trackbars', 1, 360, partial(on_change, images))
    cv.createTrackbar('HoughThreshold', 'Trackbars', 1, 255, partial(on_change, images))
    #cv.createTrackbar('bilateralColor', 'Trackbars', 1, 255,partial(on_change, images))
    #cv.createTrackbar('bilateralSpace', 'Trackbars', 1, 255,partial(on_change, images))
    #cv.createTrackbar('bilateralDiameter', 'Trackbars', 1, 255,partial(on_change, images))
    #cv.createTrackbar('bilateralFlag', 'Trackbars', 0, 1,partial(on_change, images))
    cv.createTrackbar('Image', 'Trackbars', 0, len(images), partial(on_change, images))
    #Use ESC to exit window
    while(1):
        k = cv.waitKey(1) & 0xFF
        if k == 27:
            cv.destroyAllWindows()

#Re-renders images when sliders change 
def on_change(images,val):
    #Get slider positions
    i = cv.getTrackbarPos('Image', 'Trackbars') 
    x = cv.getTrackbarPos('CannyX', 'Trackbars')
    y = cv.getTrackbarPos('CannyY', 'Trackbars')
    rho = cv.getTrackbarPos('HoughRho', 'Trackbars')
    theta = cv.getTrackbarPos('HoughTheta', 'Trackbars') * (np.pi / 180)
    threshold = cv.getTrackbarPos('HoughThreshold', 'Trackbars')
    #d = cv.getTrackbarPos('bilaterialDiameter', 'Trackbars')
    #sigmaColor = cv.getTrackbarPos('bilateralColor', 'Trackbars')
    #sigmaSpace = cv.getTrackbarPos('bilateralSpace', 'Trackbars')
    #bilateral = cv.getTrackbarPos('bilateralFlag', 'Trackbars')
    #Implement canny edge detector and hough transform 
    blur  = images[i]
    #if bilateral:
    #    blur  = cv.bilateralFilter(images[i], d, sigmaColor, sigmaSpace)
    edges = cv.Canny(blur, x,y)
    transform = cv.HoughLines(edges,rho,theta, threshold) 
    for r, t in transform[0]: 
        a = np.cos(t) 
        b = np.sin(t) 
        x1 = int(a*r + 1000*(-b))
        y1 = int(b*r + 1000*(a))
        x2 = int(a*r - 1000*(-b))
        y2 = int(b*r - 1000*(a))
        gray = cv.cvtColor(edges,cv.COLOR_GRAY2BGR)
        result = cv.line(gray,(x1,y1), (x2,y2), (0,0,255),2) 
    #Refresh image with new results 
    #concat = np.concatenate((edges,transform,result), axis=1)
    cv.imshow('HoG',result)
    
def import_images():
    path = os.getcwd() + '\\input\\'
    images = []
    for file in os.listdir(path):
        image = cv.imread(path + file, 0)
        images.append(image)
    return images 
    
main()