import os
import cv2 as cv 
import numpy as np
import helpers
from matplotlib import pyplot as plt

def main():
    img = import_images()[0]
    #train('centerline', img)
    train('circumference', img)
    train('xReference', img)
    train('yreference00', img)
    train('yReference80', img)
    train('printlocation', img)

#HELPER FUNCTIONS-----------------------------------------------------------
def train(name, img):
    #Train pattern within a search region, and store the image and coordinates
    pattern, coordinates = helpers.define_pattern(name, img)
    helpers.store_pattern(name, pattern, coordinates)
    region  = helpers.define_search_region(img)
    helpers.store_search_region(name, region)
    #Set a search region for finding edges for precise positioning
    region  = helpers.define_search_region(img)
    helpers.store_search_region('edge-'+name, region)

#Loads all images from input directory
def import_images():
    path = os.getcwd() + '\\input\\'
    images = []
    for file in os.listdir(path):
        image = cv.imread(path + file, 1)
        images.append(image)
    return images 

main()