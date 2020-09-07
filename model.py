import os
import cv2 as cv
import configparser 
import regions

class Model:
    rows = 6
    cols = 4
    type_dims = [[400,800], [200,200], [50,200]]
    available_colors = [(0,0,255),(255,0,255),(255,0,0),(255,255,0),(0,255,0),(0,255,255)]
    image = None 
    graphics = None
    paths  = {}
    change_flag = False 
    #Stored parameters
    regions = []
    fixtures = []
    templates = []
    
    #Constructor which creates model with previously saved region coordinates
    def __init__(self, image, regions_path, fixture_path, template_path):
        self.image = image
        self.graphics = image
        self.paths['regions'] = regions_path
        self.paths['fixtures'] = fixture_path
        self.paths['templates'] = template_path
        for i in range(0,self.rows):
            region_row = []
            for j in range(0,self.cols):
                name = '{0}{1}'.format(i,j)
                #Default Colors and dimensions for search regions are the same
                k = 0 if j < 2 else j-1     
                k = 0 if j < 2 else j-1
                region = regions.Region(name, self.type_dims[k], self.available_colors[i])
                region_row.append(region)
            self.regions.append(region_row)
        self.load()
        self.draw()
                
    #Loads coordinates, templates and their fixtures from ini file into model
    def load(self):
        regions_cfg = configparser.ConfigParser()
        regions_cfg.read(self.paths['regions'])
        fixtures_cfg = configparser.ConfigParser()
        fixtures_cfg.read(self.paths['fixtures'])
        for i in range(0,self.rows):
            for j in range(0,self.cols):
                name = '{0}{1}'.format(i,j)
                x0 = int(regions_cfg[name]['x0'])
                y0 = int(regions_cfg[name]['y0'])
                x1 = int(regions_cfg[name]['x1'])
                y1 = int(regions_cfg[name]['y1'])
                self.regions[i][j].load_position(x0,y0,x1,y1)
            x = int(fixtures_cfg[str(i)]['x'])
            y = int(fixtures_cfg[str(i)]['y'])
            self.fixtures.append([x,y])
            self.templates.append(cv.imread(self.paths['templates']+str(i)+'.bmp',1))

    #Accesses a specific region to modify via 'Edit Window'
    def modify(self, i, j):
        self.regions[i][j].modify(self.image, '{0}{1}'.format(i,j))
    
    #Saves coordinates as well as reference template/fixtures
    def save(self):
        #Store all regions
        regions_cfg = configparser.ConfigParser()
        regions_cfg.read(self.paths['regions'])
        fixtures_cfg = configparser.ConfigParser()
        fixtures_cfg.read(self.paths['fixtures'])
        for i in range(0,self.rows):
            for j in range(0,self.cols):
                x0,y0,x1,y1 = self.regions[i][j].save_position()
                name = '{0}{1}'.format(i,j)
                regions_cfg.set(name, 'x0', str(x0))
                regions_cfg.set(name, 'y0', str(y0))
                regions_cfg.set(name, 'x1', str(x1))
                regions_cfg.set(name, 'y1', str(y1))
                if j == 2:
                    template_name = self.paths['templates']+str(i)+'.bmp'
                    cv.imwrite(template_name, self.image[y0:y1,x0:x1])
                    fixtures_cfg.set(str(i), 'x', str(int((x0+x1)/2)))
                    fixtures_cfg.set(str(i), 'y', str(int((y0+y1)/2)))
        file = open(self.paths['regions'],'w')
        regions_cfg.write(file)
        file.close()
        file = open(self.paths['fixtures'],'w')
        fixtures_cfg.write(file)
        file.close()
        #Refresh the model with saved images, regions, fixtures
        self.load()
    
    #Refreshes the graphics page
    def draw(self):
        graphics = self.image.copy()
        for i in range(0,self.rows):
            for j in range(0,self.cols):
                x0,y0,x1,y1 = self.regions[i][j].save_position()
                impedance = 1 if j == 4 else 3
                impedance = 2 if j == 3 else impedance
                color = tuple([int(shade/impedance) for shade in self.available_colors[i]])
                cv.rectangle(graphics, (x0,y0), (x1,y1), color, 5)
        self.graphics = graphics
        self.change_flag = True