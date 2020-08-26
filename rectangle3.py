import cv2 as cv 
import numpy as np 
import os

#Example Script Code------
def main():
    path = os.getcwd() + '\\input\\test.png'
    img = cv.imread(path, 1)
    view = BoundingBox(img, 'Slot', [(0,255,0), (255,255,0)])
    start, end = view.modify()
    print('{0},{1}'.format(start, end))
      
class BoundingBox:
    image = None 
    name = ""
    colors = [(0, 255, 0), (255,255,0)] #Colors for bounding box and markers
    thickness = 20
    start  = [100,100]
    end    = [300, 300]
    anchor = [0,0]
    markers = [
        [[0,0],[0,0]],  #Topleft
        [[0,0],[0,0]],  #Topmid
        [[0,0],[0,0]],  #Topright
        [[0,0],[0,0]],  #Midleft
        [[0,0],[0,0]],  #Midright
        [[0,0],[0,0]],  #Bottomleft
        [[0,0],[0,0]],  #Bottommid
        [[0,0],[0,0]],  #Bottomright
    ]
    marker_flags = [False, False, False, False, False, False, False, False]
    drag_flag = False
    
    #Constructor sets image/color, and marker positions
    def __init__(self, image, name, colors):
        self.image = image 
        self.name = name
        self.colors = colors
        for point in range(0,len(self.markers)):
            self.refresh_marker(point)
            
    #Method to launch window to modify bounding box positions
    def modify(self):
        cv.namedWindow(self.name, cv.WINDOW_NORMAL)
        cv.resizeWindow(self.name, 1000,600)
        cv.setMouseCallback(self.name, self.on_mouse, self)
        self.draw_rectangle()
        cv.waitKey()
        return [self.start, self.end]

    #Event handler for mouse operations
    def on_mouse(self, event, x,y, flags, view):
        #Perform corresponding action to mouse event
        if event == cv.EVENT_LBUTTONDOWN:
            self.mouse_down(x,y)
        if event == cv.EVENT_LBUTTONUP:
            self.mouse_up()
        if event == cv.EVENT_MOUSEMOVE:
            self.mouse_move(x,y)
        if event == cv.EVENT_LBUTTONDBLCLK:
            self.mouse_doubleclick()
    
    #Operations for when left mouse button is pressed down
    def mouse_down(self, x,y):
        coordinates = [x,y]
        #If user pressed a specific corner, set that corner's flag to True (allows changing of box size)
        for point in range(0, len(self.markers)):
            self.marker_flags[point] = self.inside_box(coordinates, self.markers[point])
        #If user pressed inside the bounding box, set hold flag to True (moves box without changing size)
        self.drag_flag  = True if self.inside_box(coordinates, [self.start, self.end]) else False 
        if True in self.marker_flags or self.drag_flag:
            self.anchor = coordinates

    #Operation for when left mouse button is released
    def mouse_up(self):
        #Reset all flags, switch start/end points if they were reversed during size adjustment
        self.drag_flag = False 
        self.marker_flags = [False for flag in self.marker_flags]
        for i in range(0,2):
            if (self.end[i] - self.start[i]) < 0:
                temp = self.start[i]
                self.start = (self.end[i], self.start[i])
                self.end = (temp, self.end[i])

    #End modification window if mouse is double clicked
    def mouse_doubleclick(self):
        cv.destroyWindow(self.name)
        
    #Operation for when mouse is moved
    def mouse_move(self, x,y):
        if self.drag_flag or (True in self.marker_flags):
            offset = [x - self.anchor[0], y - self.anchor[1]]
            #If mouse moved while button pressed inside bounding box, keep entire offset
            if self.drag_flag:
                offset_start = offset
                offset_end   = offset
            #If mouse moved while button pressed on a marker, adjust bounding box centroid
            #Adjust the centroid by masking out parts of offset based on which marker was used to resize
            for point in range(0,len(self.markers)):
                if self.marker_flags[point]:
                    point = point + 1 if point > 3 else point
                    offset_start = (offset[0] if not (point%3) else 0, offset[1] if (point < 3) else 0)
                    offset_end   = (offset[0] if not ((point+1)%3) else 0, offset[1] if (point > 5) else 0)
            #Adjust bounding box and marker positions based on offsets, make sure bounding box is within image border
            new_start = np.add(self.start, offset_start)
            new_end  = np.add(self.end, offset_end)
            within_image    = [False, False, False, False]
            within_image[0] = True if new_start[0] > 0 else False 
            within_image[1] = True if new_end[0] < len(self.image[0]) else False 
            within_image[2] = True if new_start[1] > 0 else False 
            within_image[3] =  True if new_end[1] < len(self.image) else False  
            if not False in within_image:
                self.start = new_start
                self.end = new_end
            for point in range(0,len(self.markers)):
                self.refresh_marker(point)
            self.draw_rectangle()
        
    #Update marker position based on bounding box coordinates  
    def refresh_marker(self, point):
        x0, y0 = self.start
        x1, y1 = self.end
        #If you arrange 'point' as 3x3 matrix, skip the center position by offsetting points after 3 by 1
        point = point + 1 if point > 3 else point
        #Choose marker's centroid based on their position on bounding box
        center_y = y0 if point < 3 else int((y0+y1)/2)
        center_y = y1 if point > 5 else center_y
        center_x = x0 if not (point%3) else int((x0+x1)/2)
        center_x = x1 if not ((point+1)%3) else center_x
        #Create start and end points for marker rectangle
        point = point - 1 if point > 3 else point
        self.markers[point][0] = [center_x-self.thickness, center_y-self.thickness]
        self.markers[point][1] = [center_x+self.thickness, center_y+self.thickness]
  
    #Check if given coordinates are start/end points of bounding box
    def inside_box(self, coordinates, box):
        x0, y0 = box[0]
        x1, y1 = box[1]
        inside_x = (coordinates[0] in range(x0, x1))
        inside_y = (coordinates[1] in range(y0, y1))
        result   = inside_x and inside_y
        return result

    #Draw rectangle with markers on image
    def draw_rectangle(self):
        #Perhaps try drawing on an image of equal size to raw image for graphics, then adding the two?
        image = self.image.copy()
        image = cv.rectangle(image, tuple(self.start), tuple(self.end), self.colors[0], self.thickness-8)
        for marker in self.markers:
            image = cv.rectangle(image, tuple(marker[0]), tuple(marker[1]), self.colors[1], self.thickness)
        cv.imshow(self.name, image)
    
main()