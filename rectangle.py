import cv2 as cv 
import numpy as np 
import os

#Example Script Code------
def main():
    path = os.getcwd() + '\\input\\test.png'
    img = cv.imread(path, 1)
    view = BoundingBox(img, 'Slot', (0,255,0))
    view.modify()
      
class Marker:
    start = (0,0)
    end   = (0,0)
    thickness = 10
    color = (255,0,255)
    #Constructor 
    def __init__(self, box_start, box_end, marker_pos):
        self.refresh_resize(box_start, box_end, marker_pos)
        
    #Updates marker location for dragging based on bounding box's offset 
    def refresh_drag(self, offset):
        self.start = tuple([self.start[i] + offset[i] for i in range(0,len(offset))]) 
        self.end   = tuple([self.end[i] + offset[i] for i in range(0,len(offset))]) 
        
    #Updates places marker in initial location based on which corner of bounding box marker is in
    def refresh_resize(self, box_start, box_end, marker_pos):
        x0,y0  = box_start
        x1,y1  = box_end
        top    = ['topleft', 'topmid', 'topright']
        bottom = ['bottomleft', 'bottommid', 'bottomright']
        left   = ['topleft', 'midleft', 'bottomleft']
        right  = ['topright', 'midright', 'bottomright']
        if marker_pos in left:
            center_x = x0 
        elif marker_pos in right:
            center_x = x1 
        else:
            center_x = int((x0+x1)/2)
        if marker_pos in top:
            center_y = y0 
        elif marker_pos in bottom:
            center_y = y1 
        else:
            center_y = int((y0+y1)/2)
        self.start = (center_x-self.thickness, center_y-self.thickness)
        self.end = (center_x+self.thickness, center_y+self.thickness)

class BoundingBox:
    image = None 
    name = ""
    color = (0, 255, 0)
    start  = (0,0)
    end    = (0,0)
    limit_start = (0,0)
    limit_end   = (0,0)
    anchor = (0,0)
    markers = [
        [(0,0),(0,0)],  #Topleft
        [(0,0),(0,0)],  #Topmid
        [(0,0),(0,0)],  #Topright
        [(0,0),(0,0)],  #Midleft
        [(0,0),(0,0)],  #Midright
        [(0,0),(0,0)],  #Bottomleft
        [(0,0),(0,0)],  #Bottommid
        [(0,0),(0,0)],  #Bottomright
    ]
    marker_flags = [False, False, False, False, False, False, False, False,]
    drag_flag = False
    
    #Constructor sets image/color, and marker positions
    def __init__(self, image, name, color):
        self.image = image 
        self.name = name
        self.color = color
        self.limit_end = (image.shape[0], image.shape[1])
        self.end = (100, 100)
        markers = 
        for key in corners:
        
            start = refresh_markers(self.start, self.end, key)
            end   
            self.markers[key] = Marker(self.start, self.end, key)
        for key in self.markers:
            self.marker_flags[key] = False
            
    #Method to launch window to modify bounding box positions
    def modify(self):
        cv.namedWindow(self.name, cv.WINDOW_NORMAL)
        cv.resizeWindow(self.name, 1000,600)
        cv.setMouseCallback(self.name, self.on_mouse, self)
        self.draw_rectangle()
            
    #Event handler for mouse operations
    def on_mouse(self, event, x,y, flags, view):
        #Clip bounding box if reaching limits of image
        x = np.clip([x], self.limit_start[0],self.limit_end[0])[0]
        y = np.clip([y], self.limit_start[1],self.limit_end[1])[0]
        #Perform corresponding action to mouse event
        if event == cv.EVENT_LBUTTONDOWN:
            self.mouse_down(x,y)
        if event == cv.EVENT_LBUTTONUP:
            self.mouse_up(x,y)
        if event == cv.EVENT_MOUSEMOVE:
            self.mouse_move(x,y)
        if event == cv.EVENT_LBUTTONDBLCLK:
            self.mouse_doubleclick(x,y)
            
    #Operations for when mouse button is pressed down
    def mouse_down(self, x,y):
        #If user pressed a specific corner, set that corner's flag to True (allows changing of box size)
        for key in self.markers:
            self.marker_flags[key] = self.inside_box((x,y), self.markers[key].start , self.markers[key].end)
            #self.markers[key].color = (0,0,255)
            if True in self.marker_flags.values():
                self.anchor    = (x,y)
                
        #If user pressed inside the bounding box, set hold flag to True (moves box without changing size)
        if self.inside_box((x,y), self.start, self.end):
            self.anchor    = (x,y)
            self.drag_flag = True 
    
    #Operation for when mouse button is released
    def mouse_up(self, x,y):
        #Reset all flags
        self.drag_flag = False 
        for key in self.markers:
            self.marker_flags[key] = False
           # self.markers[key].color = (255,0,255)
        #Switch start and end points if they were reversed during size adjustment
        for i in range(0,2):
            if (self.end[i] - self.start[i] < 0):
                temp = self.start[i]
                self.start[i] = self.end[i]
                self.end[i] = self.start[i]
        self.draw_rectangle()
   
    #Operation for when mouse is moving
    def mouse_move(self, x,y):
        #If mouse is was pressed inside bounding box while moving, change bounding box location based on anchor offset
        if self.drag_flag:
            offset = [x-self.anchor[0], y-self.anchor[1]]
            self.start = tuple([self.start[i] + offset[i] for i in range(0,len(offset))]) 
            self.end   = tuple([self.end[i] + offset[i] for i in range(0,len(offset))]) 
            for key in self.markers:
                self.markers[key].refresh_drag(offset)
            self.draw_rectangle()
        #If mouse was pressed on a corner while moving, change bounding box sizing
        else:   
            for key in self.markers:
                top    = ['topleft', 'topmid', 'topright']
                bottom = ['bottomleft', 'bottommid', 'bottomright']
                left   = ['topleft', 'midleft', 'bottomleft']
                right  = ['topright', 'midright', 'bottomright']
                offset = [x-self.anchor[0], y-self.anchor[1]]
                self.start = tuple([self.start[i] + offset[i] for i in range(0,len(offset))]) 
                self.end   = tuple([self.end[i] + offset[i] for i in range(0,len(offset))]) 
                if self.marker_flags[key]:
                    self.markers[key] = self.markers[key].refresh_resize(self.start,self.end,key)
                    self.draw_rectangle()

    #End modification if mouse is double clicked inside bounding box
    def mouse_doubleclick(self, x,y):
        cv.destroyWindow(self.name)
            
    #Check if given coordinates are start/end points of bounding box
    def inside_box(self, coordinates, start, end):
        if coordinates[0] in range(start[0], end[0]):
            if coordinates[1] in range(start[1], end[1]):
                return True
        return False

    #Draw rectangle with markers on image
    def draw_rectangle(self):
        image = self.image.copy()
        cv.rectangle(image, self.start, self.end, self.color, 10)
        for key in self.markers:
            cv.rectangle(image, self.markers[key].start, self.markers[key].end, self.markers[key].color, self.markers[key].thickness)
        cv.imshow(self.name, image)
        cv.waitKey()
    
main()