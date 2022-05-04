from map import Map
from customErrors import *
from Zuvak import Zuvak
import random
from pos import *
import math
import pygame
from food import Food
from probabilityTools import * 
import glob
from eventBanners import *
from pygameTextTools import *
from matrixTools import *
from validationTools import validate_and_load_conf

class Evolution():

    def __init__(self,sizeX,sizeY,tileSize,dispSurface):
        self.sizeX = sizeX #resolution X
        self.sizeY = sizeY #resolution Y
        self.tileSize = tileSize
        self.tile_center = self.tileSize/2
        self.tilesX = int(sizeX/self.tileSize)
        self.tilesY = int(sizeY/self.tileSize)
        self.dispSurface = dispSurface
        self.loadConfig()
        self.map = Map(self.tilesX,self.tilesY,self.tileSize)
        self.map.setFertility(1/self.fertility,self.fertileFields,self.fertileFieldRadius)
        self.map.set_theme_stuff(self.theme['map_fg_color'],self.theme['map_bg_color'],self.theme['fertile_color'], self.theme['fg_percent_range'])
        self.map.generateMapImg()
        self.map.deathTilesCount = self.deathTilesCount
        self.map.addDangerTiles(self.theme_folder + '/danger/')
        self.map.addFertility()
        self.init_font_stuff()
        self.map.save()
        self.map.mapImg = self.map.mapImg.convert()
        self.populationPositions = list()#lokace vsech zuvaku ve formatu [x,y]. v jednom bode muze byt vic nez jeden zuvak
        self.pupulationNumber = self.startPopulation
        self.grid = [[[] for i in range(0,self.tilesY)] for i in range(0,self.tilesX)]  #matrix se samotnymy objekty Zuvaku
        self.generateStartPopulation()
        self.foodPositions = list()
        self.foodGrid = [[None for i in range(0,self.tilesY)] for i in range(0,self.tilesX)]
        self.initFoodSprites()
        self.activeEventBanners = list()
        self.shared_food_list = None
        self.update_cntr = 0
        self.graph = False
        self.cycle_stats = list()

    def generateStartPopulation(self):
        #vygenerovani zacateci populace
        for i in range(0,self.startPopulation):
            ag = random.uniform(0,1)
            iq = random.uniform(0,1)
            sz = random.uniform(0.2,1)
            newZuvak = Zuvak(iq,sz,ag,1)
            newZuvak.img = newZuvak.img.convert()
            while True:
                rp = RandomPos((0,self.tilesX-1),(0,self.tilesY-1))
                rp = [rp.x,rp.y]
                if not (rp in self.map.deathTiles) or (rp in self.populationPositions):
                    break     
            self.populationPositions.append(rp)
            self.grid[rp[0]][rp[1]].append(newZuvak)

    def update(self):
        # tuto metodu vola modul manager.py kazdy frame
        self.update_cntr +=1
        if  self.update_cntr > self.graph_update_rate:
            self.graph = True
        self.updateFood()
        self.updateZuvaks()
        self.updatePopulationCounter()
        self.updateEventBanners()

    def updateFood(self):
        self.updateFoodList()
        self.drawFood()

    def update_and_draw_food(self):
        '''metoda pro neparalelni vykreslovani jidla na mapu'''

        for fertileTile in self.map.fertileTiles:
            fPos = [
                fertileTile.pos.x,
                fertileTile.pos.y
                ]
            isEmpty = not(fPos in self.foodPositions)
            if isEmpty:
                doGenerate = decideBasedOnProbability(fertileTile.fertility*0.05)
                if doGenerate:
                    rndFoodObj = random.choice(self.foodSprites)
                    self.foodPositions.append(fPos)
                    self.foodGrid[fPos[0]][fPos[1]]=rndFoodObj
        for foodPos in self.foodPositions:
            foodObj = self.foodGrid[foodPos[0]][foodPos[1]]
            blitOffset = (foodPos[0]*self.tileSize,foodPos[1]*self.tileSize)
            self.dispSurface.blit(foodObj.surf,blitOffset)            

    def updateFoodList(self):
        '''metoda ceka na vystup paralelniho pracovnika, ktery
           vypocita pozice noveho jidla. Dale data zpracuje a ulozi do pameti'''

        new_f_pos = self.shared_food_list.get()
        new_f_pos = set(tuple(row) for row in new_f_pos) # convert new positions to set
        f_pos_set = set(tuple(row) for row in self.foodPositions)#convert old positions to set
        new_f_pos_unique = new_f_pos-f_pos_set
        for f_pos in new_f_pos_unique:
            x,y = f_pos
            rndFoodObj = random.choice(self.foodSprites)
            self.foodGrid[x][y]=rndFoodObj
            self.foodPositions.append([x,y])
    
    def drawFood(self):            
        '''vukreslovani jidla obdrzeneho od paralelniho procesu na mapu'''

        for foodPos in self.foodPositions:
            foodObj = self.foodGrid[foodPos[0]][foodPos[1]]
            blitOffset = (foodPos[0]*self.tileSize,foodPos[1]*self.tileSize)
            self.dispSurface.blit(foodObj.surf,blitOffset)

    def updateEventBanners(self):
        '''Vyvolani aktualizace animaci banneru'''

        for banner in self.activeEventBanners:
            if banner.finished:
                self.activeEventBanners.remove(banner)
                continue
            banner.nextFrame()

    def initFoodSprites(self):
        '''nacteni obrazku jidla'''

        try:
            er = self.conf["food"]['energyRange']
        except:
            raise BadFileFormatError("Config file in bad format, see documentation")
        energyRangeFrom = er[0]
        energyRangeTo = er[1]    
        energy = random.randint(energyRangeFrom,energyRangeTo)
        path_to_food = self.theme_folder + '/food/*.png'
        fNames = glob.glob(path_to_food)
        self.foodSprites = list()
        for fn in fNames:
            food = Food(fn,self.tileSize,energy)
            self.foodSprites.append(food)

    def init_font_stuff(self):
        '''nacteni fontu'''

        self.font_fg = (255, 240, 31)
        self.font_bg = (0,0,0)
        self.counter_font = pygame.font.Font('freesansbold.ttf', 15)

    def updatePopulationCounter(self):
        textContent = f"population: {self.pupulationNumber}"
        text = self.counter_font.render(textContent , True, self.font_fg, self.font_bg)
        self.dispSurface.blit(text,(25,25))


    def updateZuvaks(self):
        '''Tato metoda projede seznamem brouku a za kazdeho udela tah
        Ma take na starosi detekci prekazek, rozmnozovani brouku atd..'''

        self.pupulationNumber = 0
        self.bDispTCycles = self.eventBannerDispTime * self.fps
        ts = self.tileSize
        self.populationPositionsUpdated = list()
        self.gridUpdated = [[[] for i in range(0,self.tilesY)] for i in range(0,self.tilesX)] 
        for pos in self.populationPositions: #cyklus projizdi kazdou lokaci, kde se nachazi 1 a vice zuvaku; # pos [x,y]
            zuvaksOnPos = self.grid[pos[0]][pos[1]]
            for zuvak in zuvaksOnPos:

                if not zuvak.in_fight and not zuvak.being_attacked:
                    zuvak.nextCycle()

                in_fight = zuvak.in_fight
                not_alone = len(self.populationPositions) >= 2
                wtf = zuvak.wants_to_fight(self.agresivityKoef)

                if (not in_fight) and wtf and not_alone: #-> inciace boje
                    oponent = self.find_nearest_oponent(pos)
                    if oponent != None:
                        oponent.being_attacked = True
                        zuvak.start_fight(pos,oponent.pos,oponent)

                if zuvak.in_fight: 
                    if zuvak.fought_rounds >= self.frames_per_fight:
                        result = zuvak.end_fight()
                        winner,loser = result
                        zuvak = winner
                        zuvak.being_attacked = False
                        pos = winner.pos
                        loser.alive = False
                    else:
                        if zuvak.fought_rounds < 2:
                            zuvak.update_difference_vector()
                        self.attack_animator.draw_frame(zuvak.fought_rounds,
                        zuvak.pos,
                        zuvak.vector_to_oponent)
                        zuvak.next_fight_round()    
                    
                ##--generate new move 
                not_in_fight = not zuvak.in_fight and not zuvak.being_attacked
                if not_in_fight:
                    newPos = self.get_next_move(pos,False)
                    inDeathTiles = newPos in self.map.deathTiles
                    if inDeathTiles:
                        zuvaksProbOfMakingLogicalDecision = (1-self.iqKoef+(zuvak.iq*self.iqKoef))                
                        avoidedLavaDeath = decideBasedOnProbability(zuvaksProbOfMakingLogicalDecision)
                        if not avoidedLavaDeath: #zuvak spadl do lavy
                            zuvak.alive = False
                            newPosInPixels = [newPos[0]*self.tileSize,newPos[1]*self.tileSize]
                            lavaDeath = deathBanner(self.dispSurface,self.bDispTCycles,newPosInPixels)
                            self.activeEventBanners.append(lavaDeath)
                        #newPos = self.getZuvaksNextMove(pos,True)
                        newPos = self.get_next_move(pos,True)
                else:
                    inDeathTiles = False
                    newPos = pos     

                steppedOnFood = newPos in self.foodPositions
                if steppedOnFood: # nacteni energie kdyz zuvak stoupne na jidlo
                    foodBanner = textEventBanner(self.dispSurface,self.bDispTCycles,[pos[0]*ts,pos[1]*ts],'+',20,(0,255,0))
                    self.activeEventBanners.append(foodBanner)
                    zuvak.activeBanner = foodBanner
                    foodOnPos = self.foodGrid[newPos[0]][newPos[1]]
                    zuvak.fatStorage = zuvak.fatStorage + foodOnPos.energy
                    self.foodPositions.remove(newPos)

                if zuvak.activeBanner != None:
                    if zuvak.activeBanner.finished:
                        zuvak.activeBanner = None
                    else:    
                        zuvak.activeBanner.setPos(newPos[0]*ts,newPos[1]*ts)
                    
                if zuvak.alive:
                    self.pupulationNumber += 1
                    zuvak.setPos(newPos) 
                    if newPos in self.populationPositionsUpdated:
                        partner = random.choice(self.gridUpdated[newPos[0]][newPos[1]])
                        minAge = self.zuvaksAdultAge
                        areOldEnough = zuvak.age > minAge  and partner.age > minAge
                        only2OnTile = len(self.gridUpdated[newPos[0]][newPos[1]]) == 1
                        
                        if only2OnTile and areOldEnough and not_in_fight:
                            child = zuvak.haveSex(partner,self.zuvaksSexEnergyReq)
                            if child != False:
                                sexBanner = textEventBanner(self.dispSurface,self.bDispTCycles*2,[newPos[0]*ts,newPos[1]*ts],'+1',20,(0,255,0))
                                child.activeBanner = sexBanner
                                self.activeEventBanners.append(sexBanner)
                                self.gridUpdated[newPos[0]][newPos[1]].append(child)
                    
                    self.gridUpdated[newPos[0]][newPos[1]].append(zuvak)
                    if self.graph:
                        self.cycle_stats.append([
                            zuvak.iq,
                            zuvak.size,
                            zuvak.agresivity
                        ])

                    angle = getImgOrientation(pos,newPos)
                    zuvakSurfaceRotated =  pygame.transform.rotate(zuvak.surf, angle)
                    cX,cY = zuvak.center
                    centeredPos = ((newPos[0]*ts+self.tile_center)-cX,(newPos[1]*ts+self.tile_center)-cY)
                    self.dispSurface.blit(zuvakSurfaceRotated,centeredPos)
                    if newPos not in self.populationPositionsUpdated:
                        self.populationPositionsUpdated.append(newPos)
                else:
                    if not inDeathTiles: #-> vyhladověl
                        newPosInPixels = [newPos[0]*self.tileSize,newPos[1]*self.tileSize]
                        db = deathBanner(self.dispSurface,self.bDispTCycles,newPosInPixels)
                        self.activeEventBanners.append(db)
    
        self.grid = self.gridUpdated.copy()
        self.populationPositions = self.populationPositionsUpdated.copy() 
        #print(self.graph)    
        if self.graph: 
            # pokud je zapnute vykreslovani grafu,
            # tak se poslou data o broucich paralelnimu procesu a ten z nich zpracuje graf
            self.update_cntr = 0
            self.graph = False
            self.shared_stats_q.put(
                self.cycle_stats.copy()
            )
            self.cycle_stats.clear()
              
        
    def grid_to_pix(self,pos):
        #prevod jednotek

        return [pos[0]*self.tileSize,pos[1]*self.tileSize]

    def pix_to_grid(self,pos):
        #prevod jednotek

        return [int(pos[0]/self.tileSize),int(pos[1]/self.tileSize)]

    def loadConfig(self):
        #Nacteni konfiguraku

        self = validate_and_load_conf(self)

    def get_next_move(self, current_pos, avoid_danger = False):
        wrapping_points = pos_of_wrapping_points_list_format(self.tilesX,self.tilesY,current_pos,1)
        if avoid_danger:
            for wp in wrapping_points:
                if wp in self.map.deathTiles:
                    wrapping_points.remove(wp)    
        new_pos =  random.choice(wrapping_points)   
        return new_pos                               

    def find_nearest_oponent(self,pos):
        '''tato metoda hleda zuvakovi protivnika'''

        radius = 1
        while True:
            wrapping_points = pos_of_wrapping_points_list_format(self.tilesX, self.tilesY, pos, radius)
            for point in wrapping_points:
                if point in self.populationPositions:
                    zuv_on_pos = self.grid[point[0]][point[1]]
                    for i in range(0, len(zuv_on_pos)):
                        z = zuv_on_pos[i]
                        if (not z.being_attacked) and (not z.in_fight):
                            return (z)
            radius = radius + 1
            if radius >= self.tilesX:
                return None       

def getImgOrientation(pos,newPos):
    "funkce vraci cislo v stupnich o kolik se ma sprite zuvaka otocit, kdyz popojde o policko"

    diffVector = [
        newPos[0] - pos[0],
        newPos[1]  - pos[1]
        ]
    if diffVector[0] != 0:
        return  int(
            (
                math.asin(diffVector[0]*-1) * 180 / math.pi)
            ) % 360
    else:
        return  int(
            (
                math.acos(diffVector[1]*-1)) * 180.0 / math.pi
            ) % 360



    
