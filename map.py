from PIL import Image
import random
from pos import Pos,RandomPos
from fertileTile import fertileTile
from customErrors import *
import numpy as np
from matrixTools import *
from imageTools import *
from dangerousTiles import DangerousTile
import glob

class Map:
    ''' Tato trida generuje nahodne mapu s vlastnostmi podle vstupnich parametru'''
    def __init__(self,tilesX,tilesY,tileSize):
        self.tilesX = tilesX
        self.tilesY = tilesY
        self.tileSize = tileSize
        self.fertility = None
        self.fertileFields = None
        self.fertileTiles = list()# list objektu fertileTile
        self.deathTiles = list() # list souradnic ve formatu [x,y]

        
    def setFertility(self,fertility,fertileFields,fertileFieldRadius):
        '''setter urodnosti'''
        if not betweenZeroAndOne(fertileFieldRadius) and fertility < 0:
            raise ValueError("not valid fertility or fertile Field Radius") 
        self.fertility = fertility
        self.fertileFields = fertileFields
        self.fertileFieldRadius = fertileFieldRadius

    def set_theme_stuff(self,fg,bg,fertile_color,fg_percent_range):
        '''setter vzhledu'''
        
        self.bg = tuple(bg)
        self.fg = tuple(fg)
        self.fg_percent_range = fg_percent_range
        self.fertile_color = tuple(fertile_color)

    def generateMapImg(self):
        img = Image.new(mode="RGB", size=(
            self.tilesX*self.tileSize,
            self.tilesY*self.tileSize)
            )
     
        for x in range(self.tilesX):
            for y in range(self.tilesY):
                rnd_background_img = generateRandomBackgroundTile(self.tileSize,
                                                                  self.bg,
                                                                  self.fg,
                                                                  self.fg_percent_range)
                offset = (x*self.tileSize,
                          y*self.tileSize)
                img.paste(rnd_background_img,offset)
        self.mapImg = img

    def save(self):
        iName = 'textures/map.png'   
        self.mapImg.save(iName) 
        self.mapImgPath = iName 


    def addFertility(self):
        '''tato metoda prida na obrazek mapy urodne dlazdice'''
        try:
            self.mapImg
        except NameError:
            raise baseImgNotCreated("generate background image first")
        
        if self.fertility == None or self.fertileFields == None :
            raise logicError("You must set fertlity and number of fertile fields before calling addFertility method")     

        for i in range(self.fertileFields): 
            rp = RandomPos((0,self.tilesX-1),(0,self.tilesY-1))
            centerFertileTile = fertileTile(rp,self.fertility,self.fertileFieldRadius) #vygeneruju stredy urodnych poli
            self.fertileTiles.append(centerFertileTile)
            fRaduis = int(self.fertileFieldRadius*15)
            tilesInRadius = getPositionsOfWrapingPoints(self.tilesX,self.tilesY,centerFertileTile.pos,fRaduis)
            middlePoint = np.array([centerFertileTile.pos.x,centerFertileTile.pos.y])
            for tilePos in tilesInRadius:
                tilePoint = np.array([tilePos.x,tilePos.y])
                diffVector = np.linalg.norm(middlePoint-tilePoint)
                distanceFromMiddle = int(diffVector)
                reverseD = 1/distanceFromMiddle
                rndArrow = random.uniform(0,self.fertileFieldRadius)
                if rndArrow<(reverseD/2): #splnil threshold
                    tileFertility = reverseD*self.fertility
                    greenPixelsRatio = reverseD*self.fertileFieldRadius
                    newTile = fertileTile(tilePos,tileFertility,greenPixelsRatio)
                    self.fertileTiles.append(newTile)
                    if [tilePos.x,tilePos.y] in self.deathTiles:
                        self.deathTiles.remove([tilePos.x,tilePos.y])


        for ft in self.fertileTiles:
            img = generateFertileTile(self.tileSize,ft.greenPixels,self.fertile_color,self.bg,self.fg,self.fg_percent_range)
            offset = (ft.pos.x*self.tileSize,ft.pos.y*self.tileSize)
            self.mapImg.paste(img, offset)


    def addDangerTiles(self, danger_folder):
        '''tato metoda prida na obrazek mapy smrtici dlazdice'''
    
        d_imgs = glob.glob(danger_folder+'/*.png')
        assert len(d_imgs) > 0, 'danger folder empty'   
        dng_tls = list()
        ts = self.tileSize
        for img in d_imgs:
            dt = DangerousTile(img, ts)
            dng_tls.append(dt)
        for i in range(self.deathTilesCount):
            topLeftPoint = RandomPos((0,self.tilesX-1),(0,self.tilesY-1))
            #print(f"x {topLeftPoint.x}, y {topLeftPoint.y}")
            dObj = random.choice(dng_tls)
            for pos in dObj.indexes:
                offX = pos.x+topLeftPoint.x
                offY = pos.y+topLeftPoint.y
                deathTile = Pos(offX,offY)
                self.deathTiles.append([deathTile.x,deathTile.y])
            self.mapImg.paste(dObj.img,(topLeftPoint.x*self.tileSize,topLeftPoint.y*self.tileSize))
    def  __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )  



                
def betweenZeroAndOne(num):
    #validace cisla
    if num >= 0 and num <= 1:
        return True
    else:
        return False    



