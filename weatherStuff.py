from imageTools import perlinCloud
import random
import glob
import pygame
from imageTools import *
from probabilityTools import decideBasedOnProbability

class Cloud():
    '''trida mraku'''

    def __init__(self):
        super(Cloud, self).__init__()
        try:
            self.clouds = glob.glob("textures/clouds/*.png")
        except:
            mes = f'Can\'t find clouds in the textures/clouds folder'
            raise FileExistsError(mes)
        initSpritePath = random.choice(self.clouds)    
        self.surf = pygame.image.load(initSpritePath).convert()
        self.surf.set_colorkey((0, 0, 0))
        self.center = self.img.get_rect().center

    def next(self):
        '''vybere nahodny sprite mraku'''
        pth = random.choice(self.clouds)
        self.surf.set_colorkey((0, 0, 0))
        self.center = self.img.get_rect().center

    

    
class StormAnimator():
    '''tato trida ma na startost animaci bourky'''

    def __init__(self,storm_len,fps, sizeX, sizeY, disp_surface, prob_of_storm):
        storm_map_ratio = 1
        self.frames = int(storm_len * fps)
        self.map_size_x = sizeX
        self.map_size_y = sizeY
        avg_side = (sizeX + sizeY) / 2
        avg_side = int(avg_side)
        size = avg_side * storm_map_ratio 
        self.size = int(size)
        start, end = self.pick_edges_of_matrix()
        self.start_pos = start
        self.end_pos = end
        self.disp_surface = disp_surface
        self.frame_num = 1
        self.vector = self.get_vector()
        self.storm_in_prog = False
        self.prob_of_storm = prob_of_storm
        self.init_cloud()

    def get_vector(self):
        """vrati vector zacatecni a konecne pozice drahy bourky"""

        x = self.end_pos[0] - self.start_pos[0]    
        y = self.end_pos[1] - self.start_pos[1]    
        return [x,y]

    def update(self):
        if self.storm_in_prog:
            next_pos = self.next_pos()
            self.disp_surface.blit(self.surf, next_pos)
            if self.frame_num >= self.frames:
                self.storm_in_prog = False
                self.frame_num = 0
        else:
            if decideBasedOnProbability(self.prob_of_storm):
                self.storm_in_prog = True
                start, end = self.pick_edges_of_matrix()
                #print('bourka', start, end)
                self.start_pos = start
                self.end_pos = end
                self.vector = self.get_vector()
                self.init_cloud()



    def init_cloud(self):
        """nacteni obrazku mraku ze souboru"""

        try:
            imgs = glob.glob('textures/clouds/big_ones/*.png')
        except:
            mess = 'cloud imgs not found'
            raise FileError(mess)
        img_path = random.choice(imgs)  
        img_size = (self.size, self.size)  
        self.img = pygame.image.load(img_path).convert()
        self.img = pygame.transform.scale(self.img,
                                          img_size)
        self.surf = pygame.Surface(img_size)
        self.surf.set_colorkey((0, 0, 0))
        self.surf.blit(self.img,
                      (0,0))

    def next_pos(self):
        """zmeni pozici mraku"""

        progress = self.frame_num / self.frames
        prog_vector = [int(self.vector[0]*progress),
                       int(self.vector[1]*progress)]
        pos = [self.start_pos[0]+prog_vector[0],
               self.start_pos[1]+prog_vector[1]]
        self.frame_num += 1
        return pos
            
    def pick_edges_of_matrix(self):
        """nahodne vybere drahu bourky"""

        matrX = self.map_size_x 
        matrY = self.map_size_y 
        min = int((self.size * -1) )
        on_horizontal = random.choice([1,0])
        if on_horizontal:
            y_choices = [min,matrY]
            f_y_ind = random.choice([1,0])
            s_y_ind = not f_y_ind
            y1 = y_choices[f_y_ind]
            y2 = y_choices[s_y_ind]
            x1 = random.randint(0,
            matrX)
            x2 = random.randint(0,
            matrX)
        else:
            x_choices = [min,matrX]
            f_x_ind = random.choice([1,0])
            s_x_ind = not f_x_ind
            x1 = x_choices[f_x_ind]
            x2 = x_choices[s_x_ind]
            y1 = random.randint(0,
            matrY)
            y2 = random.randint(0,
            matrY)    
        op = ([x1,y1],[x2,y2])
        return op

def grid_to_pix(self,pos):
    """prevod jednotek"""
    
    return [pos[0]*self.ts,
        pos[1]*self.ts]         