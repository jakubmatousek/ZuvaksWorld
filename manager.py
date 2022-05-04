import pygame as p 
from pygame.locals import *
from evolution import Evolution
import json
from customErrors import *
import time
from evolutionTasks import *
from food import Food
from workers import FoodWorker
from workers import GraphMaker
import glob
from Zuvak import PILtoPygameImg
import os
import multiprocessing as mp
from drawingTools import AttackAnimator
from weatherStuff import StormAnimator

class Manager():
    ''' Tato trida spravuje okno samotnou simulaci (a pygame okno, v kterem se zobrazuje)
        , dale ma take na startost spoustet a synchronizovat paralelni procesy '''

    def __init__(self):
        self.fps = 0
        self.fpsLastCalcTime = time.time()
        self.loadConfig()
        p.init()
        self.dispSurface = p.display.set_mode((self.resX,self.resY))
        self.evolution = Evolution(self.resX,self.resY,self.tileSize,self.dispSurface)
        p.display.set_caption('Zuvak\'s world')
        self.font = p.font.Font('freesansbold.ttf', 15)    
        self.lastfpsSprite = self.font.render('0' , True, (255, 240, 31),(0,0,0))
        self.show_graph = True
        self.graph_size_ratio = 1/3  
        self.graph_size = int(self.resX * self.graph_size_ratio)    
        self.graph_pos = None
        self.init_food_worker()
        self.init_graph_worker()
        self.init_graph()
        self.update_graph()
        self.init_drawing_tools()
        self.init_storm()     
        self.startGame()              

        
    def loadConfig(self):
        #nascteni conf souboru
        try:
            with open('conf.json') as json_file:
                self.conf = json.load(json_file)
        except:
            raise FileNotFoundError("connection config file not found")
        try:
            self.resX = self.conf["resX"]
            self.resY = self.conf["resY"]
            self.tileSize = self.conf["tileSize"]
            self.conf["numberOfFertileFields"]
            self.conf["numberOfDangerFields"]
            self.conf['theme']['arrow_len']

        except:
            raise BadFileFormatError("Config file in bad format, see documentation")

    def init_storm(self):
        #spusteni animace bourky 
        sl = self.conf['storm_len']
        sp = self.conf['storm_prob']
        self.storm_animator = StormAnimator(sl,
         self.conf['fps'],
         self.resX,
         self.resY,
         self.dispSurface,
         sp)
    
    def init_drawing_tools(self):
        #spusteni animaci boje
        arrow_len = self.conf['theme']['arrow_len']
        if arrow_len <= 3:
            arrow_len = None
        aa =  AttackAnimator(self.dispSurface,
                             self.tileSize,
                             arrow_len)
        self.evolution.attack_animator = aa 

    def updateFPScounter(self):
        # tato funkce vykresli hodnotu FPS (frames per second) na obrazovku
        bannerTxt = f"FPS: {self.fps}"
        text = self.font.render(bannerTxt , True, (255, 240, 31),(0,0,0))
        self.dispSurface.blit(text,((self.resX-70),25))
        self.fpsLastCalcTime = time.time()
        self.lastfpsSprite = text
        self.evolution.fps = self.fps
        self.fps = 0

    def init_food_worker(self):
        # funkce spousti paralelni proces v kterem se vypocitavaji pozice nově spwannuteho jidla
        try:
            self.evolution
        except:
            m = 'must init evolution obj, before initing food worker!'
            raise logicError(m)
        self.shared_food_queue = mp.Queue() 
        self.evolution.shared_food_list = self.shared_food_queue   
        f_pos = self.evolution.foodPositions
        f_tiles = self.evolution.map.fertileTiles
        fps = self.conf['fps']
        worker = FoodWorker(f_pos,f_tiles,self.shared_food_queue,fps,5)
        proc = mp.Process(target=worker.start, args=())
        proc.daemon = True
        proc.start()

    def init_graph_worker(self):
        # funkce spousti paralelni proces v kterem se zpracovavaji a zvizualizovavaji grafem data o simluaci 
        self.graph_update_rate = int(self.conf['fps']/5)
        self.shared_stats_q = mp.Queue() 
        self.graph_output_q = mp.Queue()
        self.evolution.shared_stats_q = self.shared_stats_q
        self.evolution.graph_update_rate = self.graph_update_rate
        size = int(self.resX * self.graph_size_ratio)
        gm = GraphMaker(self.shared_stats_q,self.graph_output_q, size)
        proc = mp.Process(target=gm.start, args=())
        proc.daemon = True
        proc.start()
        self.shared_stats_q.put([[0,0,0],[0,0,0]])

    def init_graph(self):
        #vypocet pozice grafu
        pos = (
            int(self.resX - self.graph_size*5/4),
            int(self.resY/2 - self.graph_size/2)
        )  
        self.graph_pos = pos
        

    def draw_graph(self):
        #vykreslit graf na obrazovku
        try:
            self.dispSurface.blit(
                self.graph_img,
                self.graph_pos
            )
            self.update_graph()
        except:    
            pass        

    def update_graph(self):
        #nacist aktualizovany graf od paralelniho procesu a nacist do pameti
        if self.graph_output_q.qsize() > 0:
            new_g = self.graph_output_q.get()
            new_g = PILtoPygameImg(new_g)
            #new_g.set_colorkey((0,0,0))
            self.graph_img = new_g
 

    def init_zuvaks_worker(self):
        try:
            self.evolution
        except:
            m = 'must init evolution obj, before initing zuvaks worker!'
            raise logicError(m)
        deaths_births = mp.Queue()
        new_positions = mp.Queue()
        
    def displayFPSCounter(self):
        self.dispSurface.blit(self.lastfpsSprite,((self.resX-70),25))

    def startGame(self):
        # hlavni cyklus simulace
        self.clock = p.time.Clock()
        notQuit = True
        p.init()
        
        mapImp = p.image.load(self.evolution.map.mapImgPath)
        self.dispSurface.blit(mapImp,(0,0))
        self.evolution.update() 
        while notQuit:
            for event in p.event.get():
                if event.type == QUIT:
                    notQuit = False
            
                if event.type == p.KEYDOWN:
                    if event.key == p.K_ESCAPE:
                        notQuit = False 
                    if event.key == p.K_UP or event.key == 13:
                        self.show_graph =  not self.show_graph         
            self.dispSurface.blit(mapImp,(0,0))
                 
            self.evolution.update()
            self.storm_animator.update()
            if self.show_graph:
                self.draw_graph()   
            self.fps+=1
            if time.time()  - self.fpsLastCalcTime >= 1:
                self.updateFPScounter()
            else:
                self.displayFPSCounter()     
            
            p.display.update()    
            self.clock.tick(self.conf["fps"])    






if __name__ == "__main__":
    Manager()



