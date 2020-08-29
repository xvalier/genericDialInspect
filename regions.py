import cv2 as cv 
import numpy as np 

class Region:
    image = None 
    name = ""
    color= (0,255,0)
    thickness = 5 
    default_width = 0
    default_height= 0
    start  = np.array([0,0])
    end    = np.array([0,0])
    anchor = np.array([0,0])
    marker_colors = [(255,0,255) for i in range(0,8)]
    markers = np.array([
        [[0,0],[0,0]],  #Topleft
        [[0,0],[0,0]],  #Topmid
        [[0,0],[0,0]],  #Topright
        [[0,0],[0,0]],  #Midleft
        [[0,0],[0,0]],  #Midright
        [[0,0],[0,0]],  #Bottomleft
        [[0,0],[0,0]],  #Bottommid
        [[0,0],[0,0]]   #Bottomright
    ])
    marker_flags = np.full((8), False, dtype=bool) 
    drag_flag = False
    
    #Constructor sets image/color, and marker positions
    def __init__(self, name, width, height, color):
        self.name = name
        self.color = color
        #Have default dimensions when resetting size during double right click
        self.default_width  = width
        self.default_height  = height
    
    #Refreshes the bounding box with provided coordinates
    def load_position(self, x0, y0, x1, y1):
        self.start = np.array([x0,y0])
        self.end   = np.array([x1,y1])
        for point in range(0,8):
            self.refresh_marker(point)
        
    #Returns current coordinates of bounding box
    def save_position(self):
        x0,y0 = self.start 
        x1,y1 = self.end 
        return x0, y0, x1, y1
    
    #Method to launch window to modify bounding box positions
    def modify(self, image, name):
        cv.namedWindow(name, cv.WINDOW_NORMAL)
        cv.resizeWindow(name, 500,300)
        cv.setMouseCallback(name, self.on_mouse, self)
        self.image = image
        self.draw_rectangle()
        cv.waitKey()
        #Delete image from object memory to save space
        image = self.image
        self.image = None

    #Event handler for mouse operations
    def on_mouse(self, event, x,y, flags, view):
        #Perform corresponding action to mouse event
        if event == cv.EVENT_LBUTTONDOWN:
            self.mouse_down(x,y)
        if event == cv.EVENT_LBUTTONUP:
            self.mouse_up()
        if event == cv.EVENT_MOUSEMOVE:
            self.mouse_move(x,y)
        if event == cv.EVENT_RBUTTONUP:
            w = int((self.end[0]-self.start[0])/2)
            h = int((self.end[1]-self.start[1])/2)
            self.mouse_warp(x,y, w, h)
        if event == cv.EVENT_RBUTTONDBLCLK:
            w = int(self.default_width/2)
            h = int(self.default_height/2)
            self.mouse_warp(x,y, w, h)
        if event == cv.EVENT_LBUTTONDBLCLK:
            self.mouse_doubleclick()
    
    #Event when left mouse button is pressed
    def mouse_down(self, x,y):
        coordinates = np.array([x,y])
        #If user pressed a specific corner, set that corner's flag to True (allows changing of box size)
        for point in np.arange(self.markers.shape[0]):
            self.marker_flags[point] = self.inside_box(coordinates, self.markers[point])
            self.marker_colors[point] = (125,255,255) if self.marker_flags[point] else (255,0,255)
        #If user pressed inside the bounding box, set hold flag to True (moves box without changing size)
        if not True in self.marker_flags:
            self.drag_flag = self.inside_box(coordinates, np.array([self.start, self.end]))
        if True in self.marker_flags or self.drag_flag:
            self.anchor = coordinates

    #Event when left mouse button is released
    def mouse_up(self):
        #Reset all flags, switch start/end points if they were reversed during size adjustment
        self.drag_flag = False 
        self.marker_flags = np.full((8), False, dtype=bool) 
        self.marker_colors = [(255,0,255) for i in range(0,8)]
        x0,y0 = self.start 
        x1,y1 = self.end
        if (x1-x0) < 0:
            self.start[0] = x1
            self.end[0]   = x0
        if (y1-y0) < 0:
            self.start[0] = y1
            self.end[0]   = y0
        self.draw_rectangle()
    
    #Event when right mouse button is pressed. Recreates box to cursor point
    def mouse_warp(self, x,y, w, h):
        #Clip xy cursor point so that box doesn't go outside FOV
        within_image    = np.array([
            True if x-w > 0 else False,
            True if x+w < len(self.image[0]) else False,
            True if y-h > 0 else False,
            True if y+h < len(self.image) else False
        ])
        if within_image.all():
            self.start  = np.array([x-w,y-h])
            self.end    = np.array([x+w,y+h])
        i = [self.refresh_marker(point) for point in np.arange(self.markers.shape[0])]
        self.draw_rectangle()

    #Event when left mouse button is double clicked. Used to end modification
    def mouse_doubleclick(self):
        cv.destroyWindow(self.name)

    #Event when mouse is moved around
    #TODO: This is the function to make more efficient
    #Can probably make this smoother by not basing it on an offset (use actual xy cursor loc to prevent delays)
    def mouse_move(self, x,y):
        if True in self.marker_flags or self.drag_flag:
            offset = np.array([x - self.anchor[0], y - self.anchor[1]])
            #If mouse moved while button pressed inside bounding box, keep entire offset
            if self.drag_flag:
                offset_start = offset_end = offset
            #If mouse moved while button pressed on a marker, adjust bounding box centroid
            #Adjust the centroid by masking out parts of offset based on which marker was used to resize
            for point in np.arange(self.markers.shape[0]):
                if self.marker_flags[point]:
                    point = point + 1 if point > 3 else point
                    offset_start = np.array([offset[0] if not (point%3) else 0, offset[1] if (point < 3) else 0])
                    offset_end   = np.array([offset[0] if not ((point+1)%3) else 0, offset[1] if (point > 5) else 0])
            #Adjust bounding box and marker positions based on offsets, make sure bounding box is within image border
            new_start = np.add(self.start, offset_start)
            new_end   = np.add(self.end, offset_end)
            #TODO: Check if doing inside_box function x2 is faster than this
            within_image    = np.array([
                True if new_start[0] > 0 else False,
                True if new_end[0] < len(self.image[0]) else False,
                True if new_start[1] > 0 else False,
                True if new_end[1] < len(self.image) else False
            ])
            if within_image.all():
                self.start = new_start
                self.end = new_end
            #Refresh markers based on new centroid. Store in a temporary variable to avoid printing to terminal
            i = [self.refresh_marker(point) for point in np.arange(self.markers.shape[0])]
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
        self.markers[point] = np.array([ 
            [center_x-self.thickness, center_y-self.thickness],
            [center_x+self.thickness, center_y+self.thickness]
        ])
  
    #Check if given coordinates are start/end points of provided box
    def inside_box(self, coordinates, box):
        x0, y0 = box[0]
        x1, y1 = box[1]
        result = (x0 < coordinates[0] < x1) & (y0< coordinates[1] < y1)
        return result

    #Draw rectangle with markers on image
    def draw_rectangle(self):
        #Perhaps try drawing on an image of equal size to raw image for graphics, then adding the two?
        image = self.image.copy()
        cv.rectangle(image, tuple(self.start), tuple(self.end), self.color, self.thickness)
        for point in range(0,8):
            cv.rectangle(image, tuple(self.markers[point][0]), tuple(self.markers[point][1]), self.marker_colors[point], self.thickness+5)
        cv.imshow(self.name, image)
        