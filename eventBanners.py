from logging import root
from math import ceil
from re import S
from turtle import bgcolor
from customErrors import invalidFontSizeError
from customErrors import bannerError
import pygame
from pygameTextTools import *
import json
from customErrors import BadFileFormatError

class textEventBanner(pygame.sprite.Sprite):
    '''Tato trida ma na startost vykreslovat textove bannery
       Je ponekud delsi, jelikoz jsem pridal efekt fade-in/fade-out'''

    fadeInRatio = 0.4
    fadeOutRatio = 0.4
    def __init__(self,dispSurface,lengthInCycles,pos,text,fontSize,fgColor,bgColor=None):
        if fontSize < 1 or fontSize > 120:
            raise invalidFontSizeError()
        if len(text)==0:
            raise bannerError("banner text can't be empty")

        self.lengthInCycles=lengthInCycles
        self.pos = pos
        self.text = text
        self.fontSize = fontSize
        self.currentFontSize = 1
        self.currentCycle = 0
        self.fadeInCycles = lengthInCycles*self.fadeInRatio
        self.fadeOutCycles = lengthInCycles*self.fadeOutRatio
        self.normalSizeCycles = lengthInCycles-self.fadeInCycles-self.fadeOutCycles
        self.incrementByCycle = (self.fontSize)/self.fadeInCycles
        self.decrementByCycle = (self.fontSize)/self.fadeOutCycles
        self.finished = False
        self.dispSurface = dispSurface
        self.fgColor = fgColor
        self.bgColor = bgColor


    def setFadeRatio(self,fadeInRatio,fadeOutRatio):
        '''setter a validator'''
        if (fadeInRatio < 0 or fadeInRatio > 1) or (fadeOutRatio < 0 or fadeOutRatio > 1):
            raise ValueError(" ratio not in correct format -> (0;1)")
        self.fadeInRatio = fadeInRatio
        self.fadeInRatio = fadeOutRatio

    def updateFontSize(self):
        '''vypocet velikosti fontu pro dany frame'''
        if self.currentCycle < self.fadeInCycles:
            fs = ceil(self.incrementByCycle*self.currentCycle)
        elif self.currentCycle >= self.fadeInCycles and self.currentCycle < self.normalSizeCycles+self.fadeInCycles:
            fs = self.currentFontSize
        else:
            fs = self.currentFontSize-(self.decrementByCycle)
        if fs<1:
            fs = 1    
        self.currentFontSize = fs        
        self.currentCycle +=1    

    def nextFrame(self):
        '''prepne objekt do dalsiho frame'''
        if self.currentCycle >= self.lengthInCycles:
            self.finished = True
        font = pygame.font.Font('freesansbold.ttf', int(self.currentFontSize))
        #font = pygame.font.Font('freesansbold.ttf', int(15))
        textContent = self.text
        if self.bgColor==None:
            drawText(self.pos[0],self.pos[1],self.text,self.fgColor,int(self.currentFontSize),self.dispSurface)
        else:    
            drawOutlinedText(self.pos[0],self.pos[1],self.text,self.fgColor,self.bgColor,int(self.currentFontSize),1,self.dispSurface)
        self.updateFontSize()

    def setPos(self,x,y):
        self.pos[0] = x
        self.pos[1] = y

    def  __str__(self):
        '''to string metoda (hlavne uzitecna pro debugging ucely)'''
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )    



class imgEventBanner(pygame.sprite.Sprite):
    '''Tato trida ma na startost vykreslovat obrazkove bannery'''

    def __init__(self,dispSurface,imgPath,lengthInCycles,pos):
        super(imgEventBanner, self).__init__()
        self.loadConfig()
        self.img = pygame.image.load(imgPath).convert()
        self.img.set_colorkey((0, 0, 0))
        self.surf = pygame.Surface((self.tileSize, self.tileSize))
        self.surf.blit(self.img,(0,0))
        self.finished = False
        self.dispSurface = dispSurface
        self.lengthInCycles = lengthInCycles
        self.pos = pos
        self.currentFrame = 0

    def nextFrame(self,newPos=None):
        '''prehazovani na dalsi frame animace'''
        self.currentFrame += 1
        if self.currentFrame >= self.lengthInCycles:
            self.finished = True
            return 
        nextPos = self.pos
        if newPos != None:
            nextPos = newPos
        nextPos = (nextPos[0],nextPos[1])
        self.dispSurface.blit(self.img,nextPos)    

    def loadConfig(self):
        '''nacteni konfigurace'''
        conf = getConfig()
        try:
            self.tileSize = conf['tileSize']
        except:
            raise ValueError('config in bad format, tileSize missing')    
    
    def  __str__(self):
        '''to string metoda (hlavne uzitecna pro debugging ucely)'''
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )  


class deathBanner(imgEventBanner):
    ''' potomek tridy imgEventBanner, ktery vizualizuje smrt zuvaka'''
    def __init__(self,dispSurface,lengthInCycles,pos):
        self.loadImgPath()
        super().__init__(dispSurface,self.imgPath,lengthInCycles,pos)

    def loadImgPath(self):
        '''nacteni cesty k obrazku smrti z conf souboru'''
        conf = getConfig()
        try:
            root_folder = conf['theme']['root']
            d_sprite = conf['theme']['death']
            self.imgPath = root_folder + '/' + d_sprite
        except:
            raise ValueError('config in bad format, death icon image path missing')      
    



def getConfig():
    '''validace konfiguracniho souboru'''
    try:
        with open('conf.json') as json_file:
                conf = json.load(json_file)
    except:
        raise FileNotFoundError("config file not found")
    return conf

if __name__ == '__main__':
    eb = textEventBanner(100,[0,0],'cuus',10)
    for x in range(eb.lengthInCycles):
        eb.nextCycle()
        print(eb.currentCycle)


