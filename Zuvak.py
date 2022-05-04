from customErrors import *
import json
from PIL import Image
from pos import *
import pygame
from probabilityTools import decideBasedOnProbability
import numpy as np

class Zuvak(pygame.sprite.Sprite):

    def __init__(self, iq, size, agresivity, first_gen=False):
        if first_gen:
            assert type(iq) in [float, int], 'vstupni argument iq musi byt typu float nebo int'
            assert type(size) in [float, int], 'vstupni argument size musi byt typu float'
            assert type(agresivity) in [float, int], 'vstupni argument agresivity musi byt typu float'
        self.loadConfig()
        self.surf = pygame.Surface((0, 0))
        super(Zuvak, self).__init__()
        test_p_range(iq)
        test_p_range(size)
        test_p_range(agresivity)
        self.iq = iq
        self.size = size
        self.agresivity = agresivity
        self.eyeColor = random.choice([(0,255,1),
                                       (110, 38, 14),
                                       (128,0,128),
                                       (255,255,0)])
        self.loadSprite()
        self.rect = self.surf.get_rect()
        #self.pos = None # bod ve formatu [x,y]
        self.alive = True
        self.fatStorage = self.zuvakConf["startingFatStorageForDays"]*self.size 
        self.adultAge = self.zuvakConf["adultAge"]
        self.activeBanner = None
        self.age = 0
        self.growPerCycle = self.size/self.adultAge
        self.ts = self.conf["tileSize"]
        self.updateSize()
        self.in_fight = False # zuvak utoci
        self.being_attacked = False # zuvak se brani
        self.fought_rounds = 0
        self.oponent_pos = None
        self.oponent_obj = None
    def setPos(self,pos):
        self.pos = pos

    def setIq(self,iq):
        test_p_range(iq)
        self.iq = iq

    def loadSprite(self):
        root_f = self.conf["theme"]['root']
        imgPath = root_f + '/zuvak.png'
        self.img = Image.open(imgPath)
        self.applyColorToSprite()
        self.img = PILtoPygameImg(self.img)
        self.surf.set_colorkey((0, 0, 0))
        self.surf.blit(self.img,(0,0))
        self.center = self.img.get_rect().center

    def start_fight(self, my_pos, opoenent_pos, oponent_obj):
        self.in_fight = True
        self.fought_rounds = 0
        self.oponent_pos = opoenent_pos
        self.oponent_obj = oponent_obj
        self.oponent_obj.setPos(opoenent_pos)
        pos_a = np.array([my_pos[0]*self.ts, my_pos[1]*self.ts ])
        pos_b = np.array([opoenent_pos[0]*self.ts, opoenent_pos[1]*self.ts])
        distance_from_points = np.linalg.norm(pos_b-pos_a)
        self.distance_from_oponent = distance_from_points
        self.vector_to_oponent = [opoenent_pos[0]*self.ts - my_pos[0]*self.ts,
                                 opoenent_pos[1]*self.ts - my_pos[1]*self.ts]
        self.laser_length = distance_from_points / self.frames_per_attack_round
        self.setPos(my_pos)

    def next_fight_round(self):
        self.fought_rounds += 1

    def update_difference_vector(self):
        self.vector_to_oponent = [self.oponent_obj.pos[0]*self.ts - self.pos[0]*self.ts,
                                 self.oponent_obj.pos[1]*self.ts - self.pos[1]*self.ts]
            
    def updateSize(self):
        newSize = self.age*self.growPerCycle
        if self.ts*newSize<=3:
            return
        newSize = (int(self.ts*newSize),
                   int(self.ts*newSize))
        newImg = pygame.transform.scale(self.img,
                                        newSize)
        self.center = newImg.get_rect().center
        newSurf = pygame.surface.Surface((newSize))
        newSurf.set_colorkey((0, 0, 0))
        newSurf.blit(newImg,
                    (0,0))
        self.surf = newSurf
        
    def applyColorToSprite(self):
        blue = (63, 0, 255)
        red = (220,20,60)
        eyePoints = self.zuvakConf["eyePoints"]
        for point in eyePoints:
            pos = (point[0],point[1])
            self.img.putpixel(pos,self.eyeColor)

        coloredStripHeight = self.colorEnd.y - self.colorStart.y
        coloredStripWidth = self.colorEnd.x - self.colorStart.x
        iqPixels = self.iq/(self.iq+self.agresivity+1e-10)
        iqPixels = round(coloredStripHeight*iqPixels)

        for i in range(coloredStripHeight):
            for ii in range(coloredStripWidth):
                x = self.colorStart.x+ii
                y = self.colorStart.y+i
                if (i+1)<=iqPixels:
                    color = blue
                else:
                    color = red      
                self.img.putpixel((x,y),color)

    def setSize(self,size):
        test_p_range(size)
        self.size = size   

    def setAgresivity(self,agresivity):
        test_p_range(agresivity)
        self.agresivity = agresivity

    def loadConfig(self):
        try:
            with open('conf.json') as json_file:
                self.conf = json.load(json_file)
        except:
            raise FileNotFoundError("config file not found")
        try:
            self.zuvakConf = self.conf["zuvak"]
            sP = self.zuvakConf["colorStartPoint"]
            eP  = self.zuvakConf["colorEndPoint"]
            self.colorStart = Pos(sP[0],sP[1])
            self.colorEnd = Pos(eP[0],eP[1])
            self.mutationRange = test_p_range(self.conf["mutationRange"])
            self.frames_per_attack_round = self.conf["attack_round_seconds"] * self.conf['fps']
        except:
            raise BadFileFormatError("Config file in bad format, see documentation")  

    def haveSex(self,partnerZuvak,sexEnergyReq):
        """rozmnozovani zuvaku"""
        if sexEnergyReq>(self.fatStorage/self.size): #zuvak ma dostatek tukovych zasob pro rozmnozeni
            return False
        childIq  = combineZuvaksAttrs(self.iq,
                                      partnerZuvak.iq,
                                      self.mutationRange)
        childSize = combineZuvaksAttrs(self.size,
                                       partnerZuvak.size,
                                       self.mutationRange)
        if childSize < 0.1:
            childSize = 0.1
        childAgresivity  = combineZuvaksAttrs(self.agresivity,
                                              partnerZuvak.agresivity,
                                              self.mutationRange)
        parentsEyeColor = [self.eyeColor, partnerZuvak.eyeColor] 
        newZuvak = Zuvak(childIq, childSize, childAgresivity)
        newZuvak.eyeColor = random.choice(parentsEyeColor)
        return newZuvak

    def end_fight(self):
        """tato metoda se pouziva ukonceni boje a take pro zijsteni vyherce boje zuvaku."""
        self.in_fight = False
        op = None
        myAttack = random.uniform(0,
                   self.size)
        enemyAttack = random.uniform(0,
                      self.oponent_obj.size)
        i_won = myAttack > enemyAttack  
        if myAttack == enemyAttack: # remiza
            i_won = random.choice([True,False]) 

        if i_won: #vyhral
            enemy_fat = self.oponent_obj.fatStorage
            self.fatStorage = self.fatStorage + enemy_fat
            winner = (self)
            loser = (self.oponent_obj)
            op = (winner,loser)
            return op
        else:#enemak vyhral
            my_fat = self.fatStorage
            self.oponent_obj.fatStorage += my_fat
            winner = (self.oponent_obj)
            loser = (self)
            op = (winner,loser)
            return op
 


    def nextCycle(self):
        """Tato metoda mimo jine ubira energii zuvakovi z tukoveho uloziste"""
        self.fatStorage = self.fatStorage - self.size
        if self.fatStorage < 0:
            self.alive = False
            return    
        self.age += 1
        if self.age < self.adultAge:
            self.updateSize()     

    def eat(self,food):
        self.fatStorage += food.energy

    def rotate(self,deg):
        self.img = self.img.rotate(deg)    

    def wants_to_fight(self,koef):
        if self.age < self.adultAge:
            return False
        p = self.agresivity * koef
        r = decideBasedOnProbability(p)
        return r

    def  __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )

