import os
import cv2 as cv
import numpy as np
import configparser
import tkinter as tk 
from functools import partial
from tkinter import filedialog
from PIL import Image, ImageTk
import regions

file = os.getcwd() + '\\input\\test.png'
size = [480, 300]
button_width = 5
 
def main():
    #Render the base GUI
    root = tk.Tk()
    root.rowconfigure([0, 1], minsize=50, weight=1)
    root.columnconfigure([0],minsize=50, weight=1)

    #Upload input image and create models for regions
    image= cv.imread(file,1)
    image= cv.resize(image, (size[0], size[1]))

    #Render view pane
    view = tk.Frame(master=root)
    view.rowconfigure([0], minsize=50, weight=1)
    view.columnconfigure([0], minsize=50, weight=1)
    view.grid(row=0, column=0)
    
    #Render controller pane
    ctrl = tk.Frame(master=root)
    ctrl.rowconfigure([0,1,2], minsize=50, weight=1)
    ctrl.columnconfigure([0,1], minsize=50, weight=1)
    ctrl.grid(row=1, column=0)
    buttons = create_buttons(ctrl)
    
    #Image conversion
    canvas = tk.Canvas(master=view)
    result = convert_image(image)
    canvas.create_image((size[0]/2, size[1]/2),image= result)
    canvas.config(width=size[0], height=size[1])
    canvas.grid(row=0, column=0)
 
    #Refresh image whenever there is a change
    while True:
        result = convert_image(image)
        canvas.create_image((size[0]/2, size[1]/2),image= result)
        canvas.config(width=size[0], height=size[1])
        root.update_idletasks()
        root.update()

def create_buttons(window):
    buttons = [] 
    text = ['1', '2']
    for i in range(0,3):
        button_row = []
        for j in range(0,2):
            button = tk.Button(master = window, text= text[j], width = button_width)
            button.grid(row=i, column=j)
            button_row.append(button)
        buttons.append(button_row)
    return buttons 

#Converts opencv image into a tkinter image
def convert_image(image):
    converted_image = Image.fromarray(image)
    converted_image = converted_image.resize((size[0], size[1]), Image.ANTIALIAS)
    converted_image = ImageTk.PhotoImage(converted_image)
    return converted_image


main()