import os
import cv2 as cv
import numpy as np
import configparser
import tkinter as tk 
from functools import partial
from tkinter import filedialog
from PIL import Image, ImageTk
import regions

#Things to fix:
#1) Refreshing of markers when opening up 'Modify Image'
#2) Displaying the image after it is saved

file = os.getcwd() + '\\input\\test.png'
template_path  = os.getcwd() + '\\templates\\'
regions_path = os.getcwd() + '\\regions.ini'
fixture_path = os.getcwd() + '\\fixtures.ini'
size = [480, 300]
button_width = 5

super_image = None
 
def main():
    #Render the base GUI
    root = tk.Tk()
    root.rowconfigure([0], minsize=50, weight=1)
    root.columnconfigure([0,1],minsize=50, weight=1)

    #Upload input image and create models for regions
    image= cv.imread(file,1)
    raw_image = image.copy()
    model = create_model(raw_image, regions_path)

    #Render controller pane
    controller = tk.Frame(master=root)
    controller.rowconfigure([0,1,2,3,4,5,6], minsize=50, weight=1)
    controller.columnconfigure([0,1,2,3,4,5], minsize=50, weight=1)
    controller.grid(row=0, column=1)
    create_headers(controller)
 
    #Render view pane
    view = tk.Frame(master=root)
    view.rowconfigure([0], minsize=50, weight=1)
    view.columnconfigure([0], minsize=50, weight=1)
    view.grid(row=0, column=0)
    
    label = tk.Label(master=view)
    label.grid(row=0, column=0)
    
    canvas = tk.Canvas(master=view)
    canvas.grid(row=0, column=0)
    result = convert_image(model[6][0])
    #label.configure(image=result)
    canvas.create_image((size[0]/2, size[1]/2),image= result)
    canvas.config(width=size[0], height=size[1])
    
    
    buttons=create_inputs(controller, label, image, model)
    #Refresh image whenever there is a change
    while True:
        
        result = convert_image(model[6][1])
        canvas.create_image((size[0]/2, size[1]/2),image= result)
        canvas.config(width=size[0], height=size[1])
        #label.pack()
        #label.configure(image=super_image)
        root.update_idletasks()
        root.update()
        
    

#IMAGE RENDERING FUNCTIONS-----------------------------------------
#Create backend model that stores all region objects
#TODO: Perhaps turn this into an object?
class Model:
    image = None 
    graphics = None 
    change_flag = False 
    regions = []
    
    def __init__(image, path):
        
    

def create_model(image, regions_path):
    model = []
    for i in range(0,6):
        model_row = [
            regions.Region(str(i)+'0', 800,400, (255,0,0)),
            regions.Region(str(i)+'1', 800,400, (255,0,0)),
            regions.Region(str(i)+'2', 800,400, (255,0,0)),
            regions.Region(str(i)+'3', 200,200, (125,0,125)),
            regions.Region(str(i)+'4', 75, 300, (125,125,0)),
        ]
        model.append(model_row)
    model.append([image,image]) 
    model = load(model, regions_path)
    return model

#Create general GUI Headers  
def create_headers(window):
    text = ['Centerline:', 'Circumference:', 'Y Reference 1:', 'Y Reference 2:', 'X Reference:', 'Print Offset:']
    headers = [tk.Label(master = window, text= element) for element in text]
    for i in range(0,6):
        headers[i].grid(row=i, column=0)

#Create buttons for gui's edit windows and save button
def create_inputs(window, canvas, image, model):
    buttons = [] 
    text = ['Search1','Search2','Search3', 'Pattern', 'Edge']
    for i in range(0,6):
        button_row = []
        for j in range(0,5):
            button = tk.Button(master = window, text= text[j], width = button_width)
            button.grid(row=i, column=j+1)
            button.configure(command= partial(modify, [canvas, image, model, button.grid_info()]))
            button_row.append(button)
        buttons.append(button_row)
    save_button = tk.Button(master = window, text= 'SAVE', command= partial(save, [image, model]), width = button_width)
    save_button.grid(row=6, column=0)
    run_button = tk.Button(master = window, text= 'RUN', command= partial(run, [image, model]), width = button_width)
    run_button.grid(row=6, column=1)

#Converts opencv image into a tkinter image
def convert_image(image):
    converted_image = Image.fromarray(image)
    converted_image = converted_image.resize((size[0], size[1]), Image.ANTIALIAS)
    converted_image = ImageTk.PhotoImage(converted_image)
    return converted_image
   
#Draw all regions onto the image 
def draw_regions(model):
    graphics = model[6][0].copy()
    for i in range(0,6):
        for j in range(0,5):
            x0,y0,x1,y1 = model[i][j].save_position()
            available_colors = [(0,0,255),(255,0,255),(255,0,0),(255,255,0),(0,255,0),(0,255,255)]
            impedance = 1 if j == 4 else 3
            impedance = 2 if j == 3 else impedance
            color = tuple([int(shade/impedance) for shade in available_colors[i]])
            cv.rectangle(graphics, (x0,y0), (x1,y1), color, 5)
    model[6][1] = graphics
   
#TRAINING FUNCTIONS------------------------------------------------------------------   
#Event handler that puts 'Edit Window' in view pane for regions
def modify(params):
    label, image, model, pos = params
    i = pos['row']
    j = pos['column']-1
    window_name = '{0}{1}'.format(i,j)
    model[i][j].modify(image, window_name)
    #Convert to tkinter image with graphics
    draw_regions(model)

#Loads coordinates from ini file into model
def load(model, regions_path):
    config = configparser.ConfigParser()
    config.read(regions_path)
    for i in range(0,6):
        for j in range(0,5):
            name = '{0}{1}'.format(i,j)
            x0 = int(config[name]['x0'])
            y0 = int(config[name]['y0'])
            x1 = int(config[name]['x1'])
            y1 = int(config[name]['y1'])
            model[i][j].load_position(x0,y0,x1,y1)
    return model
   
#Event handler that saves all model coordinates to ini file   
def save(params):
    image, model = params
    #Store all regions
    region_config = configparser.ConfigParser()
    fixture_config = configparser.ConfigParser() 
    region_config.read(regions_path)
    fixture_config.read(fixture_path)
    for i in range(0,6):
        for j in range(0,5):
            #Store regions
            x0,y0,x1,y1 = model[i][j].save_position()
            name = '{0}{1}'.format(i,j)
            region_config.set(name, 'x0', str(x0))
            region_config.set(name, 'y0', str(y0))
            region_config.set(name, 'x1', str(x1))
            region_config.set(name, 'y1', str(y1))
            #Store pattern
            cv.imshow('a',image[y0:y1,x0:x1])
            cv.imwrite(template_path+name+'.bmp', image[y0:y1,x0:x1])
            fixture_config.set('{0}'.format(i), 'x', str(int((x0+x1)/2)))
            fixture_config.set('{0}'.format(i), 'y', str(int((y0+y1)/2)))
    region_file = open(os.getcwd()+'\\regions.ini','w')
    fixture_file = open(os.getcwd()+'\\fixtures.ini','w')
    region_config.write(region_file)
    fixture_config.write(fixture_file)
    region_file.close()
    fixture_file.close()

#Event handler that runs the model
def run(params):
    a = 1


main()