def combineZuvaksAttrs(at1,at2,mr):
    atAvg = (at1+at2)/2
    mutatedAtr = atAvg + random.uniform(-mr/2,mr/2)
    return normalizeP(mutatedAtr)         

def test_p_range(n):
    if n >= 0 and n <= 1:
        return n
    else:
        eMess  = "suplied value x is not 0>=X>=1"
        raise notAProbabiltyError(eMess)
        
def combineColor(colorRGBA1, colorRGBA2):
    alpha = 255 - ((255 - colorRGBA1[3]) * (255 - colorRGBA2[3]) / 255)
    red   = (colorRGBA1[0] * (255 - colorRGBA2[3]) + colorRGBA2[0] * colorRGBA2[3]) / 255
    green = (colorRGBA1[1] * (255 - colorRGBA2[3]) + colorRGBA2[1] * colorRGBA2[3]) / 255
    blue  = (colorRGBA1[2] * (255 - colorRGBA2[3]) + colorRGBA2[2] * colorRGBA2[3]) / 255
    return (int(red), int(green), int(blue), int(alpha))        
        
def normalizeP(p):
    if p < 0:
        p = 0
    if p > 1:
        p = 1
    return p        

def PILtoPygameImg(img):
    # Calculate mode, size and data
    mode = img.mode
    size = img.size
    data = img.tobytes()
    # Convert PIL image to pygame surface image
    py_image = pygame.image.fromstring(data,
                                       size,
                                       mode)
    return py_image  

#z1 = Zuvak(0.8,1,0.5)
#z2 = Zuvak(0.1,0.1,0.9)
#chZ = z1.haveSex(z2)