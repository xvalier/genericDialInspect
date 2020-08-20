import cv2 as cv 
import numpy as np 
import os

def main():
    img = cv.imread(os.getcwd() + '\\input\\test.png', 1)
    view = draggable(img, 'Slot', (0,255,0))
    view.modify()
    while True:
        cv.imshow('test', rect.image)
        key = cv2.waitKey(1) & 0xFF
        if k==27:
            break
    cv.destroyAllWindows()
      
class Marker:
    start = (0,0)
    end   = (0,0)
    def refresh(self, x, y):
        
        

class draggable:
    image = None 
    name = ""
    start  = (0,0)
    end    = (0,0)
    anchor = (0,0)
    
    
    anchor = [0,0,0,0]  #Used during drag/hold operations to store previous topleft/bottomright points
    limits = [0,0,0,0]  #Maximum values for bounding box before values get clipped
    markers = {}
    marker_flags = {}
    drag_flag = False
    thickness = 4
    color = (0, 255, 0)

    #Constructor sets image, bounding box color, and marker positions
    def __init__(self, name, image, color):
        self.image = image 
        self.name = name
        self.color = color
        self.limits = [0,0,image.shape[0], image.shape[1]]
        x0,y0,x1,y1 = self.pos
        self.markers = refresh_markers(view)
        for key in self.markers:
            self.marker_flags[key] = False
            
    #Method to launch window to modify bounding box positions
    def modify(self):
        cv.namedWindow(self.name)
        cv.setMouseCallback(self.name, on_mouse, self)
    
    #Event handler for mouse operations
    def on_mouse(event, x,y, flags, view):
        #Clip bounding box if reaching limits of image
        x = np.clip([x], view.limits[0],view.limits[2])[0]
        y = np.clip([y], view.limits[1],view.limits[3])[0]
        #Perform corresponding action to mouse event
        if event = cv.EVENT_LBUTTONDOWN:
            mouse_down(x,y,view)
        if event = cv.EVENT_LBUTTONUP:
            mouse_up(x,y,view)
        if event = cv.EVENT_MOUSEMOVE:
            mouse_move(x,y,view)
        if event = cv.EVENTLBUTTONDDBLCLK:
            mouse_doubleclick(x,y,view)
            
    #Operations for when mouse button is pressed down
    def mouse_down(x,y,view):
        #If user pressed a specific corner, set that corner's flag to True (allows changing of box size)
        for key in view.markers:
            view.marker_flags[key] = view.inside_box((x,y), view.markers[key])
        #If user pressed inside the bounding box, set hold flag to True (moves box without changing size)
        if view.inside_box((x,y), view.pos):
            view.anchor    = [x,y]
            view.drag_flag = True 
    
    #Operation for when mouse button is released
    def mouse_up(x,y,view):
        #Reset all flags
        view.drag_flag = False 
        for key in view.markers:
            view.marker_flags[key] = False
        #Switch start and end points if they were reversed during size adjustment
        if (view.pos[2]-view.pos[0] < 0):
            view.pos[0] = view.pos[2]
            view.pos[2] = view.pos[0]
        if (view.pos[3]-view.pos[3] < 0):
            view.pos[1] = view.pos[3]
            view.pos[3] = view.pos[1]
        draw_rectangle(view)
    
    #End modification if mouse is double clicked inside bounding box
    def mouse_doubleclick(x,y,view):
        if view.inside_box((x,y), view.pos):
            cv.destroyWindow(view.name)
            
    #Operation for when mouse is moving
    def mouse_move(x,y,view):
        #If mouse is already pressed inside bounding box, move bounding box along with mouse movement
        if view.drag:
            offset = [x-view.anchor[0], y-view.anchor[1]]
            for coordinate in view.pos:
                view.pos[coordinate] = view.pos[coordinate] + offset[coordinate%2]
            view.markers = refresh_markers(view)
            draw_rectangle(view)
        for key in view.marker_flags:
            if view

        #FIX ALL OF THIS LATER
        if view.marker_flags['topleft']:
            view.pos = [x,y,view.pos[2], view.pos[3]]
        if view.marker_flags['topmid']:
            view.pos = [view.pos[0], y, view.pos[2], view.pos[3]]
        if view.marker_flags['topright']:
            view.pos = [x, view.pos[1], view.pos[2], y]
        if view.marker_flags['midleft']:
            view.pos = [x, view.pos[1], view.pos[2], view.pos[3]]
        if view.marker_flags['midright']:
            view.pos = [view.pos[0], view.pos[1], x, view.pos[3]]
        if view.marker_flags['bottomleft']:
            view.pos = [view.pos[0], y, pos[2], view.pos[3]]
        if view.marker_flags['bottommid']:
            view.pos = [view.pos[0], y, pos[2], view.pos[3]]
        if view.marker_flags['bottomright']:
            view.pos = [view.pos[0], y, pos[2], view.pos[3]]
        view.markers = refresh_markers(view)
        draw_rectangle(view)

    def inside_box(self, coordinates, positions):
        if coordinates[0] in range(positions[0], positions[3]):
            if coordinates[1] in range(positions[1], positions[4]):
                return True
        return False
    
    def refresh_markers(view):
        x0,y0,x1,y1 = view.pos
        t = view.thickness
        markers = {}
        markers['topleft']  = create_marker_rect(x0, y0, t)
        markers['topmid']   = create_marker_rect((x0+x1)/2, y0, t)
        markers['topright'] = create_marker_rect(x1, y0, t)
        markers['midleft']  = create_marker_rect(x0, (y0+y1)/2, t)
        markers['midright'] = create_marker_rect(x1, (y0+y1)/2, t)
        markers['bottomleft']  = create_marker_rect(x0, y1, t)
        markers['bottommid']   = create_marker_rect((x0+x1)/2, y1, t)
        markers['bottomright'] = create_marker_rect(x1, y1, t)
        return markers
            
    #Helper function to concisely create marker box based on a centroid and thickness
    def create_marker_rect(x,y, thickness):
        return [x-thickness, y-thickness, x+thickness, y+thickness]

    
def draw_rectangle(view):
    temp = view.image.copy()
    x0,y0,x1,y1 = view.pos
    cv.rectangle(view, (x0,y0), (x1,y1), (0,255,0), 2)
    cv.imshow('test', temp)
    cv.waitKey()
    
def draw_markers(view):
    x0,y0,x1,y1 = view.pos
    t = view.thick
    cv.rectangle(view, (x0-t,y0-t), (x0-t+t*2, y0-t+t*2), (0,0,255),3)
    cv.rectangle(view, (x0-t,y1-t), (x0-t+t*2, y1-t+t*2), (0,0,255),3)
    cv.rectangle(view, (x0-t,y0-t), (x1-t+t*2, y0-t+t*2), (0,0,255),3)
    cv.rectangle(view, (x0-t,y1-t), (x1-t+t*2, y1-t+t*2), (0,0,255),3)
    cv.rectangle(view, (x0-t,(y0+y1)/2-t), (x1-t+t*2, (y0+y1)/2-t+t*2), (0,0,255),3)
    cv.rectangle(view, (x0-t,(y0+y1)/2-t), (x0-t+t*2, (y0+y1)/2-t+t*2), (0,0,255),3)
    
main()