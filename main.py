import os
import cv2 as cv
import numpy as np
from model import *
import tasks
import tkinter as tk 
from functools import partial
from tkinter import filedialog
from PIL import Image, ImageTk

#Things to fix:
#1) Refreshing of markers when opening up 'Modify Image'
#2) Improve mouse sensitivity via acceleration settings
#3) Load configuration params from database instead of ini file
#4) Store path variables in a json file (and load at beggining with images) instead of making them global variables
#5) Load multiple input images into a filmstrip

input_path = os.getcwd() + '\\input\\test.png'
template_path  = os.getcwd() + '\\templates\\'
regions_path = os.getcwd() + '\\regions.ini'
fixture_path = os.getcwd() + '\\fixtures.ini'
size = [480, 300]
button_width = 5
 
def main():
    #Load image and create model
    image= cv.imread(input_path,1)
    model = Model(image, regions_path, fixture_path, template_path)

    #Render GUI
    root = tk.Tk()
    root.rowconfigure([0], minsize=50, weight=1)
    root.columnconfigure([0,1],minsize=50, weight=1)
    controller = create_controller(root, model)
    view, canvas = create_view(root)

    while True:
        #Update image only when model was changed
        if model.change_flag:
            display = Image.fromarray(model.graphics)
            display = display.resize((size[0], size[1]), Image.ANTIALIAS)
            display = ImageTk.PhotoImage(display)
            canvas.create_image((size[0]/2, size[1]/2),image= display)
            canvas.config(width=size[0], height=size[1])
            model.change_flag = False
        root.update_idletasks()
        root.update()

#TKINTER RENDERING FUNCTIONS--------------------------------------------------------------------------------------
#Creates the Tkinter Controller Pane
def create_controller(window, model):
    controller = tk.Frame(master=window)
    controller.rowconfigure([0,1,2,3,4,5,6], minsize=50, weight=1)
    controller.columnconfigure([0,1,2,3,4,5], minsize=50, weight=1)
    controller.grid(row=0, column=1)
    create_headers(controller)
    create_buttons(controller, model)
    return controller

#Creates the Tkinter View Pane
def create_view(window):
    view = tk.Frame(master=window)
    view.rowconfigure([0], minsize=50, weight=1)
    view.columnconfigure([0], minsize=50, weight=1)
    view.grid(row=0, column=0)
    canvas = tk.Canvas(master=view)
    canvas.grid(row=0, column=0)
    return view, canvas

#View Rendering
#Create general GUI Headers  
def create_headers(window):
    text = ['Centerline:', 'Circumference:', 'Y Reference 1:', 'Y Reference 2:', 'X Reference:', 'Print Offset:']
    headers = [tk.Label(master = window, text= element) for element in text]
    for i in range(0,6):
        headers[i].grid(row=i, column=0)

#Create buttons for gui's edit windows and save button
def create_buttons(window, model):
    save_button = tk.Button(master = window, text= 'SAVE', command= partial(save, model), width = button_width)
    save_button.grid(row=6, column=0)
    run_button = tk.Button(master = window, text= 'RUN', command= partial(run, [image, model]), width = button_width)
    run_button.grid(row=6, column=1)
    #Create buttons for each region in model
    buttons = [] 
    text = ['Search1','Search2', 'Pattern', 'Edge']
    for i in range(0,model.rows):
        button_row = []
        for j in range(0,model.cols):
            button = tk.Button(master = window, text= text[j], width = button_width)
            button.grid(row=i, column=j+1)
            button.configure(command= partial(train, [model, button.grid_info()]))
            button_row.append(button)
        buttons.append(button_row)
    #Lookup table for hiding buttons for specific regions based on application
    mask = np.full((model.rows, model.cols), False)
    mask[0][1] = mask[5][1] = True 
    for i in range(0,model.rows):
        for j in range(0,model.cols):
            buttons[i][j].grid_forget() if mask[i][j] else None
    
   
#Event Handlers--------------------------------------------------------------------  
#Event handler that trains new region coordinates via 'Edit Window'
def train(params):
    model, pos = params
    model.modify(pos['row'],pos['column']-1)
    model.draw()
   
#Event handler for save button calls model's save method
def save(model):
    model.save()

#Event handler that runs the model
def run(params):
    image, model = params
    result = tasks.find_reference(image, model)
    result = tasks.check_quality(image, model)
    return results
    #Extract and cache search/edge region from model, and image for pattern
    #Perform find pattern and find edges tools 
        
main()
